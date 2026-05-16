from django import forms
from django.utils import timezone
from payment.models import PaymentMethodType

from order.models import CouponModel, UserAddressModel


class CheckOutForm(forms.Form):
    address_id = forms.IntegerField(required=True)
    coupon = forms.CharField(required=False)
    payment_method = forms.TypedChoiceField(
        coerce=int,
        choices=PaymentMethodType.choices,
        initial=PaymentMethodType.gateway.value,
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(CheckOutForm, self).__init__(*args, **kwargs)
        
    def clean_address_id(self):
        address_id = self.cleaned_data.get('address_id')

        # Check if the address_id belongs to the requested user
        user = self.request.user  # Assuming the user is available in the request object
        try:
            address = UserAddressModel.objects.get(id=address_id, user=user)
        except UserAddressModel.DoesNotExist:
            raise forms.ValidationError("Invalid address for the requested user.")

        return address
    
    def clean_coupon(self):
        code = self.cleaned_data.get('coupon')
        if code == "":
            return None
        # Check if the address_id belongs to the requested user
        user = self.request.user  # Assuming the user is available in the request object
        coupon = None
        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            raise forms.ValidationError("کد تخفیف اشتباه است")
        if coupon:

            if coupon.used_by.count() >= coupon.max_limit_usage:
                raise forms.ValidationError("محدودیت در تعداد استفاده")


            if coupon.expiration_date and coupon.expiration_date < timezone.now():
                raise forms.ValidationError("کد تخفیف منقضی شده است")


            if user in coupon.used_by.all():
                raise forms.ValidationError("این کد تخفیف قبلا توسط شما استفاده شده است")

        return coupon


class OrderTrackingForm(forms.Form):
    tracking_code = forms.CharField(
        label="کد سفارش",
        max_length=7,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "مثال: 123456",
                "autocomplete": "off",
                "dir": "ltr",
                "inputmode": "numeric",
                "pattern": "[0-9]{5,7}",
            }
        ),
    )

    def clean_tracking_code(self):
        code = self.cleaned_data["tracking_code"].strip()
        if not code:
            raise forms.ValidationError("کد سفارش را وارد کنید.")
        if not code.isdigit() or not (5 <= len(code) <= 7):
            raise forms.ValidationError("کد سفارش باید عددی ۵ تا ۷ رقمی باشد.")
        return code