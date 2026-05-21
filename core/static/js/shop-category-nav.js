/**
 * باز/بسته شدن زیردسته‌ها در منوی فروشگاه (هدر دسکتاپ و موبایل)
 */
function initShopCategoryNavToggles() {
    document.querySelectorAll('[data-shop-cat-toggle]').forEach(function (btn) {
        if (btn.dataset.shopCatBound === '1') {
            return;
        }
        btn.dataset.shopCatBound = '1';

        var panelId = btn.getAttribute('aria-controls');
        var panel = panelId ? document.getElementById(panelId) : null;
        if (!panel) {
            return;
        }

        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            var willOpen = panel.hidden;
            panel.hidden = !willOpen;
            btn.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
            btn.classList.toggle('is-open', willOpen);
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initShopCategoryNavToggles);
} else {
    initShopCategoryNavToggles();
}
