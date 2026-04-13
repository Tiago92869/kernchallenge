from uuid import UUID

from app.api.errors import ValidationError
from app.api.responses import success_response
from app.schemas.project_schema import ProjectSchema
from app.services.project_service import ProjectService
from flask import Blueprint, request

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
def create_project():
    data = request.get_json() or {}

    project = ProjectService.create_project(
        owner_id=UUID(data.get("owner_id")),
        name=data.get("name"),
        description=data.get("description"),
        visibility=data.get("visibility", "PRIVATE"),
    )

    return success_response(
        data=ProjectSchema.serialize_project(project),
        status_code=201,
    )


@project_bp.get("")
def list_projects():
    user_id = request.args.get("user_id")
    if not user_id:
        raise ValidationError(message="Query param 'user_id' is required")

    try:
        parsed_user_id = UUID(user_id)
    except ValueError as exc:
        raise ValidationError(message="Invalid user_id") from exc

    projects = ProjectService.list_available_projects(
        user_id=parsed_user_id,
        search=request.args.get("search"),
        my_projects=_parse_bool_query_param(
            request.args.get("my_projects"),
            field_name="my_projects",
        ),
    )

    return success_response(data=ProjectSchema.serialize_project_infos_list()(projects))


@project_bp.put("/<project_id>")
def update_project(project_id):
    data = request.get_json() or {}

    project = ProjectService.updateProject(
        project_id=UUID(project_id),
        name=data.get("name"),
        description=data.get("description"),
        visibility=data.get("visibility", "PRIVATE"),
    )

    return success_response(data=ProjectSchema.serialize_project(project))


@project_bp.patch("/<project_id>/archive")
def change_project_archive_status(project_id):
    data = request.get_json() or {}

    project = ProjectService.change_archive_status(
        project_id=UUID(project_id),
        user_id=UUID(data.get("user_id")),
        action=data.get("action"),
    )

    return success_response(data=ProjectSchema.serialize_project(project))
