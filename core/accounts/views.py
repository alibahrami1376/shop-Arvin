from django.contrib.auth import get_user_model, login, views as auth_views
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from accounts.forms import AuthenticationForm, UserRegistrationForm
from accounts.models import ensure_user_profile

User = get_user_model()

AUTH_BACKEND = "accounts.backends.EmailOrPhoneBackend"


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    form_class = AuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    pass


class RegisterView(FormView):
    template_name = "accounts/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            user = User.objects.create_customer(
                password=form.cleaned_data["password1"],
                email=form.cleaned_data.get("email"),
                is_verified=False,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        profile = ensure_user_profile(user)
        profile.first_name = form.cleaned_data.get("first_name", "")
        profile.last_name = form.cleaned_data.get("last_name", "")
        profile.save(update_fields=["first_name", "last_name", "updated_date"])
        login(self.request, user, backend=AUTH_BACKEND)
        return redirect(self.get_success_url())
