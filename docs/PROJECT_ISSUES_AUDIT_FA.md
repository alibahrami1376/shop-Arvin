# گزارش بازبینی پروژه فروشگاه (shop-Arvin)

این سند بر اساس مرور کد، تنظیمات، Docker و چند ماژول اصلی در تاریخ بررسی تهیه شده است. موارد «تأیید نشده در اجرا» را با `manage.py check`، تست‌های خودکار و اسکن امنیتی تکمیل کنید.

---

## ۱. امنیت و پیکربندی (اولویت بالا)

| موضوع | توضیح | محل تقریبی |
|--------|--------|-------------|
| **کلید مخفی پیش‌فرض ناامن** | اگر `SECRET_KEY` در محیط ست نشود، مقدار `django-insecure-...` استفاده می‌شود؛ در پروداکشن خطر جدی جعل سشن و توکن. | `core/core/settings.py` |
| **DEBUG پیش‌فرض True** | بدون `.env` مناسب، خطاها و اطلاعات حساس لو می‌روند. | همان |
| **ALLOWED_HOSTS پیش‌فرض `*`** | در کنار خطای احتمالی، با برخی تنظیمات امنیتی ناسازگار است و برای پروداکشن توصیه نمی‌شود. | همان |
| **رمز دیتابیس پیش‌فرض** | `PGDB_PASSWORD` با مقدار پیش‌فرض `your_password` — خطر در محیط‌های نادیده‌گرفته‌شده. | همان |
| **MERCHANT_ID ثابت در کد** | شناسه زرین‌پال به‌صورت placeholder در `settings`؛ باید از متغیر محیط (مثل `decouple`) خوانده شود تا در Git لو نرود. | `core/core/settings.py` |
| **عدم تنظیمات HTTPS / کوکی امن** | فلگ‌هایی مثل `SECURE_SSL_REDIRECT`، `SESSION_COOKIE_SECURE`، `CSRF_COOKIE_SECURE`، `SECURE_*` در فایل تنظیمات دیده نشدند. | `settings.py` |
| **بدون ایمیل / احراز ایمیل** | فیلد `is_verified` روی کاربر هست اما مسیر واضح تأیید ایمیل و تنظیمات `EMAIL_*` در تنظیمات اصلی دیده نشد؛ ثبت‌نام مستقیم `login` می‌کند. | `accounts/views.py`, `accounts/models.py` |
| **CKEditor با sourceEditing** | پیکربندی `extends` شامل `sourceEditing` است؛ محتوای HTML غیرقابل‌اعتماد می‌تواند XSS در سمت بازدیدکننده ایجاد کند مگر خروجی با فیلتر مناسب/sanitize شود. | `core/core/settings.py` (`CKEDITOR_5_CONFIGS`) |
| **بازگشت پرداخت بدون احراز مالکیت سفارش** | `PaymentVerifyView` با `Authority` از کوئری، بدون چک صریح که کاربر لاگین همان سفارش است؛ ریسک کمتر از حمله مستقیم است ولی بهتر است مالکیت/وضعیت قبلی پرداخت بررسی شود. | `payment/views.py` |
| **پاسخ زرین‌پال بدون اعتبارسنجی** | دسترسی مستقیم به `response["RefID"]` و `response["Status"]`؛ در پاسخ خطا KeyError و رفتار ناپایدار. | `payment/views.py` |
| **`except:` خالی** | هر خطای غیرمنتظره (از جمله `DoesNotExist`) به `example.com` ختم می‌شود؛ عیب‌یابی سخت و رفتار Callback اشتباه. | `payment/zarinpal_client.py` (`get_domain`) |

---

## ۲. استقرار، Docker و استاتیک (اولویت بالا)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **ناهماهنگی مسیر استاتیک پروداکشن** | `STATIC_ROOT = '/app/static'` در حالی که `docker-compose.prod.yml` ولوم را روی `/app/staticfiles` سوار می‌کند؛ `collectstatic` و nginx با هم جور نیستند مگر یکی اصلاح شود. | `settings.py`, `docker-compose.prod.yml`, `default.conf` |
| **`docker-compose.prod` ولوم روی ریشه پروژه** | `- .:/app` کل ریپو را جایگزین `/app` می‌کند؛ با Dockerfile که `COPY ./core /app` زده، ساختار داخل کانتینر با بیلد متفاوت می‌شود (ریسک شکست مسیرها و `manage.py`). | `docker-compose.prod.yml` |
| **`collectstatic \|\| true` در Dockerfile** | خطای جمع‌آوری استاتیک پنهان می‌شود و ممکن است تصور شود بیلد سالم است. | `Dockerfile` |
| **`docker-compose.yml` بدون سرویس Postgres** | بک‌اند به‌صورت پیش‌فرض به `HOST=postgres` وصل می‌شود؛ اگر شبکهٔ خارجی `postgres` نباشد، اجرای لوکال با این فایل ناقص است. | `docker-compose.yml`, `settings.py` |
| **سرویس Redis در compose** | کانتینر Redis تعریف شده اما در تنظیمات Django اثری از `CACHES` یا استفاده از Redis دیده نشد — منابع بلااستفاده یا پیکربندی نیمه‌کاره. | `docker-compose.yml` |
| **`STATICFILES_DIRS` به پوشهٔ ناموجود** | `BASE_DIR / 'static_assets'` در درخت پروژه وجود ندارد؛ ممکن است هشدار/خطا در اجرا یا `collectstatic` ایجاد شود. | `settings.py` |
| **شبکهٔ Docker `external: true`** | بدون مستندسازی، اجرای اولیه برای تازه‌وارد سخت است. | `docker-compose.yml` |

---

## ۳. پرداخت، سفارش و منطق تجاری (مهم)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **عدم بررسی موفقیت `payment_request`** | قبل از ساخت `PaymentModel` و ریدایرکت، کد/وضعیت پاسخ زرین‌پال چک نمی‌شود؛ امکان `Authority=None`. | `order/views.py` (`create_payment_url`) |
| **مصرف کوپن قبل از تکمیل پرداخت** | در `form_valid` با `coupon.used_by.add(user)` کوپن حتی اگر کاربر از درگاه برنگردد «مصرف» شده است. | `order/views.py` |
| **عدم کاهش موجودی انبار** | فیلد `stock` روی محصول هست اما در جریان ثبت سفارش/پرداخت موفق، کدی برای کم کردن موجودی دیده نشد — overselling. | `shop/models.py`, `order/views.py` |
| **`OrderModel.objects.get(payment=...)`** | در verify اگر رابطه یک‌به‌چند یا نبود رکورد باشد، `MultipleObjectsReturned` / `DoesNotExist` بدون هندل. | `payment/views.py` |
| **Callback زرین‌پال در کلاس** | `_callback_url` در زمان بارگذاری ماژول با `get_domain()` ساخته می‌شود؛ اگر `Site` بعداً درست شود، URL قدیمی می‌ماند. | `payment/zarinpal_client.py` |
| **`django.contrib.sites` در INSTALLED_APPS نیست** | در حالی که `get_domain()` از `Site` استفاده می‌کند؛ ممکن است در برخی نصب‌ها خطا یا جدول خالی باشد. | `settings.py`, `zarinpal_client.py` |

---

## ۴. دسترسی‌ها و نقش کاربران (مهم)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **سوپریوزر و داشبورد سفارشی** | `HasAdminAccessPermission` فقط `UserType.admin` (۲) را قبول می‌کند؛ کاربر با نوع `superuser` (۳) از پنل ادمین سفارشی محروم است مگر منطق جداگانه‌ای باشد. | `dashboard/permissions.py` |
| **`DashboardHomeView` برای نوع ۳** | اگر کاربر لاگین باشد و نه customer و نه admin (مثلاً superuser)، به `super().dispatch` می‌رسد که برای `View` خالی معنادار نیست. | `dashboard/views.py` |
| **تکرار کلاس مجوز** | `HasCustomerAccessPermission` هم در `dashboard/permissions` و هم در `order/permissions` تعریف شده — ریسک واگرایی رفتار. | دو فایل |

---

## ۵. عملکرد، پایداری و سوءاستفاده (متوسط)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **`page_size` بدون سقف در بلاگ** | مقدار `page_size` از GET مستقیم به paginator می‌رود؛ درخواست با عدد بسیار بزرگ فشار روی DB/حافظه. | `blog/views.py` |
| **`get_context_data` بلاگ و شمارش** | `total_items` با `self.get_queryset().count()` دوباره کوئری می‌زند و با صفحه‌بندی ممکن است گیج‌کننده باشد. | `blog/views.py` |
| **`get_cart_items` بدون try روی محصول** | برخلاف `get_total_price`، در صورت حذف/آرشیو محصول، `objects.get` می‌تواند خطا بدهد. | `cart/cart.py` |
| **`merge_session_cart_in_db`** | همان `get` بدون محافظ در برابر محصول ناموجود. | `cart/cart.py` |
| **رقابت در اعتبارسنجی کوپن** | دو درخواست همزمان ممکن است از سقف `max_limit_usage` عبور کنند مگر تراکنش/قفل سطح DB. | `order/views.py` (`ValidateCouponView`) |
| **Race در پرداخت verify** | دوبار باز کردن callback ممکن است وضعیت را دوباره بنویسد؛ بهتر است idempotent باشد. | `payment/views.py` |

---

## ۶. بین‌المللی‌سازی و تجربه کاربری (ساده تا متوسط)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **`LANGUAGE_CODE = 'en-us'`** | سایت RTL و فارسی است؛ تاریخ و فرمت‌ها ممکن است با انتظار کاربر هم‌خوان نباشد. | `settings.py` |
| **`TIME_ZONE` پیش‌فرض UTC** | برای فروشگاه ایران معمولاً `Asia/Tehran` منطقی‌تر است مگر عمدی باشد. | `settings.py` |
| **ناسازگاری برچسب «بلاگ» / «وبلاگ»** | در منو «بلاگ» استفاده شده؛ یکدست‌سازی با متن بازاریابی اختیاری. | قالب‌ها |
| **هدر تکراری در چند base** | هدر سایت در `base.html` و جداگانه در `dashboard/customer/base.html` و `dashboard/admin/base.html` کپی شده — هر تغییر منو باید سه جا اعمال شود (ریسک فراموشی). | قالب‌های داشبورد |

---

## ۷. کیفیت کد و وابستگی‌ها (ساده)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **`django-debug-toolbar` در requirements** | در `INSTALLED_APPS` / `urls` پروژه دیده نشد؛ یا اضافه شود یا از requirements حذف شود تا ابهام نماند. | `requirements.txt` |
| **`import *` در ویوهای ادمین** | `contacts`, `newsletters`, `users` — خوانایی و کنترل namespace پایین‌تر است. | `dashboard/admin/views/*.py` |
| **کد مرده در `DashboardHomeView`** | `return super().dispatch(...)` بعد از شاخه‌های redirect برای احراز هویت‌شده عملاً غیرقابل دسترس است (بوی کد). | `dashboard/views.py` |
| **کامنت‌های تخفیف در `apply_coupon`** | منطق تخفیف قدیمی کامنت شده؛ اگر عمدی است بهتر است TODO یا توضیح کوتاه در کد باشد. | `order/views.py` |
| **نسخه‌های قدیمی وابستگی** | نمونه: `urllib3==2.1.0`, `requests==2.31.0`, `pillow==10.2.0` — دوره‌ای با ابزار امنیتی (Dependabot/pip-audit) بررسی شوند. | `requirements.txt` |
| **`payment/models.py` و `JSONField`** | وارد کردن از `django.db.models`؛ در نسخه‌های جدیدتر معمولاً `models.JSONField` ترجیح داده می‌شود. | `payment/models.py` |

---

## ۸. تست و نگهداری (ساده اما مهم برای بلندمدت)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **فایل‌های `tests.py` خالی** | اپ‌های اصلی (`accounts`, `order`, `shop`, `cart`, `dashboard`, `blog`, …) تقریباً بدون تست خودکار هستند. | چندین `tests.py` |
| **عدم CI دیده‌شده در ریشه** | اگر GitHub Actions/GitLab CI ندارید، پیشنهاد: `ruff`/`flake8`، `pytest`، `manage.py check --deploy`. | ریشه ریپو |

---

## ۹. مدل‌ها و داده (جزئی)

| موضوع | توضیح | محل |
|--------|--------|-----|
| **`Profile.objects.create(..., pk=instance.pk)`** | ست کردن صریح `pk` غیرمعمول است؛ در سناریوهای خاص با سکانس دیتابیس می‌تواند سردرگم‌کننده باشد. | `accounts/models.py` |
| **پروفایل پیش‌فرض با شماره ثابت** | `09000000000` تا کاربر تکمیل کند — برای اعتبارسنجی/پیامک بعدی در نظر گرفته شود. | همان |

---

## جمع‌بندی اولویت اقدام

1. **فوری پروداکشن:** اصلاح `SECRET_KEY`، `DEBUG`، `ALLOWED_HOSTS`، مسیر `STATIC_ROOT` هم‌راستا با Docker/nginx، و پیکربندی HTTPS/کوکی امن.  
2. **پرداخت:** هندل خطای API زرین‌پال، جلوگیری از KeyError، و سخت‌سازی verify (وضعیت قبلی، مالکیت).  
3. **تجارت:** موجودی انبار، مصرف کوپن فقط پس از پرداخت موفق، بررسی پاسخ `payment_request`.  
4. **نقش‌ها:** رفتار واضح برای `superuser` در داشبورد و مجوزها.  
5. **تکمیلی:** تست خودکار، حذف/تکمیل وابستگی‌های بلااستفاده، یکسان‌سازی هدر با include/partials.

---

*پایان گزارش اولیه.*
