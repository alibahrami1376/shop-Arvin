"""Shared payment finalization helpers."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from order.models import OrderModel, OrderStatusType

from .models import PaymentModel, PaymentStatusType

logger = logging.getLogger(__name__)

_SUCCESS_PAYMENT_STATUSES = {
    PaymentStatusType.preparing.value,
    PaymentStatusType.shipped.value,
}


def order_already_paid(
    order: OrderModel, *, excluding_payment_id: int | None = None
) -> bool:
    """True if the order is already successfully paid (possibly via another attempt)."""
    if order.status == OrderStatusType.success.value:
        return True

    pay = order.payment
    if pay is None:
        return False
    if excluding_payment_id is not None and pay.pk == excluding_payment_id:
        return False
    return pay.status in _SUCCESS_PAYMENT_STATUSES


@transaction.atomic
def mark_payment_success(
    payment: PaymentModel,
    *,
    response_json=None,
    response_code: int | None = None,
    ref_id=None,
    bale_telegram_payment_charge_id: str | None = None,
    bale_provider_payment_charge_id: str | None = None,
) -> bool:
    """
    Mark payment + related order as successful (idempotent).

    Returns True if this call transitioned the payment to success,
    False if already successful or the order was paid by another attempt.
    """
    locked = PaymentModel.objects.select_for_update().get(pk=payment.pk)
    if locked.status in _SUCCESS_PAYMENT_STATUSES:
        return False

    order = OrderModel.objects.select_for_update().filter(payment=locked).first()
    if order is not None and order_already_paid(order, excluding_payment_id=locked.pk):
        logger.warning(
            "mark_payment_success skipped; order already paid order=%s payment=%s",
            order.pk,
            locked.pk,
        )
        return False

    if response_json is not None:
        locked.response_json = response_json
    if response_code is not None:
        locked.response_code = response_code
    if ref_id is not None:
        locked.ref_id = ref_id
    if bale_telegram_payment_charge_id:
        locked.bale_telegram_payment_charge_id = bale_telegram_payment_charge_id
    if bale_provider_payment_charge_id:
        locked.bale_provider_payment_charge_id = bale_provider_payment_charge_id

    locked.status = PaymentStatusType.preparing.value
    locked.save()

    if order is not None:
        order.status = OrderStatusType.success.value
        order.save(update_fields=["status", "updated_date"])

    return True


@transaction.atomic
def mark_payment_failed(
    payment: PaymentModel,
    *,
    response_json=None,
    response_code: int | None = None,
) -> bool:
    """Mark payment + order failed; no-op if already terminal success."""
    locked = PaymentModel.objects.select_for_update().get(pk=payment.pk)
    if locked.status in _SUCCESS_PAYMENT_STATUSES:
        return False
    if locked.status == PaymentStatusType.payment_failed.value:
        return False

    if response_json is not None:
        locked.response_json = response_json
    if response_code is not None:
        locked.response_code = response_code
    locked.status = PaymentStatusType.payment_failed.value
    locked.save()

    order = OrderModel.objects.select_for_update().filter(payment=locked).first()
    if order is not None and order.status != OrderStatusType.success.value:
        order.status = OrderStatusType.failed.value
        order.save(update_fields=["status", "updated_date"])
    return True


def payment_status_payload(payment: PaymentModel, order: OrderModel) -> dict:
    """JSON-friendly status for Bale payment polling."""
    from django.urls import reverse

    status = payment.status
    order_paid = order.status == OrderStatusType.success.value
    if status in _SUCCESS_PAYMENT_STATUSES or order_paid:
        return {
            "status": "success",
            "redirect_url": reverse("order:completed"),
        }
    if status == PaymentStatusType.payment_failed.value:
        return {
            "status": "failed",
            "redirect_url": reverse("order:failed"),
        }
    if status == PaymentStatusType.cancelled.value:
        return {
            "status": "cancelled",
            "redirect_url": reverse("order:failed"),
        }
    expired = not payment.is_link_token_valid()
    return {
        "status": "awaiting",
        "expired": expired,
        "expires_at": (
            payment.link_token_expires_at.isoformat()
            if payment.link_token_expires_at
            else None
        ),
        "server_time": timezone.now().isoformat(),
        "tracking_code": order.tracking_code,
        "amount": int(payment.amount),
    }


def inquire_transaction_matches_payment(tx: dict, payment: PaymentModel) -> bool:
    """Validate inquireTransaction payload against our payment attempt."""
    if not isinstance(tx, dict):
        return False
    status = (tx.get("status") or tx.get("Status") or "").lower()
    if status != "paid":
        return False

    tx_id = str(tx.get("id") or tx.get("transaction_id") or "")
    expected_ids = {
        str(x)
        for x in (
            payment.bale_telegram_payment_charge_id,
            payment.bale_pre_checkout_id,
            payment.bale_provider_payment_charge_id,
        )
        if x
    }
    if expected_ids and tx_id and tx_id not in expected_ids:
        return False

    amount = tx.get("amount")
    if amount is not None and int(amount) != payment.amount_rial:
        return False

    user_id = tx.get("userID") or tx.get("user_id") or tx.get("userId")
    if (
        user_id is not None
        and payment.bale_chat_id
        and str(user_id) != str(payment.bale_chat_id)
    ):
        return False

    return True
