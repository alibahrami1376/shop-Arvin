/**
 * Mobile-only helpers (loaded from base-mobile.html and dashboard mobile bases)
 */
document.addEventListener('DOMContentLoaded', function () {
    initMobileShopNav();
    if (typeof initShopCategoryNavToggles === 'function') {
        initShopCategoryNavToggles();
    }
    initShopFilterOffcanvas();
    initMobileHeaderSearch();
    initHomeProductStripSwipers();

    document.querySelectorAll('.swiper').forEach(function (el) {
        if (el.swiper && typeof el.swiper.update === 'function') {
            el.swiper.update();
        }
    });
});

window.addEventListener('resize', function () {
    document.querySelectorAll('.swiper').forEach(function (el) {
        if (el.swiper && typeof el.swiper.update === 'function') {
            el.swiper.update();
        }
    });
});

function initMobileShopNav() {
    var toggle = document.querySelector('.header__mobile-shop-toggle');
    var panel = document.getElementById('headerShopCategories');
    var offcanvas = document.getElementById('headerMobileNav');

    if (!toggle || !panel) {
        return;
    }

    function closeShopPanel() {
        panel.hidden = true;
        panel.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function () {
        var willOpen = panel.hidden;
        if (willOpen) {
            panel.hidden = false;
            panel.classList.add('is-open');
            toggle.setAttribute('aria-expanded', 'true');
        } else {
            closeShopPanel();
        }
    });

    if (offcanvas) {
        offcanvas.addEventListener('hidden.bs.offcanvas', closeShopPanel);
    }
}

function initHomeProductStripSwipers() {
    if (typeof Swiper === 'undefined') {
        return;
    }
    document.querySelectorAll('.js-home-product-strip-swiper').forEach(function (el) {
        if (el.swiper) {
            return;
        }
        var slideCount = el.querySelectorAll('.swiper-slide').length;
        if (!slideCount) {
            return;
        }
        new Swiper(el, {
            rtl: true,
            slidesPerView: 2,
            slidesPerGroup: 2,
            spaceBetween: 8,
            speed: 450,
            watchOverflow: true,
            pagination: {
                el: el.querySelector('.home-product-strip-pagination'),
                clickable: true,
            },
        });
    });
}

function initShopFilterOffcanvas() {
    var offcanvasEl = document.getElementById('shopFilterOffcanvas');
    var form = document.getElementById('shopFilterForm');
    if (!offcanvasEl || !form || typeof bootstrap === 'undefined' || !bootstrap.Offcanvas) {
        return;
    }

    form.addEventListener('submit', function () {
        var instance = bootstrap.Offcanvas.getInstance(offcanvasEl);
        if (instance) {
            instance.hide();
        }
    });
}

function initMobileHeaderSearch() {
    var offcanvas = document.getElementById('headerMobileSearch');
    var input = document.getElementById('headerMobileSearchInput');
    if (!offcanvas || !input) {
        return;
    }

    offcanvas.addEventListener('shown.bs.offcanvas', function () {
        input.focus();
        if (typeof input.select === 'function') {
            input.select();
        }
    });
}
