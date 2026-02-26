# گزارش امنیت، ریفکتور و بهبود کد — shop-Arvin

این فایل شامل تمام قسمت‌هایی است که باید ریفکتور شوند، از نظر امنیتی مشکل دارند، یا با بهبود کد کیفیت و نگهداری بهتر می‌شوند.

---

## ۱. مشکلات امنیتی

### XSS (خروجی بدون escape / استفاده نادرست از mark_safe)

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/templates/shop/product-detail.html` | ~۲۷۲ | `{{ object.description\|safe }}` — توضیحات محصول به‌صورت HTML خام رندر می‌شود. اگر ادمین یا هر منبعی بتواند HTML/JS قرار دهد، XSS ذخیره‌شده رخ می‌دهد. بهتر است از pipeline امن برای HTML استفاده شود یا برای محتوای کاربر `\|safe` حذف شود. |
| `core/templates/messages.html` | ۶ | `{{ message\|safe }}` — پیام‌های Django می‌توانند تحت کنترل کاربر باشند. استفاده از `\|safe` امکان XSS می‌دهد. از escape پیش‌فرض استفاده کنید یا فقط تگ‌های امن را مجاز کنید. |

### Open Redirect (ریدایرکت ناامن)

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/website/views.py` | ۳۷، ۴۰ | `redirect(self.request.META.get('HTTP_REFERER'))` و `get_success_url` که `HTTP_REFERER` برمی‌گرداند — referer توسط مهاجم قابل کنترل است. ریدایرکت به آن کاربر را به سایت مخرب می‌فرستد. از URL ثابت یا لیست مجاز استفاده کنید. |
| `core/review/views.py` | ۲۸ | `return redirect(self.request.META.get('HTTP_REFERER'))` در `form_invalid` — همان مشکل؛ ریدایرکت نباید به referer وابسته باشد. |

### احراز هویت / مجوزدهی

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/payment/views.py` | ۱۲–۳۶ | `PaymentVerifyView` بدون `LoginRequiredMixin` است. اگر callback از درگاه است شاید عمدی باشد، اما: (۱) اگر `Authority` نباشد، `get_object_or_404(PaymentModel, authority_id=None)` رفتار عجیب دارد؛ (۲) هر کسی با `Authority` معتبر می‌تواند URL را بزند و پرداخت را تکمیل کند. وابستگی پرداخت به کاربر/سشن را چک کنید و قبل از lookup وجود `Authority` را تضمین کنید. |
| `core/cart/views.py` | ۹–۴۷ | ویوهای سبد خرید بدون CSRF exemption؛ برای سبد مهمان احتمالاً عمدی است. |

### اسرار/تنظیمات هاردکد شده

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/core/settings.py` | ۲۷ | `SECRET_KEY = config("SECRET_KEY", default='django-insecure-...')` — اگر در production تنظیم نشود، کلید از طریق ریپو لو می‌رود. در production default نگذارید یا در صورت نبودن fail fast کنید. |
| `core/core/settings.py` | ۱۵۳ | `MERCHANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"` — شناسه درگاه هاردکد است. باید از محیط/config بیاید (مثلاً `config("MERCHANT_ID")`). |
| `core/core/settings.py` | ۸۹–۹۶ | پسورد و تنظیمات DB دارای مقدار پیش‌فرض هستند. در production پسورد پیش‌فرض نگذارید. |

### مدیریت خطا / افشای اطلاعات

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/payment/views.py` | ۱۴–۲۴ | قبل از `get_object_or_404` وجود `authority_id` چک نمی‌شود. اگر پاسخ ZarinPal فاقد `RefID`/`Status` باشد ممکن است `KeyError` و 500 و افشای ساختار پاسخ رخ دهد. پارامترهای GET و کلیدهای پاسخ را اعتبارسنجی کنید. |
| `core/payment/views.py` | ۱۹ | `OrderModel.objects.get(payment=payment_obj)` — اگر سفارش لینک نشده باشد `DoesNotExist` و 500. از `get_object_or_404` یا هندلینگ صریح استفاده کنید. |
| `core/payment/zarinpal_client.py` | ۱۱–۱۲ | `except:` خالی در `get_domain()` — همه استثناها را می‌گیرد و `"example.com"` برمی‌گرداند. باگ‌های واقعی پنهان می‌شوند. استثنای مشخص بگیرید و/یا لاگ کنید. |

### order_by از ورودی کاربر

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| چندین لیست‌ویو | مثلاً `core/dashboard/admin/views/contacts.py` ۴۰–۴۲، `core/dashboard/admin/views/users.py` ۴۷–۴۹، `core/shop/views.py` ۳۳–۳۶ | `order_by`/`ordering` از `request.GET` گرفته و به `queryset.order_by(...)` داده می‌شود و فقط `FieldError` گرفته می‌شود. بهتر است لیست مجاز فیلدهای مرتب‌سازی داشته باشید. |

---

## ۲. موارد پیشنهادی برای ریفکتور

### DRY — منطق تکراری لیست‌ویوها

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| لیست‌ویوهای داشبورد (ادمین + مشتری) | مثلاً contacts، users، reviews، orders، newsletters، coupons، products، و ویوهای customer | الگوی تکراری: `get_paginate_by` از GET، `get_queryset` با جستجو (`q`)، فیلترها، و `order_by` با try/except. نام پارامترها متفاوت است (`order_by` vs `ordering`، `page_size` vs `paginate_by`). یک mixin یا کلاس پایه (مثلاً `SearchableSortableListMixin`) برای صفحه‌بندی، جستجو و مرتب‌سازی با لیست مجاز استخراج کنید. |

### الگوهای ناسازگار

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| لیست‌ویوهای داشبورد | چند فایل | صفحه‌بندی: بعضی `page_size`، بعضی `paginate_by`. مرتب‌سازی: بعضی `order_by`، بعضی `ordering`. یک نام‌گذاری و یک پیاده‌سازی واحد در همه لیست‌ها استفاده شود. |
| `core/dashboard/admin/views/contacts.py` و مشابه | ۲۹–۳۱ در مقابل ۲۱ | `ordering = "-created_date"` روی کلاس و دوباره در `get_queryset`. فقط در یک جا (کلاس یا متد) تعریف شود. |

### استفاده نادرست یا شکننده از کوئری

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/dashboard/admin/views/orders.py` | ۲۳ | `queryset.filter(id__icontains=search_q)` — `OrderModel.id` معمولاً عدد است. `id__icontains` برای رشته است؛ از تطابق دقیق استفاده کنید، مثلاً `id=search_q` (با چک نوع یا catch کردن `ValueError`). |
| `core/dashboard/customer/views/orders.py` | ۲۲ | همان: `id__icontains=search_q` روی id سفارش؛ باید تطابق دقیق و type-safe باشد. |

### ویوهای طولانی / پیچیده

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/order/views.py` | `OrderCheckOutView` (مثلاً ۳۵–۱۰۸) | یک ویو سفارش، آیتم‌ها، خالی کردن سبد، کوپن و پرداخت را انجام می‌دهد. توابع کمکی (مثلاً `create_order`، `create_order_items`، `apply_coupon`، `create_payment_url`) را در یک سرویس یا لایه مدل استخراج کنید. |

### نبود type hint و docstring

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| اکثر ویوها و `core/cart/cart.py` | در سراسر | بسیاری از ویوها و `CartSession` type hint و docstring ندارند. اضافه کردن آن‌ها نگهداری و پشتیبانی IDE را بهتر می‌کند. |
| `core/website/views.py` | ۲۱–۴۲ | `SendContactView` docstring کوتاه دارد؛ درباره عدم استفاده از `HTTP_REFERER` در production یک خط توضیح اضافه شود. |

### روش‌های منسوخ یا شکننده

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/payment/zarinpal_client.py` | ۶–۱۲ | `get_domain()` از `Site.objects.get_current()` و `except` خالی استفاده می‌کند. برای URL callback پرداخت شکننده است؛ `settings.SITE_DOMAIN` و هندلینگ صریح استثنا را در نظر بگیرید. |
| `core/shop/views.py` | ۷۳–۷۵ | `get_object` روی `obj.product_images.prefetch_related()` صدا می‌زند بدون return؛ `prefetch_related` کوئری‌ست جدید برمی‌گرداند و obj را عوض نمی‌کند. باید در `get_queryset()` از `prefetch_related('product_images')` استفاده شود، نه روی آبجکت بعد از لود. |

### مقاومت سشن سبد خرید

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/cart/cart.py` | ۴۵–۴۶، ۸۱–۸۲، `get_cart_items` | `ProductModel.objects.get(id=item["product_id"], ...)` — اگر محصول حذف یا غیرفعال شده باشد `DoesNotExist` و 500. با `filter(...).first()` چک کنید و آیتم نامعتبر را حذف یا رد کنید. |
| `core/cart/cart.py` | ۱۲ | `int(quantity)` در `update_product_quantity` — ورودی غیرعددی `ValueError` می‌دهد. اعتبارسنجی یا catch کنید تا 500 نشود. |

### الگوهای تکراری در قالب/JS

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| قالب‌های لیست (ادمین + مشتری) | مثلاً order-list، product-list، contact-list | JS مشابه برای ساخت query string و به‌روزرسانی URL. می‌توان در یک اسکریپت/کامپوننت مشترک قرار داد. |

---

## ۳. بهبود کد (کیفیت، خوانایی، نگهداری)

### محاسبه قیمت و دقت عددی

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/shop/models.py` | ۵۱–۵۴ | در `get_price()` از `Decimal(self.discount_percent / 100)` استفاده شده. برای شفافیت و جلوگیری از خطای تقسیم صحیح در نسخه‌های مختلف، بهتر است `Decimal(self.discount_percent) / Decimal(100)` استفاده شود تا محاسبه تخفیف همیشه دقیق باشد. |

### عدم استفاده از لاگینگ

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| کل پروژه | — | هیچ ماژول `logging` یا `logger` استفاده نشده. برای خطاها (مثلاً در payment callback، exceptionها)، اقدامات مهم (ثبت سفارش، پرداخت، ورود/خروج) و دیباگ، استفاده از `logging` با سطوح مناسب (ERROR، INFO، DEBUG) پیشنهاد می‌شود. |

### نبود تست

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| پروژه | — | پوشه یا فایل‌های تست (مثلاً `tests/`، `test_*.py`) در اپ‌ها وجود ندارد. اضافه کردن تست واحد و یکپارچه برای فرم‌ها، ویوهای حساس (checkout، payment، cart) و مدل‌ها ریگرسیون را کم و refactor را امن‌تر می‌کند. |

### کامنت اشتباه و پیام‌های ناسازگار

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/order/forms.py` | ۲۹ | در `clean_coupon` کامنت «Check if the address_id belongs to the requested user» اشتباه است (کپی از `clean_address_id`). اصلاح به توضیح مربوط به کوپن. |
| `core/order/forms.py` و سایر فرم‌ها | در سراسر | ترکیب انگلیسی و فارسی در پیام‌های ValidationError (مثلاً "Invalid address..." در مقابل "کد تخفیف اشتباه است"). یک زبان یا ترجمه یکپارچه برای UX بهتر. |

### منطق اضافه و خوانایی فرم

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/order/forms.py` | ۳۱–۳۶ | بعد از `except CouponModel.DoesNotExist` مقدار `coupon` همان `None` است؛ بلافاصله بعد `if coupon:` چک می‌شود. بعد از raise کردن در DoesNotExist، شرط `if coupon:` برای آن مسیر بی‌معناست. می‌توان ساختار را ساده‌تر کرد تا خوانایی بهتر شود. |

### استفاده از `.get()` بدون هندلینگ خطا

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/dashboard/customer/views/profiles.py` | ۲۸، ۴۰ | `Profile.objects.get(user=self.request.user)` — اگر برای کاربر پروفایل ساخته نشده باشد `DoesNotExist` و 500. یا با signal برای هر User یک Profile بسازید، یا از `get_or_create` / `get_object_or_404` و هندلینگ مناسب استفاده کنید. |
| `core/dashboard/admin/views/profiles.py` | ۲۷، ۳۹ | همان مورد برای پروفایل ادمین. |
| `core/order/views.py` | ۴۱، ۱۰۲، ۱۴۴ | `CartModel.objects.get(user=...)` — در صورت نبود سبد، exception. با `get_or_create` یا `filter().first()` و ایجاد در صورت نیاز امن‌تر است. |

### اعتبارسنجی ورودی در ویوها

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/cart/views.py` | ۱۳، ۲۶، ۳۸–۳۹ | `product_id` و `quantity` مستقیم از `request.POST.get` خوانده می‌شوند. برای نوع (مثلاً عدد)، محدوده و وجود مقدار بهتر است از Django Form یا اعتبارسنجی صریح استفاده شود تا رفتار یکسان و پیام خطای مناسب داشته باشید. |
| `core/shop/views.py` | ۸۱ | `product_id = request.POST.get("product_id")` — همان پیشنهاد استفاده از فرم یا اعتبارسنجی. |
| `core/order/views.py` | ۱۲۱ | `code = request.POST.get("code")` — ترجیحاً از فرم با فیلد `code` و `clean_code` استفاده شود. |

### باگ و بدرفتاری در مدیریت دستور

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/shop/management/commands/generate_products.py` | ۳۴ | تایپو: `selected_categoreis` → `selected_categories`. |
| `core/shop/management/commands/generate_products.py` | ۳۴ | `user = user` بی‌فایده است؛ حذف شود. |
| `core/shop/management/commands/generate_products.py` | ۳۹ | `open(BASE_DIR / selected_image, "rb")` بدون `with` — فایل بسته نمی‌شود. از `with open(...) as f:` و سپس `File(file=f, ...)` استفاده کنید تا resource leak نشود. |
| `core/shop/management/commands/generate_products.py` | ۱۹–۲۹ | اگر ادمین وجود نداشته باشد `User.objects.get(type=UserType.admin.value)` باعث crash می‌شود. یا در مستندات ذکر شود یا با `get_or_create` / چک وجود و پیام واضح هندل شود. |

### استفاده نادرست از prefetch_related

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/shop/views.py` | ۷۳–۷۵ | در `get_object` بعد از لود آبجکت، `obj.product_images.prefetch_related()` صدا زده می‌شود؛ نتیجه آن استفاده نمی‌شود و روی تعداد کوئری اثر نمی‌گذارد. برای کاهش N+1 باید در همان ویو از `get_queryset()` و `prefetch_related('product_images')` روی queryset استفاده شود. |
| `core/dashboard/admin/views/products.py` | ۸۹ | همان الگوی نادرست؛ نتیجه `prefetch_related()` روی relation بعد از لود استفاده نشده. |

### امکان N+1 در کوئری‌ها

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| لیست‌ویوهای داشبورد و شاپ | چند فایل | در لیست محصولات، سفارشات، کاربران و غیره در صورت نمایش relationها (مثلاً category، user، order items) از `select_related` و `prefetch_related` در `get_queryset` استفاده شود تا N+1 query ایجاد نشود. |

### یکنواختی نام‌گذاری و فاصله‌گذاری

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| چندین فایل | — | در بعضی جاها فاصله بعد از کاما نیست (مثلاً `status=ProductStatusType.publish.value` بدون فاصله بعد از `,`). رعایت PEP 8 (مثلاً `black` یا `ruff`) برای یکنواختی و خوانایی بهتر. |
| مدل‌ها و فرم‌ها | — | نام کلاس‌ها گاهی با پسوند `Model`/`Form` و گاهی بدون؛ یک قرارداد ثابت (مثلاً همیشه پسوند مدل) نگهداری را راحت‌تر می‌کند. |

### استفاده از super() با سینتکس قدیمی

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/order/forms.py` | ۱۱ | `super(CheckOutForm, self).__init__(...)` — در Python 3 کافی است `super().__init__(*args, **kwargs)` استفاده شود. |

### پیام‌های موفقیت/خطا و دستور زبان

| محل | خط/ناحیه | توضیح |
|-----|----------|--------|
| `core/dashboard/customer/views/profiles.py` | ۴۳ | «لطف مجدد بررسی» — اصلاح به «لطفاً مجدداً بررسی» یا جمله کامل‌تر برای رفع ابهام. |
| `core/dashboard/admin/views/profiles.py` | ۴۲ | همان متن؛ یکسان‌سازی و اصلاح املایی. |

---

## جدول خلاصه

| # | نوع | فایل(ها) | خلاصه |
|---|-----|-----------|--------|
| 1 | امنیت | `core/templates/shop/product-detail.html` | XSS: `object.description\|safe` |
| 2 | امنیت | `core/templates/messages.html` | XSS: `message\|safe` |
| 3 | امنیت | `core/website/views.py`, `core/review/views.py` | Open redirect با `HTTP_REFERER` |
| 4 | امنیت | `core/payment/views.py` | callback پرداخت: بدون اعتبارسنجی، `OrderModel.objects.get` ممکن است exception بدهد |
| 5 | امنیت | `core/core/settings.py` | SECRET_KEY پیش‌فرض، MERCHANT_ID هاردکد، پسورد پیش‌فرض DB |
| 6 | امنیت | `core/payment/zarinpal_client.py` | except خالی در get_domain() |
| 7 | امنیت | چندین لیست‌ویو | order_by از GET — لیست مجاز در نظر بگیرید |
| 8 | ریفکتور | لیست‌ویوهای داشبورد و شاپ | DRY: mixin مشترک برای صفحه‌بندی، جستجو، مرتب‌سازی |
| 9 | ریفکتور | لیست‌ویوهای ادمین/مشتری | ناسازگاری page_size/paginate_by و order_by/ordering |
| 10 | ریفکتور | orders.py ادمین و مشتری | id__icontains روی id سفارش (عددی) |
| 11 | ریفکتور | `core/order/views.py` | تفکیک منطق checkout به سرویس/توابع کمکی |
| 12 | ریفکتور | `core/cart/cart.py` | هندل کردن محصول حذفشده و quantity نامعتبر |
| 13 | ریفکتور | `core/shop/views.py` | اصلاح استفاده از prefetch در ShopProductDetailView.get_object |
| 14 | ریفکتور | قالب‌های لیست | JS مشترک برای URL و query string |
| 15 | بهبود کد | `core/shop/models.py` | محاسبه تخفیف با Decimal برای دقت عددی |
| 16 | بهبود کد | کل پروژه | اضافه کردن logging برای خطاها و اقدامات مهم |
| 17 | بهبود کد | پروژه | نوشتن تست واحد و یکپارچه |
| 18 | بهبود کد | `core/order/forms.py` | اصلاح کامنت اشتباه و یکنواخت کردن زبان پیام‌ها |
| 19 | بهبود کد | `core/order/forms.py` | ساده‌سازی شرط‌های clean_coupon |
| 20 | بهبود کد | profiles (customer/admin) | هندل کردن DoesNotExist برای Profile و Cart |
| 21 | بهبود کد | `core/cart/views.py`, `core/shop/views.py`, `core/order/views.py` | اعتبارسنجی ورودی با Form یا validation صریح |
| 22 | بهبود کد | `core/shop/management/commands/generate_products.py` | تایپو، حذف تخصیص اضافه، با open از with استفاده، هندل نبود ادمین |
| 23 | بهبود کد | لیست‌ویوها | استفاده از select_related/prefetch_related برای جلوگیری از N+1 |
| 24 | بهبود کد | چندین فایل | یکنواختی PEP 8 و نام‌گذاری |
| 25 | بهبود کد | `core/order/forms.py` | استفاده از super() بدون آرگومان صریح (Python 3) |
| 26 | بهبود کد | پیام‌های داشبورد | اصلاح املاء و دستور («لطفاً مجدداً») |

---

**توصیه:** ابتدا موارد امنیتی را برطرف کنید، سپس ریفکتورهایی که روی صحت و نگهداری اثر دارند، و در نهایت بهبودهای کیفیت کد (لاگینگ، تست، خوانایی).
