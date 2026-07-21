from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.password_validation import validate_password
from accounts.models import UserType

User = get_user_model()

USER_TYPE_LABELS = {
    UserType.customer.value: "مشتری",
    UserType.admin.value: "ادمین",
    UserType.marketer.value: "مارکتر",
    UserType.editor.value: "ویراستار",
    UserType.support.value: "پشتیبانی",
}

SELECTABLE_USER_TYPE_CHOICES = [
    (value, label) for value, label in USER_TYPE_LABELS.items()
]


class UserForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "email",
            "type",
            "is_active",
            "is_verified",
        ]

    def __init__(self, *args, **kwargs):
        self.can_change_type = kwargs.pop("can_change_type", False)
        super().__init__(*args, **kwargs)

        self.fields["email"].widget.attrs["class"] = "form-control mx-3 Disabled text-center mb-3"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["is_verified"].widget.attrs["class"] = "form-check-input"

        if self.can_change_type:
            self.fields["type"].choices = SELECTABLE_USER_TYPE_CHOICES
            self.fields["type"].widget.attrs["class"] = "form-select mb-3"
        else:
            self.fields.pop("type", None)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email") or None
        user_type = cleaned_data.get("type", getattr(self.instance, "type", None))

        if self.can_change_type:
            if user_type == UserType.superuser.value:
                self.add_error("type", "امکان انتخاب سوپریوزر وجود ندارد.")
        else:
            cleaned_data["type"] = self.instance.type
            user_type = self.instance.type

        if user_type and user_type != UserType.customer.value and not email:
            self.add_error("email", "برای این نوع کاربر، ایمیل الزامی است.")

        cleaned_data["email"] = email
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if not self.can_change_type:
            user.type = self.instance.type
        if user.type == UserType.admin.value:
            user.is_staff = True
        elif not user.is_superuser:
            user.is_staff = False
        if commit:
            user.save()
        return user


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3"}),
    )
    password2 = forms.CharField(
        label="تکرار رمز عبور",
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3"}),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "phone_number",
            "type",
            "is_active",
            "is_verified",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["phone_number"].required = False
        self.fields["type"].choices = SELECTABLE_USER_TYPE_CHOICES
        self.fields["type"].initial = UserType.customer.value
        self.fields["email"].widget.attrs["class"] = "form-control mb-3"
        self.fields["phone_number"].widget.attrs["class"] = "form-control mb-3"
        self.fields["type"].widget.attrs["class"] = "form-select mb-3"
        self.fields["is_active"].widget.attrs["class"] = "form-check-input"
        self.fields["is_verified"].widget.attrs["class"] = "form-check-input"
    
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            validate_password(password)
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email") or None
        phone_number = cleaned_data.get("phone_number") or None
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        user_type = cleaned_data.get("type")

        if user_type == UserType.superuser.value:
            self.add_error("type", "امکان انتخاب سوپریوزر وجود ندارد.")

        if not email and not phone_number:
            raise forms.ValidationError("حداقل یکی از ایمیل یا شماره موبایل الزامی است.")

        if user_type and user_type != UserType.customer.value and not email:
            self.add_error("email", "برای این نوع کاربر، ایمیل الزامی است.")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "رمز عبور و تکرار آن یکسان نیستند.")

        cleaned_data["email"] = email
        cleaned_data["phone_number"] = phone_number
        return cleaned_data

    def save(self, commit=True):
        email = self.cleaned_data.get("email")
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data["password1"]
        user_type = self.cleaned_data.get("type", UserType.customer.value)
        user = User.objects.create_customer(
            email=email,
            phone_number=phone_number,
            password=password,
            phone_verified=bool(phone_number),
            type=user_type,
            is_staff=(user_type == UserType.admin.value),
            is_active=self.cleaned_data.get("is_active", True),
            is_verified=self.cleaned_data.get("is_verified", False),
        )
        return user
