from core.seo import build_canonical_url


def seo(request):
    return {"canonical_url": build_canonical_url(request)}
