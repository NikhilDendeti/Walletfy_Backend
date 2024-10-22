import json

from django.http import HttpResponse


class ProfileInteractorResponse:
    @staticmethod
    def invalid_user_response() -> HttpResponse:
        return HttpResponse(json.dumps({
            "error_code": 400,
            "error_message": "Invalid User"
        }, indent=4), status=400)

    @staticmethod
    def user_details_dto_response(user_dto) -> HttpResponse:
        user_profile_dict = {
            "email": user_dto.email,
            "username": user_dto.username,
            "full_name": user_dto.full_name,
            "role": user_dto.role,
            "gender": user_dto.gender,
            "salary": str(user_dto.salary)
        }
        return HttpResponse(json.dumps(user_profile_dict, indent=4), status=200)