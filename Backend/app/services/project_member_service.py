from datetime import datetime
from uuid import UUID

from app.api.errors import NotFoundError
from app.models.project_member import ProjectMember
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.services.user_service import UserService
from app.services.project_service import ProjectService
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

class ProjectMemberService:

    @staticmethod
    def add_member_to_project(project_id:UUID, users_ids:list[UUID]) :

        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        project = ProjectRepository.get_by_id(project_id)
        owner = project.owner
        owner_full_name = f"{owner.first_name} {owner.last_name}".strip()

        for user_id in users_ids:
            if not UserService.does_user_exist_and_active(user_id):
                raise NotFoundError(message=f"User with id {user_id} not found or is not active")

            project_member = ProjectMemberRepository.get_by_project_and_user(project_id, user_id)

            if project_member and project_member.removed_at is not None:
                project_member.removed_at = None
                project_member.removed_by_user_id = None
                ProjectMemberRepository.save(project_member)
            elif not project_member:
                project_member = ProjectMember(
                    project_id=project_id,
                    user_id=user_id,
                    # TODO missing added_by_user_id once auth context exists.
                )
                ProjectMemberRepository.save(project_member)
            else:
                continue

            NotificationService.create_notification(
                recipient_user_id=user_id,
                actor_user_id=project.owner_id,
                project_id=project_id,
                notification_type=NotificationType.ADDED,
                message=f'"{owner_full_name}" just added you to "{project.name}"',
            )

    @staticmethod
    def remove_member_from_project(project_id: UUID, user_id: UUID) -> ProjectMember:
        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        project_member = ProjectMemberRepository.get_by_id(user_id, project_id)

        if not project_member:
            raise NotFoundError(message="Project member not found")

        project = ProjectRepository.get_by_id(project_id)
        owner = project.owner
        owner_full_name = f"{owner.first_name} {owner.last_name}".strip()
        removed_at = datetime.now()

        project_member.removed_at = removed_at
        # TODO missing removed_by_user_id once auth context exists.
        project_member.removed_by_user_id = None

        updated_member = ProjectMemberRepository.save(project_member)

        NotificationService.create_notification(
            recipient_user_id=user_id,
            actor_user_id=project.owner_id,
            project_id=project_id,
            notification_type=NotificationType.REMOVED,
            message=f'"{owner_full_name}" just removed you from "{project.name}" at "{removed_at.date().isoformat()}"',
        )

        return updated_member

    @staticmethod
    def get_currently_active_members(project_id: UUID) -> list[ProjectMember]:
        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        return ProjectMemberRepository.get_currently_active_members(project_id)
            
            