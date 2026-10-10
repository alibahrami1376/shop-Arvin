(function () {
    function selectedCategoryUrl() {
        var select = document.getElementById("category-id-filter");
        if (!select || !select.options.length) {
            return null;
        }
        var option = select.options[select.selectedIndex];
        return option ? option.getAttribute("data-url") : null;
    }

    function closeShopFilterOffcanvas() {
        var el = document.getElementById("shopFilterOffcanvas");
        if (!el || typeof bootstrap === "undefined" || !bootstrap.Offcanvas) {
            return;
        }
        var instance = bootstrap.Offcanvas.getInstance(el);
        if (instance) {
            instance.hide();
        }
    }

    document.body.addEventListener("htmx:configRequest", function (event) {
        var elt = event.detail.elt;
        if (!elt || !elt.classList || !elt.classList.contains("js-shop-grid-htmx")) {
            return;
        }

        if (elt.id === "shopFilterForm") {
            var categoryUrl = selectedCategoryUrl();
            if (categoryUrl) {
                event.detail.path = categoryUrl;
            }
            return;
        }

        if (elt.tagName === "SELECT") {
            event.detail.path = window.location.pathname;
        }
    });

    document.body.addEventListener("htmx:afterRequest", function (event) {
        var elt = event.detail.elt;
        if (!elt || !event.detail.successful) {
            return;
        }
        if (elt.id === "shopFilterForm" || (elt.classList && elt.classList.contains("shop-filter-form__clear"))) {
            closeShopFilterOffcanvas();
        }
        if (elt.classList && elt.classList.contains("shop-filter-form__clear")) {
            var form = document.getElementById("shopFilterForm");
            if (form) {
                form.reset();
            }
            var categorySelect = document.getElementById("category-id-filter");
            if (categorySelect) {
                categorySelect.value = "";
            }
            var orderBy = document.getElementById("order-by-filter");
            if (orderBy) {
                orderBy.value = "";
            }
            var pageSize = document.getElementById("page-size-filter");
            if (pageSize) {
                pageSize.value = "";
            }
        }
    });
})();
