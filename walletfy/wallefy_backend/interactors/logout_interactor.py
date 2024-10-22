from django.http import HttpResponse

from walletfy.wallefy_backend.exceptions import InvalidRefreshTokenException, InvalidAccessTokenException
from walletfy.wallefy_backend.presentors.logout_response import LogoutResponse
from walletfy.wallefy_backend.storages.authenticate_db import UserAuthentication


class LogoutInteractor:
    def __init__(self, authentication: UserAuthentication, response: LogoutResponse):
        self.authentication = authentication
        self.response = response

    def logout_interactor(self, access_token, refresh_token) -> HttpResponse:
        try:
            self.authentication.expire_access_token_refresh_token(access_token, refresh_token)
            return self.response.logout_success_response()
        except InvalidRefreshTokenException:
            return self.response.invalid_refresh_token_response()
        except InvalidAccessTokenException:
            return self.response.invalid_access_token_response()