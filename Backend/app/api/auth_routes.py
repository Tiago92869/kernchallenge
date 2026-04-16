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
    """Login and receive access and refresh tokens.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
            password:
              type: string
    responses:
      200:
        description: Login successful, tokens returned
      401:
        description: Invalid credentials
    """
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
    """Logout and revoke the current access token.
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: Logged out successfully
      401:
        description: Missing or invalid token
    """
    jti = get_jwt()["jti"]
    UserService.logout(jti=jti)
    return success_response(message="Logged out successfully")


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using a refresh token.
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    responses:
      200:
        description: New access token returned
      401:
        description: Missing or invalid refresh token
    """
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return success_response(data={"auth_token": access_token})


@auth_bp.post("/forgot-password")
def forgot_password():
    """Request a password reset email.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
    responses:
      200:
        description: Reset email sent if account exists
    """
    data = request.get_json() or {}

    UserService.reset_forgotten_password(email=data.get("email", ""))
    return success_response(message="A new password was sent to your email")
