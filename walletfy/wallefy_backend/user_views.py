# Create your views here.
# Create your views here.
from rest_framework.decorators import api_view, authentication_classes, \
    permission_classes

from wallefy_backend.interactor.create_access_token_using_refresh_token import \
    CreateRefreshAccessToken
from wallefy_backend.interactor.login_interactor import LoginInteractor
from wallefy_backend.interactor.logout_interactor import LogoutInteractor
from wallefy_backend.interactor.signup_interactor import SignUpInteractor
from wallefy_backend.interactor.update_password_interactor import \
    UpdatePasswordInteractor
from wallefy_backend.interactor.update_user_profile_interactor import \
    UserProfileUpdate
from wallefy_backend.interactor.user_profile_interactor import \
    ProfileInteractor
from wallefy_backend.presenters.create_access_token_using_refresh_response import \
    CreateRefreshAccessTokensResponse
from wallefy_backend.presenters.login_response import LoginResponse
from wallefy_backend.presenters.logout_response import LogoutResponse
from wallefy_backend.presenters.signup_response import SignupResponse
from wallefy_backend.presenters.update_password_response import \
    UpdatePasswordResponse
from wallefy_backend.presenters.update_user_profile_response import \
    UserProfileUpdateResponse
from wallefy_backend.presenters.user_profile_response import \
    ProfileInteractorResponse
from wallefy_backend.storages.user_authenticate_db import UserAuthentication
from wallefy_backend.storages.user_db import UserDB


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def get_login_interactor_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    response = LoginInteractor(storage=UserDB(),
                               authentication=UserAuthentication(),
                               response=LoginResponse()).login_interactor(
        email,
        password)
    return response


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def get_signup_interactor_view(request):
    email = request.data.get("email")
    password = request.data.get("password")
    username = request.data.get("username")
    full_name = request.data.get("full_name")
    role = request.data.get("role")
    gender = request.data.get("gender")
    response = SignUpInteractor(storage=UserDB(),
                                authentication=UserAuthentication(),
                                response=SignupResponse()).signup_interactor(
        email, password, username, full_name,
        role, gender)
    return response


@api_view(['POST'])
def get_update_password_view(request):
    email = request.data.get("email")
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    response = UpdatePasswordInteractor(storage=UserDB(),
                                        response=UpdatePasswordResponse()).update_password_interactor(
        email, old_password, new_password)
    return response


@api_view(['GET'])
def get_user_profile_api_view(request):
    user_id = request.user.user_id
    user_profile_dto = ProfileInteractor(storage=UserDB(),
                                         response=ProfileInteractorResponse()).get_user_details_profile_interactor(
        user_id=str(user_id))
    return user_profile_dto


@api_view(['POST'])
def update_user_profile_view(request):
    full_name = request.data.get("full_name")
    email = request.data.get("email")
    username = request.data.get("username")
    user_id = request.user.user_id
    response = UserProfileUpdate(storage=UserDB(),
                                 response=UserProfileUpdateResponse()).update_user_profile_interactor(
        full_name=full_name, email=email, username=username, user_id=user_id)
    return response


@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def refresh_access_token_view(request):
    refresh_token = request.data.get('refresh_token')
    response = CreateRefreshAccessToken(authentication=UserAuthentication(),
                                        response=CreateRefreshAccessTokensResponse()).refresh_access_token_interactor(
        refresh_token=refresh_token)
    return response


@api_view(["POST"])
def user_logout_view(request):
    access_token = request.data.get("access_token")
    refresh_token = request.data.get("refresh_token")
    response = LogoutInteractor(authentication=UserAuthentication(),
                                response=LogoutResponse()).logout_interactor(
        access_token, refresh_token)
    return response
