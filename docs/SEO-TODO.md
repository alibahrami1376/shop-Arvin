# SEO Technical Foundation — تسک‌لیست اولویت‌دار آروین

**مرحله فعلی:** ۱ — Technical SEO Foundation  
**قبل از:** Pillar / Keyword Map / Topic Clusters / Backlinks

> داشتن `sitemap` و `robots.txt` ≠ Technical SEO تمام‌شده.  
> این فایل بر اساس وضعیت **واقعی کد** پروژه (Django Templates + django-meta) نوشته شده، نه پیشنهاد عمومی.

---

## وضعیت الان (خلاصه ممیزی)

| مورد | وضعیت | توضیح کوتاه |
|------|--------|-------------|
| `robots.txt` | ✅ هست | Disallow برای admin/cart/order/…؛ Sitemap لینک دارد |
| Sitemap XML | ✅ هست ولی ناقص/مشکل‌دار | محصول، بلاگ، استاتیک هست؛ **دسته محصول با `?category_id=`** داخل sitemap است |
| Title داینامیک | ⚠️ نیمه‌کاره | `{% block title %}` در صفحات عمومی هست؛ بعضی با mixin هم‌تراز نیستند |
| Meta description / OG / Twitter | ⚠️ از django-meta | `{% include "meta/meta.html" %}` در base؛ محصول/خانه/بعضی صفحات mixin دارند |
| Canonical | ❌ نیست | هیچ `rel=canonical` در پروژه نیست — حیاتی برای `?site=` و فیلترها |
| `noindex` (meta robots) | ❌ نیست | فقط Disallow در robots.txt (Crawl ≠ Index) |
| `{% block extra_head %}` | ❌ نیست | در `base-desktop` / `base-mobile` وجود ندارد |
| Product JSON-LD کامل | ❌ نیست | `schemaorg_type=Product` فقط props قدیمی؛ Offer/price/availability نیست |
| Breadcrumb Schema | ❌ نیست | UI محدود؛ در PDP تقریباً نیست |
| URL دسته محصول | ❌ لندینگ واقعی نیست | فقط `/shop/product/grid/?category_id=` |
| اسلاگ بلاگ | ❌ | `/blog/<int:post_id>/` |
| صفحه‌بندی قابل کراول | ❌ | دکمه JS (`changePage`) به‌جای `<a href>` |
| H1 خانه | ❌ | در `index.html` `<h1>` نیست |
| Image SEO | ⚠️ | PDP نسبتاً خوب؛ thumbهای خالی `alt=""`؛ درباره = alt اشتباه برند |

**قالب پایه (مهم):**  
`core/templates/base-desktop.html` و `base-mobile.html` — نه یک `base.html` واحد.

**Meta stack موجود:**  
`django-meta` + `SiteMetadataMixin` / `ObjectMetadataMixin` در `core/views_meta.py`  
→ Foundation را روی همین بساز؛ چرخ را از نو اختراع نکن.

---

## نقشهٔ کل SEO آروین (یادآوری ترتیب)

```text
1. Technical SEO Foundation   ← الان اینجاییم
2. URL Architecture
3. Keyword Map
4. Pillar Page
5. Topic Clusters
6. Commercial Landing Pages
7. Internal Linking
8. Backlinks / Authority
9. Search Console Optimization
```

---

# مرحله ۱ — Technical SEO Foundation (تسک‌ها)

اولویت: **P0 حیاتی → P1 ایندکس‌پذیری → P2 غنی‌سازی → P3 سرعت/ابزار**

---

## P0 — حیاتی (بدون این‌ها Foundation کامل نیست)

### SEO-F1 — Canonical خودارجاع برای همهٔ صفحات عمومی
**وضعیت:** ❌ وجود ندارد  
**کجا:** `base-desktop.html` / `base-mobile.html` + ساخت URL در backend (`views_meta` یا context processor)

**باید بشود:**
- `<link rel="canonical" href="https://arvinofficial.ir/...">` بدون queryهای نویزی
- Queryهایی مثل `?site=mobile|desktop`، `sort`، `order_by`، پارامترهای فیلتر غیرضروری در canonical نیایند
- برای PDP: URL تمیز محصول (`get_absolute_url`)
- برای لیست دسته (تا قبل از SEO-F8): موقتاً همان URL فعلی grid، ولی canonical ثابت تعریف شود

**چرا:** Google برای duplicate/`?site=` و فیلترها به canonical نیاز دارد؛ robots.txt جایگزین canonical نیست.

- [ ] SEO-F1

---

### SEO-F2 — Meta description یکدست و پر برای صفحات عمومی
**وضعیت:** ⚠️ mixin روی خانه/فروشگاه/محصول/بلاگ/قانونی؛ پوشش و کیفیت یکدست نیست  
**کجا:** viewهای `SiteMetadataMixin` + تمپلیت‌هایی که `meta` در context ندارند

**باید بشود:**
- هر صفحهٔ قابل ایندکس `meta.description` داشته باشد (۱۵۰–۱۶۰ کاراکتر هدف)
- Title تمپلیت (`{% block title %}`) با `meta.title` / OG هم‌خوان باشد یا یکی منبع حقیقت شود
- پیش‌فرض محصول: `brief_description` (الان در مدل هست) — خالی‌ها را در ادمین پر کن

**نکته:** `META_USE_TITLE_TAG = False` → title از block می‌آید؛ description از django-meta. این دو را آگاهانه هماهنگ نگه دار.

- [ ] SEO-F2

---

### SEO-F3 — کنترل Indexing با meta robots (`noindex` جایی که لازم است)
**وضعیت:** ❌ فقط `Disallow` در `robots.txt`  
**کجا:** base + صفحات cart / checkout / dashboard / accounts / searchهای بی‌ارزش / شاید wishlist

**باید بشود:**
```html
<meta name="robots" content="index,follow">   <!-- پیش‌فرض صفحات عمومی -->
<meta name="robots" content="noindex,follow"> <!-- صفحات خصوصی/تراکنشی -->
```

**چرا:** `robots.txt` جلوی crawl را می‌گیرد، ولی اگر URL از جای دیگر لینک شود یا قبلاً ایندکس شده باشد، `noindex` ابزار درست Indexing است.

- [ ] SEO-F3

---

### SEO-F4 — بلاک `extra_head` در هر دو base
**وضعیت:** ❌ نیست  
**کجا:** `base-desktop.html`, `base-mobile.html` بعد از include متا

**باید بشود:**
```django
{% block extra_head %}{% endblock %}
```
برای JSON-LD صفحه، robots خاص، یا متاهای استثنا بدون دست زدن به base در هر PR.

- [ ] SEO-F4

---

### SEO-F5 — بازبینی Sitemap (تغییر نده تا ممیزی نشود؛ بعد اصلاح هدفمند)
**وضعیت:** ✅ فایل هست — کیفیت مشکوک  
**کجا:** `core/core/sitemaps.py` + `urls.py`

**الان شامل است:** محصولات publish، پست‌های فعال، صفحات استاتیک، دسته‌های محصول با `?category_id=`، دسته بلاگ با `cat_name`.

**چک‌لیست ممیزی (اول بخوان، بعد عوض کن):**
- [ ] فقط URLهایی که می‌خواهی در Search باشند
- [ ] URLهای canonical (نه فیلتر/سورت)
- [ ] بدون 404 / پیش‌نویس / حذف‌شده
- [ ] **حذف یا جایگزینی** `ProductCategorySitemap` که `?category_id=` می‌دهد (تا وقتی لندینگ اسلاگ‌دار ساخته نشده، یا بعد از SEO-F8)
- [ ] `lastmod` درست است؟ (برای محصول/پست بله)
- [ ] بعد از اصلاح: در GSC دوباره Submit

**تسک اجرایی بعد از ممیزی:** SEO-F5b — اصلاح لیست items/location

- [ ] SEO-F5 ممیزی
- [ ] SEO-F5b اصلاح

---

## P1 — URL Architecture و ایندکس‌پذیری (پایهٔ Pillar بعدی)

> این بخش هم Foundation و هم شروع مرحله ۲ است. بدون URL تمیز، Pillar و Internal Link ضعیف می‌ماند.

### SEO-F6 — اسلاگ برای پست بلاگ
**وضعیت:** ❌ `/blog/<id>/`  
**کجا:** `blog/urls.py`, `blog/models.Post`, تمپلیت‌ها، `BlogPostSitemap`

**باید:** `/blog/<slug>/` + redirect ۳۰۱ از URL قدیمی id (اگر ایندکس شده).

- [ ] SEO-F6

---

### SEO-F7 — صفحه‌بندی قابل کراول
**وضعیت:** ❌ دکمه + JS در `product-grid-cards.html`  
**باید:** `<a href="?page=N&...">` (پارامترهای فیلتر لازم حفظ شوند) + در صورت نیاز `rel=prev/next` یا حداقل لینک واقعی در HTML.

- [ ] SEO-F7

---

### SEO-F8 — لندینگ واقعی دسته محصول با اسلاگ
**وضعیت:** ❌ فقط query؛ مدل `slug` دارد ولی URL لندینگ نیست  
**کجا:** `shop/urls.py`, `ProductCategorySitemap`, لینک‌های دسته در PDP (الان بعضی `#`)

**باید (پیشنهاد):**
```text
/shop/category/<slug>/
```
- H1 = نام دسته  
- Title/Description مخصوص دسته  
- Canonical همان اسلاگ  
- Sitemap → همین URL  
- ۳۰۱ از `?category_id=` قدیمی (اختیاری ولی توصیه‌شده)

**این مهم‌ترین آجر معماری Pillar → Category → Product است.**

- [ ] SEO-F8

---

### SEO-F9 — کوتاه‌کردن URL محصول (اختیاری ولی تمیز)
**وضعیت:** `/shop/product/<slug>/detail/`  
**پیشنهاد:** `/shop/product/<slug>/` + ۳۰۱ از مسیر قدیمی

- [ ] SEO-F9 (بعد از F6/F8 اگر ظرفیت بود)

---

## P2 — Schema و On-page (غنی‌سازی SERP)

### SEO-F10 — JSON-LD محصول (Product + Offer)
**وضعیت:** ❌ schema واقعی قیمت/موجودی نیست  
**کجا:** PDP + ساخت از `ProductModel` (قیمت `get_price()`، stock → InStock/OutOfStock، برند آروین، تصویر)

**نباید** دستی داخل هر محصول paste شود — از مدل/تمپلیت یک‌بار تولید شود (مثلاً در `extra_head` یا متد `as_json_ld`).

- [ ] SEO-F10

---

### SEO-F11 — JSON-LD مقاله (BlogPosting / Article)
**وضعیت:** ❌  
**کجا:** `blog-detail.html` + مدل Post

- [ ] SEO-F11

---

### SEO-F12 — Breadcrumb UI + BreadcrumbList Schema
**وضعیت:** UI فقط در بعضی صفحات؛ Schema نیست؛ PDP ضعیف  
**مسیر هدف:** خانه › دسته › محصول / خانه › بلاگ › پست

- [ ] SEO-F12

---

### SEO-F13 — FAQPage Schema
**وضعیت:** صفحه FAQ هست؛ Schema نیست  
**کجا:** `website/faq` + مدل سوالات

- [ ] SEO-F13

---

### SEO-F14 — H1 استاندارد
| صفحه | وضعیت |
|------|--------|
| PDP | ✅ `{{ object.title }}` |
| About / بعضی داخلی | ✅ |
| خانه | ❌ ندارد |
| Grid وقتی دسته فعال است | ⚠️ عنوان ثابت «فروشگاه»/«محصولات» |

**باید:** یک H1 معنادار در خانه؛ در grid وقتی دسته انتخاب شده H1 = نام دسته.

- [ ] SEO-F14

---

### SEO-F15 — Image SEO
- [ ] `alt` خالی تامب‌های PDP → نام محصول
- [ ] alt اشتباه «Noorbanoo Life» در `about.html` → متن آروین
- [ ] `width`/`height` جایی که هنوز نیست (جلوگیری CLS)
- [ ] تصویر LCP محصول: `loading="eager"` (الان نسبتاً رعایت شده) — گالری ثانویه lazy بماند

---

### SEO-F16 — فیلدهای SEO در ادمین (اختیاری override)
`meta_title`, `meta_description`, `og_image` برای محصول / پست / صفحات ثابت  
پیش‌فرض: title محصول + brief_description (بدون اجبار پر کردن دستی همه چیز)

- [ ] SEO-F16

---

## P3 — سرعت، کش، Search Console (مکمل Foundation)

### SEO-F17 — بازنگری `NoCacheHtmlMiddleware`
**وضعیت:** همه HTML با `no-store`  
**اثر:** به CWV و کش CDN/مرورگر ضربه می‌زند  
**باید:** فقط جایی که layout با `?site=` عوض می‌شود سختگیر باش؛ صفحات عمومی قابل ایندکس را کش‌پذیرتر کن (یا حداقل `private, max-age` کوتاه).

- [ ] SEO-F17

---

### SEO-F18 — HTTPS / HSTS / کوکی امن
اگر روی nginx/سرور نیست → در لایه سرور یا Django prod settings.

- [ ] SEO-F18

---

### SEO-F19 — Google Search Console + Bing
- تأیید مالکیت دامنه  
- Submit کردن `sitemap.xml`  
- مانیتور Coverage / Soft 404 / Duplicate  

- [ ] SEO-F19

---

### SEO-F20 — Analytics + Core Web Vitals
اندازه‌گیری LCP/CLS/INP روی موبایل (چون دو تمپلیت device دارید، هر دو را چک کن).

- [ ] SEO-F20

---

## خارج از Foundation (عمداً بعداً)

این‌ها را **الان** شروع نکن؛ بعد از P0–P1:

- Keyword Map  
- Pillar Page («صندلی کامیون» و …)  
- Topic Clusters / مقالات خوشه‌ای  
- Commercial Landing Pages  
- استراتژی Internal Linking گسترده  
- Backlink / Authority  
- بهینه‌سازی مداوم GSC (مرحله ۹)

---

# ترتیب اجرای پیشنهادی (همین اسپرینت Foundation)

```text
هفته ۱
  SEO-F4  extra_head
  SEO-F1  canonical
  SEO-F3  noindex صفحات خصوصی
  SEO-F2  تکمیل meta description
  SEO-F5  ممیزی sitemap → SEO-F5b اصلاح (حذف ?category_id از sitemap اگر لازم)

هفته ۲
  SEO-F7  pagination با <a>
  SEO-F14 H1 خانه + دسته
  SEO-F15 image altها
  SEO-F10 Product JSON-LD
  SEO-F12 Breadcrumb + schema

هفته ۳ (شروع URL Architecture)
  SEO-F8  لندینگ دسته با اسلاگ + آپدیت sitemap + لینک‌های داخلی
  SEO-F6  اسلاگ بلاگ + ۳۰۱
  SEO-F11 Article JSON-LD
  SEO-F13 FAQ schema

بعداً
  SEO-F9, F16, F17, F18, F19, F20
  سپس مرحله ۳ به بعد (Keyword → Pillar → …)
```

---

# فایل‌هایی که برای هر تسک Foundation لمس می‌شوند

| فایل | نقش |
|------|-----|
| `core/templates/base-desktop.html` | head، canonical، robots، extra_head |
| `core/templates/base-mobile.html` | همان |
| `core/core/views_meta.py` | canonical URL تمیز، meta مشترک |
| `core/core/sitemaps.py` | ممیزی/اصلاح |
| `core/core/urls.py` | مسیر sitemap/robots (فعلاً OK) |
| `core/templates/robots.txt` | فعلاً نگه دار؛ در صورت نیاز Disallow ریزتر |
| `core/shop/models.py` / `views.py` | meta محصول، JSON-LD، دسته |
| `core/templates/shop/product-detail.html` | H1/breadcrumb/schema/alt |
| `core/templates/shop/product-grid.html` + partials | pagination، H1 دسته |
| `core/blog/models.py` / `urls.py` | اسلاگ |
| `core/website/views.py` + `index.html` | meta خانه، H1 |
| `core/core/middleware.py` | کش HTML (F17) |
| `core/core/settings.py` | تنظیمات django-meta / دامنه |

---

# تعریف «Foundation تمام شد»

وقتی همهٔ این‌ها سبز شدند، می‌توانی بگویی Technical SEO Foundation آماده است:

- [ ] Canonical روی صفحات عمومی  
- [ ] Description یکتا روی صفحات ایندکس‌شونده  
- [ ] noindex روی صفحات تراکنشی/پنل  
- [ ] Sitemap فقط URLهای canonical باارزش  
- [ ] Product JSON-LD معتبر (تست Rich Results)  
- [ ] Pagination و حداقل یک سطح URL دستهٔ تمیز (یا برنامهٔ قطعی F8 در جریان)  
- [ ] GSC سایت را می‌بیند و sitemap بدون خطای بحرانی است  

**بعد از این → مرحله ۲/۳ (URL نهایی + Keyword Map) و بعد Pillar.**

---

*آخرین هم‌ترازسازی با کد: ۱۴۰۴/۰۶/۰۲ — جایگزین نسخهٔ قدیمی‌تر همین فایل که بعضی آیتم‌های انجام‌شده (robots/sitemap پایه) را هنوز «نبود» فرض می‌کرد.*
