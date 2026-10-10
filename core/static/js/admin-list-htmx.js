(function () {
    var FILTER_IDS = {
        "page-size-filter": "page_size",
        "order-by-filter": "order_by",
        "search-query-filter": "q",
        "category-id-filter": "category_id",
        "status-type-filter": "status",
        "min-price-filter": "min_price",
        "max-price-filter": "max_price",
    };

    function getRoot() {
        return document.getElementById("admin-list-root");
    }

    function syncFiltersFromUrl() {
        if (!getRoot()) {
            return;
        }
        var params = new URLSearchParams(window.location.search);
        Object.keys(FILTER_IDS).forEach(function (id) {
            var el = document.getElementById(id);
            if (!el) {
                return;
            }
            var value = params.get(FILTER_IDS[id]);
            if (el.tagName === "SELECT" || el.tagName === "INPUT") {
                el.value = value || "";
            }
        });
    }

    window.syncAdminListFiltersFromUrl = syncFiltersFromUrl;

    function loadList(url, push) {
        if (typeof htmx === "undefined" || !getRoot()) {
            window.location.href = url;
            return;
        }
        htmx
            .ajax("GET", url, {
                target: "#admin-list-root",
                select: "#admin-list-root",
                swap: "outerHTML",
            })
            .then(function () {
                if (push) {
                    history.pushState({}, "", url);
                }
                syncFiltersFromUrl();
            });
    }

    function buildUrlFromCurrent(mutator) {
        var params = new URLSearchParams(window.location.search);
        mutator(params);
        var query = params.toString();
        return window.location.pathname + (query ? "?" + query : "");
    }

    var originalChangePage = window.changePage;
    window.changePage = function (pageNumber) {
        if (!getRoot()) {
            if (typeof originalChangePage === "function") {
                return originalChangePage(pageNumber);
            }
            return;
        }
        var url = buildUrlFromCurrent(function (params) {
            params.set("page", String(pageNumber));
        });
        loadList(url, true);
    };

    document.body.addEventListener(
        "change",
        function (event) {
            if (!getRoot()) {
                return;
            }
            var target = event.target;
            if (!target || !target.id) {
                return;
            }
            if (target.id === "page-size-filter") {
                event.stopImmediatePropagation();
                loadList(
                    buildUrlFromCurrent(function (params) {
                        if (target.value) {
                            params.set("page_size", target.value);
                        } else {
                            params.delete("page_size");
                        }
                        params.delete("page");
                    }),
                    true
                );
                return;
            }
            if (target.id === "order-by-filter") {
                event.stopImmediatePropagation();
                loadList(
                    buildUrlFromCurrent(function (params) {
                        if (target.value) {
                            params.set("order_by", target.value);
                        } else {
                            params.delete("order_by");
                        }
                        params.delete("page");
                    }),
                    true
                );
            }
        },
        true
    );

    document.body.addEventListener(
        "submit",
        function (event) {
            var form = event.target;
            if (!getRoot() || !form || form.tagName !== "FORM") {
                return;
            }
            if (!form.closest("#admin-list-root")) {
                return;
            }
            event.preventDefault();
            event.stopImmediatePropagation();
            var params = new URLSearchParams(new FormData(form));
            var orderBy = document.getElementById("order-by-filter");
            var pageSize = document.getElementById("page-size-filter");
            if (orderBy && orderBy.value) {
                params.set("order_by", orderBy.value);
            }
            if (pageSize && pageSize.value) {
                params.set("page_size", pageSize.value);
            }
            params.delete("page");
            var query = params.toString();
            var url = window.location.pathname + (query ? "?" + query : "");
            loadList(url, true);
        },
        true
    );

    window.addEventListener("popstate", function () {
        if (!getRoot()) {
            return;
        }
        loadList(window.location.href, false);
    });

    document.body.addEventListener("htmx:afterSettle", function () {
        syncFiltersFromUrl();
    });

    document.addEventListener("DOMContentLoaded", syncFiltersFromUrl);
})();
