from decimal import Decimal, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes
from rest_framework.response import Response

from .Enums import TransactionType, Category
from .models import User, UserExpense, UserPreferenceDetails, UserProfile, \
    Location, LocationWiseCategoryDetails


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def get_user_expense_suggestions(request):
    try:

        user_id = request.data.get('user_id')
        salary = request.data.get('salary')

        if not salary:
            return Response({"error": "Salary is required."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({"error": "User ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        user_profile = get_object_or_404(UserProfile, user=user)

        user_preferences = UserPreferenceDetails.objects.get(
            user=user_profile)

        user_location_area = user_preferences.location
        print(f"User's location (area): {user_location_area}")

        location = get_object_or_404(Location, area=user_location_area)

        location_details = get_object_or_404(LocationWiseCategoryDetails,
                                             location=location,
                                             gender=user_profile.gender,
                                             preference=user_preferences.preference)

        base_amount = Decimal(salary)

        rent_amount = base_amount * (location_details.Rent_percentage / 100)
        food_amount = base_amount * (location_details.Food_percentage / 100)
        shopping_amount = base_amount * (
                location_details.Shopping_percentage / 100)
        travelling_amount = base_amount * (
                location_details.Travelling_percentage / 100)
        health_amount = base_amount * (location_details.Health_percentage / 100)
        entertainment_amount = base_amount * (
                location_details.Entertainment_percentage / 100)
        savings_amount = base_amount * (
                location_details.Savings_percentage / 100)
        miscellaneous_amount = base_amount * (
                location_details.Miscellaneous_percentage / 100)

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
            'location': "Hyderabad",
            'city': location.City,
            'user_id': user_id
        }

        return Response(data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def get_user_details(request):
    user_id = request.data.get('user')
    salary = request.data.get('salary')
    location = request.data.get('location')
    city = request.data.get('city')
    preference = request.data.get('preference')

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    user_profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'gender': 'Male',
            'role': 'Employee'
        }
    )

    UserPreferenceDetails.objects.create(
        user=user_profile,
        salary=salary,
        location=location,
        city=city,
        preference=preference
    )

    return JsonResponse({
        'username': user.username,
        'salary': salary,
        "Expenses": 0,
        'Income': salary
    })


@api_view(['POST'])
def update_user_expense(request):
    user_id = request.data.get('user')

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    category = request.data.get('category')
    expense_amount = request.data.get('expense_amount')
    description = request.data.get('description')

    if expense_amount is None:
        return JsonResponse({
            'message': 'Expense amount and type are required.'
        }, status=400)

    try:
        expense_amount = Decimal(expense_amount)
    except (InvalidOperation, TypeError):
        return JsonResponse({'message': 'Invalid expense amount format.'},
                            status=400)

    if expense_amount <= 0:
        return JsonResponse({
            'message': 'Expense amount must be positive.'
        }, status=400)

    current_month = timezone.now().month
    current_year = timezone.now().year

    if user.account_balance < expense_amount:
        return JsonResponse({
            'message': 'Insufficient balance'
        }, status=400)

    user.account_balance -= expense_amount
    user.save()

    user_expense = UserExpense.objects.create(
        user=user,
        category=category,
        expenses_amount=expense_amount,
        description=description
    )

    user_profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'gender': 'Male',
            'role': 'Employee'
        }
    )

    try:
        income_user = UserPreferenceDetails.objects.get(user=user_profile)
        salary = income_user.salary
    except ObjectDoesNotExist:
        return JsonResponse({
            'message': 'User preference details not found.'
        }, status=404)

    total_expense = UserExpense.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    ).annotate(total=Sum('expenses_amount')).values_list('total', flat=True)
    total_expense = sum(total_expense)

    return JsonResponse({
        'username': user.username,
        'account_balance': str(user.account_balance),
        'income_salary': str(salary),
        'total_expense': str(total_expense),
        'description': user_expense.description
    }, status=200)


@api_view(['POST'])
def get_last_five_transactions(request):
    user_id = request.data.get('user')
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    last_three_transactions = UserExpense.objects.filter(user=user).order_by(
        '-date')[:5]

    transactions_data = []
    for transaction in last_three_transactions:
        transactions_data.append({
            'category': transaction.category,
            'amount': str(transaction.expenses_amount),
            'date': transaction.date.strftime('%Y-%m-%d'),
            'time': transaction.date.strftime('%I:%M %p'),
            'description': transaction.description,
            'transaction_id': transaction.id
        })

    return JsonResponse({'transactions': transactions_data}, status=200)


@api_view(['POST'])
def get_user_all_transactions(request):
    user_id = request.data.get('user')
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    all_transactions = UserExpense.objects.filter(user=user).order_by('-date')

    transactions = []

    transactions_by_date = {}

    for transaction in all_transactions:
        transaction_date = transaction.date.strftime(
            '%Y-%m-%d')

        if transaction_date not in transactions_by_date:
            transactions_by_date[
                transaction_date] = []

        transactions_by_date[transaction_date].append({
            'time': transaction.date.strftime('%I:%M %p'),
            'amount': str(transaction.expenses_amount),
            'category': transaction.category,
            'description': transaction.description,
            'transaction_id': transaction.id
        })

    for date, transaction_list in transactions_by_date.items():
        transactions.append({
            'date': date,
            'transactions': transaction_list

        })

    return JsonResponse({'transactions': transactions}, status=200)


@api_view(['POST'])
def get_user_pie_chart_financial_transactions(request):
    user_id = request.data.get('user')
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
        user = User.objects.get(id=user_id)
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
        'total_expense': total_expense
    }, status=200)


# @api_view(['POST'])
# def get_transaction_filters(request):
#     user_id = request.data.get('user')
#
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         return JsonResponse({'message': 'User not found.'}, status=404)
#
#     highest_price_filter = request.data.get('Highest')
#     lowest_price_filter = request.data.get('Lowest')
#     oldest_transaction_filter = request.data.get('Oldest')
#     category_filter = request.data.get('Categories')
#
#     results = {}
#     if category_filter:
#         category_transactions = UserExpense.objects.filter(user=user,
#                                                            category=category_filter)
#         if highest_price_filter:
#             highest_transactions = category_transactions.order_by(
#                 "-expenses_amount")
#             results['Categories'] = list(highest_transactions.values(
#                 'category', 'expenses_amount', 'date', 'description'))
#         elif lowest_price_filter:
#             lowest_transactions = category_transactions.order_by(
#                 "expenses_amount")
#             results['Categories'] = list(lowest_transactions.values(
#                 'category', 'expenses_amount', 'date', 'description'
#             ))
#         elif oldest_transaction_filter:
#             oldest_transactions = category_transactions.order_by("date")
#             results['Categories'] = list(oldest_transactions.values(
#                 'category', 'expenses_amount', 'date', 'description'
#             ))
#         else:
#             results['Categories'] = list(
#                 category_transactions.values('category', 'expenses_amount',
#                                              'date'))
#
#     elif highest_price_filter:
#         highest_transactions = UserExpense.objects.filter(user=user).order_by(
#             '-expenses_amount')
#         results['Highest'] = list(
#             highest_transactions.values('category', 'expenses_amount', 'date'))
#
#     elif lowest_price_filter:
#         lowest_transactions = UserExpense.objects.filter(user=user).order_by(
#             'expenses_amount')
#         results['Lowest'] = list(
#             lowest_transactions.values('category', 'expenses_amount', 'date'))
#
#     elif oldest_transaction_filter:
#         oldest_transactions = UserExpense.objects.filter(user=user).order_by(
#             'date')
#         results['Oldest'] = list(
#             oldest_transactions.values('category', 'expenses_amount', 'date'))
#     else:
#         results['Categories'] = list(
#             UserExpense.objects.filter(user=user).values('category',
#                                                          'expenses_amount',
#                                                          'date').order_by(
#                 '-date'
#             ))
#
#     return JsonResponse(results, status=200)


@api_view(['POST'])
def get_transaction_filters(request):
    user_id = request.data.get('user')

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    highest_price_filter = request.data.get('Highest')
    lowest_price_filter = request.data.get('Lowest')
    oldest_transaction_filter = request.data.get('Oldest')
    category_filter = request.data.get('Categories')

    results = {}

    # Helper function to split date and time
    def split_date_time(transaction):
        transaction_date = transaction['date']
        return {
            'category': transaction['category'],
            'expenses_amount': transaction['expenses_amount'],
            'description': transaction.get('description', ''),
            'date': transaction_date.strftime('%Y-%m-%d'),  # Extract date
            'time': transaction_date.strftime('%H:%M:%S')  # Extract time
        }

    if category_filter:
        category_transactions = UserExpense.objects.filter(user=user,
                                                           category=category_filter)
        if highest_price_filter:
            highest_transactions = category_transactions.order_by(
                "-expenses_amount")
            results['Categories'] = [
                split_date_time(tx) for tx in highest_transactions.values(
                    'category', 'expenses_amount', 'date', 'description'
                )
            ]
        elif lowest_price_filter:
            lowest_transactions = category_transactions.order_by(
                "expenses_amount")
            results['Categories'] = [
                split_date_time(tx) for tx in lowest_transactions.values(
                    'category', 'expenses_amount', 'date', 'description'
                )
            ]
        elif oldest_transaction_filter:
            oldest_transactions = category_transactions.order_by("date")
            results['Categories'] = [
                split_date_time(tx) for tx in oldest_transactions.values(
                    'category', 'expenses_amount', 'date', 'description'
                )
            ]
        else:
            results['Categories'] = [
                split_date_time(tx) for tx in category_transactions.values(
                    'category', 'expenses_amount', 'date'
                )
            ]

    elif highest_price_filter:
        highest_transactions = UserExpense.objects.filter(user=user).order_by(
            '-expenses_amount')
        results['Highest'] = [
            split_date_time(tx) for tx in highest_transactions.values(
                'category', 'expenses_amount', 'date'
            )
        ]

    elif lowest_price_filter:
        lowest_transactions = UserExpense.objects.filter(user=user).order_by(
            'expenses_amount')
        results['Lowest'] = [
            split_date_time(tx) for tx in lowest_transactions.values(
                'category', 'expenses_amount', 'date'
            )
        ]

    elif oldest_transaction_filter:
        oldest_transactions = UserExpense.objects.filter(user=user).order_by(
            'date')
        results['Oldest'] = [
            split_date_time(tx) for tx in oldest_transactions.values(
                'category', 'expenses_amount', 'date'
            )
        ]
    else:
        results['Categories'] = [
            split_date_time(tx) for tx in UserExpense.objects.filter(user=user)
            .values('category', 'expenses_amount', 'date')
            .order_by('-date')
        ]

    return JsonResponse(results, status=200)


@api_view(['GET'])
def delete_user_expense(request):
    user_id = request.data.get('user')
    transaction_id = request.data.get('expense_id')

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    try:
        expense = UserExpense.objects.get(id=transaction_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'Expense not found.'}, status=404)

    expense.delete()

    return JsonResponse({'message': 'Expense deleted successfully.'},
                        status=200)


@api_view(['POST'])
def get_transaction_details(request):
    user_id = request.data.get('user')
    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

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
