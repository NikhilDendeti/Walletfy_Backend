class InvalidRefreshTokenException(Exception):
    pass


class RefreshTokenExpiredException(Exception):
    pass


class InvalidAccessTokenException(Exception):
    pass


class InvalidUserException(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass