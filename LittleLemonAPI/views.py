from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from django.core.paginator import Paginator, EmptyPage
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


# Create your views here.
@api_view(["POST", "DELETE"])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == "POST":
            managers.user_set.add(user)
        elif request.method == "DELETE":
            managers.user_set.remove(user)
        return Response({"message": "ok"})
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
class MenuItemsViewSet(viewsets.ModelViewSet):
    #  throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price"]
    # ordering_fields = ["price", "inventory"]
    # search_fields=['title']
    search_fields = ["title", "category__title"]

    # def get_throttles(self):
    #     if self.action == "create":
    #         throttle_classes = [UserRateThrottle]
    #     else:
    #         throttle_classes = []
    #     return [throttle() for throttle in throttle_classes]

# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ["price"]
#     # ordering_fields = ["price", "inventory"]

#     # filteset_fields = ["price", "inventory"]
#     # search_fields = ["title", "category__title"]
#     # search_fields=['category']
#     def get_queryset(self):
#         queryset = super().get_queryset()


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all().order_by("id")
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")

        # Pagination
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)

        if search:
            items = items.filter(title__icontains=search)

        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        # Pagination object inializing
        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []

        serialized_item = MenuItemSerializer(
            items,
            many=True,
            context={"request": request},
        )
        return Response(serialized_item.data, status.HTTP_200_OK)
    else:
        if request.user.groups.filter(name="Manager" ).exists():
            serialized_item = MenuItemSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            if request.method == "POST":
                serialized_item.save()
                return Response(serialized_item.data, status.HTTP_201_CREATED)
            if request.method == "PUT" or request.method == "PATCH":
                serialized_item.update()
                return Response(serialized_item.data, status.HTTP_200_OK)
            if request.method == "DELETE":
                serialized_item.instance.remove()
                return Response(serialized_item.data, status.HTTP_200_OK)
        else:
            return Response({"message": "You are not a Manager"}, status.HTTP_403_FORBIDDEN)
