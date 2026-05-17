/**
 * Mobile-only helpers (loaded from base-mobile.html)
 */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.swiper').forEach(function (el) {
        if (el.swiper && typeof el.swiper.update === 'function') {
            el.swiper.update();
        }
    });

    window.addEventListener('resize', function () {
        document.querySelectorAll('.swiper').forEach(function (el) {
            if (el.swiper && typeof el.swiper.update === 'function') {
                el.swiper.update();
            }
        });
    });
});
