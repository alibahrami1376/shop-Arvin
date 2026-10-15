/**
 * Keep server layout (mobile/desktop) in sync with viewport width via cookie.
 * Does not put ?site= in the URL.
 */
(function () {
    var MQ = "(max-width: 991.98px)";
    var COOKIE = "site_layout";
    var STORAGE_KEY = "arvin-layout-sync";
    var ATTEMPTS_KEY = "arvin-layout-sync-attempts";
    var MAX_ATTEMPTS = 2;

    function viewportIsMobile() {
        return window.matchMedia(MQ).matches;
    }

    function serverIsMobile() {
        return (
            document.documentElement.classList.contains("device-mobile-root") ||
            (document.body && document.body.classList.contains("device-mobile"))
        );
    }

    function setLayoutCookie(target) {
        document.cookie =
            COOKIE + "=" + target + "; path=/; max-age=2592000; SameSite=Lax";
    }

    function cleanSiteParamFromUrl() {
        var url = new URL(window.location.href);
        if (!url.searchParams.has("site")) {
            return false;
        }
        url.searchParams.delete("site");
        var next =
            url.pathname +
            (url.searchParams.toString() ? "?" + url.searchParams.toString() : "") +
            url.hash;
        window.history.replaceState(null, "", next);
        return true;
    }

    function syncLayoutIfNeeded() {
        cleanSiteParamFromUrl();

        var vpMobile = viewportIsMobile();
        var srvMobile = serverIsMobile();
        if (vpMobile === srvMobile) {
            sessionStorage.removeItem(STORAGE_KEY);
            sessionStorage.removeItem(ATTEMPTS_KEY);
            return;
        }

        var target = vpMobile ? "mobile" : "desktop";
        var attempts = parseInt(sessionStorage.getItem(ATTEMPTS_KEY) || "0", 10);
        if (attempts >= MAX_ATTEMPTS) {
            return;
        }

        sessionStorage.setItem(STORAGE_KEY, target);
        sessionStorage.setItem(ATTEMPTS_KEY, String(attempts + 1));
        setLayoutCookie(target);
        window.location.reload();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", syncLayoutIfNeeded);
    } else {
        syncLayoutIfNeeded();
    }

    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            sessionStorage.removeItem(ATTEMPTS_KEY);
            syncLayoutIfNeeded();
        }
    });

    window.addEventListener("resize", function () {
        window.clearTimeout(window.__arvinLayoutSyncTimer);
        window.__arvinLayoutSyncTimer = window.setTimeout(function () {
            sessionStorage.removeItem(ATTEMPTS_KEY);
            syncLayoutIfNeeded();
        }, 200);
    });
})();
