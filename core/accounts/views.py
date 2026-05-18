from django.contrib.auth import views as auth_views, get_user_model, login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from accounts.forms import AuthenticationForm, UserRegistrationForm
from accounts.models import UserType
from core.mixins import DeviceTemplateMixin

User = get_user_model()


class LoginView(DeviceTemplateMixin, auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class RegisterView(DeviceTemplateMixin, FormView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = User.objects.create_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password1"],
            type=UserType.customer.value,
        )
        profile = user.user_profile
        profile.first_name = form.cleaned_data["first_name"]
        profile.last_name = form.cleaned_data["last_name"]
        profile.phone_number = form.cleaned_data["phone_number"]
        profile.save()
        login(self.request, user)
        return redirect(self.get_success_url())