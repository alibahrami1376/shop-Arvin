# مستند ماژول `core` — shop-Arvin

این فایل توضیح می‌دهد **پکیج Django به نام `core`** (پوشه `core/core/`) و نقش آن در کل پروژه چیست. برای اجرای دستورات، معمولاً از پوشه `core/` (جایی که `manage.py` است) کار می‌کنی.

---

## ۱. دو تا «core»؛ گیج نشو

| مسیر | معنی |
|------|------|
| `shop-Arvin/core/` | ریشه **پروژه Django** (شامل `manage.py`، اپ‌ها، تمپلیت‌ها) |
| `shop-Arvin/core/core/` | **پکیج پایتون** همان پروژه: `settings.py`, `urls.py`, `wsgi.py`, … |

در کد، importها به شکل `from core.device import ...` هستند؛ یعنی پکیج دوم (`core.core` روی دیسک، ولی در پایتون فقط `core`).

**`BASE_DIR`** در `settings.py` به `Path(__file__).resolve().parent.parent` اشاره می‌کند؛ یعنی پوشه **`core/`** (یک سطح بالاتر از فایل `settings.py`). تمپلیت‌ها، `static/`, `media/` نسبت به همان تعریف می‌شوند.

---

## ۲. فایل‌های پکیج `core` — نقش هر کدام

| فایل | نقش کوتاه |
|------|-----------|
| `settings.py` | تنظیمات کل پروژه (اپ‌ها، middleware، DB، static، auth، PWA، CKEditor) |
| `urls.py` | مسیرهای ریشه؛ `include` به هر اپ |
| `middleware.py` | کوکی انتخاب دستی موبایل/دسکتاپ (`?site=`) |
| `device.py` | تشخیص موبایل بودن درخواست (UA، کوکی، Client Hints) |
| `device_templates.py` | انتخاب نام تمپلیت موبایل در صورت وجود (`*-mobile.html`) |
| `mixins.py` | `DeviceTemplateMixin` برای viewهای کلاس‌بیس |
| `context_processors/device.py` | متغیرهای تمپلیت سراسری مربوط به دستگاه |
| `wsgi.py` / `asgi.py` | ورودی سرور production (Gunicorn/uWSGI یا ASGI) |
| `../manage.py` | نقطه ورود CLI؛ `DJANGO_SETTINGS_MODULE=core.settings` |

---

## ۳. `settings.py` — بخش‌به‌بخش

### ۳.۱ امنیت و محیط

- **`SECRET_KEY`**, **`DEBUG`**, **`ALLOWED_HOSTS`** با **`python-decouple`** از متغیرهای محیطی (`config(...)`) خوانده می‌شوند.
- برای production حتماً در `.env` مقدار واقعی بگذار؛ مقدار پیش‌فرض `SECRET_KEY` در کد فقط برای توسعه است و نباید در سرور عمومی بماند.
- **`ALLOWED_HOSTS`**: رشته comma-separated به لیست تبدیل می‌شود؛ پیش‌فرض `"*"` برای dev راحت است، در production محدود کن.

### ۳.۲ اپ‌های نصب‌شده (`INSTALLED_APPS`)

ترتیب تقریبی:

1. اپ‌های استاندارد Django (admin, auth, sessions, …)
2. **`django_ckeditor_5`** — ویرایشگر rich text
3. اپ‌های دامنه: **`website`**, **`accounts`**, **`dashboard`**, **`shop`**, **`cart`**, **`order`**, **`payment`**, **`review`**, **`blog`**
4. **`django_user_agents`** — برای `request.user_agent` در middleware بعدی

### ۳.۳ زنجیره Middleware

ترتیب مهم است؛ خلاصه منطق:

1. **`SecurityMiddleware`** — هدرهای امنیتی پایه
2. **`SessionMiddleware`** — session روی request
3. **`UserAgentMiddleware`** (django-user-agents) — پارس UA و attach به `request`
4. **`SiteLayoutCookieMiddleware`** (پروژه) — اگر `?site=mobile|desktop` باشد، بعد از پاسخ کوکی `site_layout` می‌گذارد و روی request فلگ موقت می‌گذارد
5. **`CommonMiddleware`**, **`CsrfViewMiddleware`**, **`AuthenticationMiddleware`**, **`MessageMiddleware`**, **`XFrameOptionsMiddleware`**

چرا **`UserAgentMiddleware`** قبل از **`SiteLayoutCookieMiddleware`**؟  
چون تشخیص دستگاه به UA وابسته است؛ کوکی `site_layout` فقط «اجبار» دستی روی همان منطق است.

### ۳.۴ قالب‌ها (`TEMPLATES`)

- **`DIRS`**: `[BASE_DIR / 'templates']` → تمپلیت‌های مشترک در `core/templates/`
- **`APP_DIRS: True`** → تمپلیت داخل هر اپ هم جستجو می‌شود
- **context processors**:
  - استاندارد: `debug`, `request`, `auth`, `messages`
  - **`shop.context_processors.shop_categories`** — دسته‌های فروشگاه در همه صفحات
  - **`core.context_processors.device.device`** — `device_type`, `is_mobile_site`, `base_template`, …

### ۳.۵ دیتابیس

- **PostgreSQL** با کلیدهای `PGDB_NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` از env (با پیش‌فرض مناسب docker مثل host `postgres`).

### ۳.۶ زمان و زبان

- **`LANGUAGE_CODE`**: `en-us`
- **`TIME_ZONE`**: از env با پیش‌فرض `UTC`

### ۳.۷ فایل‌های استاتیک و مدیا

| تنظیم | مقدار | معنی |
|--------|--------|------|
| `STATIC_URL` | `/static/` | URL پایه فایل‌های استاتیک |
| `MEDIA_URL` | `/media/` | URL پایه آپلودها |
| `STATIC_ROOT` | `BASE_DIR / 'staticfiles'` | جمع‌آوری برای production |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | ذخیره فایل‌های کاربر |
| `STATICFILES_DIRS` | `BASE_DIR / "static"` | استاتیک اضافی در dev |

در **`urls.py`** وقتی **`DEBUG=True`** است:

- **`staticfiles_urlpatterns()`** اضافه می‌شود تا استاتیک اپ‌ها (مثل bundle ادیتور) بدون `collectstatic` هم سرو شود.
- **`static(MEDIA_URL, MEDIA_ROOT)`** برای سرو مستقیم مدیا در dev.

### ۳.۸ کاربر سفارشی و redirect بعد از login

- **`AUTH_USER_MODEL = 'accounts.User'`** — مدل کاربر پیش‌فرض Django جایگزین شده.
- **`LOGIN_REDIRECT_URL`** و **`LOGOUT_REDIRECT_URL`** هر دو **`"/"`**.

### ۳.۹ پرداخت و PWA (ثابت‌ها در settings)

- **`MERCHANT_ID`**: در فایل با placeholder است؛ معمولاً باید از env خوانده شود (نکته ریفکتور بعدی).
- **`PWA_*`**: نام کوتاه، توضیح، نسخه کش برای manifest/service worker (جزئیات در `website/pwa_views.py`).

### ۳.۱۰ CKEditor 5

- **`CKEDITOR_5_CONFIGS`**: پیکربندی toolbar و بلاک‌ها برای فیلدهای rich text در ادمین/فرم‌ها.

---

## ۴. `urls.py` — درخت مسیر ریشه

| مسیر | مقصد |
|------|------|
| `admin/` | پنل Django admin |
| `manifest.webmanifest` | manifest PWA |
| `sw.js` | Service Worker |
| `''` | `website.urls` (صفحه اصلی و صفحات سایت) |
| `accounts/` | ثبت‌نام، لاگین، … |
| `shop/` | محصولات |
| `cart/` | سبد |
| `dashboard/` | پنل ادمین/مشتری |
| `order/` | سفارش، checkout |
| `payment/` | درگاه |
| `review/` | نظرات |
| `blog/` | وبلاگ |
| `ckeditor5/` | استاتیک/endpoint ادیتور |

---

## ۵. تشخیص دستگاه — `device.py`

این ماژول **تصمیم می‌گیرد layout موبایل است یا دسکتاپ** (تبلت عمداً مثل دسکتاپ).

### ۵.۱ `is_mobile_site(request) -> bool`

ترتیب منطق:

1. **اجبار با query یا کوکی**  
   - اگر `request.GET.get("site")` یا `request.COOKIES.get("site_layout")` برابر **`"mobile"`** → `True`  
   - اگر **`"desktop"`** → `False`

2. **Client Hints (Chrome/Android)**  
   - اگر `HTTP_SEC_CH_UA_MOBILE == "?1"` → موبایل

3. **django-user-agents**  
   - اگر `request.user_agent` نبود → `False`  
   - اگر `ua.is_mobile` و **نه** `ua.is_tablet` → موبایل

### ۵.۲ `get_device_type(request) -> str`

برمی‌گرداند: `"mobile"` یا `"desktop"` بر اساس `is_mobile_site`.

### ۵.۳ `filter_queryset_for_device(queryset, request, field_name="display_target")`

برای querysetهایی که فیلدی مثل `display_target` دارند، فقط ردیف‌هایی را نگه می‌دارد که برای دستگاه فعلی مجازند:

- موبایل: `("all", "mobile")`
- دسکتاپ: `("all", "desktop")`

---

## ۶. انتخاب تمپلیت — `device_templates.py`

- **`MOBILE_TEMPLATE_SUFFIX`**: `"-mobile"`  
  مثال: `shop/product-grid.html` → `shop/product-grid-mobile.html`

- **`template_exists(name)`** با `get_template` چک می‌کند تمپلیت وجود دارد یا نه.

- **`resolve_device_template(request, template_name, ...)`**  
  - اگر موبایل: اول تمپلیت موبایل (نام سفارشی یا suffix)؛ اگر وجود نداشت، همان `template_name` دسکتاپ.  
  - اگر دسکتاپ: `desktop_template_name` یا همان `template_name`.

این تابع جایی که view دو نسخه HTML جدا دارد، **بدون تکرار view** بین دو فایل سوئیچ می‌کند.

---

## ۷. Middleware — `middleware.py`

کلاس **`SiteLayoutCookieMiddleware`**:

- اگر در query **`site`** مقدار **`mobile`** یا **`desktop`** باشد:
  - روی **`request`** مقدار **`request.site_layout_cookie`** همان layout را می‌گذارد (برای استفاده‌های بعدی در همان request اگر لازم شود؛ منطق اصلی تشخیص در `device.py` از GET و COOKIE است).
  - روی **response** کوکی **`site_layout`** با مدت **۳۰ روز**، **`SameSite=Lax`** می‌نویسد.

نتیجه: کاربر یا تستر می‌تواند با **`?site=mobile`** یک بار layout را قفل کند تا با رفرش از بین نرود.

---

## ۸. Mixin برای viewها — `mixins.py`

**`DeviceTemplateMixin`** برای کلاس‌بیس ویوها (`TemplateView`, `ListView`, …):

- **`get_template_names()`**: اگر لیست نام تمپلیت از superclass خالی نباشد، فقط **اولین** نام را از **`resolve_device_template`** رد می‌کند و همان یک نام را برمی‌گرداند.
- **`get_template_name()`**: برای ویوهایی که یک `template_name` دارند (مثل `LoginView`).

ویژگی‌های اختیاری روی subclass:

- `mobile_template_name`
- `desktop_template_name`

**`dashboard/mixins.py`** فقط alias می‌دهد: `DashboardDeviceTemplateMixin = DeviceTemplateMixin` (خوانایی در کد داشبورد).

---

## ۹. Context processor — `context_processors/device.py`

تابع **`device(request)`** در همه تمپلیت‌ها این کلیدها را اضافه می‌کند:

| کلید | معنی |
|------|------|
| `device_type` | `"mobile"` یا `"desktop"` |
| `is_mobile_site` | بولین |
| `is_desktop_site` | نقیض موبایل |
| `base_template` | `base-mobile.html` یا `base-desktop.html` (برای `{% extends %}` قدیمی) |
| `base_mobile_template` / `base_desktop_template` | نام صریح baseها |

---

## ۱۰. تمپلیت تگ‌های مرتبط (خارج از پکیج `core` ولی هم‌موضوع)

فایل **`website/templatetags/device_tags.py`**:

- **`device_type`** (simple_tag): نوع دستگاه از روی `request` در context.
- **`mobile_site`** / **`desktop_site`** (filter روی `request`): برای شرط‌ها در تمپلیت.

این تگ‌ها همان **`core.device`** را صدا می‌زنند؛ پس رفتار با context processor یکسان است اگر `request` درست پاس داده شود.

---

## ۱۱. جریان یک درخواست (خلاصه ذهنی)

```
HTTP Request
  → SecurityMiddleware
  → SessionMiddleware
  → UserAgentMiddleware        # request.user_agent
  → SiteLayoutCookieMiddleware # ?site= → کوکی + فلگ روی request
  → … auth, csrf …
  → View (ممکن است DeviceTemplateMixin داشته باشد)
       → resolve_device_template → فلان-mobile.html یا دسکتاپ
  → Template با context از device() + بقیه processors
  → Response
```

---

## ۱۲. نکات یادگیری و ریفکتور بعدی (اختیاری)

1. **`MERCHANT_ID`** در settings بهتر است مثل بقیه از `config()` بیاید تا در repo ثابت نماند.
2. **`django-debug-toolbar`** در `requirements.txt` هست ولی در این `settings.py` دیده نمی‌شود؛ یا اضافه کن یا از requirements حذف کن تا ابهام نماند.
3. **تست واحد** برای `is_mobile_site` (حالت‌های: کوکی، query، Client Hint، UA موبایل/تبلت) ارزش زیاد دارد.
4. اگر جایی **`request.site_layout_cookie`** استفاده نشود، می‌توان مستند کرد یا حذفش کرد تا API request شلوغ نشود.

---

## ۱۳. اجرای محلی (یادآوری)

از پوشه **`core/`**:

```bash
python manage.py runserver
```

متغیرهای محیطی طبق `python-decouple` (فایل `.env` در کنار `manage.py` یا مسیر استاندارد decouple).

---

## ۱۴. فهرست مطالعه بعد از `core`

1. **`website/views.py`** — نمونه استفاده از mixin و بنرها  
2. **`website/urls.py`** — تطبیق URL با صفحه اصلی  
3. **`shop/context_processors.py`** — چرا دسته‌ها سراسری‌اند  

---

*آخرین به‌روزرسانی این سند هم‌راستا با کد پروژه در مسیر `core/core/` نوشته شده است.*
