from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import UserExpense, UserPreferenceDetails, UserProfile, \
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
    print(request.data)
    user_id = request.user.user_id
    user = get_object_or_404(User, user_id=user_id)

    salary = request.data.get('salary')
    if not salary:
        return JsonResponse({'message': 'Salary is required.'}, status=400)

    if salary <= 0:
        return JsonResponse({'message': 'Salary should not be in Negative'},
                            status=400)

    if salary < 500:
        return JsonResponse({'message': 'Salary should be greater than 500'},
                            status=400)

    if salary > 10000000:
        return JsonResponse({'message': 'Maximum limit is 1 Crore'},
                            status=400)

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
            base_amount * (location_details.Entertainment_percentage / 100),
            2),
        'Savings': round(
            base_amount * (location_details.Savings_percentage / 100), 2),
        'Miscellaneous': round(
            base_amount * (location_details.Miscellaneous_percentage / 100),
            2),
    }

    # Handle category naming mismatch, for example, mapping 'Travel' to 'Travelling'
    category_mapping = {
        'Travel': 'Travelling'
    }

    user_expenses_history = UserExpense.objects.filter(
        user=user,
        date__month=month
    ).values('category').annotate(total=Sum('expenses_amount'))

    total_expense = UserExpense.objects.filter(
        user=user, date__month=month
    ).aggregate(total=Sum('expenses_amount'))['total'] or 0

    # Categorize expenses into over-spent, under-spent, and zero-spent
    over_spent = []
    under_spent = []
    zero_spent = []  # New list for categories with zero spending

    for expense in user_expenses_history:
        category = expense['category']
        actual_amount = round(float(expense['total']), 2)
        # Map category to standardized name if necessary
        standardized_category = category_mapping.get(category, category)
        recommended_amount = recommended_amounts.get(standardized_category, 0)

        if actual_amount > recommended_amount:
            over_spent.append({
                'category': category,
                'actual_amount': actual_amount,
                'recommended_amount': recommended_amount
            })
        elif actual_amount == 0:
            zero_spent.append({
                'category': category,
                'actual_amount': actual_amount,
                'recommended_amount': recommended_amount
            })
        else:
            under_spent.append({
                'category': category,
                'actual_amount': actual_amount,
                'recommended_amount': recommended_amount
            })

    # Include categories with zero spending in zero_spent (those not present in user_expenses_history)
    for category, recommended_amount in recommended_amounts.items():
        if not any(expense['category'] == category or expense[
            'category'] == category_mapping.get(category) for expense in
                   user_expenses_history):
            zero_spent.append({
                'category': category,
                'actual_amount': 0.0,
                'recommended_amount': recommended_amount
            })

    return JsonResponse({
        'over_spent': over_spent,
        'under_spent': under_spent,
        'zero_spent': zero_spent,
        # Include the zero_spent list in the response
        'total_expense': round(float(total_expense), 2),
        'recommended_amounts': recommended_amounts
    }, status=200)


# @api_view(['POST'])
# def get_feedback(request):
#     user_id = request.user.user_id
#
#     try:
#         user = User.objects.get(user_id=user_id)
#     except ObjectDoesNotExist:
#         return JsonResponse({'message': 'User not found.'}, status=404)
#
#     description = request.data.get('description')
#     rating = request.data.get('rating')
#     Feedback.objects.create(user=user, feedback=description,
#                             rating_stars=rating)
#
#     return JsonResponse({'message': 'Feedback submitted successfully.'},
#                         status=200)


from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Feedback, User


@api_view(['POST'])
def get_feedback(request):
    user_id = request.user.user_id

    try:
        user = User.objects.get(user_id=user_id)
    except ObjectDoesNotExist:
        return JsonResponse({'message': 'User not found.'}, status=404)

    description = request.data.get('description')
    rating = request.data.get('rating')

    # Check if description and rating are present
    if description is None or rating is None:
        return JsonResponse(
            {'message': 'Description and rating are required.'}, status=400)

    try:
        rating = int(rating)
    except ValueError:
        return JsonResponse({'message': 'Rating must be an integer.'},
                            status=400)

    # Create Feedback instance
    Feedback.objects.create(user_feedback=user, description=description,
                            rating_stars=rating)

    return JsonResponse({'message': 'Feedback submitted successfully.'},
                        status=200)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI
from .models import User, UserProfile, UserPreferenceDetails, UserExpense

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)


@api_view(['POST'])
def generate_personalized_response(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)
            user_id = request.user.user_id
            user_message = data.get("message", "")

            if not user_id or not user_message:
                return JsonResponse(
                    {"error": "User ID and message are required."}, status=400)

            try:
                user = User.objects.get(user_id=user_id)
                profile = UserProfile.objects.get(user=user)
                preference_details = UserPreferenceDetails.objects.get(
                    user=user)
                recent_expenses = UserExpense.objects.filter(
                    user=user).order_by('-date')[:5]
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found."}, status=404)
            except UserProfile.DoesNotExist:
                return JsonResponse({"error": "User profile not found."},
                                    status=404)
            except UserPreferenceDetails.DoesNotExist:
                return JsonResponse(
                    {"error": "User preference details not found."},
                    status=404)

            # Prepare personalized prompt
            expenses_summary = "\n".join(
                [f"{expense.category}: {expense.expenses_amount}" for expense
                 in recent_expenses])
            user_data_prompt = (
                f"User {user.full_name} has a monthly salary of {preference_details.salary}, "
                f"prefers {preference_details.preference} items, lives in {preference_details.city}. "
                f"Their recent expenses are:\n{expenses_summary}\n\n"
            )

            full_prompt = user_data_prompt + user_message

            # Call the NVIDIA model API
            completion = client.chat.completions.create(
                model="nvidia/llama-3.1-nemotron-70b-instruct",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.5,
                top_p=1,
                max_tokens=1024,
                stream=True
            )

            # Gather streamed response
            generated_text = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    generated_text += chunk.choices[0].delta.content

            return JsonResponse({"response": generated_text})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            # Log the exception for further debugging if needed
            print(f"An error occurred: {e}")
            return JsonResponse(
                {"error": "An internal server error occurred."}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed."},
                        status=405)
