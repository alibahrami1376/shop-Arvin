from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from core.caching import (
    get_contact_settings,
    get_faq_published,
    get_home_banners,
    get_home_bestseller_products,
    get_home_latest_posts,
    get_home_newest_products,
    get_home_top_products,
    get_legal_page,
)
from core.device import get_device_type
from core.seo import faq_page_json_ld
from core.views_meta import SiteMetadataMixin

from .forms import ContactForm, NewsLetterForm
from .models import LegalPage


class IndexView(SiteMetadataMixin, TemplateView):
    template_name = "website/index.html"
    title = f"{settings.SITE_NAME}"
    description = (
        "فروشگاه آروین؛ خرید آنلاین صندلی راننده ماشین سنگین، نیمه‌سنگین و راهسازی "
        "مشاوره تخصصی، پشتیبانی مطمئن و  ارسال سریع به سراسر ایران."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device = get_device_type(self.request)

        context["top_products"] = get_home_top_products()
        context["newest_products"] = get_home_newest_products()
        context["bestseller_products"] = get_home_bestseller_products()
        context["latest_posts"] = get_home_latest_posts()
        context["home_banners"] = get_home_banners(device)

        return context


class ContactView(SiteMetadataMixin, TemplateView):
    template_name = "website/contact.html"
    title = f"تماس با ما - {settings.SITE_NAME}"
    description = (
        "تماس با فروشگاه آروین؛ تلفن، آدرس، شبکه‌های اجتماعی و فرم پیام. "
        "برای مشاوره خرید صندلی راننده ماشین سنگین، نیمه سنگین و راهسازی "
        "و پیگیری سفارش با ما در ارتباط باشید."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings_obj = get_contact_settings()
        context["contact_settings"] = settings_obj
        context["contact_social_links"] = settings_obj.get_social_links()
        return context


class LegalPageView(SiteMetadataMixin, TemplateView):
    template_name = "website/legal-page.html"

    def get_meta_title(self, context=None):
        page = getattr(self, "_legal_page", None) or (context or {}).get("page")
        if page:
            return f"{page.title} - {settings.SITE_NAME}"
        return super().get_meta_title(context)

    def get_meta_description(self, context=None):
        from core.seo import normalize_meta_description

        page = getattr(self, "_legal_page", None) or (context or {}).get("page")
        if page and page.content:
            return normalize_meta_description(page.content)
        return super().get_meta_description(context)

    def get_context_data(self, **kwargs):
        page_type = self.kwargs["page_type"]
        if page_type not in LegalPage.PageType.values:
            raise Http404()
        self._legal_page = get_legal_page(page_type)
        context = super().get_context_data(**kwargs)
        context["page"] = self._legal_page
        context["meta"] = self.get_meta(context=context)
        return context


class AboutView(SiteMetadataMixin, TemplateView):
    template_name = "website/about.html"
    title = f"درباره ما - {settings.SITE_NAME}"
    description = (
        "درباره فروشگاه آروین؛ عرضه‌کننده صندلی راننده ماشین سنگین، "
        "نیمه سنگین و راهسازی با تمرکز بر کیفیت، ارسال سریع "
        "و خدمات پس از فروش قابل اعتماد."
    )


class FAQView(SiteMetadataMixin, TemplateView):
    template_name = "website/faq.html"
    title = f"سوالات متداول - {settings.SITE_NAME}"
    description = (
        "سوالات متداول فروشگاه آروین درباره خرید آنلاین، ارسال، مرجوعی، "
        "پرداخت و پشتیبانی؛ پاسخ‌های کوتاه برای تصمیم سریع‌تر "
        "در خرید صندلی راننده ماشین سنگین، نیمه سنگین و راهسازی."
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faq_items = get_faq_published()
        context["faq_items"] = faq_items
        context["faq_json_ld"] = faq_page_json_ld(faq_items)
        return context


class SendContactView(CreateView):
    """
    a class based view to show index page
    """

    http_method_names = ["post"]
    form_class = ContactForm
    success_url = reverse_lazy("website:contact")

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "تیکت شما با موفقیت ثبت شد و در اسرع وقت با شما تماس حاصل خواهد شد",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request,
            (
                "مشکلی در ارسال فرم شما پیش آمد لطفا ورودی ها رو بررسی کنین "
                "و مجدد ارسال نمایید"
            ),
        )
        return redirect("website:contact")


class NewsletterView(CreateView):
    http_method_names = ["post"]
    form_class = NewsLetterForm
    success_url = "/"

    def form_valid(self, form):
        # handle successful form submission
        messages.success(
            self.request,
            "از ثبت نام شما ممنونم، اخبار جدید رو براتون ارسال می کنم 😊👍",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        # handle unsuccessful form submission
        messages.error(
            self.request, "مشکلی در ارسال فرم شما وجود داشت که می دونم برا چی بود!!"
        )
        return redirect("website:index")
