from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from .Enums import TransactionType
from .models import User, UserExpense, UserPreferenceDetails, UserProfile


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

@api_view(["POST"])
def get_user_details(request):
    user_id = request.data.get('user')
    salary = request.data.get('salary')
    location = request.data.get('location')
    city = request.data.get('city')
    preference = request.data.get('preference')

    # Validation logic can be added here if required

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)
    except ValueError:
        return JsonResponse({'message': 'Invalid user ID format.'}, status=400)

    # Try to get the UserProfile or create it if not found
    user_profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'gender': 'Male',  # Set a default value or extract from request
            'role': 'Employee'  # Set a default value or extract from request
        }
    )

    # Now you can create UserPreferenceDetails using the user_profile
    UserPreferenceDetails.objects.create(
        user=user_profile,  # Correctly passing UserProfile instance
        salary=salary,
        location=location,
        city=city,
        preference=preference
    )

    return JsonResponse({
        'username': user.username,
        'salary': salary,
        'location': location,
        'city': city,
        'preference': preference
    })


#
# @api_view(["POST"])
# def get_user_details(request):
#     user_id = request.data.get('user')
#     salary = request.data.get('salary')
#     location = request.data.get('location')
#     city = request.data.get('city')
#     preference = request.data.get('preference')
#
#     # if salary is None or location is None or city is None or preference is None:
#     #     return JsonResponse({
#     #         'message': 'Salary, location, city and preference are required.'
#     #     }, status=400)
#     #
#     # if salary <= 0:
#     #     return JsonResponse({
#     #         'message': 'Salary must be positive.'
#     #     }, status=400)
#     #
#     # if location not in UserPreferenceDetails.LocationChoices.list_of_values():
#     #     return JsonResponse({
#     #         'message': 'Invalid location.'
#     #     }, status=400)
#     #
#     # if city not in UserPreferenceDetails.LocationChoices.list_of_values():
#     #     return JsonResponse({
#     #         'message': 'Invalid city.'
#     #     }, status=400)
#     #
#     # if preference not in UserPreferenceDetails.PreferenceChoices.list_of_values():
#     #     return JsonResponse({
#     #         'message': 'Invalid preference.'
#     #     }, status=400)
#
#     try:
#         user = User.objects.get(id=user_id)
#     except ObjectDoesNotExist:
#         return JsonResponse({'message': 'User not found.'}, status=404)
#     except ValueError:
#         return JsonResponse({'message': 'Invalid user ID format.'}, status=400)
#     UserPreferenceDetails.objects.create(user=user, salary=salary,
#                                          location=location,
#                                          city=city,
#                                          preference=preference)
#     return JsonResponse({
#         'username': user.username,
#         'salary': salary,
#         'location':location,
#         'city': city,
#         'preference': preference
#     })
