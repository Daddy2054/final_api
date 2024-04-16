from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework import generics
from .serializers import (
    CartSerializer,
    CategorySerializer,
    OrderItemSerializer,
    OrderSerializer,
    UserSerializer,
    MenuItemSerializer,
)
from .models import Cart, Category, MenuItem, Order, OrderItem
from decimal import Decimal
from datetime import datetime


@api_view(["POST", "DELETE"])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data["username"]
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name="Manager")
        if request.method == "POST":
            managers.user_set.add(user)  # type: ignore
        elif request.method == "DELETE":
            managers.user_set.remove(user)  # type: ignore
        return Response({"message": "ok"})
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


class ManagerView(generics.ListCreateAPIView, generics.DestroyAPIView):

    group = Group.objects.get(name="Manager")
    queryset = group.user_set.all()  # type: ignore
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        # if request.user.IsAdminUser or request.user.groups.filter(name="Manager").exists():

        # group = Group.objects.get(name="Manager")
        users = group.user_set.all()  # type: ignore
        serialized_users = UserSerializer(users, many=True)
        return Response(
            serialized_users.data,
            status=status.HTTP_200_OK,
        )

    # return Response(
    #     {"message": "You are not a Manager"},
    #     status=status.HTTP_403_FORBIDDEN,
    # )

    def create(self, request, *args, **kwargs):
        # if request.user.groups.filter(name="Manager").exists():
        username = request.data["username"]
        group = Group.objects.get(name="Manager")

        if username:
            user = get_object_or_404(User, username=username)
            group.user_set.add(user)  # type: ignore
            return Response(
                {"message": "ok"},
                status=status.HTTP_201_CREATED,
            )

    # return Response(
    #     {"message": "You are not a Manager"},
    #     status=status.HTTP_403_FORBIDDEN,
    # )


class DeliveryView(generics.ListCreateAPIView):

    group, _ = Group.objects.get_or_create(name="Delivery crew")
    # group = Group.objects.get(name="Delivery crew")
    queryset = group.user_set.all()  # type: ignore
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():

            group = Group.objects.get(name="Delivery crew")
            users = group.user_set.all()  # type: ignore
            serialized_users = UserSerializer(users, many=True)
            return Response(
                serialized_users.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "You are not a Manager"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def create(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Manager").exists():
            username = request.data["username"]
            group, _ = Group.objects.get_or_create(name="Delivery crew")

            # group = Group.objects.get(name="Delivery crew")

            if username:
                user = get_object_or_404(User, username=username)
                group.user_set.add(user)  # type: ignore
                return Response(
                    {"message": "ok"},
                    status=status.HTTP_201_CREATED,
                )
        return Response(
            {"message": "You are not a Manager"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def remove_from_group(request, pk, group):
    # if request.user.groups.filter(name="Manager").exists():
    user = get_object_or_404(User, pk=pk)
    role = Group.objects.get(name=group)
    role.user_set.remove(user)  # type: ignore
    return Response(
        {"message": "ok"},
        status=status.HTTP_200_OK,
    )


# else:
#     return Response(
#         {"message": "You are not a Manager"},
#         status=status.HTTP_403_FORBIDDEN,
#     )


class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        # if not request.user.has_perm("LittleLemonAPI.add_menuitem"):
        if not request.user.is_staff:
            return Response(
                {"message": "You are not a Manager"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all().order_by("id")
    serializer_class = MenuItemSerializer
    ordering_fields = [
        "price"
    ]  # http://127.0.0.1:8000/api/menu-items?page=1&ordering=price
    search_fields = [
        "title",
        "category__title",
    ]  # http://127.0.0.1:8000/api/menu-items?search=dessert
    filterset_fields = ["id", "price", "category__title", "title"]
    permission_classes = [IsAuthenticated]
    pagination_class = (
        PageNumberPagination  # http://127.0.0.1:8000/api/menu-items?page=2
    )

    # @permission_classes([IsAdminUser]) # type: ignore
    def create(self, request, *args, **kwargs):

        # if not request.user.has_perm("LittleLemonAPI.add_menuitem"):
        if not request.user.is_staff:
            return Response(
                {"message": "You are not a Manager"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().create(request, *args, **kwargs)


class MenuItemsViewSet(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ["price"]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if not request.user.has_perm("LittleLemonAPI.change_menuitem"):
            # if not request.user.is_staff:

            return Response(
                {"message": "You are not a Manager"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.has_perm("LittleLemonAPI.delete_menuitem"):
            # if not request.user.is_staff:
            return Response(
                {"message": "You are not a Manager"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class CartItemsView(generics.ListCreateAPIView, generics.DestroyAPIView):

    # serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

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
        try:
            menuitems_id = request.data.get("menuitem")
            menuitems = MenuItem.objects.get(id=menuitems_id)
        except MenuItem.DoesNotExist:
            return Response(
                {"message": "menuitem does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        unit_price = MenuItem.objects.get(id=menuitems_id).price
        quantity = request.data.get("quantity")
        if quantity is None:
            return Response(
                {"message": "quantity is required"},
                status=status.HTTP_400_BAD_REQUEST,
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
        cart.save()
        # return super().create(request, *args, **kwargs)
        return Response(status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        queryset = Cart.objects.filter(user=request.user.id)
        queryset.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersViewSet(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get("pk")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "This order does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if order.user == User.objects.get(id=request.user.id) is False:
            return Response(
                {"message": "This is not an order of current user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = OrderItem.objects.filter(order_id=order_id).select_related(
            "menuitem"
        )
        if queryset.count() == 0:
            return Response(
                {"message": "This order have no order items"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer_class = OrderItemSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer_class.data)

    # checked!
    def update(self, request, *args, **kwargs):
        order_id = kwargs.get("pk")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "This order does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user.groups.filter(name="Manager").exists():
            try:
                # order.status = request.data["status"]
                order.delivery_crew = User.objects.get(id=request.data["delivery_crew"])
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            order.save()
            return Response(status=status.HTTP_200_OK)
        if not request.user.groups.filter(name="Delivery crew").exists():
            return Response(
                {"message": "You are not a Delivery crew"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if order.delivery_crew == request.user.id is False:
            return Response(
                {"message": "This order is not assigned to current user"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            order.status = request.data["status"]
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        order.save()
        return Response(status=status.HTTP_200_OK)

    # checked!
    def destroy(self, request, *args, **kwargs):
        order_id = kwargs.get("pk")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"message": "This order does not exist"},
                404,
            )
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                {"message": "You are not a Manager"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = PageNumberPagination

    def get(self, request, *args, **kwargs):
        # searching
        search = request.query_params.get("search")
        # filtering
        to_price = request.query_params.get("to_price")
        from_price = request.query_params.get("from_price")
        to_date = request.query_params.get("to_date")
        from_date = request.query_params.get("from_date")
        status = request.query_params.get("status")
        delivery_crew = request.query_params.get("delivery_crew")
        # ordering
        ordering = request.query_params.get("ordering")
        # Pagination
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)

        queryset = (
            OrderItem.objects.all().order_by("-order__date").select_related("menuitem")
        )
        # queryset = OrderItem.objects.all().select_related("menuitem")
        if search:
            queryset = queryset.filter(menuitem__title__icontains=search)
        if to_price:
            queryset = queryset.filter(price__lte=to_price)
        if from_price:
            queryset = queryset.filter(price__gte=from_price)
        if to_date:
            queryset = queryset.filter(order__date__lte=to_date)
        if from_date:
            queryset = queryset.filter(order__date__gte=from_date)
        if status:
            queryset = queryset.filter(order__status=status)
        if delivery_crew:
            queryset = queryset.filter(
                order__delivery_crew=User.objects.get(id=request.data["delivery_crew"])
            )
        if ordering:
            ordering_fields = ordering.split(",")
            queryset = queryset.order_by(*ordering_fields)

        if request.user.groups.filter(name="Manager").exists():
            user_group = "Manager"
        elif request.user.groups.filter(name="Delivery crew").exists():
            user_group = "Delivery crew"
        else:
            user_group = "Customer"

        match user_group:
            case "Manager":
                pass
            case "Delivery crew":
                queryset = queryset.filter(
                    order__delivery_crew=User.objects.get(id=request.user.id)
                ).select_related("menuitem")
            case "Customer":

                queryset = queryset.filter(order__user=request.user.id).select_related(
                    "menuitem"
                )
        if queryset is None or queryset.count() == 0:
            return Response(
                {"message": "Such order do not exists"},
                404,
            )
        # Pagination object inializing
        paginator = Paginator(queryset, per_page=perpage)
        try:
            queryset = paginator.page(number=page)
        except EmptyPage:
            queryset = []
        serializer_class = OrderItemSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(
            serializer_class.data,
            200,
        )

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
        # date = args.ge/t('date')
        if request.query_params["date"] is not None:
            date_str = request.query_params["date"]
            order.date = datetime.strptime(date_str, "%Y-%m-%d").date()
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
