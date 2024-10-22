from dataclasses import dataclass


@dataclass
class CreateRefreshTokenDTO:
    access_token: str


@dataclass
class AccessTokenDTO:
    user_id: str
    access_token: str


@dataclass
class RefreshTokenDTO:
    user_id: str
    refresh_token: str


@dataclass
class LoginResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class ProfileDTO:
    email: str
    username: str
    full_name: str
    role: str
    gender: str


@dataclass
class SignupResponseDTO:
    access_token: str
    refresh_token: str


@dataclass
class userDetailsDTO:
    email: str
    username: str
    first_name: str
    last_name: str


@dataclass
class UserProfileDTO:
    email: str
    username: str
    full_name: str
    role: str
    gender: str
    salary: float