(function () {
    var ADMIN_PREFIX = "/dashboard/admin";
    var CONTENT_ID = "admin-dashboard-content";

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
            if (!hasActive) {
                return;
            }
            el.classList.add("show");
            if (btn) {
                btn.classList.remove("collapsed");
                btn.setAttribute("aria-expanded", "true");
            }
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
            !!elt.closest("#" + CONTENT_ID) ||
            !!elt.closest("#sidebarNav") ||
            !!elt.closest("#adminSidebarMobileNav")
        );
    }

    function syncAdminListFilters() {
        if (typeof window.syncAdminListFiltersFromUrl === "function") {
            window.syncAdminListFiltersFromUrl();
        }
    }

    function extractShellPieces(html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var content = doc.getElementById(CONTENT_ID);
        if (!content) {
            return null;
        }
        return {
            contentHtml: content.outerHTML,
            breadcrumb: doc.getElementById("admin-dashboard-breadcrumb"),
            messages: doc.getElementById("django-htmx-messages"),
            formMedia: doc.getElementById("django-htmx-form-media"),
            title: doc.title || "",
        };
    }

    function applyOob(fromEl, id) {
        if (!fromEl) {
            return;
        }
        var live = document.getElementById(id);
        if (live) {
            live.outerHTML = fromEl.outerHTML;
        }
    }

    document.body.addEventListener("htmx:configRequest", function (event) {
        var elt = event.detail && event.detail.elt;
        if (!isDashboardNavRequest(elt)) {
            return;
        }
        event.detail.headers["Cache-Control"] = "no-cache";
        event.detail.headers["Pragma"] = "no-cache";
    });

    document.body.addEventListener("htmx:beforeRequest", function (event) {
        var elt = event.detail && event.detail.elt;
        if (!elt || !elt.closest("#" + CONTENT_ID)) {
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

    // اگر پاسخ صفحه کامل بود (مثلاً به‌خاطر unset شدن hx-select)، فقط شل محتوا را بردار
    document.body.addEventListener("htmx:beforeSwap", function (event) {
        var target = event.detail && event.detail.target;
        if (!target || target.id !== CONTENT_ID) {
            return;
        }
        if (!isDashboardNavRequest(event.detail.elt)) {
            return;
        }

        var response = event.detail.serverResponse || "";
        if (!/<html[\s>]/i.test(response) && !/<body[\s>]/i.test(response)) {
            return;
        }

        var pieces = extractShellPieces(response);
        if (!pieces) {
            event.detail.shouldSwap = false;
            var path =
                (event.detail.requestConfig && event.detail.requestConfig.path) ||
                window.location.href;
            window.location.assign(path);
            return;
        }

        event.detail.serverResponse = pieces.contentHtml;
        applyOob(pieces.breadcrumb, "admin-dashboard-breadcrumb");
        applyOob(pieces.messages, "django-htmx-messages");
        applyOob(pieces.formMedia, "django-htmx-form-media");
        if (pieces.title) {
            document.title = pieces.title;
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
        if (
            target.id === CONTENT_ID ||
            target.id === "admin-list-root" ||
            target.id === "django-htmx-form-media"
        ) {
            syncActiveNav();
            syncAdminListFilters();
        }
        if (typeof formatVisiblePrices === "function" && target.id === CONTENT_ID) {
            formatVisiblePrices(target);
        }
    });

    document.addEventListener("DOMContentLoaded", function () {
        syncActiveNav();
        syncAdminListFilters();
    });
})();
