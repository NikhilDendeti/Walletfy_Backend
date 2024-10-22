from wallefy_backend.dto.dtos import LoginResponseDTO
from wallefy_backend.exceptions import InvalidUserException
from wallefy_backend.presenters.login_response import LoginResponse
from wallefy_backend.storages.user_authenticate_db import UserAuthentication
from wallefy_backend.storages.user_db import UserDB



class LoginInteractor:
    def __init__(self, storage: UserDB, authentication: UserAuthentication,
                 response: LoginResponse):
        self.storage = storage
        self.authentication = authentication
        self.response = response

    def login_interactor(self, email, password):
        try:
            user_login = self.storage.validate_password(email, password)
            if user_login is False:
                return self.response.invalid_password_exception_response()
        except InvalidUserException:
            return self.response.invalid_user_response()
        user_id = self.storage.get_user_id(email)
        access_token = self.authentication.create_access_token(user_id)
        refresh_token = self.authentication.create_refresh_token(access_token,
                                                                 user_id)
        user_login_dto = LoginResponseDTO(
            access_token=access_token.access_token,
            refresh_token=refresh_token.refresh_token
        )
        user_response = self.response.user_login_dto_response(user_login_dto)
        return user_response
