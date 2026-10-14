# Lighthouse Mobile — لیست تغییرات پیشنهادی

منبع: گزارش Lighthouse موبایل برای `https://arvinseat.ir/` (۱۴ اکتبر ۲۰۲۶)

**امتیازها:** Performance ~44 · Accessibility ~87 · Best Practices ~96 · SEO 100

**نکته تست:** اکستنشن‌های Chrome (VPN، Wappalyzer) روی نتیجه اثر گذاشته‌اند؛ بعد از تغییرات در Incognito دوباره اندازه بگیرید.

---

## اولویت ۱ — بیشترین اثر روی Performance

1. **کاهش TTFB سرور** (~1.3s)
   - کش HTML/fragment، بهینه‌سازی کوئری‌های هوم، CDN/edge، warm DB.

2. **Cache-Control برای static/media** (الان TTL≈0، صرفه‌جویی تخمینی ~1.4MB در بازدیدهای بعدی)
   - هدرهای طولانی برای `/static/`، فونت، JS/CSS hashed، و تصاویر media با hash.

3. **کوچک‌کردن باندل JS** (`CACHE/js/output.*.js` — ~70% unused، long taskهای سنگین)
   - جدا کردن vendor/صفحه، حذف/defer کردن jQuery+Bootstrap جایی که لازم نیست، code-split برای موبایل.

4. **کاهش unused CSS** (~86% از باندل فشرده)
   - critical CSS برای above-the-fold موبایل، بقیه defer؛ پالایش Bootstrap/کامپوننت‌های بلااستفاده.

5. **بهینه‌سازی تصاویر (~796KB)**
   - بنر اسلایدر: نسخه موبایل (~412–824w) به‌جای 1920w
   - `img2.webp` / `img3.webp` dual-banner: خیلی بزرگ برای عرض نمایش
   - لوگو/favicon/سبد خرید: سایز واقعی نمایش
   - کارت محصول/بلاگ: srcset یا سایز ImageKit نزدیک به نمایش
   - تبدیل لوگو/سبد از PNG به WebP/AVIF در صورت امکان

6. **رفع render-blocking**
   - CSS بحرانی inline یا preload؛ `layout-sync.js` و `defer-images.js` را `defer`/`async` یا بعد از FCP.

7. **`font-display: swap` (یا optional)** برای Bootstrap Icons و فونت‌های Vazir؛ فقط وزن‌های لازم روی موبایل (الان ۵ فونت، شامل TTF).

8. **حذف `Cache-Control: no-store` از صفحه اصلی** (در صورت امن بودن) تا bfcache کار کند.

---

## اولویت ۲ — CLS و تعامل

9. **ثابت‌کردن ارتفاع/ابعاد Swiper بخش خدمات** (`home-services-swiper`) — عامل اصلی CLS (~0.091).

10. **آیکون سبد bottom-nav:** ابعاد ثابت واقعی در CSS (width/height روی img کافی نیست اگر CSS عوض کند).

11. **سبک کردن long tasks صفحه و `pwa.js`** (تقسیم کار، `requestIdleCallback`، init دیرتر).

12. **انیمیشن pagination بنر:** به‌جای animate کردن `width`/`border-radius`، فقط `transform`/`opacity`.

---

## اولویت ۳ — Accessibility

13. **Pagination `home-services`:** یا `aria-hidden` را بردارید یا bulletها را از فوکوس خارج کنید (`tabindex="-1"` وقتی مخفی/دکوراتیو است).

14. **کنتراست دکمه بنر** (`#6b4e3d` روی `#e6b422`) — حداقل 4.5:1.

15. **ترتیب heading:** از پرش به `h4` در کارت محصول پرهیز کنید (مثلاً `h3` یا ساختار صحیح).

16. **دکمه‌های سوشال فوتر:** حداقل 24×24px و فاصله کافی.

17. **alt لوگو فوتر:** تکراری با متن کنارش نباشد (`alt=""` اگر دکوراتیو است).

18. **لینک‌های بنر:** متن یکسان «مشاهده جزئیات» برای مقصدهای مختلف — متن/aria-label متمایز.

---

## اولویت ۴ — Best Practices / امنیت (اختیاری ولی توصیه‌شده)

19. هدر **HSTS**

20. **CSP** (حداقل گزارش‌دهی، بعد enforcement)

21. رفع هشدار CSP در Issues پنل DevTools

---

## خارج از scope سایت (نادیده بگیرید در پیاده‌سازی)

- اسکریپت‌های `chrome-extension://...`
- `llms.txt` (غیراجباری برای Performance فعلی)
- WebMCP / Agentic browsing

---

## پیشنهاد ترتیب کار عملی

1. Cache headers + TTFB
2. تصاویر responsive (مخصوصاً LCP بنر و dual-banner)
3. JS/CSS bundle و render-blocking
4. فونت‌ها
5. CLS swiper + a11y صفحات اصلی
