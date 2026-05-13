# فرصت‌های ریفکتور پروژه (shop-Arvin)

این سند **جای‌هایی که ریفکتور ارزش دارد** را فهرست می‌کند (ساختار، تکرار، خوانایی، جداسازی لایه‌ها). اصلاح باگ‌های امنیتی/منطقی در سند جداگانهٔ «ایرادات» آمده است؛ اینجا تمرکز بر **کیفیت معماری و نگهداری کد** است.

---

## ۱. ساختار فایل‌ها و واردات (اولویت بالا)

| موضوع | پیشنهاد ریفکتور | محل |
|--------|------------------|-----|
| **`import *` گسترده** | جایگزینی با import صریح (`from X import A, B`) در ویوها، فرم‌ها و `website/views.py` تا IDE، type checker و مرور diff شفاف شود. | `website/views.py`, `dashboard/admin/views/*.py`, `dashboard/customer/views/*.py`, `__init__.py` اپ‌ها |
| **فایل `products.py` ادمین — دو بلوک import و تعریف کلاس** | ادغام تمیز: یک بلوک import در بالا، سپس همهٔ کلاس‌ها؛ حذف import تکراری میانی (خطوط ~۵۷–۶۴). این نشانهٔ ادغام دستی دو فایل است. | `dashboard/admin/views/products.py` |
| **`ProductImageModel` بدون import صریح** | اضافه کردن `from shop.models import ProductImageModel` (یا تجمیع importهای `shop.models`) برای شفافیت؛ اتکا به `import *` برای مدل خطرناک است. | همان فایل |
| **`order/views.py` — import استفاده‌نشده** | حذف `HttpResponse` در صورت عدم استفاده؛ مرتب‌سازی importها طبق isort/PEP8. | `order/views.py` |

---

## ۲. تکرار منطق (DRY) — ویوها و کوئری

| موضوع | پیشنهاد | محل‌های مشابه |
|--------|---------|----------------|
| **فیلتر لیست: `order_by` از GET + `FieldError`** | یک mixin مثلاً `OrderByFromQueryMixin` با **لیست سفید** فیلدهای مجاز (امنیت + یکسان‌سازی). | `shop/views.py`, `blog/views.py`, `dashboard/admin/views/products.py`, `dashboard/admin/views/categories.py`, `dashboard/customer/views/addresses.py` |
| **`get_paginate_by` و `page_size` از GET** | mixin مشترک + **سقف** برای `page_size` (جلوگیری از درخواست‌های سنگین). | `shop/views.py`, `blog/views.py`, `dashboard/admin/views/products.py`, `dashboard/admin/views/categories.py` |
| **`total_items = self.get_queryset().count()`** | استفاده از `context['paginator'].count` جایی که paginator موجود است، یا یک کوئری شمارش بهینه‌تر؛ جلوگیری از اجرای دوبارهٔ فیلترهای سنگین. | `shop`, `blog`, `dashboard/admin` لیست‌ها |
| **سه ویوی سشن سبد (`Session*View`)** | یک کلاس پایه با متد `post` که `action` را به متدهای کوچک (`add`/`remove`/`update`) واگذار کند، یا یک endpoint با پارامتر معتبر؛ کاهش تکرار `merge_session_cart_in_db`. | `cart/views.py` |
| **`HasCustomerAccessPermission` دوبار تعریف شده** | نگه داشتن یک نسخه (مثلاً در `dashboard.permissions` یا `core/permissions.py`) و import از یک مکان؛ حذف `order/permissions.py` یا تبدیل آن به re-export نازک. | `dashboard/permissions.py`, `order/permissions.py` |

---

## ۳. لایهٔ سرویس و ضخامت ویوها

| موضوع | پیشنهاد | محل |
|--------|---------|------|
| **`OrderCheckOutView` — تراکنش طولانی در `form_valid`** | استخراج سرویس مثلاً `CheckoutService` یا توابع ماژول `order/services/checkout.py`: ایجاد سفارش، آیتم‌ها، پاک‌سازی سبد، کوپن، فراخوانی درگاه؛ ویو فقط ورودی/خروج HTTP. | `order/views.py` |
| **`ValidateCouponView` — منطق طولانی در `post`** | متدهای خصوصی یا سرویس `CouponValidationService` + پاسخ JSON یک‌شکل (schema ثابت). | `order/views.py` |
| **`PaymentVerifyView`** | سرویس `PaymentVerificationService` با هندل خطا و idempotency؛ ویو نازک. | `payment/views.py` |
| **`ZarinPalSandbox` — URL کلاس در سطح ماژول** | ساخت `callback_url` در `__init__` یا property با `request`/تنظیمات تا وابستگی به زمان import کم شود. | `payment/zarinpal_client.py` |

---

## ۴. مدل سبد (`CartSession`) و دوگانگی DB / Session

| موضوع | پیشنهاد |
|--------|---------|
| **منطق طولانی در یک کلاس** | شکستن به: `SessionCartStore`, `DbCartRepository`, یا متدهای کوچک با نام‌گذاری یکدست (`product_id` همیشه `int` یا همیشه `str`). |
| **`get_cart_items` vs `get_total_price` — ناهمگونی خطا** | یکسان‌سازی: هر دو از try/except یا هر دو از prefetch با خطای کنترل‌شده. |
| **`sync_cart_items_from_db` فراخوانی `merge` در انتها** | مستندسازی ترتیب یا بازطراحی جریان برای جلوگیری از حلقه/فراخوانی‌های مبهم. | `cart/cart.py` |

---

## ۵. کوئری و عملکرد

| موضوع | پیشنهاد | محل |
|--------|---------|-----|
| **`ShopProductDetailView` — شمارش امتیازها** | حلقه روی `range(1,6)` با `reviews.filter(rate=rate).count()` → چند کوئری؛ استفاده از `values('rate').annotate(count=Count('id'))` یا یک کوئری تجمیعی. | `shop/views.py` |
| **`get_object` و `prefetch_related`** | نتیجهٔ `prefetch_related` به queryset دوباره assign شود (مثلاً `queryset = queryset.prefetch_related(...)`) یا در `get_queryset` ویو/مدل انجام شود؛ فراخوانی بدون assign اثر ندارد. | `shop/views.py` (`ShopProductDetailView`)، مشابه در `dashboard/admin/views/products.py` (`AdminProductEditView`) |
| **`BlogPostListView.get_context_data`** | `posts` را با `page_obj` هم‌تراز کردن بدون فراخوانی مجدد سنگین `get_queryset()` برای count؛ استفاده از paginator یا annotate. | `blog/views.py` |

---

## ۶. قالب‌ها (Django templates)

| موضوع | پیشنهاد |
|--------|---------|
| **هدر تکراری در سه base** | `{% include "partials/header.html" %}` با همان context؛ یک منبع برای منوی اصلی. | `base.html`, `dashboard/customer/base.html`, `dashboard/admin/base.html` |
| **فوتر/اسکریپت‌های مشترک** | در صورت تکرار، partial مشابه. | قالب‌های سایت |

---

## ۷. تنظیمات پروژه

| موضوع | پیشنهاد |
|--------|---------|
| **بلوک بزرگ `CKEDITOR_5_CONFIGS` و `customColorPalette`** | انتقال به `core/ckeditor_config.py` و import در `settings.py` برای خوانایی. | `core/settings.py` |
| **`cart_processor`** | یا ثبت در `TEMPLATES['OPTIONS']['context_processors']` اگر همهٔ قالب‌ها به `cart` نیاز دارند، یا حذف اگر مرده است. | `cart/context_processors.py`, `settings.py` |

---

## ۸. جزئیات سبک و نگهداری (کم‌هزینه)

| موضوع | پیشنهاد | محل |
|--------|---------|-----|
| **`super(ClassName, self)`** | جایگزینی با `super()` (پایتون ۳). | `order/views.py` و هر فایل قدیمی مشابه |
| **Docstring اشتباه** | اصلاح توضیح کلاس (`SendContactView`). | `website/views.py` |
| **پیام خطای `NewsletterView.form_invalid`** | متن حرفه‌ای و قابل نمایش به کاربر (بدون اتهام ربات بودن مگر منطق CAPTCHA واقعی دارید). | `website/views.py` |
| **`SubmitReviewView`** | حذف importهای استفاده‌نشده؛ `get_queryset` روی `CreateView` معمولاً بی‌ربط است — حذف یا جایگزینی با منطق درست؛ یک مسیر ذخیره (`super().form_valid` vs `form.save()`). | `review/views.py` |
| **`CustomerAddressCreateView.form_valid`** | ترتیب `super().form_valid` و `redirect` با `SuccessMessageMixin` را با الگوی رسمی جنگو هم‌راستا کنید تا پیام و ریدایرکت قابل پیش‌بینی باشد. | `dashboard/customer/views/addresses.py` |
| **`AdminProduct*ImageView.form_invalid` روی DeleteView** | متد `form_invalid` روی ویوی حذف معمولاً فراخوانی نمی‌شود — بازنگری یا حذف مرده. | `dashboard/admin/views/products.py` |
| **فاصله‌گذاری و کاما در مدل‌ها** | یکدست‌سازی با black/ruff format (اختیاری ولی ارزشمند برای PR). | کل پروژهٔ پایتون |

---

## ۹. تست‌پذیری

| موضوع | پیشنهاد |
|--------|---------|
| **منطق در ویو بدون تست** | بعد از استخراج سرویس، تست واحد برای `CheckoutService`، اعتبار کوپن، و `CartSession`. |
| **`import *`** | مانع پیدا کردن نمادها در تست و mock است؛ ریفکتور import کمک مستقیم به تست است. |

---

## ۱۰. ترتیب پیشنهادی کار (Roadmap کوتاه)

1. تمیز کردن `dashboard/admin/views/products.py` (importها + `ProductImageModel`).  
2. حذف تکرار `HasCustomerAccessPermission` و یکسان‌سازی importها (`import *` → صریح در ویوهای پرتکرار).  
3. Mixin مشترک فیلتر/مرتب‌سازی/صفحه‌بندی برای لیست‌های فروشگاه/بلاگ/ادمین.  
4. نازک کردن `OrderCheckOutView` با سرویس checkout.  
5. Partial هدر در قالب‌ها.  
6. بهینه‌سازی کوئری نظرات محصول و اصلاح `prefetch_related`.

---

*این فهرست بر اساس مرور کد در زمان تهیه است؛ بعد از هر بازطراحی بزرگ، بخش‌های مرتبط را به‌روز کنید.*
