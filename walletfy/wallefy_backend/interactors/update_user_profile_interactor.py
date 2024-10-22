from walletfy.wallefy_backend.exceptions import InvalidUserException
from walletfy.wallefy_backend.presentors.update_user_profile_response import UserProfileUpdateResponse
from walletfy.wallefy_backend.storages.user_db import UserDB


class UserProfileUpdate:
    def __init__(self, storage: UserDB, response: UserProfileUpdateResponse):
        self.storage = storage
        self.response = response
    def update_user_profile_interactor(self, full_name, email, user_id):
        try:
            self.storage.validate_user_id(user_id)
        except InvalidUserException:
            return self.response.invalid_user_exception()
        self.storage.update_user_profile(full_name, email, user_id)
        return self.response.update_user_profile_success_response()
