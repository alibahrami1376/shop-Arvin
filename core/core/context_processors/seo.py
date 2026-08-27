from core.seo import build_canonical_url, get_meta_robots


def seo(request):
    return {
        "canonical_url": build_canonical_url(request),
        "meta_robots": get_meta_robots(request),
    }
