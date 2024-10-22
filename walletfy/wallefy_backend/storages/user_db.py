from django.contrib.auth.hashers import make_password

from walletfy.wallefy_backend.dto.user_dto.dtos import ProfileDTO, userDetailsDTO, UserProfileDTO
from walletfy.wallefy_backend.exceptions import InvalidUserException, UserAlreadyExistsException
from walletfy.wallefy_backend.models import User, UserRole, UserProfile, UserIncomeDetails


class UserDB:

    @staticmethod
    def validate_password(email, password) -> bool:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise InvalidUserException
        return user.check_password(password)

    @staticmethod
    def get_user_id(email) -> str:
        user = User.objects.get(email=email)
        return str(user.user_id)

    @staticmethod
    def create_user_for_signup(email, password, username, full_name, role, gender):
        if User.objects.filter(email=email).exists():
            raise UserAlreadyExistsException()
        hashed_password = make_password(password)
        user = User.objects.create(email=email, password=hashed_password, username=username, full_name=full_name,
                                   )
        user_role = UserRole.objects.create(role=role, user=user)
        user_gender = UserProfile.objects.create(gender=gender, user=user)
        user_profile_dto = ProfileDTO(
            email=user.email,
            full_name=user.first_name,
            username=user.username,
            gender=user_gender.gender,
            role=user_role.role
        )
        return user_profile_dto

    @staticmethod
    def setup_newpassword(user_id, new_password) -> userDetailsDTO:
        user = User.objects.get(user_id=user_id)
        hashed_password = make_password(new_password)
        user.password = hashed_password
        user.save()
        user_dto = userDetailsDTO(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )
        return user_dto

    @staticmethod
    def profile(user_id) -> UserProfileDTO:
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            raise InvalidUserException
        user_role = UserRole.objects.get(user=user)
        user_gender = UserProfile.objects.get(user=user)
        user_salary = UserIncomeDetails.objects.get(user=user)
        user_profile_dto = UserProfileDTO(
            email=user.email,
            full_name=user.full_name,
            username=user.username,
            gender=user_gender.gender,
            role=user_role.role,
            salary=user_salary.salary
        )
        return user_profile_dto

    @staticmethod
    def validate_user_id(user_id) -> None:
        try:
            User.objects.get(user_id=str(user_id))
        except User.DoesNotExist:
            raise InvalidUserException()

    @staticmethod
    def update_user_profile(full_name, email, user_id) -> int:
        user_profile_update = User.objects.filter(user_id=user_id).update(
            full_name=full_name, email=email)
        # it returns the number of rows that updated
        return user_profile_update
