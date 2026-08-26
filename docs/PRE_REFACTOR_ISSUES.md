# ایرادها و تسک‌های پیش از ریفکتور — shop-Arvin

تاریخ بررسی: ۱۴۰۴/۰۶/۰۲ (۲۰۲۶-۰۸-۲۴)

این فایل نتیجهٔ مرور کل پروژه است تا قبل از ریفکتور بدانی **کجاها مشکل واقعی دارند** و با چه اولویتی سراغ‌شان بروی. هر آیتم یک تسک قابل‌اقدام است؛ توضیح کوتاه برای «چرا مهم است» آمده.

**اولویت‌ها:** 🔴 بحرانی / پول و داده · 🟠 مهم / امنیت و پایداری · 🟡 معماری و کیفیت · 🟢 تمیزکاری

---

## خلاصهٔ وضعیت

فروشگاه Django 4.2 با اپ‌های `accounts`, `shop`, `cart`, `order`, `payment`, `dashboard`, `website`, `blog`, `review`. جریان اصلی کار می‌کند، ولی چند نقطهٔ حساس (موجودی، پرداخت، کوپن، OTP، تنظیمات production) قبل از ریفکتور ظاهری باید درست یا حداقل مشخص شوند؛ وگرنه ریفکتور روی پایه‌ای شکننده می‌نشیند.

---

## ۱) منطق کسب‌وکار و داده (اولویت بالا)

### 🔴 T1 — موجودی (`stock`) فقط نمایشی است؛ موقع سفارش کم نمی‌شود

**کجا:** `shop.models.ProductModel.stock`؛ checkout در `order/views.py` (`create_order_items`)؛ افزودن به سبد در `cart/views.py` / `cart/cart.py`

**مشکل:** فیلد `stock` وجود دارد و در داشبورد «کمبود موجودی» هم نشان داده می‌شود، ولی:
- هنگام ثبت سفارش از موجودی کم نمی‌شود
- هنگام افزودن به سبد / تغییر تعداد، با `stock` مقایسه نمی‌شود

**چرا خطرناک:** فروش بیش از موجودی واقعی، سفارش‌هایی که قابل ارسال نیستند.

**تسک:** در یک تراکنش اتمیک با `select_for_update` موجودی را چک و کم کن؛ در سبد هم سقف تعداد را به `stock` محدود کن.

---

### 🔴 T2 — سبد خالی می‌تواند به سفارش تبدیل شود

**کجا:** `OrderCheckOutView.form_valid` → `create_order_items` روی `cart.cart_items.all()` بدون چک خالی بودن

**مشکل:** اگر `CartModel` کاربر بدون آیتم باشد (یا session با DB ناهم‌خوان باشد)، سفارش خالی با پرداخت ساخته می‌شود.

**تسک:** در فرم یا قبل از `create_order` اگر هیچ آیتم معتبری نبود، خطا بده و جلوی ساخت سفارش را بگیر.

---

### 🔴 T3 — دو منبع حقیقت برای سبد (Session + DB) و ناهم‌خوانی با checkout

**کجا:** `cart/cart.py` (`CartSession`) در برابر `CartModel` / `CartItemModel`؛ checkout فقط از **DB** می‌خواند (`CartModel.objects.get`)

**مشکل:** UI و هدر از session کار می‌کنند؛ ثبت سفارش از DB. اگر `persist_to_db` جا بیفتد یا race رخ بدهد، کاربر چیزی در سبد می‌بیند ولی سفارش چیز دیگری می‌شود (یا برعکس).

**توضیح:** طراحی dual-cart برای مهمان/لاگین قابل دفاع است، ولی باید **یک منبع حقیقت در لحظهٔ checkout** مشخص باشد (معمولاً: قبل از checkout اجباری sync، یا checkout فقط از همان منبعی که UI نشان می‌دهد).

**تسک:** قرارداد واضح بنویس (session ↔ DB)؛ قبل از checkout `persist`/`merge` اجباری؛ تست سناریوی مهمان→لاگین→checkout.

---

### 🔴 T4 — فراخوانی شبکه زرین‌پال داخل `transaction.atomic`

**کجا:** `order/views.py` → `_create_gateway_payment_url` داخل بلوک `atomic`

**مشکل:** تا وقتی HTTP به زرین‌پال تمام شود، قفل تراکنش دیتابیس باز می‌ماند. کندی/timeout درگاه = قفل طولانی و ریسک deadlock زیر بار.

**تسک:** ساخت سفارش و آیتم‌ها در atomic؛ درخواست درگاه **بعد** از commit؛ در صورت شکست درگاه، سفارش را `failed`/`pending` کن و سبد را برنگردان مگر سیاست مشخصی داشته باشی.

---

### 🔴 T5 — `clear_cart` بیرون از atomic و بعد از ساخت پرداخت

**کجا:** `OrderCheckOutView.form_valid` — بعد از `try/except`

**مشکل:** اگر بعد از commit سفارش، پاک‌کردن سبد fail شود، سفارش ثبت شده ولی سبد هنوز پر است (سفارش تکراری آسان). همچنین منطق «موفقیت درگاه» و «پاک شدن سبد» از هم جدا نیستند.

**تسک:** سیاست مشخص: سبد فقط وقتی پاک شود که سفارش با وضعیت معتبر commit شده؛ ترجیحاً در همان flow کنترل‌شده با تست.

---

### 🔴 T6 — تأیید پرداخت (`PaymentVerifyView`) بدون idempotency

**کجا:** `payment/views.py`

**مشکل:** هر بار با همان `Authority` می‌توان verify زد و `status` سفارش/پرداخت را دوباره نوشت. رفرش کاربر یا درخواست تکراری درگاه می‌تواند وضعیت را خراب کند (مثلاً بعد از موفقیت، verify دوباره با خطای شبکه → failed).

**تسک:** اگر پرداخت قبلاً موفق/ناموفق نهایی شده، دوباره به درگاه نزن؛ زود return کن. با `select_for_update` از race دو درخواست همزمان جلوگیری کن.

---

### 🔴 T7 — زرین‌پال همیشه Sandbox؛ پروتکل callback وابسته به تنظیم ناموجود

**کجا:** `payment/zarinpal_client.py` — URLهای `sandbox.zarinpal.com`؛ `get_protocol()` با `SECURE_SSL_REDIRECT` (که در settings ست نشده)

**مشکل:**
- در production هم احتمالاً sandbox صدا زده می‌شود مگر دستی عوض شود
- callback ممکن است `http://` ساخته شود در حالی که سایت HTTPS است → شکست verify

**تسک:** سوییچ `ZARINPAL_SANDBOX` / env؛ URLهای live؛ callback را از `Site` + `META_SITE_PROTOCOL` یا تنظیم صریح `PAYMENT_CALLBACK_BASE` بساز.

---

### 🟠 T8 — کوپن: race، نبود unique، و چک شل

**کجا:** `order/models.CouponModel`؛ `apply_coupon`؛ `ValidateCouponView`

**مشکل:**
- `code` یکتا (`unique`) نیست → دو کوپن هم‌کد ممکن است
- `used_by.count()` و `max_limit_usage` بدون قفل اتمیک → دو کاربر همزمان می‌توانند از ظرفیت رد شوند
- کاربر به محض ثبت سفارش به `used_by` اضافه می‌شود حتی اگر بعداً پرداخت fail شود (بسته به سیاست کسب‌وکار ممکن است اشتباه باشد)

**تسک:** `unique=True` روی code؛ در apply از `select_for_update` استفاده کن؛ سیاست «مصرف کوپن بعد از پرداخت موفق» را مشخص و پیاده کن.

---

### 🟠 T9 — پیگیری سفارش عمومی با کد کوتاه عددی (۵–۷ رقم)

**کجا:** `generate_tracking_code`؛ `OrderTrackingView` (بدون لاگین)

**مشکل:** فضای کدها کوچک است و قابل حدس/اسکن. هر کسی با کد، جزئیات سفارش (آیتم، وضعیت، …) را می‌بیند.

**تسک:** کد طولانی‌تر (مثلاً ۱۲+ کاراکتر تصادفی امن) یا الزام لاگین/شماره موبایل همراه کد؛ محدود کردن فیلدهای نمایش عمومی.

---

### 🟠 T10 — OTP بدون rate-limit و با `random` ضعیف

**کجا:** `accounts/models.OTPCode.save` (`random.randint`)؛ `OTPService.create_and_send`؛ ویوهای ارسال OTP

**مشکل:** بدون محدودیت تعداد درخواست، امکان اسپم پیامک و brute-force روی کد ۶ رقمی هست. `random` برای امنیت مناسب نیست (`secrets` بهتر است).

**تسک:** سقف ارسال per-phone / per-IP (cache/redis)؛ افزایش تأخیر؛ تولید کد با `secrets`؛ قفل بعد از N تلاش غلط.

---

### 🟠 T11 — نقش‌های `marketer` / `editor` / `support` تعریف شده‌اند ولی دسترسی واقعی ندارند

**کجا:** `accounts.UserType`؛ `dashboard/permissions.HasAdminAccessPermission` فقط `admin` و `superuser`

**مشکل:** در فرم کاربران این نقش‌ها ساخته می‌شوند، ولی داشبورد ادمین را نمی‌بینند و مشتری هم نیستند → نه خرید درست (checkout فقط `customer`) نه پنل ادمین.

**تسک:** یا نقش‌ها را با permissionهای جزئی پیاده کن، یا تا قبل از پیاده‌سازی از انتخاب UI حذف‌شان کن تا دادهٔ مرده نسازی.

---

### 🟡 T12 — وضعیت سفارش و پرداخت قاطی شده

**کجا:** `OrderStatusType` در برابر `PaymentStatusType` (شامل `preparing` و `shipped`)

**مشکل:** وضعیت ارسال داخل enum پرداخت است؛ نمایش مشتری از هر دو مدل خوانده می‌شود. فهم و ریفکتور بعدی سخت می‌شود.

**تسک:** دامنه را جدا کن: Payment = پول؛ Order/Fulfillment = آماده‌سازی و ارسال. migration یک‌باره بعداً در فاز جدا.

---

### 🟡 T13 — سیگنال میانگین امتیاز نظر ناقص است

**کجا:** `review/models.py` → `calculate_avg_review`

**مشکل:** فقط وقتی `status == accepted` میانگین آپدیت می‌شود. اگر نظری از accepted به rejected برود، `avg_rate` کهنه می‌ماند.

**تسک:** روی هر تغییر status، میانگین را از نو حساب کن (یا اگر هیچ accepted نبود → ۰).

---

## ۲) امنیت و Production

### 🟠 T14 — پیش‌فرض‌های ناامن در `settings.py`

**کجا:** `core/core/settings.py`

| تنظیم | وضعیت فعلی | پیشنهاد |
|--------|------------|---------|
| `DEBUG` | پیش‌فرض `True` | در prod اجباری `False`؛ بدون default خطرناک |
| `SECRET_KEY` | default ناامن در کد | بدون default در prod (fail fast) |
| `ALLOWED_HOSTS` | پیش‌فرض `"*"` | لیست دامنه واقعی |
| `SECURE_*` / cookie secure | تقریباً فقط `SECURE_PROXY_SSL_HEADER` | HSTS، `SESSION_COOKIE_SECURE`، `CSRF_COOKIE_SECURE` وقتی HTTPS |
| `CSRF_TRUSTED_ORIGINS` | ممکن است خالی باشد | دامنه‌های واقعی با `https://` |
| `LOGGING` | تعریف نشده | حداقل error به فایل/stderr |

**تسک:** settings را به `base` / `dev` / `prod` بشکن یا با env سخت‌گیرانه کن.

---

### 🟠 T15 — دو فایل `.env` (ریشه و `core/`) و مسیر مبهم

**مشکل:** `python-decouple` معمولاً از CWD می‌خواند؛ docker از `.env` ریشه؛ اجرای محلی از داخل `core/` ممکن است env دیگری ببیند → رفتار متفاوت debug/merchant.

**تسک:** یک منبع env؛ در README مسیر قطعی؛ از commit شدن `.env` مطمئن شو (الان gitignore هست — خوب است).

---

### 🟡 T16 — `django-debug-toolbar` در requirements ولی استفاده نمی‌شود

**مشکل:** وابستگی اضافه در image پروداکشن؛ اگر کسی اشتباهی فعالش کند ریسک دارد.

**تسک:** به `requirements-dev.txt` منتقل کن یا حذف کن.

---

### 🟡 T17 — آپلود تصویر بدون محدودیت صریح اندازه/نوع در همه جا

**کجا:** `ImageField`/`FileField` در shop/blog/website/accounts

**مشکل:** بخشی validation لوگو دارد؛ بقیه ممکن است فایل بزرگ/نامعتبر بپذیرند.

**تسک:** validator مشترک (حجم، پسوند، ابعاد) برای همهٔ آپلودهای کاربر/ادمین.

---

### 🟡 T18 — `ImageField(default="/default/product-image.png")`

**کجا:** `shop.models.ProductModel.image`

**مشکل:** مقدار با `/` اول برای FileField معمولاً مسیر اشتباه است و فایل پیش‌فرض واقعی در media وجود ندارد.

**تسک:** default نسبی درست + فایل واقعی در media، یا `blank=True` + placeholder در تمپلیت.

---

## ۳) معماری، عملکرد، ساختار کد

### 🟡 T19 — حدود ۱۵۰ تمپلیت و الگوی موبایل/دسکتاپ نیمه‌کاره

**کجا:** `core/templates/` (~۱۳ تا `*-mobile.html`)؛ فایل یتیم `Untitled` شامل `DeviceTemplateMixin`؛ `CORE.md` به `mixins.py` / `device_templates.py` اشاره می‌کند که در پکیج `core` نیستند.

**مشکل:** تشخیص دستگاه در context هست، ولی mixin رسمی داخل پروژه نیست (کدش در `Untitled` مانده). نگهداری دو نسخهٔ تمپلیت هزینهٔ ریفکتور را بالا می‌برد.

**تسک قبل از ادغام تمپلیت‌ها:** یا mixin را درست وارد کن و convention را یکدست کن، یا عمداً به CSS responsive برو و فایل‌های `*-mobile` را فاز جدا حذف کن. اول docs را با واقعیت هم‌تراز کن.

---

### 🟡 T20 — Context processorهای سنگین روی هر درخواست

**کجا:** `website.context_processors.site_branding` (۳× `get_solo`)؛ `shop_categories`؛ `cart_processor`

**مشکل:** هر صفحه HTML چند query اضافه می‌گیرد. زیر ترافیک محسوس می‌شود.

**تسک:** cache کوتاه‌مدت برای تنظیمات solo و درخت دسته؛ cart را سبک نگه دار (فقط تعداد، نه hydrate کامل در همه صفحات مگر لازم).

---

### 🟡 T21 — N+1 در سبد

**کجا:** `CartSession.get_cart_items` و `get_total_price` — برای هر آیتم یک `ProductModel.objects.get`

**تسک:** یک `filter(id__in=...)` + map؛ یا annotate.

---

### 🟡 T22 — `SESSION_SAVE_EVERY_REQUEST = True`

**مشکل:** هر request سشن را می‌نویسد (DB/فایل) → IO زیاد.

**تسک:** فقط وقتی سبد/فلگ عوض شد `modified=True`؛ این تنظیم را بردار مگر دلیل قوی داری.

---

### 🟡 T23 — Permission مشتری تکراری

**کجا:** `order/permissions.py` و `dashboard/permissions.py` هر دو `HasCustomerAccessPermission`

**تسک:** یک ماژول مشترک (مثلاً `accounts/permissions.py` یا `core/permissions.py`).

---

### 🟡 T24 — لایهٔ سرویس فقط در accounts؛ بقیه fat view

**کجا:** داشبورد ~۸۵ فایل پایتون؛ checkout/payment منطق داخل view

**تسک تدریجی:** `order/services/checkout.py`، `payment/services/verify.py`؛ view فقط orchestration. این کار ریفکتور بعدی را امن‌تر می‌کند.

---

### 🟡 T25 — الگوی singleton با `get_or_create(pk=1)` بدون ضمانت قوی

**کجا:** Payment/Card/Branding/Pricing/Contact settings

**مشکل:** تحت race دو ردیف ممکن است (هرچند pk=1 محدود می‌کند). بهتر از django-solo یا constraint صریح.

**تسک:** یک abstract SoloModel مشترک + مستند «فقط یک ردیف».

---

### 🟡 T26 — Redis در docker هست ولی در Django استفاده نمی‌شود

**کجا:** `docker-compose.yml` سرویس `redis`؛ settings بدون `CACHES`/Celery

**مشکل:** وابستگی زیرساختی بی‌مصرف؛ در حالی که برای OTP rate-limit و cache تنظیمات عالی است.

**تسک:** یا Redis را به cache وصل کن، یا از compose حذف کن تا گمراه‌کننده نباشد.

---

### 🟠 T27 — تست خودکار تقریباً صفر؛ CI/CD کامنت شده

**کجا:** `.github/workflows/ci.yml` و `cd.yml` کامل کامنت؛ هیچ `tests.py` اپلیکیشنی نیست

**مشکل:** هر ریفکتور بدون تور ایمنی است.

**تسک حداقل قبل از ریفکتور بزرگ:**
1. تست checkout (سبد خالی، موجودی، کوپن)
2. تست verify پرداخت (موفق، تکراری، کاربر غلط)
3. تست OTP rate-limit
4. فعال‌کردن CI برای `manage.py check` + `test`

---

## ۴) DevOps، وابستگی‌ها، فایل‌های اضافی

### 🟡 T28 — دو `requirements.txt` یکسان (ریشه و `core/`)

**تسک:** یکی را منبع حقیقت کن؛ دیگری را حذف یا به symlink/docs تبدیل کن.

---

### 🟡 T29 — ناسازگاری نسخهٔ Python در Docker

**کجا:** ریشه `Dockerfile` → Python **3.12**؛ `dockerfiles/dev/django` → **3.10-slim-buster** (قدیمی)

**تسک:** یک نسخهٔ هدف (مثلاً 3.12) در dev و prod.

---

### 🟡 T30 — `docker-compose` بدون Postgres؛ شبکه `external: true`

**مشکل:** برای کسی که از صفر clone می‌کند، بدون شبکه/DB بیرونی بالا نمی‌آید. `postgres/data` محلی هست ولی در compose سرویس postgres نیست.

**تسک:** compose کامل dev (postgres + redis + web) با network داخلی؛ prod جدا.

---

### 🟡 T31 — `collectstatic ... || true` در Dockerfile

**مشکل:** شکست collectstatic را قورت می‌دهد و image «سالم» به نظر می‌رسد.

**تسک:** خطا را fail کن؛ یا collectstatic را در entrypoint با env درست بزن.

---

### 🟢 T32 — استاتیک CKEditor تکراری (~۵.۸MB × ۲)

**کجا:** `core/static/vendor/ckeditor` و `core/public/static/vendor/ckeditor`

**تسک:** یکی را نگه دار؛ مسیر STATIC را یکدست کن. (اگر از django-ckeditor-5 استفاده می‌کنی، vendor قدیمی ممکن است زاید باشد.)

---

### 🟢 T33 — فایل‌ها و اسناد یتیم / ناقص

| مورد | توضیح |
|------|--------|
| `Untitled` | کد `DeviceTemplateMixin` که باید یا merge شود یا حذف |
| `CORE.md` | به فایل‌های ناموجود اشاره می‌کند — هم‌تراز با کد کن |
| `docs/` | خالی بود؛ این فایل اولین سند ساختاریافته است |
| کامنت‌های settings | هنوز «Django 3.2» می‌گویند |

**تسک:** پاکسازی و به‌روزرسانی docs در یک PR کوچک جدا از فیچر.

---

### 🟢 T34 — پین کردن وابستگی‌ها

**مشکل:** بعضی پکیج‌ها بازه‌ای‌اند (`Django>4.2,<4.3`) و بعضی freeze؛ بازتولید build سخت‌تر است. چند dependency HTTP قدیمی (urllib3/requests/certifi) ممکن است CVE داشته باشند.

**تسک:** `pip-compile` یا قفل نسخه؛ یک‌بار audit امنیتی.

---

## ۵) پیشنهاد ترتیب کار قبل از ریفکتور ظاهری/ساختاری

اگر هدف «ریفکتور تمیز» است، این ترتیب ریسک را کم می‌کند:

1. **T27** اسکلت تست + CI حداقلی  
2. **T1, T2, T3, T5** موجودی و سبد/checkout  
3. **T4, T6, T7** پرداخت  
4. **T8, T9, T10** کوپن، پیگیری، OTP  
5. **T14, T15, T29, T30** سخت‌کردن production و docker  
6. بعد: **T19** (تمپلیت موبایل)، **T24** (سرویس‌ها)، **T12** (جداسازی وضعیت‌ها)

ریفکتور UI/ادغام تمپلیت‌ها را قبل از پایدار شدن checkout/payment شروع نکن.

---

## ۶) چیزهایی که نسبتاً خوب‌اند (برای تعادل)

- جدا بودن اپ‌های دامنه (shop/cart/order/payment) منطقی است  
- پرداخت کارت‌به‌کارت + تنظیمات solo در داشبورد پیاده شده  
- OTP و SMS در `accounts/services` لایه گرفته‌اند (الگوی خوب برای بقیه)  
- `.env` در gitignore است  
- Sitemap / robots / PWA پایه‌ای وجود دارد  
- فرم‌ها و پیام‌های فارسی و password validators بومی‌سازی شده‌اند  

---

## چک‌لیست سریع (تیک بزن)

- [ ] T1 موجودی اتمیک  
- [ ] T2 جلوگیری سفارش خالی  
- [ ] T3 قرارداد session/DB سبد  
- [ ] T4 درگاه بیرون از atomic  
- [ ] T5 پاک‌سازی امن سبد  
- [ ] T6 verify ایدمپوتنت  
- [ ] T7 زرین‌پال live + callback HTTPS  
- [ ] T8 کوپن امن و یکتا  
- [ ] T9 کد پیگیری امن‌تر  
- [ ] T10 محدودیت OTP  
- [ ] T11 نقش‌های ناقص  
- [ ] T12 جداسازی status دامنه  
- [ ] T13 میانگین نظر  
- [ ] T14 settings امن prod  
- [ ] T15 یک منبع env  
- [ ] T16–T18 آپلود و toolbar و default image  
- [ ] T19 تمپلیت/device mixin  
- [ ] T20–T22 عملکرد درخواست/سشن/سبد  
- [ ] T23–T25 ساختار permission/service/solo  
- [ ] T26 Redis واقعی یا حذف  
- [ ] T27 تست + CI  
- [ ] T28–T34 devops و تمیزکاری  

---

*این سند فقط فهرست ایراد/تسک است؛ عمداً کد ریفکتور نشده. وقتی فاز را شروع کردی، می‌توانی کنار هر `T#` لینک PR یا commit بگذاری.*
