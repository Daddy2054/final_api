from decimal import Decimal
from rest_framework import serializers
from LittleLemonAPI.models import Category, MenuItem
from rest_framework.validators import UniqueTogetherValidator
import bleach
from django.contrib.auth.models import User
from .models import Order, OrderItem, Cart


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_staff",
            "is_active",
            "date_joined",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "title",
        ]


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    # To sanitize the title field v2
    def validate(self, attrs):
        attrs["title"] = bleach.clean(attrs["title"])
        if attrs["price"] < 2:
            raise serializers.ValidationError("Price should not be less than 2.0")
        # if(attrs['inventory']<0):
        #     raise serializers.ValidationError('Stock cannot be negative')
        return super().validate(attrs)

    class Meta:
        model = MenuItem
        depth = 1
        fields = [
            "id",
            "title",
            "price",
            "category",
            "category_id",
        ]

        # UniqueTogetherValidator
        validators = [
            UniqueTogetherValidator(
                queryset=MenuItem.objects.all(), fields=["title", "category_id"]
            )
        ]


class CartMenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem
        depth = 1
        fields = [
            "id",
            "title",
            "category",
        ]


class CartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "menuitems",
            "quantity",
            "unit_price",
            "price",
        ]
