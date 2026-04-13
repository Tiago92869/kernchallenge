from app.api.errors import ApiError
from app.api.responses import error_response
from werkzeug.exceptions import HTTPException


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(error):
        return error_response(
            code=error.error_code,
            message=error.message,
            details=error.details,
            status_code=error.status_code,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return error_response(
            code=error.name.lower().replace(" ", "_"),
            message=error.description,
            status_code=error.code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        return error_response(
            code="internal_error",
            message="An unexpected error occurred",
            status_code=500,
        )
