# SEO Technical Foundation — تسک‌لیست اولویت‌دار آروین

**مرحله فعلی:** ۱ — Technical SEO Foundation (**کد ✅ · دیپلوی production ✅ · GSC sitemap ✅**)  
**شاخه کار:** `seo/foundation-p0` → merge به `dev` → `production` → سرور  
**قبل از:** Pillar / Keyword Map / Topic Clusters / Backlinks

> داشتن `sitemap` و `robots.txt` ≠ Technical SEO تمام‌شده.  
> این فایل بر اساس وضعیت **واقعی کد و production** پروژه (Django Templates + django-meta) نوشته شده.

---

## دیپلوی production — انجام‌شده (۱۴۰۵/۰۶/۰۷)

| مورد | وضعیت | یادداشت |
|------|--------|---------|
| Merge → production → سرور | ✅ | Foundation روی `arvinofficial.ir` زنده است |
| `migrate` (اسلاگ بلاگ) | ✅ | URLهای `/blog/<slug>/` کار می‌کنند |
| `SITE_DOMAIN=arvinofficial.ir` در `.env` | ✅ | canonical و JSON-LD دیگر `localhost:8000` نیست |
| `robots.txt` روی nginx | ✅ | duplicate `location` حذف شد؛ پروکسی به Django → **200** |
| Fix 500 بلاگ (`get_full_name`) | ✅ | `User.get_full_name()` → Profile |
| GSC: Submit sitemap | ✅ | `https://arvinofficial.ir/sitemap.xml` — منتظر Success در GSC |

**هنوز در production چک/انجام نشده:** Rich Results Test · PageSpeed · HSTS · legacy `.html` redirects · title لیست بلاگ (`بلاگ - …`).

**مرجع بهبود Performance / A11y / ops:** [`docs/SITE-IMPROVEMENT-TODO.md`](SITE-IMPROVEMENT-TODO.md)

---

| مورد | وضعیت | توضیح کوتاه |
|------|--------|-------------|
| `robots.txt` | ✅ production | Django + nginx پروکسی؛ Sitemap لینک دارد؛ [تست زنده](https://arvinofficial.ir/robots.txt) |
| Sitemap XML | ✅ به‌روز | محصول، دسته با اسلاگ، بلاگ، استاتیک؛ بدون `?category_id=` |
| Title داینامیک | ✅ | `<title>` از `meta.title` (mixin/view/مدل) — یک منبع با OG |
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

# کارهایی که **تو** باید انجام بدهی (به ترتیب)

> Foundation روی production دیپلوی شده. موارد زیر **باقی‌ماندهٔ عملیاتی** هستند.

## فاز ۱ — دیپلوی و صحت‌سنجی

- [x] **۱. Merge و دیپلوی**  
  `seo/foundation-p0` → `dev` → `production` → سرور — **انجام شد.**

- [x] **۲. Migration روی سرور**  
  `blog/0004_post_slug` — اسلاگ بلاگ روی production فعال است.

- [x] **۲b. env production**  
  `SITE_DOMAIN=arvinofficial.ir` — canonical/JSON-LD درست شد.

- [x] **۲c. nginx `robots.txt`**  
  فقط **یک** `location = /robots.txt` (پروکسی به Django)؛ duplicate location حذف شد.

- [ ] **۳. تست دستی چند URL مهم** (مرورگر + incognito) — **بخشی انجام شد؛ بقیه را خودت تأیید کن**  
  | URL | انتظار | تست production |
  |-----|--------|----------------|
  | `/robots.txt` | 200 + Sitemap | ✅ |
  | `/sitemap.xml` | 200 + index | ✅ |
  | `/blog/<slug>/` | 200 (نه 500) | ✅ |
  | `/shop/product/<slug>/` | PDP | ✅ (نمونه تست شد) |
  | `/shop/product/<slug>/` | PDP باز شود (نه `/detail/`) | [ ] |
  | `/shop/product/<slug>/detail/` | ۳۰۱ به URL کوتاه | [ ] |
  | `/shop/category/<slug>/` | لندینگ دسته | [ ] |
  | `/shop/product/grid/?category_id=1` | ۳۰۱ به `/shop/category/...` | [ ] |
  | `/blog/<id>/` | ۳۰۱ به اسلاگ | [ ] |
  | `/faq/` | صفحه FAQ | ✅ |
  | View Source → canonical | `https://arvinofficial.ir/...` | ✅ |
  | View Source → `<title>` لیست بلاگ | `بلاگ - فروشگاه آروین` | [ ] (الان فقط نام سایت) |

- [ ] **۴. Rich Results Test** (بعد از دیپلوی)  
  [search.google.com/test/rich-results](https://search.google.com/test/rich-results)  
  - یک **محصول** → Product + Offer  
  - یک **پست بلاگ** → BlogPosting  
  - **FAQ** → FAQPage  

## فاز ۲ — Google Search Console

- [x] **۵. تأیید مالکیت** دامنه `arvinofficial.ir` (برای Submit sitemap لازم بود — انجام شد).

- [x] **۶. Submit sitemap**  
  ```
  https://arvinofficial.ir/sitemap.xml
  ```  
  **فقط همین یک URL** — sub-sitemapها (`sitemap-products.xml`, …) خودکار از index خوانده می‌شوند.  
  `robots.txt` را جدا Submit **نکن** (گوگل خودش می‌خواند).  
  → چند روز صبر کن تا وضعیت «Success» / تعداد URL به‌روز شود.

- [ ] **۷. Pages → Why pages aren’t indexed** — هر ردیف را باز کن و URLها را ببین:

  | وضعیت GSC | معمولاً یعنی | کار تو |
  |-----------|--------------|--------|
  | **Not found (404)** | URL قدیمی مرده (`cart.html`, `product-overview.html`, …) | اگر عمدی ۴۰۴ است → **Validate fix**؛ اگر هنوز لینک داخلی دارد → در کد ۳۰۱ بگیر (هنوز انجام نشده) |
  | **Page with redirect** | ۳۰۱ عمدی (دسته، بلاگ id، `/detail/`) | درست است؛ Validate زده باشی کافی است |
  | **Duplicate without canonical** | نسخه با query / URL قدیمی | بعد از دیپلوی canonical باید کم شود؛ ۱–۲ هفته صبر + دوباره چک |
  | **Blocked 4xx** | خطای دسترسی غیر ۴۰۴ | URL را دستی باز کن و علت را پیدا کن |
  | **Crawled – not indexed** | گوگل فعلاً ایندکس نکرده | برای cart/صفحات کم‌اهمیت OK؛ برای محصول/دسته مهم → محتوا و لینک داخلی |

- [ ] **۸. URL Inspection** برای ۲–۳ صفحه مهم (خانه، یک محصول، یک دسته) → **Request indexing** (اختیاری، شتاب اولیه).

- [ ] **۹. (اختیاری) Bing Webmaster Tools** — همان sitemap را Submit کن.

## فاز ۳ — کیفیت و سرور (هفتهٔ بعد یا موازی)

- [ ] **۱۰. PageSpeed Insights (F20)**  
  موبایل + دسکتاپ؛ هر دو layout (`?site=mobile` و بدون آن).  
  → تسک‌های جزئی: [`docs/SITE-IMPROVEMENT-TODO.md`](SITE-IMPROVEMENT-TODO.md) (baseline: Perf 76 desktop / 60 mobile)

- [ ] **۱۱. HTTPS / HSTS (F18)**  
  روی nginx/هاستینگ: `X-Forwarded-Proto` از `$thescheme` (نه `$scheme` خام)؛ redirect HTTP→HTTPS؛ HSTS اگر CDN اجازه می‌دهد.

- [ ] **۱۲. محتوا در ادمین**  
  - `brief_description` محصولات مهم (برای meta و JSON-LD)  
  - پست‌های بلاگ با `slug` و `published_date`  
  - FAQ منتشرشده در پنل

## فاز ۴ — هنوز در کد نیست (با توسعه‌دهنده / بعداً)

- [x] **۱۳. URLهای قدیمی `.html`** — 301 + حذف لینک دمو (`legacy_redirects.py`, `base-desktop.html`)

- [ ] **۱۴. F16** — فیلدهای override متا در ادمین (اختیاری).

- [ ] **۱۵. F17** — بازنگری کش HTML (`NoCacheHtmlMiddleware`) برای CWV.

## فاز ۵ — بعد از سبز شدن GSC (شروع مرحله ۲/۳ SEO)

- [ ] **۱۶. Keyword Map** — کلمات هدف هر دسته/محصول  
- [ ] **۱۷. Pillar Page** — مثلاً «صندلی راننده کامیون»  
- [ ] **۱۸. Topic Clusters / لینک‌سازی داخلی / بک‌لینک**

---

**خلاصه یک خطی:** ~~دیپلوی → migrate →~~ تست URL باقی → Rich Results → ~~GSC sitemap~~ → مانیتور Coverage → بعد Keyword/Pillar.

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

**انجام‌شده:** description + title از یک منبع (`meta.title` در base + `get_meta_title` در view/مدل).

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
- [x] بعد از دیپلوی: در GSC Submit — **انجام شد** (`sitemap.xml`); منتظر Success

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
- [x] تأیید مالکیت دامنه  
- [x] Submit کردن `sitemap.xml` (index — sub-sitemapها خودکار)  
- [ ] مانیتور Coverage تا «Success» و تعداد URL  
- [ ] درخواست حذف/به‌روزرسانی URLهای قدیمی بلاگ id و `?category_id=` در صورت نیاز  

- [ ] SEO-F19 (کامل — مانیتور مداوم)

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

# ترتیب اجرا — وضعیت کد (توسعه‌دهنده)

```text
✅ انجام‌شده در کد (F1–F15, F9, F10–F13)
  F1 canonical · F2 title+description · F3 noindex · F4 extra_head
  F5/F5b sitemap · F6 blog slug · F7 pagination · F8 category landing
  F9 product URL کوتاه · F10–F13 JSON-LD + breadcrumb · F14 H1 · F15 image alt

⏳ باقی در کد (اختیاری / بعداً)
  F16 ادمین meta override · F17 کش HTML · legacy .html redirects

👤 کارهای تو → بخش «کارهایی که تو باید انجام بدهی» بالا  
   ✅ دیپلوی · env · robots.txt · GSC sitemap Submit  
   ⏳ Rich Results · Coverage مانیتور · PageSpeed · legacy URL
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
- [x] GSC: sitemap Submit شد — **منتظر Success / Coverage** (F19)  
- [ ] Rich Results Test روی محصول/بلاگ/FAQ بدون خطای بحرانی (کار تو)

**بعد از GSC سبز → Keyword Map و Pillar (مرحله ۲/۳).**

---

*آخرین هم‌ترازسازی: ۱۴۰۵/۰۶/۰۷ — production دیپلوی + robots.txt/nginx + GSC sitemap Submit؛ Rich Results و Coverage مانیتور باقی.*
