from django.conf import settings
from django.db import migrations, models
from django.contrib.auth.models import Group, User


def create_default_group(apps, schema_editor):
    user1 = User.objects.create_user("john2", "lennon@thebeatles.com", "johnpassword")
    user2 = User.objects.create_user("john3", "lennon@thebeatles.com", "johnpassword")
    user3 = User.objects.create_user("john4", "lennon@thebeatles.com", "johnpassword")
    user4 = User.objects.create_user("john5", "lennon@thebeatles.com", "johnpassword")


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_default_group),
    ]
