# مستندات: احراز هویت، ثبت‌نام، OTP و کاوه‌نگار

این سند به‌صورت خلاصه اما کامل توضیح می‌دهد در پروژه **shop-Arvin** برای حساب کاربری، API، پیامک OTP و یکپارچگی با **کاوه‌نگار** چه کارهایی انجام شده است.

---

## ۱. هدف کلی

- **ثبت‌نام با ایمیل**: ایمیل + رمز (بدون OTP ایمیل).
- **ثبت‌نام با موبایل**: شماره ایرانی → ارسال OTP (کاوه‌نگار) → تأیید کد + تعیین رمز → ایجاد کاربر با موبایل تأییدشده.
- **ورود (لاگین)**: با **ایمیل یا شماره موبایل** + رمز.
- **تأیید اجباری موبایل در checkout**: اگر موبایل ثبت نشده یا **تأیید نشده** باشد، کاربر به ویرایش پروفایل هدایت می‌شود و باید OTP را تکمیل کند.
- **اعتبارسنجی موبایل ایرانی**: فرمت `09xxxxxxxxx` (۱۱ رقم) با نرمال‌سازی ارقام فارسی در لایه اعتبارسنجی.
- **API**: Django REST Framework + **Simple JWT** برای توکن‌های دسترسی.

---

## ۲. مدل‌ها (`accounts/models.py`)

### کاربر (`User`)

- **`email`**: اختیاری، یکتا در صورت مقداردهی (`null=True`, `unique=True` مطابق رفتار PostgreSQL برای چند رکورد بدون ایمیل).
- **`phone_number`**: اختیاری، یکتا، حداکثر ۱۱ کاراکتر، با validator شماره ایرانی.
- **`is_verified`**: برای سناریوی «تأیید ایمیل» در آینده؛ در ثبت‌نام ایمیلی فعلی `False` می‌ماند.
- **`phone_verified`**: آیا موبایل با OTP (ثبت‌نام یا تأیید بعدی) تأیید شده است.
- **`CheckConstraint`**: حداقل یکی از `email` یا `phone_number` باید پر باشد.

**`UserManager`**

- **`create_user(password, email=None, phone_number=None, **extra_fields)`**: حداقل یکی از ایمیل یا موبایل الزامی است؛ نرمال‌سازی ایمیل و موبایل انجام می‌شود.
- **`create_superuser`**: برای سوپریوزر، `is_verified` و `phone_verified` به‌صورت پیش‌فرض **True** تنظیم می‌شوند (طبق نیاز پروژه).

**`save()` روی `User`**

- رشته‌های خالی برای ایمیل/موبایل به `NULL` تبدیل می‌شوند تا محدودیت یکتایی و Check درست عمل کنند.

### پروفایل (`Profile`)

- فقط **`first_name`**, **`last_name`** (هر دو می‌توانند خالی باشند)، **`image`** و ارتباط **OneToOne** با `User`.
- فیلد **`phone_number` از پروفایل حذف شده**؛ شماره موبایل فقط روی مدل **`User`** نگه داشته می‌شود.

**سیگنال `post_save`**

- با ایجاد هر `User`، یک `Profile` خالی به‌صورت خودکار ساخته می‌شود.

### کد OTP (`OTPCode`)

- **`mobile`**, **`code`** (۶ رقم)، **`created_at`**, **`is_used`**.
- در **`save()`** اگر کد خالی باشد، کد ۶ رقمی تصادفی تولید می‌شود.
- **`is_valid()`**: کد استفاده‌نشده و حداکثر **۲ دقیقه** از زمان ایجاد گذشته باشد.
- **`Meta.ordering`**: `-created_at`.

---

## ۳. بک‌اند احراز هویت (`accounts/backends.py`)

کلاس **`EmailOrPhoneBackend`**:

- اگر ورودی شبیه ایمیل باشد (`@` دارد)، کاربر با ایمیل نرمال‌شده پیدا می‌شود.
- در غیر این صورت، ورودی به صورت شماره موبایل (با تبدیل ارقام فارسی به لاتین و در صورت نیاز اضافه کردن صفر ابتدای ۱۰ رقمی) با فیلد **`phone_number`** جستجو می‌شود.
- رمز با **`check_password`** بررسی می‌شود.
- در **`AUTHENTICATION_BACKENDS`** در تنظیمات، **قبل از** `ModelBackend` قرار گرفته تا ورود با موبایل ممکن باشد.

---

## ۴. اعتبارسنجی موبایل (`accounts/validators.py`)

تابع **`validate_iranian_cellphone_number`**:

- ارقام فارسی به لاتین تبدیل می‌شوند.
- فقط الگوی **`^09\d{9}$`** پذیرفته می‌شود؛ در غیر این صورت خطا با پیام فارسی.

---

## ۵. کاوه‌نگار و OTP (`accounts/utils.py`)

- **`generate_otp_code()`**: عدد تصادفی ۶ رقمی به‌صورت رشته.
- **`send_otp_via_kavenegar(phone_number, code)`**:
  - مطابق **نمونه رسمی** کاوه‌نگار: `KavenegarAPI` + **`verify_lookup`** با پارامترهای `receptor`, `template`, `token` (کد OTP), `token2` (مدت اعتبار به دقیقه), `type='sms'`.
  - `token2` از **`OTPCode.VALIDITY_MINUTES`** (پیش‌فرض: ۲) پر می‌شود.
  - خطاهای **`APIException`** و **`HTTPException`** جداگانه لاگ می‌شوند؛ در صورت موفقیت، پاسخ در سطح INFO لاگ می‌شود.

**تنظیمات محیط** (در `core/settings.py` و معمولاً `.env`):

| متغیر | توضیح |
|--------|--------|
| `KAVENEGAR_API_KEY` | کلید API |
| `KAVENEGAR_TEMPLATE` | نام الگوی verify در پنل (پیش‌فرض: `verify`) |

**متن پیشنهادی الگو در پنل کاوه‌نگار:**

```
کد ورود به فروشگاه آروین:
%token

مدت اعتبار : %token2
```

الگو باید دقیقاً با **`%token`** و **`%token2`** هم‌خوان باشد؛ `token2` فقط عدد لاتین (مثلاً `2`) است.

---

## ۶. سریالایزرهای API (`accounts/serializers.py`)

| سریالایزر | کاربرد |
|-----------|--------|
| `UserSerializer` | خروجی اطلاعات کاربر (بدون رمز) |
| `RegisterEmailSerializer` | ایمیل، رمز، تکرار رمز؛ ایجاد کاربر با `is_verified=False` |
| `SendOTPSerializer` | شماره موبایل؛ بررسی تکراری نبودن کاربر |
| `VerifyOTPRegisterSerializer` | موبایل، کد، رمز، تکرار؛ اعتبار OTP؛ ایجاد کاربر با `phone_verified=True` و علامت‌گذاری OTP مصرف‌شده |
| `LoginSerializer` | فیلد `username` (ایمیل یا موبایل) + `password`؛ `authenticate` |
| `VerifyPhoneOTPSerializer` | فقط `code` برای کاربر لاگین‌شده؛ تطبیق با آخرین OTP معتبر برای **`request.user.phone_number`** |

پیام‌های خطای فیلدها به فارسی هستند؛ **رمز** در پاسخ JSON برگردانده نمی‌شود.

---

## ۷. ویوها (`accounts/views.py`)

### وب (سشن)

- **`LoginView` / `LogoutView` / `RegisterView`**: فرم‌های کلاسیک؛ ثبت‌نام با **`create_user(password, email=..., phone_number=...)`** و به‌روزرسانی نام روی `Profile` (بدون ذخیره موبایل روی پروفایل).
- **`WebSendVerifyPhoneOTPView`**: برای کاربر لاگین؛ ساخت `OTPCode` و ارسال با کاوه‌نگار؛ ریدایرکت به پروفایل مشتری یا ادمین بر اساس نقش.
- **`WebVerifyPhoneOTPView`**: تأیید کد از `POST` فرم؛ همان منطق سریالایزر؛ پیام flash و ریدایرکت.

### API (DRF)

- **`RegisterEmailView`**: `POST` → ایجاد کاربر → **`UserSerializer` + JWT** (`refresh` / `access`).
- **`SendOTPView`**: `POST` → ذخیره OTP → ارسال پیامک.
- **`VerifyOTPRegisterView`**: `POST` → ایجاد کاربر + JWT.
- **`LoginAPIView`**: `POST` → JWT.
- **`SendVerifyPhoneOTPView`**: `POST`، **نیازمند احراز هویت** (JWT پیش‌فرض DRF).
- **`VerifyPhoneOTPView`**: `POST`، احراز هویت + بدنه `{ "code": "..." }`.

تابع کمکی **`_jwt_payload(user)`** با **`RefreshToken.for_user`** توکن تولید می‌کند.

---

## ۸. مسیرها (URL)

### پیشوند `/api/accounts/` — فایل `accounts/api_urls.py`

| متد | مسیر | نام route |
|-----|------|-----------|
| POST | `/api/accounts/register/email/` | `api-register-email` |
| POST | `/api/accounts/register/phone/send-otp/` | `api-register-send-otp` |
| POST | `/api/accounts/register/phone/verify-otp/` | `api-register-verify-otp` |
| POST | `/api/accounts/login/` | `api-login` |
| POST | `/api/accounts/verify-phone/send-otp/` | `api-verify-phone-send-otp` |
| POST | `/api/accounts/verify-phone/verify-otp/` | `api-verify-phone-verify-otp` |

اتصال در **`core/urls.py`**:

```python
path('api/accounts/', include('accounts.api_urls')),
```

### پیشوند `/accounts/` — فایل `accounts/urls.py`

- ورود / خروج / ثبت‌نام وب.
- **`/accounts/verify-phone/web/send-otp/`** و **`/accounts/verify-phone/web/verify-otp/`** برای فرم‌های داخل داشبورد.

---

## ۹. تنظیمات Django (`core/settings.py`)

- **`INSTALLED_APPS`**: `rest_framework`, `rest_framework_simplejwt`.
- **`AUTHENTICATION_BACKENDS`**: ابتدا `accounts.backends.EmailOrPhoneBackend`، سپس `ModelBackend`.
- **`REST_FRAMEWORK`**: پیش‌فرض احراز هویت **`JWTAuthentication`**.
- **`SIMPLE_JWT`**: مثلاً access یک روز، refresh هفت روز (مقادیر دقیق در همان فایل).

---

## ۱۰. وابستگی‌ها (`requirements.txt`)

از جمله:

- `djangorestframework`
- `djangorestframework-simplejwt`
- `kavenegar`

---

## ۱۱. فرم‌ها و داشبورد

- **`accounts/forms.py`**: `AuthenticationForm` با برچسب «ایمیل یا شماره موبایل»؛ `UserRegistrationForm` با نرمال‌سازی ایمیل/موبایل و جلوگیری از تکراری بودن.
- **`dashboard/customer/forms/profiles.py`** و **`dashboard/admin/forms/profiles.py`**: فیلد موبایل روی فرم ولی ذخیره روی **`User.phone_number`**؛ در صورت **تغییر شماره**، **`phone_verified=False`** می‌شود تا دوباره OTP لازم باشد.
- **قالب‌های** `templates/dashboard/.../profile-edit.html`: نمایش ایمیل (حتی اگر خالی)، فرم موبایل، و در صورت داشتن موبایل و نبود تأیید، دکمه ارسال کد و فیلد تأیید که به URLهای وب `accounts` POST می‌کنند.

---

## ۱۲. ادمین (`accounts/admin.py`)

- در لیست و فرم کاربر، فیلدهای **`phone_number`** و **`phone_verified`** دیده می‌شوند.
- در پروفایل، **`phone_number` حذف شده**؛ جستجو می‌تواند روی `user__email` و `user__phone_number` باشد.

---

## ۱۳. سفارش (`order/views.py`)

در **`OrderCheckOutView.dispatch`**:

- اگر کاربر **موبایل ندارد** یا **`phone_verified` برابر False** باشد، با پیام فارسی به **`dashboard:customer:profile-edit`** ریدایرکت می‌شود تا ابتدا شماره را ثبت/تأیید کند.

---

## ۱۴. مهاجرت پایگاه داده

- **`0002_user_phone_otp_profile`**: اضافه شدن فیلدهای موبایل به `User`، nullable کردن ایمیل، حذف `phone_number` از `Profile`، کپی شماره از پروفایل قدیمی به کاربر، برای داده‌های مهاجرت‌شده **`phone_verified=True`** تا رفتار قبلی فروشگاه قطع نشود، ایجاد مدل **`OTPCode`**, محدودیت Check روی کاربر.
- **`0003_meta_verbose`**: هم‌راستاسازی `verbose_name` و Meta پروفایل با مدل فعلی.

پس از deploy:

```bash
cd core && python manage.py migrate
```

---

## ۱۵. نمونه درخواست API (خلاصه)

**ثبت‌نام ایمیل**

```http
POST /api/accounts/register/email/
Content-Type: application/json

{"email": "user@example.com", "password": "********", "password2": "********"}
```

**ارسال OTP ثبت‌نام موبایل**

```json
{"phone_number": "09123456789"}
```

**تأیید OTP + ثبت‌نام**

```json
{"phone_number": "09123456789", "code": "123456", "password": "********", "password2": "********"}
```

**لاگین**

```json
{"username": "user@example.com یا 09123456789", "password": "********"}
```

**تأیید موبایل (با هدر Authorization: Bearer <access>)**

```json
POST /api/accounts/verify-phone/send-otp/
{}

POST /api/accounts/verify-phone/verify-otp/
{"code": "123456"}
```

---

## ۱۶. نکات امنیتی و عملیاتی

- کلید کاوه‌نگار و `SECRET_KEY` را در مخزن git قرار ندهید؛ از `.env` استفاده کنید.
- برای اپ موبایل/فرانت جدا، CORS و محدودیت نرخ درخواست OTP را در نظر بگیرید.
- انقضای OTP دو دقیقه است؛ در صورت نیاز کسب‌وکار، فقط مقدار ثابت در **`OTPCode.is_valid()`** را تغییر دهید.

---

## ۱۷. فهرست فایل‌های مرتبط

| مسیر | نقش |
|------|-----|
| `core/accounts/models.py` | `User`, `Profile`, `OTPCode`, مدیر کاربر، سیگنال |
| `core/accounts/backends.py` | ورود با ایمیل یا موبایل |
| `core/accounts/validators.py` | اعتبار موبایل ایرانی |
| `core/accounts/utils.py` | OTP تصادفی + کاوه‌نگار `verify_lookup` |
| `core/accounts/serializers.py` | سریالایزرهای DRF |
| `core/accounts/views.py` | ویو وب + ویو API + ویو وب OTP |
| `core/accounts/api_urls.py` | مسیرهای `/api/accounts/` |
| `core/accounts/urls.py` | مسیرهای `/accounts/` |
| `core/core/urls.py` | include کردن `api/accounts` و `accounts` |
| `core/core/settings.py` | DRF، JWT، backends، کاوه‌نگار |
| `requirements.txt` | پکیج‌ها |
| `core/accounts/migrations/0002_*.py`, `0003_*.py`, `0004_smssettings.py` | تغییر اسکیما + تنظیمات پیامک |

---

## ۱۸. روشن/خاموش کردن ارسال پیامک

مدل **`SMSSettings`** (یک ردیف، مثل تنظیمات پرداخت):

- فیلد **`sms_enabled`**: اگر **غیرفعال** باشد، قبل از ساخت `OTPCode` در API و وب بررسی می‌شود و درخواست با پیام فارسی **۴۰۰** (API) یا پیام flash (وب) رد می‌شود؛ در **`send_otp_via_kavenegar`** هم به‌صورت تدافعی بررسی می‌شود.

**داشبورد ادمین (پیشنهادی):**

- مسیر: **`/dashboard/admin/settings/sms/`** (نام route: `dashboard:admin:sms-settings`)
- منو: بخش **کاربران → تنظیمات پیامک (OTP)**
- سوئیچ «ارسال پیامک OTP فعال است» — همان مدل `SMSSettings`؛ تغییر از Django Admin و داشبورد ادمین روی یک ردیف است.

**Django Admin (اختیاری):** بخش **«تنظیمات پیامک (OTP)»** در اپ accounts.

مهاجرت: **`accounts/migrations/0004_smssettings.py`**

---

*آخرین به‌روزرسانی این سند با وضعیت پیاده‌سازی در مخزن هم‌خوان است؛ در صورت تغییر کد، این فایل را نیز به‌روز کنید.*
