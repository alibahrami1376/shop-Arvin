from django.urls import path,include
from .. import views

urlpatterns = [
    path("order/list/",views.AdminOrderListView.as_view(),name="order-list"),
    path("order/<int:pk>/detail/",views.AdminOrderDetailView.as_view(),name="order-detail"),
    path(
        "order/<int:pk>/status/",
        views.AdminOrderChangeStatusView.as_view(),
        name="order-change-status",
    ),
    path(
        "order/<int:pk>/payment-status/",
        views.AdminOrderPaymentStatusView.as_view(),
        name="order-change-payment-status",
    ),
    path(
        "order/<int:pk>/invoice/",
        views.AdminOrderInvoiceView.as_view(),
        name="order-invoice",
    ),
]

