from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

from .Enums import *

from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    groups = models.ManyToManyField(
        Group,
        related_name='wallefy_backend_user_groups',  # Custom related name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='wallefy_backend_user_permissions',  # Custom related name
        blank=True
    )


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.list_of_values()
    )

    role = models.CharField(
        max_length=10,
        choices=RoleChoices.list_of_values(),
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"


class UserPreferenceDetails(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField(auto_now=True)
    preference = models.CharField(max_length=150, choices=PreferenceChoices.list_of_values())
    location = models.CharField(max_length=150, choices=AreaEnum.list_of_values())
    city = models.CharField(max_length=150, choices=LocationChoices.list_of_values(),
                            default='hyderabad')


class Location(models.Model):
    city_name = models.CharField(
        max_length=50,
        choices=AreaEnum.list_of_values(),
        unique=True
    )

    def __str__(self):
        return self.get_name_display()





# this is configration table we need to run the script to add the data
class UserLocationWisePreferences(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    high_percentage = models.FloatField(null=True, blank=True)
    medium_percentage = models.FloatField(null=True, blank=True)
    low_percentage = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=Category.list_of_values())

    class Meta:
        unique_together = ('location', 'category',)

    def __str__(self):
        return f"{self.location.name} - {self.get_category_display()} "


class UserExpense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=Category.list_of_values())
    description = models.TextField(blank=True, null=True)
    expenses_amount = models.DecimalField(max_digits=10, decimal_places=2)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    user_preference = models.ForeignKey(UserPreferenceDetails, on_delete=models.CASCADE)
    total_expenses_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.category}: {self.expenses_amount}"

    class Meta:
        ordering = ['-date']
