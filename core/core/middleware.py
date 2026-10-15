"""Site layout cookie when forcing mobile/desktop via ?site= query param."""


class NoCacheHtmlMiddleware:
    """
    HTML caching headers.

    Layout switch (?site=mobile|desktop) must not be bfcache'd with wrong layout.
    Public HTML uses must-revalidate without no-store so bfcache can work.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        layout_switch = request.GET.get("site") in ("mobile", "desktop") or getattr(
            request, "site_layout_cookie", None
        )
        response["Vary"] = "Cookie, User-Agent, Sec-CH-UA-Mobile"
        if layout_switch:
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        else:
            # Allow bfcache; still revalidate personalized HTML.
            response["Cache-Control"] = "private, max-age=0, must-revalidate"
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
