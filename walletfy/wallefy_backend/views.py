from decimal import Decimal, InvalidOperation
from unicodedata import decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import User, UserExpense, UserPreferenceDetails, UserProfile, \
    Location, LocationWiseCategoryDetails


@api_view(['GET'])
def get_user_details(request):
    user_id = request.user.user_id
    user = get_object_or_404(User, user_id=user_id)

    user_preferential_instance, created = UserPreferenceDetails.objects.get_or_create(
        user=user
    )

    current_month = timezone.now().month
    current_year = timezone.now().year

    total_expense = UserExpense.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0.00

    round_total_expense = round(total_expense, 2)

    # Use string formatting to ensure 0.00 format
    data = {
        'user_name': user.username,
        'Income': f"{user_preferential_instance.salary:.2f}",
        'Account_Balance': f"{user_preferential_instance.account_balance:.2f}",
        'Expense': f"{round_total_expense:.2f}"
    }

    return JsonResponse(data, status=status.HTTP_200_OK)


@api_view(['POST'])
def store_user_data(request):
    user_id = request.user.user_id
    user = get_object_or_404(User, user_id=user_id)

    salary = request.data.get('salary')
    if not salary:
        return JsonResponse({'message': 'Salary is required.'}, status=400)

    spending_preference = request.data.get('user_preference')
    if not spending_preference:
        return JsonResponse({'message': 'Spending preference is required.'},
                            status=400)

    location = request.data.get('location')
    if not location:
        return JsonResponse({'message': 'Location is required.'}, status=400)

    user_preference, created = UserPreferenceDetails.objects.get_or_create(
        user=user,
        defaults={
            'salary': salary,
            'preference': spending_preference,
            'location': location,
            'account_balance': Decimal(salary)
        }
    )

    if not created:
        user_preference.salary = Decimal(salary)
        user_preference.preference = spending_preference
        user_preference.location = location
        user_preference.account_balance = Decimal(salary)
        user_preference.save()

    return JsonResponse({
        'message': 'User data stored successfully.',
        'Income': f"{user_preference.salary:.2f}",
        'Account_Balance': f"{user_preference.account_balance:.2f}"
    }, status=200)


@api_view(['POST'])
def update_user_expense(request):
    user_id = request.user.user_id

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    category = request.data.get('category')
    expense_amount = request.data.get('expense_amount')
    description = request.data.get('description')

    if expense_amount is None:
        return JsonResponse(
            {'message': 'Expense amount and category are required.'},
            status=400)

    try:
        expense_amount = Decimal(expense_amount)
    except (InvalidOperation, TypeError):
        return JsonResponse({'message': 'Invalid expense amount format.'},
                            status=400)

    if expense_amount <= 0:
        return JsonResponse({'message': 'Expense amount must be positive.'},
                            status=400)

    try:
        user_preferences = UserPreferenceDetails.objects.get(user=user)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User preference details not found.'},
                            status=404)

    if user_preferences.account_balance < expense_amount:
        return JsonResponse({'message': 'Insufficient balance'}, status=400)

    user_preferences.account_balance -= expense_amount
    user_preferences.save()

    user_expense = UserExpense.objects.create(
        user=user,
        category=category,
        expenses_amount=expense_amount,
        description=description
    )

    current_month = timezone.now().month
    current_year = timezone.now().year
    total_expense = UserExpense.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0
    total_expense = round(total_expense, 2)

    return JsonResponse({
        'username': user.username,
        'account_balance': str(user_preferences.account_balance),
        'income': str(user_preferences.salary),
        'total_expense': str(total_expense),
        'description': user_expense.description
    }, status=200)


@api_view(['POST'])
def get_last_five_transactions(request):
    user_id = request.user.user_id

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    last_three_transactions = UserExpense.objects.filter(user=user).order_by(
        '-date')[:5]

    transactions_by_date = {}

    for transaction in last_three_transactions:
        transaction_date = transaction.date.strftime(
            '%Y-%m-%d')
        if transaction_date not in transactions_by_date:
            transactions_by_date[transaction_date] = []

        transactions_by_date[transaction_date].append({
            'category': transaction.category,
            'amount': str(transaction.expenses_amount),
            'time': transaction.date.strftime('%I:%M %p'),
            'description': transaction.description,
            'transaction_id': transaction.id
        })

    response_data = []
    for date, transaction_list in transactions_by_date.items():
        response_data.append({
            'date': date,
            'transactions': transaction_list
        })

    return JsonResponse({'transactions_by_date': response_data}, status=200)


@api_view(['POST'])
def get_last_all_transactions(request):
    user_id = request.user.user_id

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    transactions = UserExpense.objects.filter(user=user).order_by('-date')

    transactions_by_date = {}

    for transaction in transactions:
        transaction_date = transaction.date.strftime(
            '%Y-%m-%d')
        if transaction_date not in transactions_by_date:
            transactions_by_date[transaction_date] = []

        transactions_by_date[transaction_date].append({
            'category': transaction.category,
            'amount': str(transaction.expenses_amount),
            'time': transaction.date.strftime('%I:%M %p'),
            'description': transaction.description,
            'transaction_id': transaction.id
        })

    response_data = []
    for date, transaction_list in transactions_by_date.items():
        response_data.append({
            'date': date,
            'transactions': transaction_list
        })

    return JsonResponse({'transactions_by_date': response_data}, status=200)


@api_view(['POST'])
def get_transaction_filters(request):
    user_id = request.user.user_id

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    highest_price_filter = request.data.get('Highest')
    lowest_price_filter = request.data.get('Lowest')
    oldest_transaction_filter = request.data.get('Oldest')
    category_filter = request.data.get('Categories')

    transactions = UserExpense.objects.filter(user=user)

    if category_filter:
        transactions = transactions.filter(category=category_filter)

    if highest_price_filter:
        transactions = transactions.order_by('-expenses_amount')
    elif lowest_price_filter:
        transactions = transactions.order_by('expenses_amount')
    elif oldest_transaction_filter:
        transactions = transactions.order_by('date')
    else:
        transactions = transactions.order_by('-date')

    transactions_by_date = {}

    for transaction in transactions:
        transaction_date = transaction.date.strftime('%Y-%m-%d')
        if transaction_date not in transactions_by_date:
            transactions_by_date[transaction_date] = []

        transactions_by_date[transaction_date].append({
            'category': transaction.category,
            'amount': str(transaction.expenses_amount),
            'time': transaction.date.strftime('%I:%M %p'),
            'description': transaction.description,
            'transaction_id': transaction.id
        })

    response_data = []
    for date, transaction_list in transactions_by_date.items():
        response_data.append({
            'date': date,
            'transactions': transaction_list
        })

    return JsonResponse({'transactions_by_date': response_data}, status=200)


@api_view(['POST'])
def get_user_pie_chart_financial_transactions(request):
    user_id = request.user.user_id
    month = request.data.get('month')

    if not month:
        return JsonResponse({'message': 'Month is required.'}, status=400)

    try:
        month = int(month)
        if month < 1 or month > 12:
            return JsonResponse({'message': 'Invalid month.'}, status=400)
    except ValueError:
        return JsonResponse({'message': 'Month must be a number.'}, status=400)

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    user_expenses_history = UserExpense.objects.filter(
        user=user,
        date__month=month
    ).values('category').annotate(total=Sum('expenses_amount'))

    total_expense = UserExpense.objects.filter(
        user=user, date__month=month
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0

    return JsonResponse({
        'user_expenses_history': list(user_expenses_history),
        'total_expense': round(total_expense, 2)
    }, status=200)


@api_view(['GET'])
def get_user_income_pie_chart(request):
    user_id = request.user.user_id
    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    user_income = UserPreferenceDetails.objects.get(user=user).salary
    return JsonResponse({'user_income': user_income}, status=200)


@api_view(['POST'])
def delete_user_expense(request):
    user_id = request.user.user_id
    transaction_id = request.data.get('expense_id')

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    try:
        expense = UserExpense.objects.get(id=transaction_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Expense not found.'}, status=404)
    expense.delete()
    expense_amount = expense.expenses_amount
    update_account_balance = UserPreferenceDetails.objects.get(user=user)
    update_account_balance.account_balance += expense_amount
    update_account_balance.save()

    return JsonResponse({'message': 'Expense deleted successfully.'},
                        status=200)


@api_view(['POST'])
def get_transaction_details(request):
    transaction_id = request.data.get('transaction_id')
    try:
        transaction = UserExpense.objects.get(id=transaction_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Transaction not found.'}, status=404)

    return JsonResponse({
        'category': transaction.category,
        'amount': str(transaction.expenses_amount),
        'date': transaction.date.strftime('%Y-%m-%d'),
        'time': transaction.date.strftime('%I:%M %p'),
        'description': transaction.description,
        'transaction_id': transaction.id
    }, status=200)


@api_view(['POST'])
def get_user_expense_suggestions(request):
    try:

        user_id = request.user.user_id
        if not user_id:
            return Response({"error": "User ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, user_id=user_id)

        user_profile = get_object_or_404(UserProfile, user=user)

        user_preferences = UserPreferenceDetails.objects.get(
            user=user)
        salary = user_preferences.salary

        user_location_area = user_preferences.location
        print(f"User's location (area): {user_location_area}")

        location = get_object_or_404(Location, area=user_location_area)

        location_details = get_object_or_404(LocationWiseCategoryDetails,
                                             location=location,
                                             gender=user_profile.gender,
                                             preference=user_preferences.preference)

        base_amount = Decimal(salary)

        rent_amount = round(
            base_amount * (location_details.Rent_percentage / 100), 2)
        food_amount = round(
            base_amount * (location_details.Food_percentage / 100), 2)
        shopping_amount = round(
            base_amount * (location_details.Shopping_percentage / 100), 2)
        travelling_amount = round(
            base_amount * (location_details.Travelling_percentage / 100), 2)
        health_amount = round(
            base_amount * (location_details.Health_percentage / 100), 2)
        entertainment_amount = round(
            base_amount * (location_details.Entertainment_percentage / 100), 2)
        savings_amount = round(
            base_amount * (location_details.Savings_percentage / 100), 2)
        miscellaneous_amount = round(
            base_amount * (location_details.Miscellaneous_percentage / 100), 2)

        data = {
            'salary': base_amount,
            'rent': rent_amount,
            'food': food_amount,
            'shopping': shopping_amount,
            'travelling': travelling_amount,
            'health': health_amount,
            'entertainment': entertainment_amount,
            'savings': savings_amount,
            'miscellaneous': miscellaneous_amount,
            'gender': user_profile.gender,
            'preference': user_preferences.preference,
            'city': "Hyderabad",
            'location': user_preferences.location,
            'user_id': user_id
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_user_expenses_comparison_at_eom(request):
    user_id = request.user.user_id
    month = request.data.get('month')

    if not month:
        return JsonResponse({'message': 'Month is required.'}, status=400)

    try:
        month = int(month)
        if month < 1 or month > 12:
            return JsonResponse({'message': 'Invalid month.'}, status=400)
    except ValueError:
        return JsonResponse({'message': 'Month must be a number.'}, status=400)

    # Try to get the user
    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    try:
        user_profile = UserProfile.objects.get(user=user)
        user_preference = UserPreferenceDetails.objects.get(user=user)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User preferences not found.'},
                            status=404)

    try:
        location_details = LocationWiseCategoryDetails.objects.get(
            location__area=user_preference.location,
            preference=user_preference.preference,
            gender=user_profile.gender
        )
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Location details not found.'},
                            status=404)

    base_amount = user_preference.salary
    recommended_amounts = {
        'Rent': round(base_amount * (location_details.Rent_percentage / 100),
                      2),
        'Food': round(base_amount * (location_details.Food_percentage / 100),
                      2),
        'Shopping': round(
            base_amount * (location_details.Shopping_percentage / 100), 2),
        'Travelling': round(
            base_amount * (location_details.Travelling_percentage / 100), 2),
        'Health': round(
            base_amount * (location_details.Health_percentage / 100), 2),
        'Entertainment': round(
            base_amount * (location_details.Entertainment_percentage / 100), 2),
        'Savings': round(
            base_amount * (location_details.Savings_percentage / 100), 2),
        'Miscellaneous': round(
            base_amount * (location_details.Miscellaneous_percentage / 100), 2),
    }

    print(f"Recommended amounts: {recommended_amounts}")

    user_expenses_history = UserExpense.objects.filter(
        user=user,
        date__month=month
    ).values('category').annotate(total=Sum('expenses_amount'))

    total_expense = UserExpense.objects.filter(
        user=user, date__month=month
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0

    print(f"User's actual expenses: {list(user_expenses_history)}")

    expenses_with_recommended = []
    for expense in user_expenses_history:
        category = expense['category']
        actual_amount = round(expense['total'],
                              2)
        recommended_amount = recommended_amounts.get(category,
                                                     0)

        print(
            f"Category: {category}, Actual: {actual_amount}, Recommended: {recommended_amount}")

        expenses_with_recommended.append({
            'category': category,
            'actual_amount': actual_amount,
            'recommended_amount': recommended_amount
        })

    return JsonResponse({
        'user_expenses_history': expenses_with_recommended,
        'total_expense': round(total_expense, 2),

        'recommended_amounts': recommended_amounts

    }, status=200)
