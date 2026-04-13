from uuid import UUID

from app.api.responses import success_response
from app.schemas.project_schema import ProjectSchema
from app.services.project_service import ProjectService
from flask import Blueprint, request

project_bp = Blueprint("projects", __name__, url_prefix="/projects")


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
