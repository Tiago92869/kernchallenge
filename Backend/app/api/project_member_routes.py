from uuid import UUID

from flask import Blueprint, request

from app.api.responses import success_response
from app.schemas.project_member_schema import ProjectMemberSchema
from app.services.project_member_service import ProjectMemberService


project_member_bp = Blueprint("project_members", __name__, url_prefix="/project-members")


@project_member_bp.get("/<project_id>/active")
def get_currently_active_members(project_id):
    project_members = ProjectMemberService.get_currently_active_members(UUID(project_id))

    return success_response(
        data=[
            ProjectMemberSchema.serialize_project_member(project_member)
            for project_member in project_members
        ]
    )


@project_member_bp.put("/<project_id>/add")
def add_member_to_project(project_id):
    data = request.get_json() or {}

    ProjectMemberService.add_member_to_project(
        project_id=UUID(project_id),
        users_ids=[UUID(user_id) for user_id in data.get("users_ids", [])],
    )

    return success_response(message="Project members added successfully")


@project_member_bp.put("/<project_id>/<user_id>/remove")
def remove_member_from_project(project_id, user_id):
    ProjectMemberService.remove_member_from_project(
        project_id=UUID(project_id),
        user_id=UUID(user_id),
    )

    return success_response(message="Project member removed successfully")
