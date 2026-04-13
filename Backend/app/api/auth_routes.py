from app.api.responses import success_response
from app.schemas.user_schema import UserSchema
from app.services.user_service import UserService
from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}

    user = UserService.login(
        email=data.get("email", ""),
        password=data.get("password", ""),
    )

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response(
        data=UserSchema.serialize_login(access_token, refresh_token),
        status_code=200,
    )


@auth_bp.post("/logout")
@auth_bp.post("/signout")
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    UserService.logout(jti=jti)
    return success_response(message="Logged out successfully")


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return success_response(data={"auth_token": access_token})


@auth_bp.post("/forgot-password")
def forgot_password():
    data = request.get_json() or {}

    UserService.reset_forgotten_password(email=data.get("email", ""))
    return success_response(message="A new password was sent to your email")
