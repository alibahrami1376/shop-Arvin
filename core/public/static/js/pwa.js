(function () {
    "use strict";

    var installBanner = document.getElementById("pwa-install-banner");
    var installBtn = document.getElementById("pwa-install-btn");
    var dismissBtn = document.getElementById("pwa-install-dismiss");
    var deferredPrompt = null;
    var DISMISS_KEY = "pwa-install-dismissed";

    function isStandalone() {
        return (
            window.matchMedia("(display-mode: standalone)").matches ||
            window.navigator.standalone === true
        );
    }

    function isIos() {
        return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
    }

    function showBanner() {
        if (!installBanner || isStandalone()) return;
        if (sessionStorage.getItem(DISMISS_KEY) === "1") return;
        installBanner.classList.remove("d-none");
        document.body.classList.add("has-pwa-install-banner");
    }

    function hideBanner() {
        if (!installBanner) return;
        installBanner.classList.add("d-none");
        document.body.classList.remove("has-pwa-install-banner");
    }

    function registerServiceWorker() {
        if (!("serviceWorker" in navigator)) return;
        window.addEventListener("load", function () {
            navigator.serviceWorker
                .register("/sw.js", { scope: "/" })
                .then(function (registration) {
                    registration.update();
                })
                .catch(function (err) {
                    console.warn("PWA service worker registration failed:", err);
                });
        });
    }

    window.addEventListener("beforeinstallprompt", function (e) {
        e.preventDefault();
        deferredPrompt = e;
        showBanner();
    });

    if (installBtn) {
        installBtn.addEventListener("click", function () {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                deferredPrompt.userChoice.then(function (choice) {
                    deferredPrompt = null;
                    hideBanner();
                    if (choice.outcome === "accepted") {
                        sessionStorage.removeItem(DISMISS_KEY);
                    }
                });
                return;
            }
            if (isIos()) {
                alert(
                    "برای نصب: دکمه اشتراک‌گذاری (Share) را بزنید و «Add to Home Screen» یا «افزودن به صفحه اصلی» را انتخاب کنید."
                );
            }
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener("click", function () {
            sessionStorage.setItem(DISMISS_KEY, "1");
            hideBanner();
        });
    }

    window.addEventListener("appinstalled", function () {
        deferredPrompt = null;
        hideBanner();
    });

    if (isIos() && !isStandalone() && installBanner) {
        var desc = installBanner.querySelector(".pwa-install-banner__desc");
        if (desc) {
            desc.textContent = "از Share گزینه «افزودن به صفحه اصلی» را بزنید";
        }
        showBanner();
    }

    registerServiceWorker();
})();
