# from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from rest_framework import status
from .models import MenuItem, Cart, Order, OrderItem
from .views import (
    ManagerView,
    DeliveryView,
    MenuItemsView,
    MenuItemsViewSet,
    CartItemsView,
    OrdersViewSet,
    OrdersView,
)
from decimal import Decimal


class ManagerViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Manager")
        self.user.groups.add(self.group)

    def test_get_managers(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/managers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    def test_create_manager(self):
        self.client.force_login(self.user)
        data = {"username": "newuser"}
        response = self.client.post("/api/managers/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_manager_not_authenticated(self):
        data = {"username": "newuser"}
        response = self.client.post("/api/managers/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeliveryViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Delivery crew")
        self.user.groups.add(self.group)

    def test_get_delivery_crew(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/delivery-crew/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    def test_create_delivery_crew(self):
        self.client.force_login(self.user)
        data = {"username": "newuser"}
        response = self.client.post("/api/delivery-crew/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_create_delivery_crew_not_authenticated(self):
        data = {"username": "newuser"}
        response = self.client.post("/api/delivery-crew/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MenuItemsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Manager")
        self.user.groups.add(self.group)
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=Decimal("10.00")
        )

    def test_get_menu_items(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/menu-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    def test_create_menu_item(self):
        self.client.force_login(self.user)
        data = {"title": "New Item", "price": "12.00"}
        response = self.client.post("/api/menu-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuItem.objects.count(), 2)

    def test_create_menu_item_not_authenticated(self):
        data = {"title": "New Item", "price": "12.00"}
        response = self.client.post("/api/menu-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class MenuItemsViewSetTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Manager")
        self.user.groups.add(self.group)
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=Decimal("10.00")
        )

    def test_get_menu_item(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/menu-items/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Item") # type: ignore

    def test_update_menu_item(self):
        self.client.force_login(self.user)
        data = {"title": "Updated Item", "price": "12.00"}
        response = self.client.put("/api/menu-items/1/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MenuItem.objects.get(id=1).title, "Updated Item")

    def test_delete_menu_item(self):
        self.client.force_login(self.user)
        response = self.client.delete("/api/menu-items/1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(MenuItem.objects.count(), 0)

    def test_update_menu_item_not_authenticated(self):
        data = {"title": "Updated Item", "price": "12.00"}
        response = self.client.put("/api/menu-items/1/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_menu_item_not_authenticated(self):
        response = self.client.delete("/api/menu-items/1/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CartItemsViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=Decimal("10.00")
        )

    def test_get_cart_items(self):
        self.client.force_login(self.user)
        Cart.objects.create(
            user=self.user, menuitems=self.menu_item, quantity=1, price=Decimal("10.00")
        )
        response = self.client.get("/api/cart-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    def test_create_cart_item(self):
        self.client.force_login(self.user)
        data = {"menuitems": 1, "quantity": 1}
        response = self.client.post("/api/cart-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)

    def test_delete_cart_items(self):
        self.client.force_login(self.user)
        Cart.objects.create(
            user=self.user, menuitems=self.menu_item, quantity=1, price=Decimal("10.00")
        )
        response = self.client.delete("/api/cart-items/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cart.objects.count(), 0)

    def test_create_cart_item_not_authenticated(self):
        data = {"menuitems": 1, "quantity": 1}
        response = self.client.post("/api/cart-items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_cart_items_not_authenticated(self):
        response = self.client.delete("/api/cart-items/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrdersViewSetTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Manager")
        self.user.groups.add(self.group)
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=Decimal("10.00")
        )
        self.order = Order.objects.create(user=self.user)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            menuitem=self.menu_item,
            quantity=1,
            price=Decimal("10.00"),
        )

    def test_get_order(self):
        self.client.force_login(self.user)
        response = self.client.get("/api/orders/1/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # type: ignore

    def test_update_order(self):
        self.client.force_login(self.user)
        data = {"status": "shipped", "delivery_crew": 1}
        response = self.client.put("/api/orders/1/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=1).status, "shipped")

    # def test_delete_order(self):
    #     self.client.force_login(self.user)
    #     response = self.client.delete("/api/orders/1/")
    #     self.assertEqual (
    #         response.status_code,
    #         status.HTTP_200_OK,
    #     )
    #     self.assertEqual(Order.objects.count(), 0)

    def test_update_order_not_authenticated(self):
        data = {"status": "shipped", "delivery_crew": 1}
        response = self.client.put("/api/orders/1/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order_not_authenticated(self):
        response = self.client.delete("/api/orders/1/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrdersViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.group = Group.objects.create(name="Manager")
        self.user.groups.add(self.group)
        self.menu_item = MenuItem.objects.create(
            title="Test Item", price=Decimal("10.00")
        )
        self.order = Order.objects.create(user=self.user)
        self.order_item = OrderItem.objects.create(
            order=self.order,
            menuitem=self.menu_item,
            quantity=1,
            price=Decimal("10.00"),
        )

    # def test_get_orders(self):
    #     self.client.force_login(self.user)
    #     response = self.client.get("/api/orders/")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)

    # def test_create_order(self):
    #     self.client.force_login(self.user)
    #     data = {'menuitems': 1, 'quantity': 1}
    #     response = self.client.post('/api/orders/', data, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     self.assertEqual(Order.objects.count(), 2)

    def test_create_order_not_authenticated(self):
        data = {"menuitems": 1, "quantity": 1}
        response = self.client.post("/api/orders/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
