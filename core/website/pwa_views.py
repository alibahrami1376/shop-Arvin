import json

from django.conf import settings
from django.http import HttpResponse
from django.views import View


class WebAppManifestView(View):
    """Web App Manifest for PWA install."""

    def get(self, request):
        icon_base = request.build_absolute_uri("/static/img/pwa/")
        manifest = {
            "name": getattr(settings, "PWA_APP_NAME", "آروین صندلی"),
            "short_name": getattr(settings, "PWA_SHORT_NAME", "آروین"),
            "description": getattr(
                settings, "PWA_APP_DESCRIPTION", "فروشگاه آنلاین آروین صندلی"
            ),
            "start_url": request.build_absolute_uri("/"),
            "scope": request.build_absolute_uri("/"),
            "display": "standalone",
            "orientation": "portrait-primary",
            "background_color": "#FFFFFF",
            "theme_color": "#6B4E3D",
            "lang": "fa",
            "dir": "rtl",
            "icons": [
                {
                    "src": f"{icon_base}icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any",
                },
                {
                    "src": f"{icon_base}icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any",
                },
                {
                    "src": f"{icon_base}icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "maskable",
                },
            ],
        }
        response = HttpResponse(
            json.dumps(manifest, ensure_ascii=False),
            content_type="application/manifest+json; charset=utf-8",
        )
        response["Cache-Control"] = "public, max-age=3600"
        return response


class ServiceWorkerView(View):
    """Minimal offline-capable service worker."""

    def get(self, request):
        cache_version = getattr(settings, "PWA_CACHE_VERSION", "v3")
        cache_name = f"arvin-shop-{cache_version}"
        static_url = settings.STATIC_URL.rstrip("/")
        precache = [
            request.build_absolute_uri(f"{static_url}/css/styles.css"),
            request.build_absolute_uri(f"{static_url}/css/styles-mobile.css"),
            request.build_absolute_uri(f"{static_url}/css/styles-desktop.css"),
            request.build_absolute_uri(f"{static_url}/css/vendor.min.css"),
            request.build_absolute_uri(
                f"{static_url}/vendor/bootstrap-icons/font/bootstrap-icons.css"
            ),
            request.build_absolute_uri(f"{static_url}/vendor/js/bootstrap.bundle.min.js"),
            request.build_absolute_uri(f"{static_url}/vendor/js/swiper-bundle.min.js"),
            request.build_absolute_uri(f"{static_url}/js/jquery.min.js"),
            request.build_absolute_uri(f"{static_url}/js/layout-sync.js"),
            request.build_absolute_uri(f"{static_url}/js/custom.js"),
            request.build_absolute_uri(f"{static_url}/js/mobile.js"),
            request.build_absolute_uri(f"{static_url}/img/pwa/icon-192.png"),
            request.build_absolute_uri(f"{static_url}/img/pwa/icon-512.png"),
            request.build_absolute_uri("/manifest.webmanifest"),
        ]
        start_url = request.build_absolute_uri("/")
        precache_json = json.dumps(precache)

        js = f"""const CACHE_NAME = {json.dumps(cache_name)};
const PRECACHE_URLS = {precache_json};
const START_URL = {json.dumps(start_url)};

function shouldHandleFetch(url, request) {{
  if (request.method !== "GET") return false;
  if (url.origin !== self.location.origin) return false;
  const path = url.pathname;
  if (path.startsWith("/media/")) return false;
  if (path.startsWith("/admin/")) return false;
  if (request.mode === "navigate") return true;
  if (path.startsWith("/static/")) return true;
  return false;
}}

function cacheOkResponse(request, response) {{
  if (!response || response.status !== 200 || response.type !== "basic") return;
  caches.open(CACHE_NAME).then((cache) => cache.put(request, response.clone()));
}}

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) =>
        Promise.allSettled(
          PRECACHE_URLS.map((url) =>
            fetch(url).then((response) => {{
              if (response.ok) return cache.put(url, response);
            }})
          )
        )
      )
      .then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
        )
      )
      .then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  const url = new URL(event.request.url);
  if (!shouldHandleFetch(url, event.request)) return;

  if (event.request.mode === "navigate") {{
    event.respondWith(
      fetch(event.request).catch(() =>
        caches.match(event.request).then((cached) => cached || caches.match(START_URL))
      )
    );
    return;
  }}

  event.respondWith(
    fetch(event.request)
      .then((response) => {{
        cacheOkResponse(event.request, response);
        return response;
      }})
      .catch(() =>
        caches.match(event.request).then((cached) => cached || Response.error())
      )
  );
}});
"""
        response = HttpResponse(js, content_type="application/javascript; charset=utf-8")
        response["Service-Worker-Allowed"] = "/"
        response["Cache-Control"] = "no-cache"
        return response
