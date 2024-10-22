import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .Enums import *


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    groups = models.ManyToManyField(
        Group,
        related_name='wallefy_backend_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='wallefy_backend_user_permissions',
        blank=True
    )
    account_balance = models.DecimalField(max_digits=10, decimal_places=2,
                                          default=0.00)  # Added field for balance


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10,
                              choices=GenderChoices.list_of_values())
    role = models.CharField(max_length=10, choices=RoleChoices.list_of_values())

    def __str__(self):
        return f"{self.user}'s Profile"


class UserPreferenceDetails(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(auto_now=True)
    preference = models.CharField(max_length=150,
                                  choices=PreferenceChoices.list_of_values())
    location = models.CharField(max_length=150,
                                choices=AreaEnum.list_of_values())
    city = models.CharField(max_length=150,
                            choices=LocationChoices.list_of_values(),
                            default='hyderabad')


class Location(models.Model):
    City = models.CharField(max_length=150,
                            choices=LocationChoices.list_of_values(),
                            default="Hyderabad")
    area = models.CharField(max_length=50,
                            choices=AreaEnum.list_of_values(), unique=True)

    def __str__(self):
        return self.area


class LocationWiseCategoryDetails(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    Rent_percentage = models.FloatField(max_length=120)
    Food_percentage = models.FloatField(max_length=120)
    Shopping_percentage = models.FloatField(max_length=120)
    Travelling_percentage = models.FloatField(max_length=120)
    Health_percentage = models.FloatField(max_length=120)
    Entertainment_percentage = models.FloatField(max_length=120)
    Savings_percentage = models.FloatField(max_length=120)
    Miscellaneous_percentage = models.FloatField(max_length=120)

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.list_of_values(),
        # Use the static method from the imported class
    )

    preference = models.CharField(
        max_length=150,
        choices=PreferenceChoices.list_of_values(),
        # Use the static method from the imported class
    )

    def __str__(self):
        return f"{self.location} - {self.preference}"


class UserExpense(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    category = models.CharField(max_length=50,
                                choices=Category.list_of_values())
    description = models.TextField(blank=True, null=True)
    expenses_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.category}: {self.expenses_amount}"
