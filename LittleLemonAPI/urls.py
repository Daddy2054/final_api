from django.urls import path
from . import views

urlpatterns = [
    # /api/users User registration: POST,username,password
    # /api/token/login token create: POST,username,password
    path(
        "groups/manager/users",
        views.managers,
    ),
    path(
        "groups/delivery-crew/users",
        views.DeliveryView.as_view(),
    ),
    path(
        "groups/delivery-crew/users/<int:pk>",
        views.remove_from_group,
        {"group": "Delivery crew"},
    ),
    path("categories", views.CategoriesView.as_view()),
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.MenuItemsViewSet.as_view()),
    path("cart/menu-items", views.CartItemsView.as_view()),
    path("orders", views.OrdersView.as_view()),
    path("orders/<int:pk>", views.OrdersViewSet.as_view()),
]
