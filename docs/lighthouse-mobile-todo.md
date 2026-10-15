# Lighthouse Mobile — لیست تغییرات پیشنهادی

منبع: گزارش Lighthouse موبایل برای `https://arvinseat.ir/` (۱۴ اکتبر ۲۰۲۶)

**امتیازها (قبل):** Performance ~44 · Accessibility ~87 · Best Practices ~96 · SEO 100

**نکته تست:** اکستنشن‌های Chrome (VPN، Wappalyzer) روی نتیجه اثر گذاشته‌اند؛ بعد از تغییرات در Incognito دوباره اندازه بگیرید.

برنچ پیاده‌سازی: `perf/lighthouse-mobile`

---

## اولویت ۱ — بیشترین اثر روی Performance

1. **کاهش TTFB سرور** (~1.3s) — عمدتاً ops (CDN/edge، warm DB). کش fragment هوم از قبل در کد هست؛ LocMem per-worker است.
   - [ ] باقی‌ماندهٔ infra

2. **Cache-Control برای static/media** — انجام شد (`default.conf`: static 30d immutable، media 7d)

3. **کوچک‌کردن باندل JS** — جزئی: `pwa.js` با `requestIdleCallback`؛ جداسازی کامل vendor هنوز باز است
   - [ ] code-split بزرگ‌تر (جدا کردن Swiper فقط برای هوم)

4. **کاهش unused CSS** — باز (critical CSS / پالایش Bootstrap)
   - [ ] critical CSS

5. **بهینه‌سازی تصاویر** — انجام شد
   - بنر: ImageKit موبایل 824w + srcset
   - dual-banner: `static/img/900x900/mobile/*.webp` (~800w)
   - کارت محصول موبایل: ImageKit 540×720

6. **رفع render-blocking** — `layout-sync.js` و `defer-images.js` با `defer`

7. **`font-display: swap`** — Bootstrap Icons، Font Awesome، VazirHeader → woff2

8. **حذف `Cache-Control: no-store` از صفحه اصلی** — انجام شد (`NoCacheHtmlMiddleware`: `private, max-age=0, must-revalidate` مگر `?site=`)

---

## اولویت ۲ — CLS و تعامل

9. **ارتفاع ثابت `home-services-swiper`** — انجام شد

10. **آیکون سبد bottom-nav:** اندازه ثابت 24×24px — انجام شد

11. **سبک کردن `pwa.js`** — idle registration — انجام شد

12. **انیمیشن pagination بنر/خدمات:** `transform` به‌جای `width` — انجام شد

---

## اولویت ۳ — Accessibility

13. **Pagination `home-services`:** `tabindex="-1"` روی bulletها — انجام شد

14. **کنتراست دکمه بنر:** متن `#4a372c` روی طلایی — انجام شد

15. **ترتیب heading:** `h4` → `h3` در کارت‌های استریپ / latest — انجام شد؛ پرفروش‌ها با carousel موبایل

16. **دکمه‌های سوشال فوتر:** حداقل 44×44 — انجام شد

17. **alt لوگو فوتر:** دکوراتیو `alt=""` — انجام شد

18. **لینک‌های بنر:** `aria-label` متمایز با عنوان — انجام شد

---

## اولویت ۴ — Best Practices / امنیت

19. هدر **HSTS** — انجام شد (وقتی `DEBUG=False`)

20. **CSP** — باز (نیاز به سیاست و تست دقیق)
   - [ ] CSP report-only سپس enforce

21. رفع هشدار CSP در Issues — وابسته به ۲۰

---

## خارج از scope سایت (نادیده بگیرید در پیاده‌سازی)

- اسکریپت‌های `chrome-extension://...`
- `llms.txt`
- WebMCP / Agentic browsing

---

## پیشنهاد ترتیب کار باقی‌مانده

1. اندازه‌گیری دوباره در Incognito بعد از دیپلوی این برنچ
2. code-split JS/CSS (آیتم ۳–۴)
3. CSP گزارش‌دهی
4. TTFB / CDN در لایهٔ سرور
