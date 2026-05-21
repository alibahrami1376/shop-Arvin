from django.shortcuts import render


def page_not_found(request, exception=None):
    return render(
        request,
        "errors/404.html",
        {
            "title": "صفحه پیدا نشد",
            "message": "آدرسی که وارد کرده‌اید وجود ندارد یا حذف شده است.",
        },
        status=404,
    )


def server_error(request):
    return render(
        request,
        "errors/500.html",
        {
            "title": "خطای سرور",
            "message": "مشکلی در پردازش درخواست پیش آمد. لطفاً چند لحظه بعد دوباره تلاش کنید.",
        },
        status=500,
    )


def permission_denied(request, exception=None):
    return render(
        request,
        "errors/403.html",
        {
            "title": "دسترسی مجاز نیست",
            "message": "شما اجازهٔ مشاهده یا انجام این عملیات را ندارید.",
        },
        status=403,
    )
