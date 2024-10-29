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
from django.urls import path, include

from wallefy_backend.user_views import get_login_interactor_view, \
    get_signup_interactor_view, get_update_password_view, \
    update_user_profile_view, get_user_profile_api_view, \
    refresh_access_token_view, user_logout_view
from wallefy_backend.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user_account/login/v1', get_login_interactor_view),
    path('user_account/signup/v1', get_signup_interactor_view),
    path('user_account/update_password/v1', get_update_password_view),
    path('get/user_profile/v1', get_user_profile_api_view),
    path('update/user_profile/v1', update_user_profile_view),
    path("get/refresh_access_token/v1", refresh_access_token_view),
    path("user_account/logout/v1", user_logout_view),
    path('get_user_details/', get_user_details, name='get_user_details'),
    path('update_user_expense', update_user_expense,
         name='update_user_expense'),
    path('feedback/', get_feedback),
    path('store_user_data/', store_user_data),
    path('get_last_five_transactions/', get_last_five_transactions),
    path('get_last_all_transactions/', get_last_all_transactions),
    path('get_transaction_filters/', get_transaction_filters),
    path('get_user_pie_chart_financial_transactions/',
         get_user_pie_chart_financial_transactions),
    path('get_user_income_pie_chart/', get_user_income_pie_chart),
    path('delete_user_expense/', delete_user_expense),
    path('get_transaction_details/', get_transaction_details),
    path('get_user_expense_suggestions/', get_user_expense_suggestions),
    path('get_user_expenses_comparison_at_eom/',
         get_user_expenses_comparison_at_eom),
    path('accounts/', include('allauth.urls')),

    path('generate-personalized-response/',
         generate_personalized_response,
         name='generate_personalized_response'),

]
