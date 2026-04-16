from uuid import UUID

from app.api.errors import ValidationError
from app.api.responses import success_response
from app.schemas.project_schema import ProjectSchema
from app.services.project_service import ProjectService
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

project_bp = Blueprint("projects", __name__, url_prefix="/projects")


def _parse_bool_query_param(value: str | None, *, field_name: str) -> bool:
    if value is None:
        return False

    normalized_value = value.strip().lower()
    if normalized_value in {"true", "1", "yes"}:
        return True
    if normalized_value in {"false", "0", "no"}:
        return False

    raise ValidationError(message=f"Invalid '{field_name}' value. Use true or false")


@project_bp.post("")
@jwt_required()
def create_project():
    """Create a new project.
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            description:
              type: string
            visibility:
              type: string
              enum: [PUBLIC, PRIVATE]
              default: PRIVATE
    responses:
      201:
        description: Project created
      401:
        description: Missing or invalid auth token
      400:
        description: Validation error
    """
    data = request.get_json() or {}

    project = ProjectService.create_project(
        owner_id=UUID(get_jwt_identity()),
        name=data.get("name"),
        description=data.get("description"),
        visibility=data.get("visibility", "PRIVATE"),
    )

    return success_response(
        data=ProjectSchema.serialize_project(project),
        status_code=201,
    )


@project_bp.get("")
@jwt_required()
def list_projects():
    """List available projects.
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: query
        name: search
        type: string
        required: false
        description: Optional project name search text
      - in: query
        name: my_projects
        type: boolean
        required: false
        description: When true, returns only projects where user is owner
    responses:
      200:
        description: Project list returned
      401:
        description: Missing or invalid auth token
      400:
        description: Validation error
    """
    parsed_user_id = UUID(get_jwt_identity())

    projects = ProjectService.list_available_projects(
        user_id=parsed_user_id,
        search=request.args.get("search"),
        my_projects=_parse_bool_query_param(
            request.args.get("my_projects"),
            field_name="my_projects",
        ),
    )

    return success_response(data=ProjectSchema.serialize_project_infos_list()(projects))


@project_bp.get("/dashboard/activity")
@jwt_required()
def get_project_dashboard_activity():
    """Get dashboard project activity split by joined and owned projects.
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    responses:
      200:
        description: Project dashboard activity returned
      401:
        description: Missing or invalid auth token
      404:
        description: Authenticated user not found or inactive
    """
    user_id = UUID(get_jwt_identity())

    payload = ProjectService.get_dashboard_project_activity(user_id=user_id)
    return success_response(data=ProjectSchema.serialize_dashboard_project_activity(payload))


@project_bp.put("/<project_id>")
def update_project(project_id):
    """Update project metadata.
    ---
    tags:
      - Projects
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
            description:
              type: string
            visibility:
              type: string
              enum: [PUBLIC, PRIVATE]
              default: PRIVATE
    responses:
      200:
        description: Project updated
      400:
        description: Validation error
      404:
        description: Project not found
    """
    data = request.get_json() or {}

    project = ProjectService.updateProject(
        project_id=UUID(project_id),
        name=data.get("name"),
        description=data.get("description"),
        visibility=data.get("visibility", "PRIVATE"),
    )

    return success_response(data=ProjectSchema.serialize_project(project))


@project_bp.patch("/<project_id>/archive")
@jwt_required()
def change_project_archive_status(project_id):
    """Archive or unarchive a project.
    ---
    tags:
      - Projects
    security:
      - Bearer: []
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - action
          properties:
            action:
              type: string
              enum: [archive, unarchive]
    responses:
      200:
        description: Project archive status changed
      401:
        description: Missing or invalid auth token
      400:
        description: Validation error
      403:
        description: User is not the project owner
      404:
        description: Project not found
    """
    data = request.get_json() or {}

    project = ProjectService.change_archive_status(
        project_id=UUID(project_id),
        user_id=UUID(get_jwt_identity()),
        action=data.get("action"),
    )

    return success_response(data=ProjectSchema.serialize_project(project))
