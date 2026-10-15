"""Bale bot webhook handlers: /start, pre_checkout_query, successful_payment."""

from __future__ import annotations

import logging

from django.db import transaction
from django.utils import timezone
from order.models import OrderModel, OrderStatusType

from .bale_client import BaleAPIError, BaleClient, toman_to_rial
from .models import PaymentMethodType, PaymentModel, PaymentStatusType
from .services import mark_payment_success, order_already_paid

logger = logging.getLogger(__name__)

_SUCCESS_PAYMENT_STATUSES = {
    PaymentStatusType.preparing.value,
    PaymentStatusType.shipped.value,
}


def _client() -> BaleClient:
    return BaleClient()


def handle_update(update: dict) -> None:
    """Dispatch a single Bale Bot API update."""
    if not isinstance(update, dict):
        return

    if "pre_checkout_query" in update:
        handle_pre_checkout_query(update["pre_checkout_query"])
        return

    message = update.get("message") or update.get("edited_message")
    if not message:
        return

    if message.get("successful_payment"):
        handle_successful_payment(message)
        return

    text = (message.get("text") or "").strip()
    if text.startswith("/start"):
        handle_start(message, text)


def _order_stock_ok(order: OrderModel) -> bool:
    for item in order.order_items.select_related("product").all():
        product = item.product
        if product is None:
            continue
        stock = getattr(product, "stock", None)
        if stock is not None and item.quantity > stock:
            return False
    return True


@transaction.atomic
def handle_start(message: dict, text: str) -> None:
    client = _client()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if chat_id is None:
        return

    parts = text.split(maxsplit=1)
    token = parts[1].strip() if len(parts) > 1 else ""
    if not token:
        client.send_message(
            chat_id,
            "برای پرداخت سفارش، از صفحهٔ فروشگاه روی «باز کردن ربات بله» بزنید.",
        )
        return

    payment = (
        PaymentModel.objects.select_for_update()
        .filter(link_token=token, method=PaymentMethodType.bale.value)
        .order_by("-id")
        .first()
    )
    if payment is None:
        client.send_message(chat_id, "لینک پرداخت نامعتبر است.")
        return

    if payment.status in _SUCCESS_PAYMENT_STATUSES:
        client.send_message(chat_id, "این سفارش قبلاً پرداخت شده است.")
        return

    if payment.status != PaymentStatusType.awaiting_payment.value:
        client.send_message(chat_id, "این پرداخت دیگر قابل استفاده نیست.")
        return

    # Link expiry only blocks opening a new invoice.
    if not payment.is_link_token_valid():
        client.send_message(
            chat_id,
            "مهلت لینک پرداخت تمام شده است. لطفاً دوباره از سایت سفارش ثبت کنید.",
        )
        return

    order = OrderModel.objects.select_for_update().filter(payment=payment).first()
    if order is None:
        client.send_message(chat_id, "سفارش مرتبط پیدا نشد.")
        return

    if order_already_paid(order, excluding_payment_id=payment.pk):
        client.send_message(chat_id, "این سفارش قبلاً پرداخت شده است.")
        return

    if order.status == OrderStatusType.failed.value:
        client.send_message(chat_id, "این سفارش لغو یا ناموفق است.")
        return

    chat_id_str = str(chat_id)
    if payment.bale_chat_id and payment.bale_chat_id != chat_id_str:
        client.send_message(
            chat_id,
            "این لینک پرداخت قبلاً به حساب دیگری در بله متصل شده است.",
        )
        return

    if not payment.bale_chat_id:
        payment.bale_chat_id = chat_id_str
        payment.save(update_fields=["bale_chat_id", "updated_date"])

    tracking = order.tracking_code or str(order.pk)
    title = f"سفارش {tracking}"[:32]
    description = f"پرداخت سفارش {tracking} فروشگاه آروین"[:255]
    prices = [{"label": title, "amount": toman_to_rial(payment.amount)}]

    try:
        result = client.send_invoice(
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payment.authority_id,
            prices=prices,
        )
    except BaleAPIError as exc:
        logger.exception("sendInvoice failed for payment %s", payment.pk)
        client.send_message(
            chat_id,
            "ارسال صورتحساب ناموفق بود. لطفاً کمی بعد دوباره تلاش کنید.",
        )
        payment.response_json = {
            **(payment.response_json or {}),
            "sendInvoice_error": str(exc),
        }
        payment.save(update_fields=["response_json", "updated_date"])
        return

    msg_id = result.get("message_id") if isinstance(result, dict) else None
    payment.bale_invoice_message_id = msg_id
    payment.response_json = {
        **(payment.response_json or {}),
        "sendInvoice": result,
    }
    payment.save(
        update_fields=["bale_invoice_message_id", "response_json", "updated_date"]
    )


@transaction.atomic
def handle_pre_checkout_query(query: dict) -> None:
    client = _client()
    query_id = query.get("id")
    if not query_id:
        return

    query_id = str(query_id)
    payload = query.get("invoice_payload") or ""
    total_amount = query.get("total_amount")
    currency = (query.get("currency") or "").upper()
    payer = query.get("from") or {}
    payer_id = payer.get("id")

    payment = (
        PaymentModel.objects.select_for_update()
        .filter(authority_id=payload, method=PaymentMethodType.bale.value)
        .first()
    )

    # Persist id before answering so inquireTransaction can recover.
    if payment is not None:
        payment.bale_pre_checkout_id = query_id
        payment.save(update_fields=["bale_pre_checkout_id", "updated_date"])

    ok = True
    error_message = None

    if payment is None:
        ok = False
        error_message = "صورتحساب نامعتبر است."
    elif payment.status in _SUCCESS_PAYMENT_STATUSES:
        ok = False
        error_message = "این سفارش قبلاً پرداخت شده است."
    elif payment.status != PaymentStatusType.awaiting_payment.value:
        ok = False
        error_message = "این سفارش قابل پرداخت نیست."
    elif currency and currency != "IRR":
        ok = False
        error_message = "واحد پول نامعتبر است."
    elif int(total_amount or 0) != payment.amount_rial:
        ok = False
        error_message = "مبلغ صورتحساب با سفارش مطابقت ندارد."
    else:
        order = (
            OrderModel.objects.select_for_update()
            .filter(payment=payment)
            .prefetch_related("order_items__product")
            .first()
        )
        if order is None:
            ok = False
            error_message = "سفارش پیدا نشد."
        elif order.status == OrderStatusType.failed.value:
            ok = False
            error_message = "سفارش قابل پرداخت نیست."
        elif order_already_paid(order, excluding_payment_id=payment.pk):
            ok = False
            error_message = "این سفارش قبلاً پرداخت شده است."
        elif order.status != OrderStatusType.pending.value:
            ok = False
            error_message = "وضعیت سفارش برای پرداخت مناسب نیست."
        elif not _order_stock_ok(order):
            ok = False
            error_message = "موجودی کالا کافی نیست."
        elif (
            payment.bale_chat_id
            and payer_id is not None
            and str(payer_id) != str(payment.bale_chat_id)
        ):
            ok = False
            error_message = "پرداخت‌کننده با لینک سفارش مطابقت ندارد."
        # Link expiry intentionally ignored here.

    try:
        client.answer_pre_checkout_query(query_id, ok, error_message=error_message)
    except BaleAPIError:
        logger.exception("answerPreCheckoutQuery failed for %s", query_id)


@transaction.atomic
def handle_successful_payment(message: dict) -> None:
    sp = message.get("successful_payment") or {}
    payload = sp.get("invoice_payload") or ""
    total_amount = sp.get("total_amount")
    currency = (sp.get("currency") or "").upper()
    charge_id = sp.get("telegram_payment_charge_id")
    provider_charge_id = sp.get("provider_payment_charge_id")

    payment = (
        PaymentModel.objects.select_for_update()
        .filter(authority_id=payload, method=PaymentMethodType.bale.value)
        .first()
    )
    if payment is None:
        logger.warning("successful_payment unknown payload=%s", payload)
        return

    # Never reject a completed wallet charge because the deep-link expired.
    if currency and currency != "IRR":
        logger.error(
            "successful_payment currency mismatch payment=%s currency=%s",
            payment.pk,
            currency,
        )
        return

    if int(total_amount or 0) != payment.amount_rial:
        logger.error(
            "successful_payment amount mismatch payment=%s got=%s expected=%s",
            payment.pk,
            total_amount,
            payment.amount_rial,
        )
        return

    order = OrderModel.objects.select_for_update().filter(payment=payment).first()
    if order is not None and order_already_paid(order, excluding_payment_id=payment.pk):
        logger.warning(
            "successful_payment ignored; order %s already paid via another attempt",
            order.pk,
        )
        return

    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if (
        payment.bale_chat_id
        and chat_id is not None
        and str(chat_id) != str(payment.bale_chat_id)
    ):
        logger.error(
            "successful_payment chat mismatch payment=%s expected=%s got=%s",
            payment.pk,
            payment.bale_chat_id,
            chat_id,
        )
        return

    mark_payment_success(
        payment,
        response_json={
            **(payment.response_json or {}),
            "successful_payment": sp,
            "paid_at": timezone.now().isoformat(),
        },
        bale_telegram_payment_charge_id=str(charge_id) if charge_id else None,
        bale_provider_payment_charge_id=(
            str(provider_charge_id) if provider_charge_id else None
        ),
    )

    if chat_id is not None:
        try:
            _client().send_message(
                chat_id,
                "پرداخت با موفقیت انجام شد. می‌توانید به سایت برگردید.",
            )
        except BaleAPIError:
            logger.exception("post-payment thank-you message failed")
