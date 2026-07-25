from django.db import models
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator


class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")


class ProductCategoryModel(models.Model):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته والد",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True, unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "دسته‌بندی محصول"
        verbose_name_plural = "دسته‌بندی‌های محصول"

    def __str__(self):
        return self.title

    def get_self_and_descendant_ids(self):
        if not self.pk:
            return []
        ids = [self.pk]
        for child in self.children.all():
            ids.extend(child.get_self_and_descendant_ids())
        return ids

    def get_indented_title(self, prefix="— "):
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        if depth == 0:
            return self.title
        return f"{prefix * depth}{self.title}"

    @classmethod
    def get_tree_ordered(cls):
        result = []

        def walk(parent=None):
            for category in cls.objects.filter(parent=parent).order_by("title"):
                result.append(category)
                walk(category)

        walk()
        return result


class ProductTagModel(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(allow_unicode=True, unique=True, verbose_name="اسلاگ")

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "تگ محصول"
        verbose_name_plural = "تگ‌های محصول"

    def __str__(self):
        return self.title


# Create your models here.
class ProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    category = models.ManyToManyField(ProductCategoryModel)
    tags = models.ManyToManyField(ProductTagModel, blank=True, related_name="products", verbose_name="تگ‌ها")
    title = models.CharField(max_length=255)
    slug = models.SlugField(allow_unicode=True,unique=True)
    image = models.ImageField(default="/default/product-image.png",upload_to="product/img/")
    description = models.TextField()
    brief_description = models.TextField(null=True,blank=True)
    
    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    price = models.DecimalField(default=0,max_digits=10,decimal_places=0)
    discount_percent = models.IntegerField(default=0,validators = [MinValueValidator(0),MaxValueValidator(100)])
    
    avg_rate = models.FloatField(default=0.0)
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
    def __str__(self):
        return self.title
    
    def get_price(self):        
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)
    
    def is_discounted(self):
        return self.discount_percent != 0
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("shop:product-detail", kwargs={"slug": self.slug})
    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE,related_name="product_images")
    file = models.ImageField(upload_to="product/extra-img/")
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_date"]
        
class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title