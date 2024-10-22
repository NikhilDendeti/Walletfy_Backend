from decimal import Decimal, InvalidOperation

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from .Enums import TransactionType, Category
from .models import User, UserExpense, UserPreferenceDetails, UserProfile


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


def get_recent_transaction_history(request):
    user_id = request.data.get('user')
    current_month = timezone.now().month
    current_year = timezone.now().year

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    expenses = UserExpense.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    )


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
            'time': transaction.date.strftime('%I:%M %p')
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
            'category': transaction.category
        })

    return JsonResponse({'transactions_by_date': transactions_by_date},
                        status=200)
