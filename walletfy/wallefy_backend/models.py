import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from .Enums import *


# User Model with Custom Fields
class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                               editable=False)
    username = models.CharField(max_length=50, null=True, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=50)

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

    def __str__(self):
        return self.username


# UserRole Model
class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=RoleChoices.list_of_values())

    def __str__(self):
        return f"{self.user} - {self.role}"


# UserProfile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10,
                              choices=GenderChoices.list_of_values())

    def __str__(self):
        return f"{self.user}'s Profile"


# UserPreferenceDetails Model for storing salary and preferences
class UserPreferenceDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(auto_now=True)
    preference = models.CharField(max_length=150,
                                  choices=PreferenceChoices.list_of_values())
    location = models.CharField(max_length=150,
                                choices=AreaEnum.list_of_values())
    city = models.CharField(max_length=150,
                            choices=LocationChoices.list_of_values(),
                            default='hyderabad')
    account_balance = models.DecimalField(max_digits=10, decimal_places=2,
                                          default=0.00)

    def __str__(self):
        return f"{self.user} - {self.location}"


# Location Model
class Location(models.Model):
    city = models.CharField(max_length=150,
                            choices=LocationChoices.list_of_values(),
                            default="Hyderabad")
    area = models.CharField(max_length=50, choices=AreaEnum.list_of_values(),
                            unique=True)

    def __str__(self):
        return self.area


# LocationWiseCategoryDetails Model for storing expense percentages
class LocationWiseCategoryDetails(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    Rent_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Food_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Shopping_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Travelling_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Health_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Entertainment_percentage = models.DecimalField(max_digits=10,
                                                   decimal_places=2)
    Savings_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    Miscellaneous_percentage = models.DecimalField(max_digits=10,
                                                   decimal_places=2)

    gender = models.CharField(max_length=10,
                              choices=GenderChoices.list_of_values())
    preference = models.CharField(max_length=150,
                                  choices=PreferenceChoices.list_of_values())

    def __str__(self):
        return f"{self.location} - {self.preference}"


# UserExpense Model for tracking expenses
class UserExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50,
                                choices=Category.list_of_values())
    description = models.TextField(blank=True, null=True)
    expenses_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.category}: {self.expenses_amount}"
