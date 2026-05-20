from django.http import Http404
from django.views.generic import TemplateView
from django.db.models import IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce

from blog.models import Post
from order.models import OrderStatusType
from shop.models import ProductModel, ProductStatusType

from core.device import filter_queryset_for_device

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

        banners = HomeBanner.objects.filter(is_active=True)
        context["home_banners"] = filter_queryset_for_device(banners, self.request)

        return context

class ContactView(TemplateView):
    template_name = "website/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = ContactPageSettings.get_solo()
        context["contact_settings"] = settings
        context["contact_social_links"] = settings.get_social_links()
        context["faq_items"] = FAQItem.objects.filter(is_published=True)[:3]
        return context


class LegalPageView(TemplateView):
    template_name = "website/legal-page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_type = self.kwargs["page_type"]
        if page_type not in LegalPage.PageType.values:
            raise Http404()
        context["page"] = LegalPage.get_by_type(page_type)
        return context


class AboutView(TemplateView):
    template_name = "website/about.html"


class FAQView(TemplateView):
    template_name = "website/faq.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faq_items"] = FAQItem.objects.filter(is_published=True)
        return context


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