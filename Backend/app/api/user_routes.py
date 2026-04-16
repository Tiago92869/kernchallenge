from uuid import UUID

from app.api.responses import success_response
from app.schemas.user_schema import UserSchema
from app.services.user_service import UserService
from flask import Blueprint, request

user_bp = Blueprint("users", __name__, url_prefix="/users")


@user_bp.post("")
def create_user():
    """Create a new user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - firstname
            - lastname
            - password
          properties:
            email:
              type: string
              format: email
            firstname:
              type: string
            lastname:
              type: string
            password:
              type: string
    responses:
      201:
        description: User created
      400:
        description: Validation error
      409:
        description: Email already registered
    """
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
    """Update user profile fields.
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              format: email
            firstname:
              type: string
            lastname:
              type: string
    responses:
      200:
        description: User updated
      400:
        description: Validation error
      404:
        description: User not found
    """
    data = request.get_json() or {}

    user = UserService.update_user(
        user_id=UUID(user_id),
        email=data.get("email"),
        firstname=data.get("firstname"),
        lastname=data.get("lastname"),
    )

    return success_response(data=UserSchema.serialize_user(user))


@user_bp.get("/<user_id>")
def get_user_by_id(user_id):
    """Get a user by id.
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: User found
      404:
        description: User not found
    """
    user = UserService.get_user_by_id(UUID(user_id))

    return success_response(data=UserSchema.serialize_user(user))


@user_bp.put("/password/<user_id>")
def update_password(user_id):
    """Update user password.
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - old_password
            - new_password
          properties:
            old_password:
              type: string
            new_password:
              type: string
    responses:
      200:
        description: Password updated
      400:
        description: Validation error
      404:
        description: User not found
    """
    data = request.get_json() or {}

    UserService.update_password(
        user_id=UUID(user_id),
        old_password=data.get("old_password"),
        new_password=data.get("new_password"),
    )

    return success_response(message="Password updated successfully")


@user_bp.get("")
def get_all_users():
    """List all users with optional filters.
    ---
    tags:
      - Users
    parameters:
      - in: query
        name: search
        type: string
        required: false
        description: Search by name or email
      - in: query
        name: is_active
        type: boolean
        required: false
        description: Filter by active status
    responses:
      200:
        description: User list returned
    """
    users = UserService.get_all_users(
        search=request.args.get("search", ""),
        is_active=request.args.get("is_active"),
    )
    return success_response(data=[UserSchema.serialize_user(user) for user in users])


@user_bp.get("/login")
def login():
    data = request.get_json() or {}

    user = UserService.login(
        email=data.get("email", ""),
        password=data.get("password", ""),
    )

    return success_response(
        data=UserSchema.serialize_user(user),
        status_code=200,
    )
