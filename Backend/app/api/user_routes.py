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

@user_bp.put("/<user_id>")
def update_user(user_id):
    data = request.get_json() or {}

    user = UserService.update_user(
        user_id = UUID(user_id),
        email = data.get("email"),
        firstname = data.get("firstname"),
        lastname = data.get("lastname")
    )

    return success_response(
        data=UserSchema.serialize_user(user)
    ) 

@user_bp.get("/<user_id>")
def get_user_by_id(user_id):
    user = UserService.get_user_by_id(UUID(user_id))

    return success_response(data = UserSchema.serialize_user(user))