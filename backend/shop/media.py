"""Bounded image decoding and storage-backed responsive renditions for admin uploads."""

from io import BytesIO
import uuid
import warnings

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_PIXELS = 25_000_000
FORMATS = {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}


def decode_upload(value):
    try:
        value.seek(0)
        raw = value.read(MAX_UPLOAD_BYTES + 1)
        value.seek(0)
        if len(raw) > MAX_UPLOAD_BYTES:
            raise ValidationError("Upload an image no larger than 8 MB.")
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(raw)) as probe:
                if probe.format not in FORMATS:
                    raise ValidationError("Only JPEG, PNG and WebP images are supported.")
                extension = FORMATS[probe.format]
                if probe.width * probe.height > MAX_PIXELS:
                    raise ValidationError("Images must contain no more than 25 million pixels.")
                if getattr(probe, "n_frames", 1) != 1:
                    raise ValidationError(
                        "Upload a still image; animated images are not supported."
                    )
                probe.verify()
            with Image.open(BytesIO(raw)) as source:
                source.load()
                oriented = ImageOps.exif_transpose(source)
                decoded = oriented.convert("RGBA" if "A" in oriented.getbands() else "RGB")
        return raw, extension, decoded
    except ValidationError:
        raise
    except (
        OSError,
        ValueError,
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ValidationError("Upload a valid JPEG, PNG or WebP image.") from exc


def validate_upload(value):
    # Existing stored names are trusted application records, not a new upload.
    if value and not getattr(value, "_committed", False):
        decode_upload(value)


def webp(decoded, width):
    resized = decoded.copy()
    if resized.width > width:
        resized = resized.resize(
            (width, max(1, round(resized.height * width / resized.width))), Image.Resampling.LANCZOS
        )
    stream = BytesIO()
    resized.save(stream, format="WEBP", quality=85, method=4)
    return ContentFile(stream.getvalue()), resized.size


class ProcessedImageFile(ImageFieldFile):
    def save(self, name, content, save=True):
        raw, extension, decoded = decode_upload(content)
        token = uuid.uuid4().hex
        # ProductImage retains the validated original and responsive image names.
        # Storage.url is resolved at read time, supporting local and S3 backends.
        if self.field.name == "image" and hasattr(self.instance, "renditions"):
            original = self.instance.original
            original.save(f"{token}.{extension}", ContentFile(raw), save=False)
            renditions = {}
            for width in (160, 480, 800, 1200, 1600):
                if width >= decoded.width:
                    continue
                rendered, (actual_width, height) = webp(decoded, width)
                path = self.field.generate_filename(self.instance, f"{token}-{width}.webp")
                stored = self.storage.save(path, rendered)
                renditions[str(actual_width)] = {"name": stored, "height": height}
            self.instance.renditions = renditions
        rendered, _ = webp(decoded, 2000)
        # Django's image descriptor treats an unnamed ContentFile as empty and
        # clears its dimension fields when ImageFieldFile.save assigns it.
        rendered.name = f"{token}.webp"
        super().save(f"{token}.webp", rendered, save=save)


class ProcessedImageField(ImageField):
    attr_class = ProcessedImageFile
    default_validators = [validate_upload]
