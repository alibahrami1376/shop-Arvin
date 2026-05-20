"""Site layout cookie when forcing mobile/desktop via ?site= query param."""


class NoCacheHtmlMiddleware:
    """Prevent browser from serving stale HTML when switching mobile/desktop."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" in content_type:
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["Vary"] = "Cookie, User-Agent, Sec-CH-UA-Mobile"
        return response


class SiteLayoutCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        layout = request.GET.get("site")
        if layout in ("mobile", "desktop"):
            request.site_layout_cookie = layout

        response = self.get_response(request)

        if layout in ("mobile", "desktop"):
            response.set_cookie(
                "site_layout",
                layout,
                max_age=60 * 60 * 24 * 30,
                samesite="Lax",
            )
        return response
