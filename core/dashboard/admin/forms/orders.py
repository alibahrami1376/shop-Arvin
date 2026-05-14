from django import forms

from order.models import OrderModel
from payment.models import PaymentModel


class AdminOrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ("status",)
        labels = {"status": "وضعیت سفارش"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.setdefault("class", "form-select")


class AdminPaymentStatusForm(forms.ModelForm):
    """وضعیت پرداخت/ارسال؛ prefix برای جلوگیری از تداخل id با فرم وضعیت سفارش."""

    class Meta:
        model = PaymentModel
        fields = ("status",)
        labels = {"status": "مرحلهٔ پرداخت و ارسال"}

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("prefix", "payment")
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.setdefault("class", "form-select")
