class ApiError(Exception):
    status_cpde = 400
    error_code = "api_error"
    message = "Request failed"

    def __init__(self, message=None, details=None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class ValidationError(ApiError):
    status_code = 400
    error_code = "validation_error"
    message = "Request validation failed"


class AuthenticationError(ApiError):
    status_code = 401
    error_code = "authentication_required"
    message = "Authentication is required"


class ForbiddenError(ApiError):
    status_code = 403
    error_code = "forbidden"
    message = "You do not have permission to perform this action"


class NotFoundError(ApiError):
    status_code = 404
    error_code = "not_found"
    message = "Requested resource was not found"


class ConflictError(ApiError):
    status_code = 409
    error_code = "conflict"
    message = "Request conflicts with current state"
