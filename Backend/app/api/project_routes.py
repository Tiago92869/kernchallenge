from flask import Blueprint, request
from uuid import UUID
from app.api.responses import success_response
from app.services.project_service import ProjectService
from app.schemas.project_schema import ProjectSchema

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
