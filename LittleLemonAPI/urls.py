from django.urls import include, path
from . import views

urlpatterns = [
    path(
        "groups/manager/users",
        views.managers,
    ),
    path("menu-items/", views.menu_items),
    path("menu-items/<int:pk>", views.MenuItemsViewSet.as_view({"get": "retrieve"})),
]
