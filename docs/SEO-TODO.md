# SEO Technical Foundation — تسک‌لیست اولویت‌دار آروین

**مرحله فعلی:** ۱ — Technical SEO Foundation (P0 و بخش زیادی از P1 تمام)  
**شاخه کار:** `seo/foundation-p0`  
**قبل از:** Pillar / Keyword Map / Topic Clusters / Backlinks

> داشتن `sitemap` و `robots.txt` ≠ Technical SEO تمام‌شده.  
> این فایل بر اساس وضعیت **واقعی کد** پروژه (Django Templates + django-meta) نوشته شده، نه پیشنهاد عمومی.

---

## وضعیت الان (خلاصه ممیزی)

| مورد | وضعیت | توضیح کوتاه |
|------|--------|-------------|
| `robots.txt` | ✅ هست | Disallow برای admin/cart/order/…؛ Sitemap لینک دارد |
| Sitemap XML | ✅ به‌روز | محصول، دسته با اسلاگ، بلاگ، استاتیک؛ بدون `?category_id=` |
| Title داینامیک | ⚠️ نیمه‌کاره | `{% block title %}` در صفحات عمومی هست؛ بعضی با mixin هم‌تراز نیستند |
| Meta description / OG / Twitter | ✅ پایه | `normalize_meta_description` + mixin روی صفحات عمومی اصلی |
| Canonical | ✅ هست | `build_canonical_url` — path بدون query (`?site=` و فیلترها حذف) |
| `noindex` (meta robots) | ✅ هست | صفحات خصوصی/تراکنشی `noindex,follow`؛ عمومی `index,follow` |
| `{% block extra_head %}` | ✅ هست | در `base-desktop` / `base-mobile` (+ داشبوردها) |
| Product JSON-LD کامل | ✅ | Product + Offer از `as_json_ld` در PDP `extra_head` |
| Breadcrumb Schema | ✅ | UI + BreadcrumbList روی PDP، دسته، گرید، بلاگ |
| URL دسته محصول | ✅ لندینگ اسلاگ | `/shop/category/<slug>/` + ۳۰۱ از `?category_id=` |
| اسلاگ بلاگ | ✅ | `/blog/<slug>/` + ۳۰۱ از `/blog/<id>/` |
| صفحه‌بندی قابل کراول | ✅ | `<a href>` + تگ `pagination_url` |
| H1 خانه | ✅ | `visually-hidden` در `index.html` — برند + موضوع |
| H1 دسته | ✅ | نام دسته در لندینگ `/shop/category/<slug>/` |
| Image SEO | ✅ پایه | تامب PDP با نام محصول؛ about بدون برند اشتباه |

**قالب پایه (مهم):**  
`core/templates/base-desktop.html` و `base-mobile.html` — نه یک `base.html` واحد.

**Meta stack موجود:**  
`django-meta` + `SiteMetadataMixin` / `ObjectMetadataMixin` در `core/views_meta.py`  
+ helpers در `core/core/seo.py` (canonical، robots، normalize description)  
→ Foundation را روی همین بساز؛ چرخ را از نو اختراع نکن.

---

## نقشهٔ کل SEO آروین (یادآوری ترتیب)

```text
1. Technical SEO Foundation   ← الان اینجاییم (P0 ✅؛ P1 عمدتاً ✅؛ باقی P2/P3)
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
**وضعیت:** ✅ `build_canonical_url` + context processor / base templates  
**کجا:** `core/core/seo.py`, context processors، `base-desktop.html` / `base-mobile.html`

**انجام‌شده:**
- `<link rel="canonical">` بدون queryهای نویزی (`?site=`, فیلتر، سورت)
- PDP از path تمیز محصول
- لندینگ دسته مسیر اسلاگ بدون query

- [x] SEO-F1

---

### SEO-F2 — Meta description یکدست و پر برای صفحات عمومی
**وضعیت:** ✅ نرمال‌سازی + پوشش صفحات عمومی اصلی  
**کجا:** `normalize_meta_description`، viewهای `SiteMetadataMixin` / ObjectMeta

**انجام‌شده:**
- description صفحات ایندکس‌شونده نرمال و پر می‌شود
- پیش‌فرض محصول از `brief_description` / description مدل

**باقی (اختیاری کیفیت):** هم‌ترازی کامل `{% block title %}` با `meta.title` / OG در همهٔ صفحات.

- [x] SEO-F2

---

### SEO-F3 — کنترل Indexing با meta robots (`noindex` جایی که لازم است)
**وضعیت:** ✅ `should_noindex` / `robots_meta_content` روی baseهای عمومی و داشبورد  
**کجا:** `core/core/seo.py` + base templates

**انجام‌شده:**
```html
<meta name="robots" content="index,follow">   <!-- پیش‌فرض صفحات عمومی -->
<meta name="robots" content="noindex,follow"> <!-- صفحات خصوصی/تراکنشی -->
```

- [x] SEO-F3

---

### SEO-F4 — بلاک `extra_head` در هر دو base
**وضعیت:** ✅ هست  
**کجا:** `base-desktop.html`, `base-mobile.html` (+ داشبوردها) بعد از include متا

```django
{% block extra_head %}{% endblock %}
```
برای JSON-LD صفحه، robots خاص، یا متاهای استثنا بدون دست زدن به base در هر PR.

- [x] SEO-F4

---

### SEO-F5 — بازبینی Sitemap (تغییر نده تا ممیزی نشود؛ بعد اصلاح هدفمند)
**وضعیت:** ✅ ممیزی + اصلاح (F5b) انجام شد؛ بعد از F8 دوباره دسته با اسلاگ برگشت  
**کجا:** `core/core/sitemaps.py` + `urls.py`

**الان شامل است:** محصولات publish، پست‌های فعال، صفحات استاتیک، **دسته‌های محصول با `/shop/category/<slug>/`**, دسته بلاگ با `cat_name`.

**چک‌لیست:**
- [x] فقط URLهایی که می‌خواهی در Search باشند (هدف فعلی)
- [x] URLهای canonical (نه فیلتر/سورت)
- [x] بدون 404 / پیش‌نویس / حذف‌شده (محصول/پست فیلترشده)
- [x] `ProductCategorySitemap` → اسلاگ لندینگ (نه `?category_id=`)
- [x] `lastmod` برای محصول/پست
- [ ] بعد از دیپلوی: در GSC دوباره Submit / پاک‌کردن URLهای قدیمی دسته

**تسک اجرایی:** SEO-F5b — ✅ انجام شد (حذف query دسته، سپس ثبت مجدد با اسلاگ در F8)

- [x] SEO-F5 ممیزی
- [x] SEO-F5b اصلاح

---

## P1 — URL Architecture و ایندکس‌پذیری (پایهٔ Pillar بعدی)

> این بخش هم Foundation و هم شروع مرحله ۲ است. بدون URL تمیز، Pillar و Internal Link ضعیف می‌ماند.

### SEO-F6 — اسلاگ برای پست بلاگ
**وضعیت:** ✅ `/blog/<slug>/` + ۳۰۱ از `/blog/<id>/`  
**کجا:** `blog/urls.py`, `blog/models.Post`, تمپلیت‌ها، `BlogPostSitemap`, migration `0004_post_slug`

- [x] SEO-F6

---

### SEO-F7 — صفحه‌بندی قابل کراول
**وضعیت:** ✅ `<a href>` + تگ `pagination_url` (حفظ فیلترها) در `product-grid-cards.html`  
**کجا:** `shop/templatetags/shop_tags.py`, partial گرید

- [x] SEO-F7

---

### SEO-F8 — لندینگ واقعی دسته محصول با اسلاگ
**وضعیت:** ✅ `/shop/category/<slug>/` + ۳۰۱ از `?category_id=` + sitemap اسلاگ‌دار + لینک‌های داخلی  
**کجا:** `shop/urls.py`, `ShopProductCategoryView`, `ProductCategoryModel.get_absolute_url`, منو/PDP/فیلتر، `ProductCategorySitemap`

```text
/shop/category/<slug>/
```
- H1 = نام دسته  
- Title/Description مخصوص دسته  
- Canonical همان اسلاگ  
- Sitemap → همین URL  
- ۳۰۱ از `?category_id=` قدیمی  

**این مهم‌ترین آجر معماری Pillar → Category → Product است.**

- [x] SEO-F8

---

### SEO-F9 — کوتاه‌کردن URL محصول (اختیاری ولی تمیز)
**وضعیت:** ✅ `/shop/product/<slug>/` + ۳۰۱ از `/detail/`  
**کجا:** `shop/urls.py`, `product_detail_legacy_redirect` — لینک‌های داخلی از `get_absolute_url` / `{% url 'shop:product-detail' %}` خودکار به URL جدید می‌روند.

- [x] SEO-F9

---

## P2 — Schema و On-page (غنی‌سازی SERP) ← اولویت بعدی کد

### SEO-F10 — JSON-LD محصول (Product + Offer)
**وضعیت:** ✅ `ProductModel.as_json_ld` → `<script type="application/ld+json">` در PDP  
**کجا:** `shop/models.py`, `product-detail.html` (`extra_head`)

شامل: name، description، image، brand آروین، Offer (قیمت `get_price()`، IRR، InStock/OutOfStock)، و در صورت وجود نظر `aggregateRating`.

- [x] SEO-F10

---

### SEO-F11 — JSON-LD مقاله (BlogPosting / Article)
**وضعیت:** ✅ `Post.as_json_ld` → `<script type="application/ld+json">` در `blog-detail.html`  
**کجا:** `blog/models.py`, `blog-detail.html` (`extra_head`)

شامل: headline، description، image، تاریخ انتشار/ویرایش، نویسنده، publisher آروین.

- [x] SEO-F11

---

### SEO-F12 — Breadcrumb UI + BreadcrumbList Schema
**وضعیت:** ✅ مسیر قابل‌مشاهده + JSON-LD  
**مسیر:** خانه › فروشگاه › [دسته…] › محصول / خانه › بلاگ › [دسته] › پست  

**کجا:** `core/seo.py` (helpers)، `includes/breadcrumb.html`، PDP / گرید / دسته / بلاگ

- [x] SEO-F12

---

### SEO-F13 — FAQPage Schema
**وضعیت:** ✅ `faq_page_json_ld` از سوالات منتشرشده → `faq.html` (`extra_head`)  
**کجا:** `core/seo.py`, `website/views.py`, `website/faq.html`

- [x] SEO-F13

---

### SEO-F14 — H1 استاندارد
| صفحه | وضعیت |
|------|--------|
| PDP | ✅ `{{ object.title }}` |
| About / بعضی داخلی | ✅ |
| خانه | ✅ `فروشگاه آروین \| صندلی راننده…` (visually-hidden، بنر به‌هم نمی‌خورد) |
| لندینگ دسته | ✅ H1 = نام دسته |

- [x] SEO-F14

---

### SEO-F15 — Image SEO
**وضعیت:** ✅ موارد اصلی انجام شد  
- [x] `alt` خالی تامب‌های PDP → نام محصول  
- [x] alt اشتباه «Noorbanoo Life» در `about.html` → متن آروین  
- [x] `width`/`height` روی تصاویر about (۹۰۰×۹۰۰)  
- [x] تصویر LCP محصول: `loading="eager"` (از قبل رعایت شده) — گالری ثانویه lazy  

**باقی اختیاری:** alt کارت‌های بلاگ خانه / گالری پست در صورت نیاز.

- [x] SEO-F15

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
- Submit کردن `sitemap.xml` (به‌خصوص بعد از F5b/F6/F8)  
- مانیتور Coverage / Soft 404 / Duplicate  
- درخواست حذف/به‌روزرسانی URLهای قدیمی بلاگ id و `?category_id=` در صورت نیاز  

- [ ] SEO-F19

---

### SEO-F20 — Analytics + Core Web Vitals
اندازه‌گیری LCP/CLS/INP روی موبایل (چون دو تمپلیت device دارید، هر دو را چک کن).

- [ ] SEO-F20

---

## خارج از Foundation (عمداً بعداً)

این‌ها را **الان** شروع نکن؛ بعد از بستن P2 پایه و GSC:

- Keyword Map  
- Pillar Page («صندلی کامیون» و …)  
- Topic Clusters / مقالات خوشه‌ای  
- Commercial Landing Pages  
- استراتژی Internal Linking گسترده  
- Backlink / Authority  
- بهینه‌سازی مداوم GSC (مرحله ۹)

---

# ترتیب اجرا (وضعیت اسپرینت)

```text
✅ انجام‌شده (P0 + بخش P1)
  SEO-F4  extra_head
  SEO-F1  canonical
  SEO-F3  noindex صفحات خصوصی
  SEO-F2  تکمیل meta description
  SEO-F5 / F5b  ممیزی + اصلاح sitemap
  SEO-F6  اسلاگ بلاگ + ۳۰۱
  SEO-F7  pagination با <a>
  SEO-F8  لندینگ دسته با اسلاگ + sitemap + لینک‌های داخلی

⏭️ بعدی پیشنهادی
  SEO-F19 (GSC: submit sitemap + Coverage)
  SEO-F16–F18, F20 (ادمین SEO، کش، سرعت)

  سپس مرحله ۳ به بعد (Keyword → Pillar → …)
```

---

# فایل‌هایی که برای هر تسک Foundation لمس می‌شوند

| فایل | نقش |
|------|-----|
| `core/templates/base-desktop.html` | head، canonical، robots، extra_head |
| `core/templates/base-mobile.html` | همان |
| `core/core/seo.py` | canonical، robots meta، normalize description |
| `core/core/views_meta.py` | meta مشترک mixin |
| `core/core/sitemaps.py` | محصول / دسته اسلاگ / بلاگ / استاتیک |
| `core/core/urls.py` | مسیر sitemap/robots + ثبت `product-categories` |
| `core/templates/robots.txt` | فعلاً نگه دار؛ در صورت نیاز Disallow ریزتر |
| `core/shop/models.py` / `views.py` | دسته لندینگ، meta محصول، JSON-LD بعدی |
| `core/shop/templatetags/shop_tags.py` | `pagination_url` |
| `core/templates/shop/product-detail.html` | H1/breadcrumb/schema/alt |
| `core/templates/shop/product-grid.html` + partials | pagination، H1 دسته، فیلتر |
| `core/blog/models.py` / `urls.py` | اسلاگ + ۳۰۱ |
| `core/website/views.py` + `index.html` | meta خانه، H1 (F14 باقی) |
| `core/core/middleware.py` | کش HTML (F17) |
| `core/core/settings.py` | تنظیمات django-meta / دامنه |

---

# تعریف «Foundation تمام شد»

وقتی همهٔ این‌ها سبز شدند، می‌توانی بگویی Technical SEO Foundation آماده است:

- [x] Canonical روی صفحات عمومی  
- [x] Description یکتا روی صفحات ایندکس‌شونده (پایه)  
- [x] noindex روی صفحات تراکنشی/پنل  
- [x] Sitemap فقط URLهای canonical باارزش (محصول + دسته اسلاگ + بلاگ + استاتیک)  
- [x] Product JSON-LD معتبر (تست Rich Results) — **F10** (بعد از دیپلوی در Rich Results Test تأیید کن)  
- [x] Pagination و URL دستهٔ تمیز (`/shop/category/<slug>/`)  
- [ ] GSC سایت را می‌بیند و sitemap بدون خطای بحرانی است — **F19**

**بعد از این → تکمیل P2 (schema/H1 خانه/image) سپس Keyword Map و Pillar.**

---

*آخرین هم‌ترازسازی با کد: ۱۴۰۵/۰۶/۰۵ — P0 کامل؛ P1 تا F8؛ بعدی پیشنهادی F14 (خانه) / F15 / F10.*
