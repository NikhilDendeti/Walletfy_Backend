from walletfy.wallefy_backend.dto.user_dto.dtos import CreateRefreshTokenDTO
from walletfy.wallefy_backend.exceptions import InvalidRefreshTokenException, RefreshTokenExpiredException
from walletfy.wallefy_backend.presentors.create_access_token_using_refresh_token_response import \
    CreateRefreshAccessTokensResponse
from walletfy.wallefy_backend.storages.authenticate_db import UserAuthentication


class CreateRefreshAccessToken:
    def __init__(self, authentication: UserAuthentication, response: CreateRefreshAccessTokensResponse):
        self.authentication = authentication
        self.response = response

    def refresh_access_token_interactor(self, refresh_token):
        try:
            get_refresh_token = self.authentication.create_refresh_access_token(
                refresh_token)
        except InvalidRefreshTokenException:
            return self.response.invalid_refresh_token_response()
        except RefreshTokenExpiredException:
            return self.response.token_expired_response()
        refresh_access_token_dto = CreateRefreshTokenDTO(
            access_token=get_refresh_token.access_token
        )
        response = self.response.get_refresh_access_token_success_response(refresh_access_token_dto)
        return response
