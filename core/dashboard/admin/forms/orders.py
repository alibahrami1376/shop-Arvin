from django import forms

from order.models import OrderModel


class AdminOrderStatusForm(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ("status",)
        labels = {"status": "وضعیت سفارش"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.setdefault("class", "form-select")
