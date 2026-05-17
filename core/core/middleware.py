"""Site layout cookie when forcing mobile/desktop via ?site= query param."""


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
