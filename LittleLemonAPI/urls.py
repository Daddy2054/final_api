from django.urls import path
from . import views

urlpatterns = [
    path("groups/manager/users", views.assign2group, {"group": "Manager"}),
    path(
        "groups/manager/users/<int:pk>", views.remove_from_group, {"group": "Manager"}
    ),
    path("groups/delivery-crew/users", views.assign2group, {"group": "Delivery crew"}),
    path(
        "groups/delivery-crew/users/<int:pk>",
        views.remove_from_group,
        {"group": "Delivery crew"},
    ),
    path("menu-items/", views.menu_items),
    path("menu-items/<int:pk>", views.MenuItemsViewSet.as_view({"get": "retrieve"})),
]
