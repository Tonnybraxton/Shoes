"""Plain structured merchandising values; no arbitrary HTML or remote redirects."""

from django.core.exceptions import ValidationError

TEXT_LIMITS = {"eyebrow": 100, "image_alt": 220, "footnote": 160, "edition": 80, "caption": 240}


def validate_local_href(value):
    if (
        not isinstance(value, str)
        or not value.startswith("/")
        or value.startswith("//")
        or "\\" in value
        or any(ord(char) < 32 for char in value)
        or len(value) > 200
    ):
        raise ValidationError("Use a local store link beginning with a single slash.")


def validate_section_settings(value):
    if not isinstance(value, dict):
        raise ValidationError({"settings": "Settings must be a JSON object."})
    for key, limit in TEXT_LIMITS.items():
        if key in value and (not isinstance(value[key], str) or len(value[key]) > limit):
            raise ValidationError(
                {"settings": f"{key} must be plain text up to {limit} characters."}
            )
    if "tiles" in value:
        tiles = value["tiles"]
        if not isinstance(tiles, list) or not 1 <= len(tiles) <= 6:
            raise ValidationError({"settings": "Provide between one and six category tiles."})
        for tile in tiles:
            if not isinstance(tile, dict):
                raise ValidationError({"settings": "Each tile must be an object."})
            for key, limit in {"title": 80, "subtitle": 160, "href": 200}.items():
                if (
                    not isinstance(tile.get(key), str)
                    or len(tile[key]) > limit
                    or (key != "subtitle" and not tile[key].strip())
                ):
                    raise ValidationError({"settings": f"Each tile requires valid {key} text."})
            try:
                validate_local_href(tile["href"])
            except ValidationError as exc:
                raise ValidationError({"settings": exc.messages}) from exc
