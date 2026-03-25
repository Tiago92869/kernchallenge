from datetime import datetime
from uuid import UUID

from app.api.errors import NotFoundError, ValidationError
from app.models.project_member import ProjectMember
from app.models.project import Project
from app.models.user import User
from app.repositories.project_member_repository import ProjectMemberRepository
from app.services.user_service import UserService
from app.services.project_service import ProjectService

class ProjectMemberService:

    @staticmethod
    def add_member_to_project(project_id:UUID, users_ids:list[UUID]) :

        #call project service to if the project exits and is not archived
        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        #for each user uuid make sure the user exists and is active
        for user_id in users_ids:
            if not UserService.does_user_exist_and_active(user_id):
                raise NotFoundError(message=f"User with id {user_id} not found or is not active")

            project_member = ProjectMemberRepository.get_by_project_and_user(project_id, user_id)

            #if he is but we have a removed_at date we will set it to null and save the project member
            if project_member and project_member.removed_at is not None:
                project_member.removed_at = None
                project_member.removed_by_user_id = None
                ProjectMemberRepository.save(project_member)
                continue

            if not project_member:
                project_member = ProjectMember(
                    project_id=project_id,
                    user_id=user_id,
                    # TODO missing added_by_user_id once auth context exists.
                )
                ProjectMemberRepository.save(project_member)

    @staticmethod
    def remove_member_from_project(project_id: UUID, user_id: UUID) -> ProjectMember:
        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        project_member = ProjectMemberRepository.get_by_id(user_id, project_id)

        if not project_member:
            raise NotFoundError(message="Project member not found")

        project_member.removed_at = datetime.now()
        # TODO missing removed_by_user_id once auth context exists.
        project_member.removed_by_user_id = None

        return ProjectMemberRepository.save(project_member)
            
            