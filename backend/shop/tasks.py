from celery import shared_task
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from .models import Outbox, Order
from .services import expire_order


@shared_task
def deliver_outbox():
    # SMTP has no universal exactly-once primitive. Records prevent normal duplicate sends;
    # a crash after SMTP acceptance and before commit may cause a duplicate delivery.
    for pk in Outbox.objects.filter(sent_at=None, attempts__lt=10).values_list("pk", flat=True)[
        :100
    ]:
        with transaction.atomic():
            row = Outbox.objects.select_for_update().get(pk=pk)
            if row.sent_at:
                continue
            row.attempts += 1
            try:
                send_mail(row.subject, row.body, None, [row.recipient], fail_silently=False)
                row.sent_at = timezone.now()
            except Exception:
                pass  # retry next sweep, never emit addresses or message bodies to error logs
            row.save(update_fields=["attempts", "sent_at"])


@shared_task
def expire_reservations():
    for pk in Order.objects.filter(
        status="payment_pending", expires_at__lte=timezone.now()
    ).values_list("pk", flat=True):
        expire_order(pk)
