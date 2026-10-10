(function () {
    var CUSTOMER_PREFIX = "/dashboard/customer";

    function normalizePath(path) {
        if (!path) {
            return "/";
        }
        return path.replace(/\/+$/, "") || "/";
    }

    function isCustomerDashboardPath(pathname) {
        var path = normalizePath(pathname);
        return path === CUSTOMER_PREFIX || path.indexOf(CUSTOMER_PREFIX + "/") === 0;
    }

    function syncActiveNav() {
        var path = normalizePath(window.location.pathname);
        var best = null;

        document.querySelectorAll(".js-customer-dash-nav").forEach(function (link) {
            link.classList.remove("active");
            var href = normalizePath(link.getAttribute("href") || "");
            if (!href) {
                return;
            }
            var matches = path === href || path.indexOf(href + "/") === 0;
            if (!matches) {
                return;
            }
            if (!best || href.length > best.hrefLength) {
                best = { link: link, hrefLength: href.length };
            }
        });

        if (best) {
            best.link.classList.add("active");
        }
    }

    function closeMobileSidebar() {
        var el = document.getElementById("dashboardCustomerSidebar");
        if (!el || typeof bootstrap === "undefined" || !bootstrap.Offcanvas) {
            return;
        }
        var instance = bootstrap.Offcanvas.getInstance(el);
        if (instance) {
            instance.hide();
        }
    }

    function updateTitleFromXhr(xhr) {
        if (!xhr || !xhr.responseText) {
            return;
        }
        var match = /<title[^>]*>([^<]*)<\/title>/i.exec(xhr.responseText);
        if (match && match[1]) {
            document.title = match[1].trim();
        }
    }

    function isDashboardNavRequest(elt) {
        if (!elt) {
            return false;
        }
        return (
            (elt.classList && elt.classList.contains("js-customer-dash-nav")) ||
            !!elt.closest("#customer-dashboard-content")
        );
    }

    document.body.addEventListener("htmx:beforeRequest", function (event) {
        var elt = event.detail && event.detail.elt;
        if (!elt || !elt.closest("#customer-dashboard-content")) {
            return;
        }
        if (elt.tagName !== "A") {
            return;
        }

        var path = (event.detail.requestConfig && event.detail.requestConfig.path) || elt.getAttribute("href") || "";
        var url;
        try {
            url = new URL(path, window.location.origin);
        } catch (err) {
            return;
        }

        if (url.origin !== window.location.origin || !isCustomerDashboardPath(url.pathname)) {
            event.preventDefault();
            window.location.href = url.href;
        }
    });

    document.body.addEventListener("htmx:beforeSwap", function (event) {
        var target = event.detail && event.detail.target;
        if (!target || target.id !== "customer-dashboard-content") {
            return;
        }
        if (!isDashboardNavRequest(event.detail.elt)) {
            return;
        }
        var response = event.detail.serverResponse || "";
        if (!/<html[\s>]/i.test(response) && !/<body[\s>]/i.test(response)) {
            return;
        }
        var doc = new DOMParser().parseFromString(response, "text/html");
        var content = doc.getElementById("customer-dashboard-content");
        if (!content) {
            event.detail.shouldSwap = false;
            var path =
                (event.detail.requestConfig && event.detail.requestConfig.path) ||
                window.location.href;
            window.location.assign(path);
            return;
        }
        event.detail.serverResponse = content.outerHTML;
        ["customer-dashboard-breadcrumb", "django-htmx-messages"].forEach(function (id) {
            var fromEl = doc.getElementById(id);
            var live = document.getElementById(id);
            if (fromEl && live) {
                live.outerHTML = fromEl.outerHTML;
            }
        });
        if (doc.title) {
            document.title = doc.title;
        }
    });

    document.body.addEventListener("htmx:afterOnLoad", function (event) {
        var elt = event.detail && event.detail.elt;
        if (!isDashboardNavRequest(elt)) {
            return;
        }
        updateTitleFromXhr(event.detail.xhr);
        syncActiveNav();
        closeMobileSidebar();
    });

    document.body.addEventListener("htmx:historyRestore", function () {
        syncActiveNav();
    });

    document.body.addEventListener("htmx:afterSettle", function (event) {
        var target = event.detail && event.detail.target;
        if (!target || target.id !== "customer-dashboard-content") {
            return;
        }
        syncActiveNav();
        if (typeof formatVisiblePrices === "function") {
            formatVisiblePrices(target);
        }
    });

    document.addEventListener("DOMContentLoaded", syncActiveNav);
})();
