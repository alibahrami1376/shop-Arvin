from django.utils.text import slugify


def unique_post_slug(title: str, *, exclude_pk=None, model=None) -> str:
    """Build a unique unicode slug from a post title."""
    from blog.models import Post

    model = model or Post
    base = slugify(title or "", allow_unicode=True) or "post"
    slug = base
    qs = model.objects.all()
    if exclude_pk:
        qs = qs.exclude(pk=exclude_pk)
    i = 2
    while qs.filter(slug=slug).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug
