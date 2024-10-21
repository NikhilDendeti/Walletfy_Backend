from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, \
    authentication_classes
from .models import User, UserExpense
from .Enums import TransactionType
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal


@api_view(['POST'])
# @authentication_classes([])
# @permission_classes([IsAuthenticated])
def update_user_expense(request):
    user_id = request.data.get('user')  # Example: user ID passed in the body

    try:
        user = User.objects.get(id=user_id)  # Use the UUIDField for fetching
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    expense_amount = request.data.get('expense_amount')
    expense_type = request.data.get('expense_type')

    if expense_amount is None or expense_type is None:
        return JsonResponse({
            'message': 'Expense amount and type are required.'
        }, status=400)

    expense_amount = Decimal(expense_amount)  # Convert to Decimal

    if expense_amount <= 0:
        return JsonResponse({
            'message': 'Expense amount must be positive.'
        }, status=400)

    current_month = timezone.now().month
    current_year = timezone.now().year

    if expense_type == TransactionType.INCOME.value:
        user.account_balance += expense_amount
        user.save()
        UserExpense.objects.create(user=user, category='Income',
                                   expenses_amount=expense_amount)

    elif expense_type == TransactionType.EXPENSE.value:
        if user.account_balance < expense_amount:
            return JsonResponse({
                'message': 'Insufficient balance'
            }, status=400)
        else:
            user.account_balance -= expense_amount
            user.save()
            UserExpense.objects.create(user=user, category='Expense',
                                       expenses_amount=expense_amount)
    total_income = UserExpense.objects.filter(
        user=user,
        category=TransactionType.INCOME.value,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0

    total_expense = UserExpense.objects.filter(
        user=user,
        category=TransactionType.EXPENSE.value,
        date__month=current_month,
        date__year=current_year
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0

    return JsonResponse({
        'username': user.username,
        'account_balance': str(user.account_balance),
        'total_income': str(total_income),
        'total_expense': str(total_expense),
    }, status=200)
