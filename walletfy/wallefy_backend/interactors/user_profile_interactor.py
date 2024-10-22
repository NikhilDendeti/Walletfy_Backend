from walletfy.wallefy_backend.dto.user_dto.dtos import UserProfileDTO
from walletfy.wallefy_backend.exceptions import InvalidUserException
from walletfy.wallefy_backend.presentors.user_profile_response import ProfileInteractorResponse
from walletfy.wallefy_backend.storages.user_db import UserDB


class ProfileInteractor:
    def __init__(self, storage: UserDB, response: ProfileInteractorResponse):
        self.storage = storage
        self.response = response

    def get_user_details_profile_interactor(self, user_id: str):
        try:
            user_details = self.storage.profile(user_id)
        except InvalidUserException:
            return self.response.invalid_user_response()

        user_profile_dto = UserProfileDTO(
            email=user_details.email,
            full_name=user_details.full_name,
            username=user_details.username,
            gender=user_details.gender,
            role=user_details.role,
            salary=user_details.salary
        )
        user_details_response = self.response.user_details_dto_response(user_profile_dto)
        return user_details_response
