from django.urls import path
from . import views

urlpatterns = [
    path(
        "groups/manager/users",
        views.ManagerView.as_view(),
    ),
    path(
        "groups/manager/users/<int:pk>",
        views.remove_from_group,
        {"group": "Manager"},
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
    path("menu-items", views.MenuItemsView.as_view()),
    path("menu-items/<int:pk>", views.MenuItemsViewSet.as_view()),
]
