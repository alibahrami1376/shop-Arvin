# راهنمای نصب و راه‌اندازی اپلیکیشن Blog

## فایل‌های ایجاد شده

### 1. مدل‌ها (`core/blog/models.py`)
- **Category**: مدل دسته‌بندی بلاگ
- **Post**: مدل پست بلاگ با فیلدهای زیر:
  - author: نویسنده (ForeignKey به User)
  - image: تصویر پست
  - title: عنوان
  - content: محتوا (با CKEditor)
  - url: لینک اختیاری
  - category: دسته‌بندی‌ها (ManyToMany)
  - counted_view: تعداد بازدید
  - status: وضعیت انتشار
  - published_date: تاریخ انتشار
  - created_date: تاریخ ایجاد
  - updated_date: تاریخ بروزرسانی

### 2. Admin Panel (`core/blog/admin.py`)
- پنل ادمین کامل برای مدیریت پست‌ها و دسته‌بندی‌ها
- امکان ویرایش محتوا با CKEditor
- فیلتر و جستجو

### 3. Views (`core/blog/views.py`)
- `blog_home`: نمایش لیست پست‌ها با pagination
- `blog_detail`: نمایش جزئیات پست + افزایش بازدید
- `blog_search`: جستجو در پست‌ها

### 4. URLs
- **core/urls.py**: مسیرهای blog و ckeditor اضافه شده
- **blog/urls.py**: ایجاد شده

### 5. Templates
- **blog-home.html**: صفحه لیست مقالات با sidebar و pagination
- **blog-detail.html**: صفحه جزئیات مقاله با مقالات مرتبط
- **blog-search.html**: صفحه جستجو در مقالات

## مراحل نصب

### 1. ایجاد فایل urls.py در blog
به دلیل محدودیت دسترسی، باید فایل `core/blog/urls.py` را به صورت دستی ایجاد کنید:

```bash
sudo nano /home/bahrami/Desktop/projects/shop-Arvin/core/blog/urls.py
```

و محتوای زیر را در آن قرار دهید:

```python
from django.urls import path
from blog.views import blog_home, blog_detail, blog_search

app_name = "blog"

urlpatterns = [
    path("", blog_home, name="blog_home"),
    path("<int:post_id>/", blog_detail, name="blog_detail"),
    path("category/<str:cat_name>/", blog_home, name="category"),
    path("search/", blog_search, name="search"),
]
```

### 2. نصب پکیج‌های مورد نیاز

```bash
pip install django-ckeditor-5>=0.2.12
```

یا:

```bash
pip install -r requirements.txt
```

### 3. اجرای Migration

```bash
cd core
python manage.py makemigrations blog
python manage.py migrate
```

### 4. ایجاد تصویر پیش‌فرض
یک تصویر با نام `default.png` در مسیر `core/media/blog/` قرار دهید.

### 5. ایجاد Superuser (در صورت نیاز)

```bash
python manage.py createsuperuser
```

## استفاده

### دسترسی به Admin Panel
1. به آدرس `/admin/` بروید
2. وارد شوید
3. از بخش Blog می‌توانید:
   - دسته‌بندی ایجاد کنید
   - پست جدید اضافه کنید
   - پست‌ها را ویرایش کنید

### URLهای بلاگ
- `/blog/` - لیست تمام پست‌ها
- `/blog/<post_id>/` - جزئیات یک پست
- `/blog/category/<cat_name>/` - پست‌های یک دسته‌بندی
- `/blog/search/?q=<query>` - جستجو در پست‌ها

## تنظیمات انجام شده

### settings.py
- `django_ckeditor_5` به INSTALLED_APPS اضافه شد
- تنظیمات CKEditor پیکربندی شد

### core/urls.py
- مسیر `blog/` اضافه شد
- مسیر `ckeditor5/` برای آپلود تصویر اضافه شد

## نکات مهم

1. **تصویر پیش‌فرض**: حتماً یک تصویر default.png در `media/blog/` قرار دهید
2. **دسترسی‌ها**: اطمینان حاصل کنید که پوشه media قابل نوشتن است
3. **Template‌ها**: باید template‌های زیر را ایجاد کنید:
   - `templates/blog/blog-home.html`
   - `templates/blog/blog-detail.html`
   - `templates/blog/blog-search.html`

## مثال استفاده در Template

```django
{% for post in posts %}
    <article>
        <h2>{{ post.title }}</h2>
        <img src="{{ post.image.url }}" alt="{{ post.title }}">
        <div>{{ post.content|safe }}</div>
        <p>بازدید: {{ post.counted_view }}</p>
        <p>نویسنده: {{ post.author }}</p>
        <a href="{{ post.get_absolute_url }}">ادامه مطلب</a>
    </article>
{% endfor %}
```

## رفع مشکلات احتمالی

### خطای Import CKEditor
```bash
pip install --upgrade django-ckeditor-5
```

### خطای Migration
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### مشکل آپلود تصویر
بررسی کنید که:
- پوشه media وجود دارد
- دسترسی نوشتن دارد
- MEDIA_URL و MEDIA_ROOT در settings تنظیم شده‌اند
