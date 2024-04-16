from django.db import models
from django.contrib.auth.models import User, Group, Permission

# Create your models here.


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255, db_index=True)

    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    title = models.CharField(
        max_length=255,
        db_index=True,
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_index=True,
    )
    featured = models.BooleanField(
        db_index=True,
        default=False,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        default=1, # type: ignore
    ) # type: ignore

    def set_perms(): # type: ignore
        group, _ = Group.objects.get_or_create(name="Manager")
        group.permissions.add(Permission.objects.get(codename="add_menuitem"))
        group.permissions.add(Permission.objects.get(codename="change_menuitem"))
        group.permissions.add(Permission.objects.get(codename="delete_menuitem"))
        group.permissions.add(Permission.objects.get(codename="view_menuitem"))
        group.save()


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menuitems = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    class Meta:
        unique_together = (
            "menuitems",
            "quantity",
            "unit_price",
            "price",
            "user",
        )


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="delivery_crew",
        null=True,
    )
    status = models.BooleanField(
        db_index=True,
        default=False,
    )
    total = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00, # type: ignore
    ) # type: ignore
    date = models.DateField(
        db_index=True,
        # auto_now_add=True,
    )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.SmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = (
            "order",
            "menuitem",
        )
