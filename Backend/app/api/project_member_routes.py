from uuid import UUID

from app.api.responses import success_response
from app.schemas.project_member_schema import ProjectMemberSchema
from app.services.project_member_service import ProjectMemberService
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

project_member_bp = Blueprint("project_members", __name__, url_prefix="/project-members")


@project_member_bp.get("/<project_id>/active")
@jwt_required()
def get_currently_active_members(project_id):
    """Get active members of a project.
    ---
    tags:
      - Project Members
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Active member list returned
      404:
        description: Project not found or archived
    """
    project_members = ProjectMemberService.get_currently_active_members(
      UUID(project_id),
      actor_user_id=UUID(get_jwt_identity()),
    )

    return success_response(
        data=[
            ProjectMemberSchema.serialize_project_member(project_member)
            for project_member in project_members
        ]
    )


@project_member_bp.put("/<project_id>/add")
@jwt_required()
def add_member_to_project(project_id):
    """Add one or more members to a project.
    ---
    tags:
      - Project Members
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
            - users_ids
          properties:
            users_ids:
              type: array
              items:
                type: string
                format: uuid
    responses:
      200:
        description: Members added successfully
      404:
        description: Project or user not found
    """
    data = request.get_json() or {}

    ProjectMemberService.add_member_to_project(
        project_id=UUID(project_id),
        users_ids=[UUID(user_id) for user_id in data.get("users_ids", [])],
      actor_user_id=UUID(get_jwt_identity()),
    )

    return success_response(message="Project members added successfully")


@project_member_bp.put("/<project_id>/<user_id>/remove")
@jwt_required()
def remove_member_from_project(project_id, user_id):
    """Remove a member from a project.
    ---
    tags:
      - Project Members
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
      - in: path
        name: user_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Member removed successfully
      404:
        description: Project, user, or membership not found
    """
    ProjectMemberService.remove_member_from_project(
        project_id=UUID(project_id),
        user_id=UUID(user_id),
      actor_user_id=UUID(get_jwt_identity()),
    )

    return success_response(message="Project member removed successfully")
