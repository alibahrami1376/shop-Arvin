/**
 * Keep server layout (mobile/desktop) in sync with viewport width.
 * Fixes broken layout when testing with DevTools device mode without hard refresh.
 */
(function () {
    var MQ = '(max-width: 991.98px)';
    var COOKIE = 'site_layout';
    var STORAGE_KEY = 'arvin-layout-sync';

    function viewportIsMobile() {
        return window.matchMedia(MQ).matches;
    }

    function serverIsMobile() {
        return document.documentElement.classList.contains('device-mobile-root') ||
            (document.body && document.body.classList.contains('device-mobile'));
    }

    function getCookie(name) {
        var match = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : '';
    }

    function syncLayoutIfNeeded() {
        var vpMobile = viewportIsMobile();
        var srvMobile = serverIsMobile();
        if (vpMobile === srvMobile) {
            sessionStorage.removeItem(STORAGE_KEY);
            return;
        }

        var target = vpMobile ? 'mobile' : 'desktop';
        if (sessionStorage.getItem(STORAGE_KEY) === target) {
            return;
        }

        sessionStorage.setItem(STORAGE_KEY, target);
        document.cookie = COOKIE + '=' + target + '; path=/; max-age=2592000; SameSite=Lax';

        var url = new URL(window.location.href);
        url.searchParams.set('site', target);
        window.location.replace(url.toString());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', syncLayoutIfNeeded);
    } else {
        syncLayoutIfNeeded();
    }

    window.addEventListener('pageshow', function (event) {
        if (event.persisted) {
            syncLayoutIfNeeded();
        }
    });

    window.addEventListener('resize', function () {
        window.clearTimeout(window.__arvinLayoutSyncTimer);
        window.__arvinLayoutSyncTimer = window.setTimeout(syncLayoutIfNeeded, 200);
    });
})();
