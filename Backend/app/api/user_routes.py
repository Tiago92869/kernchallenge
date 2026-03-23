from flask import Blueprint, request
from uuid import UUID
from app.api.responses import success_response
from app.services.user_service import UserService
from app.schemas.user_shcema import UserSchema

user_bp = Blueprint("users", __name__, url_prefix="/users")

@user_bp.post("")
def create_user():
    data = request.get_json() or {}

    user = UserService.create_user(
        email=data.get("email"),
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
        password=data.get("password"),
    )

    return success_response(
        data=UserSchema.serialize_user(user),
        status_code=201,
    )