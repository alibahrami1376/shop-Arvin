# Site Improvement — تسک‌لیست مشکلات شناسایی‌شده

**منبع:** Lighthouse (۲۸ اوت ۲۰۲۶)، production `arvinofficial.ir`، ممیزی SEO  
**گزارش‌های خام:** `arvinofficial.ir-20260828T202028.html` (desktop) · `arvinofficial.ir-20260828T202503.html` (mobile)  
**مرجع SEO Foundation:** [`docs/SEO-TODO.md`](SEO-TODO.md)

---

## baseline امتیاز Lighthouse (صفحهٔ خانه `/`)

| دسته | Desktop | Mobile |
|------|---------|--------|
| Performance | **76** | **60** |
| Accessibility | 95 | **87** |
| Best Practices | 92 | 96 |
| SEO | 100 | 100 |

| متریک | Desktop | Mobile |
|--------|---------|--------|
| LCP | 0.9 s ✅ | 2.3 s ✅ |
| CLS | 0.001 ✅ | 0.002 ✅ |
| TTFB | 640 ms ⚠️ | **5,830 ms** 🔴 |
| TBT | 450 ms ⚠️ | **2,900 ms** 🔴 |
| Speed Index | 1.9 s | **10.4 s** 🔴 |
| حجم کل | ~1.2 MB | **~3.0 MB** 🔴 |

> تست با Chrome extension انجام شده — برای baseline دقیق‌تر: **Incognito بدون extension** دوباره بگیر.

---

# P0 — فوری (بیشترین اثر روی Performance موبایل)

## PERF-P0-1 — تصویر سنگین `img2.png` (~1.9 MB روی موبایل)

**مشکل:** `static/img/900x900/img2.png` در موبایل ~۱.۹ MB دانلود می‌شود؛ بزرگ‌ترین فایل صفحه.  
**کجا:** `core/templates/website/index.html` (بنر «پیشنهاد ویژه»)

- [ ] تبدیل به WebP/AVIF با کیفیت مناسب (هدف: زیر ۱۵۰ KB برای موبایل)
- [ ] `srcset` / `<picture>` — نسخهٔ کوچک‌تر برای موبایل (مثلاً ۶۰۰px عرض)
- [ ] تأیید `loading="lazy"` برای غیر-LCP (الان lazy است — OK)
- [ ] بعد از fix: Lighthouse موبایل دوباره → حجم کل باید زیر ~1.5 MB بیاید

---

## PERF-P0-2 — TTFB بالا (موبایل ~5.8 s · دسکتاپ ~640 ms)

**مشکل:** HTML اصلی دیر می‌رسد؛ در LCP breakdown موبایل ~۵.۸ s فقط TTFB است.  
**علت محتمل:** `NoCacheHtmlMiddleware` + بدون کش صفحه + cold start gunicorn

**کجا:** `core/core/middleware.py` (`NoCacheHtmlMiddleware`), `settings.py`

- [ ] بازنگری F17: `no-store` فقط وقتی `?site=mobile|desktop` یا تعویض layout — نه همهٔ HTML
- [ ] صفحات عمومی indexable (خانه، گرید، PDP، بلاگ): `Cache-Control: private, max-age=60` یا کش per-view
- [ ] بررسی تعداد worker gunicorn و warmup بعد از deploy
- [ ] اندازه‌گیری TTFB واقعی: `curl -w '%{time_starttransfer}\n' -o /dev/null -s https://arvinofficial.ir/`

---

## PERF-P0-3 — Total Blocking Time (موبایل 2.9 s)

**مشکل:** JS زیاد روی main-thread — باندل `output.*.js` ~۲.۵ s اجرا

- [ ] آنالیز باندل compress: چه اسکریپت‌هایی در خانه لازم نیست؟
- [ ] `defer` برای همهٔ JS غیرضروری در `<head>`
- [ ] vendor.js / theme.js فقط در صفحاتی که نیاز دارند
- [ ] حذف یا lazy-load اسکریپت‌های سنگین موبایل (swiper، …) اگر در viewport اول لازم نیست

---

# P1 — سرور و nginx

## OPS-P1-1 — Cache-Control برای static و media

**مشکل:** Lighthouse ~1–3 MB صرفه‌جویی کش — CSS، JS، فونت، بنر، media

**روی nginx سرور** (`/etc/nginx/sites-enabled/default`):

- [ ] `/static/` → `expires 30d` + `Cache-Control: public, immutable`
- [ ] `/media/` → `expires 7d` + `Cache-Control: public`
- [ ] `nginx -t && nginx -s reload`
- [ ] تأیید: `curl -sI https://arvinofficial.ir/static/CACHE/css/output.*.css | grep -i cache`

---

## OPS-P1-2 — `X-Forwarded-Proto` درست پشت gateway

**مشکل:** اگر `$scheme` خام باشد، Django فکر می‌کند HTTP است

- [ ] در `proxy_set_header X-Forwarded-Proto` از `$thescheme` استفاده شود (map از `http_x_forwarded_proto`)
- [ ] تأیید: کوکی secure / redirectها درست

---

## OPS-P1-3 — HTTPS / HSTS (F18)

- [ ] redirect HTTP → HTTPS در gateway/nginx
- [ ] HSTS اگر CDN/هاست اجازه می‌دهد (`Strict-Transport-Security`)

---

# P2 — Performance (کد و asset)

## PERF-P2-1 — Render-blocking CSS/JS

**Desktop:** CSS فشرده ~۱۰۵ KB + `layout-sync.js` + `defer-images.js` در head

- [ ] `preload` برای CSS بحرانی یا critical CSS inline (اختیاری، پرهزینه)
- [ ] `layout-sync.js` و `defer-images.js` → `defer` یا انتهای `<body>`
- [ ] بررسی django-compressor: split CSS per-page اگر ممکن است

---

## PERF-P2-2 — فونت Vazir (~90 KB TTF)

- [ ] مهاجرت به **woff2** (فایل‌های `Vazir-*-FD.woff` موجود — اولویت woff2)
- [ ] `font-display: swap` در `@font-face`
- [ ] `preload` فقط وزن‌های استفاده‌شده در above-the-fold (مثلاً Regular + Bold)

---

## PERF-P2-3 — تصاویر بنر home (~۱۰۰–۱۲۰ KB هر کدام)

**کجا:** media بنرهای swiper در `index.html`

- [ ] سایز responsive (عرض ۴۱۲px برای موبایل کافی است نه ۱۲۰۰px)
- [ ] کیفیت WebP پایین‌تر برای بنرهای غیرفعال در اسلاید اول
- [ ] ImageKit spec جدا برای mobile banner اگر لازم است

---

## PERF-P2-4 — Unused CSS/JS

| مورد | Desktop | Mobile |
|------|---------|--------|
| Unused JS | ~392 KiB | ~385 KiB |
| Unused CSS | ~73 KiB | ~28 KiB |

- [ ] حذف CSS/JS استفاده‌نشده از bundle خانه
- [ ] بررسی bootstrap-icons — آیا همه آیکون‌ها لازم است یا subset؟

---

## PERF-P2-5 — favicon.ico (~76 KB)

- [ ] فشرده‌سازی favicon یا SVG favicon کوچک‌تر

---

## PERF-P2-6 — تصاویر بدون width/height

- [ ] audit `unsized-images` — اضافه کردن `width`/`height` روی imgهای بدون ابعاد (CLS پیشگیرانه)

---

# P3 — Accessibility (موبایل 87)

## A11Y-P3-1 — `aria-hidden` با focusable داخل

- [ ] پیدا کردن المنت (احتمالاً offcanvas/modal/swiper) و `aria-hidden` را فقط وقتی بسته است بگذار
- [ ] یا `tabindex="-1"` / حذف focus از فرزندان وقتی hidden

---

## A11Y-P3-2 — ترتیب heading (`heading-order`)

- [ ] خانه موبایل: پرش H1 → H3 (یا مشابه) — ترتیب منطقی H1 → H2 → H3

---

## A11Y-P3-3 — لینک بدون نام (`link-name`)

- [ ] لینک‌های icon-only: `aria-label` فارسی اضافه شود

---

## A11Y-P3-4 — Touch target کوچک (`target-size`)

- [ ] دکمه‌ها/لینک‌های header موبایل: حداقل ۴۸×۴۸ px فاصله/اندازه

---

# P4 — SEO باقی‌مانده (جزئیات در SEO-TODO)

> موارد زیر در [`docs/SEO-TODO.md`](SEO-TODO.md) هم هست؛ اینجا برای یک‌جا دیدن.

## SEO-P4-1 — Rich Results Test

- [ ] [Rich Results Test](https://search.google.com/test/rich-results): یک محصول، یک پست بلاگ، FAQ

## SEO-P4-2 — GSC Coverage مانیتور

- [ ] Sitemap Submit شده — منتظر **Success** و تعداد URL
- [ ] Pages → Why pages aren't indexed — Validate fix برای 404/redirect قدیمی

## SEO-P4-3 — Title لیست بلاگ

- [x] `BlogPostListView.title = f"بلاگ - {settings.SITE_NAME}"` — `/blog/` دیگر مثل خانه نیست

## SEO-P4-4 — تست دستی 301 (هنوز تأیید نشده)

- [ ] `/shop/product/<slug>/detail/` → 301
- [ ] `/shop/product/grid/?category_id=1` → 301
- [ ] `/shop/category/<slug>/` → 200
- [ ] `/blog/<id>/` → 301

## SEO-P4-5 — URLهای legacy `.html`

**علت 404:** لینک‌های دمو `./product-overview.html` در offcanvas قالب دسکتاپ — روی هر صفحه مسیر نسبی می‌ساخت.

- [x] حذف لینک‌های دمو در `base-desktop.html` → لینک به `cart:cart-summary` و `shop:product-grid`
- [x] 301: `cart.html` → `/cart/summary/`
- [x] 301: `**/product-overview.html` → `/shop/product/grid/` (`core/core/legacy_redirects.py`)
- [ ] بعد از deploy: GSC → Validate fix برای 404های قدیمی

## SEO-P4-6 — محتوای ادمین

- [ ] `brief_description` محصولات مهم
- [ ] نام نویسنده در پروفایل (نه `admin@admin.com` در JSON-LD)
- [ ] FAQ منتشرشده

## SEO-P4-7 — F16 اختیاری

- [ ] فیلدهای override متا در ادمین (`meta_title`, `meta_description`, `og_image`)

---

# P5 — بعداً (مرحله ۲ SEO)

- [ ] Keyword Map
- [ ] Pillar Page
- [ ] Topic Clusters / Internal Linking
- [ ] Bing Webmaster Tools (اختیاری)
- [ ] Analytics + CWV مانیتور مداوم

---

# چک‌لیست تست بعد از هر فاز

```bash
# TTFB
curl -w 'TTFB: %{time_starttransfer}s\n' -o /dev/null -s https://arvinofficial.ir/

# Cache header
curl -sI https://arvinofficial.ir/static/CACHE/css/output.*.css | grep -i cache-control

# robots + sitemap
curl -sI https://arvinofficial.ir/robots.txt | head -1
curl -sI https://arvinofficial.ir/sitemap.xml | head -1
```

- [ ] Lighthouse **desktop** Incognito — هدف Performance ≥ 85
- [ ] Lighthouse **mobile** Incognito — هدف Performance ≥ 75، TTFB < 1.5 s (واقعی)
- [ ] PageSpeed Insights هر دو layout

---

# ترتیب پیشنهادی اجرا

```text
۱. PERF-P0-1  img2.png فشرده/responsive     ← سریع‌ترین برد موبایل
۲. OPS-P1-1   nginx cache static/media
۳. PERF-P0-2  NoCacheHtmlMiddleware (F17)
۴. PERF-P0-3  سبک‌کردن JS خانه
۵. SEO-P4-3   title بلاگ (یک خط کد)
۶. SEO-P4-5   legacy .html redirects
۷. PERF-P2-*  فونت، بنر، render-blocking
۸. A11Y-P3-*  دسترسی‌پذیری موبایل
۹. SEO-P4-1/2 Rich Results + GSC مانیتور
```

---

*ایجاد: ۱۴۰۵/۰۶/۰۷ — از گزارش Lighthouse و وضعیت production.*
