function updateCartBadges(totalQuantity) {
    var qty = parseInt(totalQuantity, 10);
    if (Number.isNaN(qty) || qty < 0) {
        qty = 0;
    }

    var headerBadge = document.getElementById('total-cart-item-count');
    if (headerBadge) {
        headerBadge.textContent = qty > 0 ? String(qty) : (headerBadge.dataset.emptyLabel || '۰');
    }

    var mobileBadge = document.getElementById('mobile-bottom-cart-count');
    if (mobileBadge) {
        mobileBadge.textContent = qty > 0 ? String(qty) : '';
        mobileBadge.classList.toggle('d-none', qty <= 0);
    }
}

function changePage(page_number) {
    let current_url_params = new URLSearchParams(window.location.search)
    current_url_params.set("page", page_number)
    let new_url = window.location.pathname + "?" + current_url_params.toString()
    window.location.href = new_url
}

function formatPriceInToman(element) {
    if (!element || element.dataset.priceFormatted === "1") {
        return;
    }
    const raw =
        element.dataset.price ??
        element.textContent.replace(/[^\d.]/g, "");
    const rawPrice = parseFloat(raw);
    if (Number.isNaN(rawPrice)) {
        return;
    }
    const formatter = new Intl.NumberFormat("fa-IR");
    element.textContent = `${formatter.format(rawPrice)} تومان`;
    element.dataset.priceFormatted = "1";
}

function initPriceThousandInputs() {
    var digitMap = {
        "۰": "0", "۱": "1", "۲": "2", "۳": "3", "۴": "4",
        "۵": "5", "۶": "6", "۷": "7", "۸": "8", "۹": "9",
        "٠": "0", "١": "1", "٢": "2", "٣": "3", "٤": "4",
        "٥": "5", "٦": "6", "٧": "7", "٨": "8", "٩": "9",
    };

    function toDigits(value) {
        return String(value || "").replace(/[۰-۹٠-٩]/g, function (ch) {
            return digitMap[ch] || ch;
        }).replace(/\D/g, "");
    }

    function withCommas(digits) {
        if (!digits) {
            return "";
        }
        return digits.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    document.querySelectorAll(".js-price-thousands").forEach(function (input) {
        if (input.dataset.thousandsBound === "1") {
            return;
        }
        input.dataset.thousandsBound = "1";
        input.value = withCommas(toDigits(input.value));

        input.addEventListener("input", function () {
            var digits = toDigits(input.value);
            var formatted = withCommas(digits);
            input.value = formatted;
        });

        var form = input.closest("form");
        if (form && !form.dataset.priceThousandsSubmit) {
            form.dataset.priceThousandsSubmit = "1";
            form.addEventListener("submit", function () {
                form.querySelectorAll(".js-price-thousands").forEach(function (field) {
                    field.value = toDigits(field.value);
                });
            });
        }
    });
}

function initQuantityCounters() {
    document.querySelectorAll('.js-quantity-counter').forEach(function (wrap) {
        if (wrap.dataset.qtyBound) {
            return;
        }
        wrap.dataset.qtyBound = '1';
        var input = wrap.querySelector('.js-result, input[type="number"], input[type="text"]');
        var minus = wrap.querySelector('.js-minus');
        var plus = wrap.querySelector('.js-plus');
        if (!input || !minus || !plus) {
            return;
        }
        var min = parseInt(input.getAttribute('min'), 10) || 1;
        var max = parseInt(input.getAttribute('max'), 10) || 99;
        function setValue(next) {
            var value = parseInt(input.value, 10) || min;
            value = Math.max(min, Math.min(max, next !== undefined ? next : value));
            input.value = String(value);
        }
        minus.addEventListener('click', function (e) {
            e.preventDefault();
            setValue((parseInt(input.value, 10) || min) - 1);
        });
        plus.addEventListener('click', function (e) {
            e.preventDefault();
            setValue((parseInt(input.value, 10) || min) + 1);
        });
    });
}

function initProductGallerySwipers() {
    if (typeof Swiper === 'undefined') {
        return;
    }
    var thumbEl = document.querySelector('.js-swiper-shop-product-thumb');
    var thumbSwiper = null;
    if (thumbEl && !thumbEl.swiper) {
        thumbSwiper = new Swiper(thumbEl, {
            slidesPerView: 4,
            spaceBetween: 8,
            watchSlidesProgress: true,
            watchSlidesVisibility: true,
            breakpoints: { 360: { slidesPerView: 5 } },
        });
    } else if (thumbEl && thumbEl.swiper) {
        thumbSwiper = thumbEl.swiper;
    }
    var productEl = document.querySelector('.js-swiper-shop-product');
    if (productEl && !productEl.swiper) {
        new Swiper(productEl, {
            rtl: true,
            effect: 'fade',
            fadeEffect: { crossFade: true },
            loop: productEl.querySelectorAll('.swiper-slide').length > 1,
            navigation: {
                nextEl: '.js-swiper-shop-product-button-next',
                prevEl: '.js-swiper-shop-product-button-prev',
            },
            thumbs: thumbSwiper ? { swiper: thumbSwiper } : undefined,
        });
    }
}

function initPasswordToggle() {
    document.querySelectorAll('.js-password-toggle').forEach(function (btn) {
        if (btn.dataset.passToggleBound) {
            return;
        }
        btn.dataset.passToggleBound = '1';

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            var group = btn.closest('.input-group, .auth-field-password');
            var input = group
                ? group.querySelector('input[type="password"], input[type="text"]')
                : null;
            if (!input && btn.getAttribute('aria-controls')) {
                input = document.getElementById(btn.getAttribute('aria-controls'));
            }
            var icon = btn.querySelector('i');
            if (!input) {
                return;
            }
            var show = input.type === 'password';
            input.type = show ? 'text' : 'password';
            btn.setAttribute('aria-label', show ? 'مخفی کردن رمز عبور' : 'نمایش رمز عبور');
            if (icon) {
                icon.classList.toggle('bi-eye', !show);
                icon.classList.toggle('bi-eye-slash', show);
            }
        });
    });
}

function initBootstrapTooltips() {
    if (typeof bootstrap === 'undefined' || !bootstrap.Tooltip) {
        return;
    }
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        if (!bootstrap.Tooltip.getInstance(el)) {
            new bootstrap.Tooltip(el);
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    let priceElements = document.querySelectorAll('.formatted-price');
    priceElements.forEach(element => formatPriceInToman(element));
    initPriceThousandInputs();
    initQuantityCounters();
    initProductGallerySwipers();
    initPasswordToggle();
    initBootstrapTooltips();
    
    /**
     * Header Scroll Behavior - Intelligent Hide/Show System
     * 
     * Features:
     * - Hide on scroll down
     * - Show on scroll up
     * - Sticky after scroll threshold
     * - Smooth transform-based animations
     * - Performance optimized with requestAnimationFrame
     */
    
    const header = document.querySelector('.header');
    const contentElement = document.querySelector('#content');
    
    if (header && !document.body.classList.contains('device-mobile')) {
        let lastScrollTop = 0;
        let isScrolling = false;
        let scrollTimeout = null;
        const scrollThreshold = 100; // Threshold for sticky state
        const scrollDelta = 5; // Minimum scroll delta to trigger hide/show
        
        /**
         * Handle scroll events with intelligent hide/show behavior
         */
        function handleScroll() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';
            const scrollDistance = Math.abs(scrollTop - lastScrollTop);
            
            // Only process if scroll distance is significant
            if (scrollDistance < scrollDelta) {
                lastScrollTop = scrollTop;
                return;
            }
            
            // Sticky state - after threshold
            if (scrollTop > scrollThreshold) {
                if (!header.classList.contains('header--sticky')) {
                    header.classList.add('header--sticky');
                    document.body.classList.add('header-sticky-active');
                    
                    // Calculate header height and add padding to content
                    if (contentElement) {
                        const headerHeight = header.offsetHeight;
                        contentElement.style.paddingTop = headerHeight + 'px';
                    }
                }
                
                // Hide on scroll down, show on scroll up
                if (scrollDirection === 'down' && !header.classList.contains('header--hidden')) {
                    header.classList.add('header--hidden');
                } else if (scrollDirection === 'up' && header.classList.contains('header--hidden')) {
                    header.classList.remove('header--hidden');
                }
            } else {
                // Reset to normal state when at top
                if (header.classList.contains('header--sticky')) {
                    header.classList.remove('header--sticky');
                    header.classList.remove('header--hidden');
                    document.body.classList.remove('header-sticky-active');
                    
                    if (contentElement) {
                        contentElement.style.paddingTop = '0';
                    }
                }
            }
            
            lastScrollTop = scrollTop;
            isScrolling = true;
            
            // Clear existing timeout
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            // Reset scrolling flag after scroll ends
            scrollTimeout = setTimeout(function() {
                isScrolling = false;
            }, 150);
        }
        
        /**
         * Throttled scroll handler using requestAnimationFrame
         */
        let ticking = false;
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
        
        // Initial check on page load
        setTimeout(function() {
            handleScroll();
        }, 100);
    }
});