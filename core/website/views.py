from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce

from blog.models import Post
from order.models import OrderStatusType
from shop.models import ProductModel, ProductStatusType

from .models import *
from .forms import ContactForm, NewsLetterForm
from django.contrib import messages
from django.views.generic import CreateView
from django.shortcuts import redirect
from django.urls import reverse_lazy
# Create your views here.

class IndexView(TemplateView):
    template_name = "website/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        published = ProductStatusType.publish.value
        order_success = OrderStatusType.success.value

        base = ProductModel.objects.filter(status=published).prefetch_related(
            "category"
        )

        context["top_products"] = base.order_by("-avg_rate", "-created_date")[:8]
        context["newest_products"] = base.order_by("-created_date")[:8]
        context["bestseller_products"] = (
            base.annotate(
                sold_qty=Coalesce(
                    Sum(
                        "orderitemmodel__quantity",
                        filter=Q(orderitemmodel__order__status=order_success),
                    ),
                    Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("-sold_qty", "-avg_rate")[:8]
        )

        context["latest_posts"] = (
            Post.objects.filter(status=True)
            .select_related("author")
            .prefetch_related("category")
            .order_by("-published_date", "-created_date")[:4]
        )

        return context

class ContactView(TemplateView):
    template_name = "website/contact.html" 
    
class AboutView(TemplateView):
    template_name = "website/about.html" 
    
    
class SendContactView(CreateView):
    """
    a class based view to show index page
    """
    http_method_names = ['post']
    form_class = ContactForm
    success_url = reverse_lazy('website:contact')

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request, 'تیکت شما با موفقیت ثبت شد و در اسرع وقت با شما تماس حاصل خواهد شد')
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, 'مشکلی در ارسال فرم شما پیش آمد لطفا ورودی ها رو بررسی کنین و مجدد ارسال نمایید')
        return redirect('website:contact')
    
class NewsletterView(CreateView):
    http_method_names = ['post']
    form_class = NewsLetterForm
    success_url = '/'

    def form_valid(self, form):
        # handle successful form submission
        messages.success(
            self.request, 'از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم 😊👍')
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, 'مشکلی در ارسال فرم شما وجود داشت که می دونم برا چی بود!! چون ربات هستید!')
        return redirect('website:index')