from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from accounts.models import UserType


class DashboardHomeView(LoginRequiredMixin,View):
    
    def dispatch(self, request,*args, **kwargs):
                                        
        if request.user.is_authenticated:
            user_type = request.user.type 
            if user_type == UserType.customer.value:
                return redirect(reverse_lazy('dashboard:customer:home'))
            if user_type == UserType.admin.value  or user_type == UserType.superuser.value:
                return redirect(reverse_lazy('dashboard:admin:home'))
        else:
            return redirect(reverse_lazy('accounts:login'))
        return super().dispatch(request, *args, **kwargs)
    