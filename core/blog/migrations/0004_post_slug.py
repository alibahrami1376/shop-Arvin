from django.db import migrations, models
from django.utils.text import slugify


def populate_post_slugs(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    for post in Post.objects.all().order_by("id"):
        base = slugify(post.title or "", allow_unicode=True) or f"post-{post.pk}"
        slug = base
        i = 2
        while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        post.slug = slug
        post.save(update_fields=["slug"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0003_add_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="slug",
            field=models.SlugField(
                allow_unicode=True,
                blank=True,
                default="",
                max_length=255,
                verbose_name="اسلاگ",
            ),
        ),
        migrations.RunPython(populate_post_slugs, noop_reverse),
        # AlterField(unique=True) on SlugField emits duplicate _like indexes on Postgres.
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=[
                        'ALTER TABLE "blog_post" ADD CONSTRAINT "blog_post_slug_uniq" UNIQUE ("slug");',
                        'CREATE INDEX "blog_post_slug_like" ON "blog_post" ("slug" varchar_pattern_ops);',
                    ],
                    reverse_sql=[
                        'DROP INDEX IF EXISTS "blog_post_slug_like";',
                        'ALTER TABLE "blog_post" DROP CONSTRAINT IF EXISTS "blog_post_slug_uniq";',
                    ],
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="post",
                    name="slug",
                    field=models.SlugField(
                        allow_unicode=True,
                        max_length=255,
                        unique=True,
                        verbose_name="اسلاگ",
                    ),
                ),
            ],
        ),
    ]
