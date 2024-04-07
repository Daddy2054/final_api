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
from .serializers import CartSerializer, OrderSerializer, UserSerializer
from .models import Cart, MenuItem, Order, OrderItem
from decimal import Decimal


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

    group, _ = Group.objects.get_or_create(name="Delivery crew")
    # group = Group.objects.get(name="Delivery crew")
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
            group, _ = Group.objects.get_or_create(name="Delivery crew")

            # group = Group.objects.get(name="Delivery crew")

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


class CartItemsView(generics.ListCreateAPIView, generics.DestroyAPIView):

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = Cart.objects.filter(user=request.user.id)
        serializer_class = CartSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer_class.data)

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        menuitems_id = request.data.get("menuitems")
        if menuitems_id is None:
            return Response(
                {"message": "menuitems is required"},
                status.HTTP_400_BAD_REQUEST,
            )
        menuitems = MenuItem.objects.get(id=menuitems_id)
        unit_price = MenuItem.objects.get(id=menuitems_id).price
        quantity = request.data.get("quantity")
        if quantity is None:
            return Response(
                {"message": "quantity is required"},
                status.HTTP_400_BAD_REQUEST,
            )
        # convert str to decimal
        quantity = Decimal(quantity)
        # calculate price
        price = unit_price * quantity
        # create cart item
        cart = Cart(
            user=user,
            # menuitem_id=menuitems_id,
            menuitems=menuitems,
            unit_price=unit_price,
            quantity=quantity,
            price=price,
        )
        #  cart.save()
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        queryset = Cart.objects.filter(user=request.user.id)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersViewSet(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


class OrdersView(generics.ListCreateAPIView):
    # serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
# TODO: find a query to return orders with related items ????
    # Returns all orders with related order items created by this user
    def get(self, request, *args, **kwargs):
        queryset = (
            Order.objects.filter(user=request.user.id).join(OrderItem).all())
        serializer_class = OrderSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer_class.data)

    # Creates a new order item for the current user.
    # Gets current cart items from the cart endpoints
    # and adds those items to the order items table.
    # Then deletes all items from the cart for this user.
    def create(self, request, *args, **kwargs):
        # get cart items
        user = User.objects.get(id=request.user.id)
        cart_items = Cart.objects.filter(user=request.user.id)

        # create order
        order = Order(user=user)
        order.save()

        # create order items
        order_total = Decimal("0.00")
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                menuitem=cart_item.menuitems,
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
                price=cart_item.price,
            )

            # add cart_item.price to total_price
            order_total += order_item.price
            order_item.save()
        # update order total
        order.total = order_total
        order.save()

        # delete cart items
        cart_items.delete()

        return Response(status=status.HTTP_201_CREATED)
