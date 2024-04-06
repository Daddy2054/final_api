from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User, Group
from rest_framework.decorators import permission_classes
from LittleLemonAPI.models import MenuItem
from LittleLemonAPI.serializers import MenuItemSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .models import MenuItem


class ManagerView(generics.ListCreateAPIView):

    group = Group.objects.get(name="Manager")
    queryset = group.user_set.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():

            group = Group.objects.get(name="Manager")
            users = group.user_set.all()
            serialized_users = UserSerializer(users, many=True)
            return Response(
                serialized_users.data,
                status.HTTP_200_OK,
            )
        return Response(
            {"message": "You are not a Manager"},
            status.HTTP_403_FORBIDDEN,
        )

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            username = request.data["username"]
            group = Group.objects.get(name="Manager")

            if username:
                user = get_object_or_404(User, username=username)
                group.user_set.add(user)
                return Response(
                    {"message": "ok"},
                    status.HTTP_201_CREATED,
                )
        return Response(
            {"message": "You are not a Manager"},
            status.HTTP_403_FORBIDDEN,
        )


class DeliveryView(generics.ListCreateAPIView):

    group = Group.objects.get(name="Delivery crew")
    queryset = group.user_set.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():

            group = Group.objects.get(name="Delivery crew")
            users = group.user_set.all()
            serialized_users = UserSerializer(users, many=True)
            return Response(
                serialized_users.data,
                status.HTTP_200_OK,
            )
        return Response(
            {"message": "You are not a Manager"},
            status.HTTP_403_FORBIDDEN,
        )

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            username = request.data["username"]
            group = Group.objects.get(name="Delivery crew")

            if username:
                user = get_object_or_404(User, username=username)
                group.user_set.add(user)
                return Response(
                    {"message": "ok"},
                    status.HTTP_201_CREATED,
                )
        return Response(
            {"message": "You are not a Manager"},
            status.HTTP_403_FORBIDDEN,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_group(request, pk, group):
    if request.user.groups.filter(name="Manager").exists():
        user = get_object_or_404(User, pk=pk)
        role = Group.objects.get(name=group)
        role.user_set.remove(user)
        return Response(
            {"message": "ok"},
            status.HTTP_200_OK,
        )
    else:
        return Response(
            {"message": "You are not a Manager"},
            status.HTTP_403_FORBIDDEN,
        )


class MenuItemsView(generics.ListCreateAPIView):

    queryset = MenuItem.objects.all().order_by("id")
    serializer_class = MenuItemSerializer
    ordering_fields = ["price"]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.has_perm("LittleLemonAPI.add_menuitem"):
            return Response(
                {"message": "You are not a Manager"},
                status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class MenuItemsViewSet(generics.RetrieveUpdateDestroyAPIView):

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price"]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not request.user.has_perm("LittleLemonAPI.change_menuitem"):

            return Response(
                {"message": "You are not a Manager"},
                status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_perm("LittleLemonAPI.delete_menuitem"):
            return Response(
                {"message": "You are not a Manager"},
                status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
