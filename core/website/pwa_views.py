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
        cache_version = getattr(settings, "PWA_CACHE_VERSION", "v1")
        cache_name = f"arvin-shop-{cache_version}"
        static_url = settings.STATIC_URL.rstrip("/")
        precache = [
            request.build_absolute_uri("/"),
            request.build_absolute_uri(f"{static_url}/css/styles.css"),
            request.build_absolute_uri(f"{static_url}/css/theme.min.css"),
            request.build_absolute_uri(f"{static_url}/css/vendor.min.css"),
            request.build_absolute_uri(
                f"{static_url}/vendor/bootstrap-icons/font/bootstrap-icons.css"
            ),
            request.build_absolute_uri(f"{static_url}/js/jquery.min.js"),
            request.build_absolute_uri(f"{static_url}/js/vendor.min.js"),
            request.build_absolute_uri(f"{static_url}/js/theme.min.js"),
            request.build_absolute_uri(f"{static_url}/js/custom.js"),
            request.build_absolute_uri(f"{static_url}/img/pwa/icon-192.png"),
            request.build_absolute_uri(f"{static_url}/img/pwa/icon-512.png"),
            request.build_absolute_uri("/manifest.webmanifest"),
        ]
        start_url = request.build_absolute_uri("/")
        precache_json = json.dumps(precache)

        js = f"""const CACHE_NAME = {json.dumps(cache_name)};
const PRECACHE_URLS = {precache_json};
const START_URL = {json.dumps(start_url)};

self.addEventListener("install", (event) => {{
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      Promise.allSettled(PRECACHE_URLS.map((url) => cache.add(url)))
    ).then(() => self.skipWaiting())
  );
}});

self.addEventListener("activate", (event) => {{
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
}});

self.addEventListener("fetch", (event) => {{
  if (event.request.method !== "GET") return;
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (event.request.mode === "navigate") {{
    event.respondWith(
      fetch(event.request)
        .then((response) => {{
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        }})
        .catch(() => caches.match(event.request).then((r) => r || caches.match(START_URL)))
    );
    return;
  }}

  event.respondWith(
    caches.match(event.request).then((cached) => {{
      if (cached) return cached;
      return fetch(event.request).then((response) => {{
        if (!response || response.status !== 200 || response.type !== "basic") {{
          return response;
        }}
        const copy = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return response;
      }});
    }})
  );
}});
"""
        response = HttpResponse(js, content_type="application/javascript; charset=utf-8")
        response["Service-Worker-Allowed"] = "/"
        response["Cache-Control"] = "no-cache"
        return response
