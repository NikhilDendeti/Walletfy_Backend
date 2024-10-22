"""
URL configuration for walletfy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from wallefy_backend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account-balance/', update_user_expense, name='account_balance'),
    path('get-user-details/', get_user_details, name='get_user_details'),
    path('get-user-five-transaction/', get_last_five_transactions,
         name='get_user_last_five_transactions'),
    path('get-user-all-transaction/', get_user_all_transactions,
         name='get_user_all_transactions'),
    path('get-user-financial-transaction/',
         get_user_pie_chart_financial_transactions,
         name='get_user_financial_transactions'),
    path('get-transaction-filters/', get_transaction_filters,
         name='get_transaction_filters'),
    path('delete-user-expense/', delete_user_expense,
         name='delete_user_expense'),
    path('get-transaction-details/', get_transaction_details,
         name='get_transaction_details'),
    path('get-user-expense-suggestions/', get_user_expense_suggestions,
         name='get_user_expense_suggestions'),
    path('get-user-expenses-comparison-at-eom',
         get_user_expenses_comparison_at_eom,
         name='get_user_expenses_comparison_at_eom'),
]
