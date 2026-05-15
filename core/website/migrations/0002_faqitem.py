from django.db import migrations, models


def seed_faq_items(apps, schema_editor):
    FAQItem = apps.get_model("website", "FAQItem")
    defaults = [
        (
            "آروین چه محصولاتی عرضه می‌کند؟",
            "فروشگاه آروین تامین‌کننده لوازم یدکی و جانبی کامیون و کامیونت شامل صندلی، قطعات موتور، ترمز، تعلیق و سایر اقلام مرتبط با خودروهای سنگین و نیمه‌سنگین است.",
            1,
        ),
        (
            "آیا قطعات ارائه‌شده اصل و دارای گارانتی هستند؟",
            "بله؛ محصولات معرفی‌شده در فروشگاه با تاکید بر اصالت و کیفیت عرضه می‌شوند. برای بسیاری از کالاها گارانتی ۶ ماهه در نظر گرفته شده و در صورت بروز مشکل فنی، طبق شرایط فروشگاه پشتیبانی می‌شود.",
            2,
        ),
        (
            "چگونه می‌توانم سفارش ثبت کنم؟",
            "پس از انتخاب محصول در فروشگاه، آن را به سبد خرید اضافه کنید، سپس مراحل تسویه حساب را تکمیل کنید. در صورت نیاز به راهنمایی می‌توانید با پشتیبانی تماس بگیرید.",
            3,
        ),
        (
            "ارسال به شهرستان چگونه انجام می‌شود؟",
            "ارسال سفارش‌ها به سراسر کشور انجام می‌شود. زمان تحویل بسته به مقصد و نوع کالا متفاوت است و پس از ثبت سفارش، وضعیت ارسال از طریق پشتیبانی اطلاع‌رسانی می‌شود.",
            4,
        ),
        (
            "آیا امکان نصب قطعات روی خودرو وجود دارد؟",
            "بله؛ خدمات نصب تخصصی برای انواع خودروهای سنگین، نیمه‌سنگین و راهسازی ارائه می‌شود. برای هماهنگی زمان و جزئیات نصب با تیم فنی تماس بگیرید.",
            5,
        ),
        (
            "روش‌های پرداخت چیست؟",
            "پرداخت آنلاین و سایر روش‌های تعریف‌شده در صفحه تسویه حساب فعال است. در صورت فعال بودن پرداخت کارت‌به‌کارت، راهنمای واریز در همان مرحله نمایش داده می‌شود.",
            6,
        ),
        (
            "شرایط مرجوعی یا تعویض کالا چگونه است؟",
            "در صورت مغایرت کالا با سفارش یا وجود ایراد فنی، طبق قوانین فروشگاه و شرایط گارانتی، امکان پیگیری مرجوعی یا تعویض وجود دارد. برای ثبت درخواست با پشتیبانی تماس بگیرید.",
            7,
        ),
        (
            "چطور با پشتیبانی آروین در ارتباط باشم؟",
            "از طریق صفحه تماس با ما می‌توانید تیکت ثبت کنید یا با شماره‌های درج‌شده در همان صفحه تماس بگیرید. تیم پشتیبانی در ساعات کاری پاسخگوی شماست.",
            8,
        ),
    ]
    for question, answer, sort_order in defaults:
        FAQItem.objects.create(
            question=question,
            answer=answer,
            sort_order=sort_order,
            is_published=True,
        )


def unseed_faq_items(apps, schema_editor):
    FAQItem = apps.get_model("website", "FAQItem")
    FAQItem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FAQItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("question", models.CharField(max_length=500, verbose_name="سوال")),
                ("answer", models.TextField(verbose_name="پاسخ")),
                (
                    "sort_order",
                    models.PositiveIntegerField(
                        default=0, verbose_name="ترتیب نمایش"
                    ),
                ),
                (
                    "is_published",
                    models.BooleanField(default=True, verbose_name="منتشر شده"),
                ),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                ("updated_date", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "سوال متداول",
                "verbose_name_plural": "سوالات متداول",
                "ordering": ["sort_order", "-created_date"],
            },
        ),
        migrations.RunPython(seed_faq_items, unseed_faq_items),
    ]
