(function () {
    var ADMIN_PREFIX = "/dashboard/admin";

    function normalizePath(path) {
        if (!path) {
            return "/";
        }
        return path.replace(/\/+$/, "") || "/";
    }

    function isAdminDashboardPath(pathname) {
        var path = normalizePath(pathname);
        return path === ADMIN_PREFIX || path.indexOf(ADMIN_PREFIX + "/") === 0;
    }

    function syncActiveNav() {
        var path = normalizePath(window.location.pathname);
        var best = null;

        document.querySelectorAll(".js-admin-dash-nav").forEach(function (link) {
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

        expandActiveCollapses();
    }

    function expandActiveCollapses() {
        document.querySelectorAll(".js-admin-sidebar-collapse").forEach(function (el) {
            var hasActive = !!el.querySelector(".js-admin-dash-nav.active");
            var btn = document.querySelector('[data-bs-target="#' + el.id + '"]');
            if (hasActive) {
                el.classList.add("show");
                if (btn) {
                    btn.classList.remove("collapsed");
                    btn.setAttribute("aria-expanded", "true");
                }
                return;
            }
            // Leave manually opened groups alone; only collapse ones that lost active
            // when another section became active.
        });
    }

    function closeMobileSidebar() {
        var el = document.getElementById("dashboardAdminSidebar");
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
            (elt.classList && elt.classList.contains("js-admin-dash-nav")) ||
            !!elt.closest("#admin-dashboard-content") ||
            !!elt.closest("#sidebarNav") ||
            !!elt.closest("#adminSidebarMobileNav")
        );
    }

    function syncAdminListFilters() {
        if (typeof window.syncAdminListFiltersFromUrl === "function") {
            window.syncAdminListFiltersFromUrl();
        }
    }

    document.body.addEventListener("htmx:beforeRequest", function (event) {
        var elt = event.detail && event.detail.elt;
        if (!elt || !elt.closest("#admin-dashboard-content")) {
            return;
        }
        if (elt.tagName !== "A") {
            return;
        }

        var path =
            (event.detail.requestConfig && event.detail.requestConfig.path) ||
            elt.getAttribute("href") ||
            "";
        var url;
        try {
            url = new URL(path, window.location.origin);
        } catch (err) {
            return;
        }

        if (url.origin !== window.location.origin || !isAdminDashboardPath(url.pathname)) {
            event.preventDefault();
            window.location.href = url.href;
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
        syncAdminListFilters();
    });

    document.body.addEventListener("htmx:historyRestore", function () {
        syncActiveNav();
        syncAdminListFilters();
    });

    document.body.addEventListener("htmx:afterSettle", function (event) {
        var target = event.detail && event.detail.target;
        if (!target) {
            return;
        }
        if (target.id === "admin-dashboard-content" || target.id === "admin-list-root") {
            syncActiveNav();
            syncAdminListFilters();
        }
        if (typeof formatVisiblePrices === "function" && target.id === "admin-dashboard-content") {
            formatVisiblePrices(target);
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        syncActiveNav();
        syncAdminListFilters();
    });
})();
