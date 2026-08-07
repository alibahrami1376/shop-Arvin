from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile

User = get_user_model()


class AdminPasswordChangeForm(auth_forms.PasswordChangeForm):
    error_messages = {
        "password_incorrect": _(
            "پسورد قبلی شما اشتباه وارد شده است، لطفا تصحیح نمایید."
        ),
        "password_mismatch": _("دو پسورد ورودی با همدیگر مطابقت ندارند"),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget.attrs["class"] = "form-control text-center"
        self.fields["new_password1"].widget.attrs["class"] = "form-control text-center"
        self.fields["new_password2"].widget.attrs["class"] = "form-control text-center"
        self.fields["old_password"].widget.attrs["placeholder"] = (
            "پسورد قبلی خود را وارد نمایید"
        )
        self.fields["new_password1"].widget.attrs["placeholder"] = (
            "پسورد جایگزین خود را وارد نمایید"
        )
        self.fields["new_password2"].widget.attrs["placeholder"] = (
            "پسورد جایگزین خود را مجدد وارد نمایید"
        )


class AdminProfileEditForm(forms.ModelForm):
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=20,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control text-center",
                "placeholder": "شماره همراه را وارد نمایید",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ["first_name", "last_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs["class"] = "form-control"
        self.fields["first_name"].widget.attrs["placeholder"] = "نام خود را وارد نمایید"
        self.fields["last_name"].widget.attrs["class"] = "form-control "
        self.fields["last_name"].widget.attrs["placeholder"] = (
            "نام خانوادگی را وارد نمایید"
        )
        if self.instance and self.instance.pk:
            self.fields["phone_number"].initial = self.instance.user.phone_number or ""

    def clean_phone_number(self):
        phone = User.objects.normalize_phone(self.cleaned_data["phone_number"])
        qs = User.objects.filter(phone_number=phone)
        if self.instance and self.instance.user_id:
            qs = qs.exclude(pk=self.instance.user_id)
        if qs.exists():
            raise forms.ValidationError("این شماره موبایل توسط کاربر دیگری استفاده شده است.")
        return phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
            profile.save()
        return profile
