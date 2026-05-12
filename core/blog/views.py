
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from blog.models import Post, Category
from django.db.models import Q


def blog_home(request, cat_name=None):
    """
    نمایش لیست پست‌های بلاگ با امکان فیلتر بر اساس دسته‌بندی
    """
    posts = Post.objects.filter(status=True)
    
    if cat_name:
        category = get_object_or_404(Category, name=cat_name)
        posts = posts.filter(category=category)
    
    # Pagination
    paginator = Paginator(posts, 9)  # 9 پست در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'posts': page_obj,
        'category': cat_name,
        'categories': categories,
    }
    return render(request, 'blog/blog-home.html', context)


def blog_detail(request, post_id):
    """
    نمایش جزئیات یک پست بلاگ
    """
    post = get_object_or_404(Post, id=post_id, status=True)
    
    # افزایش تعداد بازدید
    post.counted_view += 1
    post.save()
    
    # پست‌های مرتبط (از همان دسته‌بندی)
    related_posts = Post.objects.filter(
        category__in=post.category.all(),
        status=True
    ).exclude(id=post.id).distinct()[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/blog-detail.html', context)


def blog_search(request):
    """
    جستجو در پست‌های بلاگ
    """
    query = request.GET.get('q', '')
    posts = Post.objects.filter(status=True)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'query': query,
    }
    return render(request, 'blog/blog-search.html', context)

