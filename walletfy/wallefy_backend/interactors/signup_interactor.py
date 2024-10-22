from walletfy.wallefy_backend.dto.user_dto.dtos import SignupResponseDTO
from walletfy.wallefy_backend.exceptions import UserAlreadyExistsException
from walletfy.wallefy_backend.presentors.signup_response import SignupResponse
from walletfy.wallefy_backend.storages.authenticate_db import UserAuthentication
from walletfy.wallefy_backend.storages.user_db import UserDB


class SignUpInteractor:
    def __init__(self, storage: UserDB, authentication: UserAuthentication, response: SignupResponse):
        self.storage = storage
        self.response = response
        self.authentication = authentication

    def signup_interactor(self, email, password, full_name, role, username, gender):
        try:
            self.storage.create_user_for_signup(email, password, full_name, role, username, gender)
        except UserAlreadyExistsException:
            return self.response.user_already_exists_response()
        user_id = self.storage.get_user_id(email)

        access_token = self.authentication.create_access_token(user_id)
        refresh_token = self.authentication.create_refresh_token(access_token, user_id)
        user_signup_dto = SignupResponseDTO(
            access_token=access_token.access_token,
            refresh_token=refresh_token.refresh_token
        )
        response = self.response.user_signup_dto_response(user_signup_dto)
        return response
