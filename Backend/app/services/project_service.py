from datetime import datetime
from types import SimpleNamespace
from uuid import UUID

from app.api.errors import ForbiddenError, NotFoundError, ValidationError
from app.models.notification import NotificationType
from app.models.project import Project, ProjectVisibility
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.services.notification_service import NotificationService
from app.services.user_service import UserService


class ProjectService:
    @staticmethod
    def _notify_active_members_project_archived(*, project_id: UUID, actor_user_id: UUID) -> None:
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return

        owner_full_name = f"{project.owner.first_name} {project.owner.last_name}".strip()
        members = ProjectMemberRepository.get_currently_active_members(project_id)

        for project_member in members:
            recipient_user_id = project_member.user_id
            if recipient_user_id == actor_user_id:
                continue

            NotificationService.create_notification(
                recipient_user_id=recipient_user_id,
                actor_user_id=actor_user_id,
                project_id=project_id,
                notification_type=NotificationType.ARCHIVED,
                message=f'"{owner_full_name}" archived project "{project.name}"',
            )

    @staticmethod
    def create_project(
        *,
        owner_id: UUID,
        name: str,
        description: str | None,
        visibility: str,
    ) -> Project:
        # remove empty spaces
        normalized_name = name.strip()

        if not normalized_name:
            raise ValidationError(message="Project name is required")

        try:
            project_visibility = ProjectVisibility[visibility.upper()]
        except KeyError as exc:
            raise ValidationError(message="Invalid project visibility") from exc

        project = Project(
            name=normalized_name,
            description=description.strip() if description else None,
            visibility=project_visibility,
            owner_id=owner_id,
        )

        return ProjectRepository.save(project)

    @staticmethod
    def updateProject(
        *,
        project_id: UUID,
        name: str,
        description: str | None,
        visibility: str,
    ) -> Project:
        project = ProjectRepository.get_by_id(project_id)

        if not project:
            raise NotFoundError(message="Project not found")

        normalized_name = name.strip()

        if not normalized_name:
            raise ValidationError(message="Project name is required")

        try:
            project_visibility = ProjectVisibility[visibility.upper()]
        except KeyError as exc:
            raise ValidationError(message="Invalid project visibility") from exc

        project.name = normalized_name
        project.description = description.strip() if description else None
        project.visibility = project_visibility

        return ProjectRepository.save(project)

    @staticmethod
    def does_project_exist_and_active(project_id: UUID) -> bool:
        project = ProjectRepository.get_by_id(project_id)
        return project is not None and project.archived_at is None

    @staticmethod
    def change_archive_status(*, project_id: UUID, user_id: UUID, action: str) -> Project:
        project = ProjectRepository.get_by_id(project_id)

        if not project:
            raise NotFoundError(message="Project not found")

        if project.owner_id != user_id:
            raise ForbiddenError(message="User is not the project owner")

        normalized_action = (action or "").strip().lower()
        if normalized_action not in {"archive", "unarchive"}:
            raise ValidationError(message="Invalid action. Use 'archive' or 'unarchive'")

        should_archive = normalized_action == "archive"

        if project.is_archived == should_archive:
            raise ValidationError(message="Project already in requested state")

        if should_archive:
            project.is_archived = True
            project.archived_at = datetime.now()
            project.archived_by_user_id = user_id
        else:
            project.is_archived = False
            project.archived_at = None
            project.archived_by_user_id = None
            project.archived_reason = None

        updated_project = ProjectRepository.save(project)

        if should_archive:
            ProjectService._notify_active_members_project_archived(
                project_id=project.id,
                actor_user_id=user_id,
            )

        return updated_project

    @staticmethod
    def list_available_projects(
        *,
        user_id: UUID,
        search: str | None = None,
        my_projects: bool = False,
    ):
        projects = ProjectRepository.list_available_projects(
            user_id=user_id,
            search=search,
            my_projects=my_projects,
        )

        serialized_projects = []
        for project in projects:
            members_by_id = {}
            is_owner = project.owner_id == user_id
            is_member = False

            owner = project.owner
            if owner and owner.is_active:
                members_by_id[owner.id] = SimpleNamespace(
                    id=owner.id,
                    first_name=owner.first_name,
                    last_name=owner.last_name,
                    email=owner.email,
                )

            for project_member in project.project_members:
                if project_member.removed_at is not None:
                    continue

                user = project_member.user
                if not user or not user.is_active:
                    continue

                if user.id == user_id and project_member.removed_at is None:
                    is_member = True

                members_by_id[user.id] = SimpleNamespace(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                )

            members = list(members_by_id.values())

            serialized_projects.append(
                SimpleNamespace(
                    id=project.id,
                    name=project.name,
                    visibility=project.visibility,
                    is_archived=project.is_archived,
                    is_owner=is_owner,
                    is_member=is_member,
                    user_role=("OWNER" if is_owner else "MEMBER" if is_member else "VIEWER"),
                    number_of_members=len(members),
                    created_at=project.created_at,
                    last_entry_at=project.last_entry_added_at,
                    members=members,
                )
            )

        return serialized_projects

    @staticmethod
    def get_project_details(*, project_id: UUID, user_id: UUID):
        project = ProjectRepository.get_by_id(project_id)

        if not project:
            raise NotFoundError(message="Project not found")

        is_owner = project.owner_id == user_id
        is_member = ProjectMemberRepository.get_by_id(user_id, project_id) is not None
        is_public = project.visibility == ProjectVisibility.PUBLIC

        if not is_owner and not is_member and not is_public:
            raise ForbiddenError(message="User does not have access to this project")

        members_by_id = {}
        owner = project.owner
        if owner and owner.is_active:
            members_by_id[owner.id] = SimpleNamespace(
                id=owner.id,
                first_name=owner.first_name,
                last_name=owner.last_name,
                email=owner.email,
            )

        for project_member in project.project_members:
            if project_member.removed_at is not None:
                continue

            user = project_member.user
            if not user or not user.is_active:
                continue

            members_by_id[user.id] = SimpleNamespace(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
            )

        return SimpleNamespace(
            id=project.id,
            name=project.name,
            description=project.description,
            visibility=project.visibility,
            is_archived=project.is_archived,
            owner_id=project.owner_id,
            is_owner=is_owner,
            user_role="OWNER" if is_owner else "MEMBER",
            number_of_members=len(members_by_id),
            created_at=project.created_at,
            last_entry_at=project.last_entry_added_at,
            members=list(members_by_id.values()),
        )

    @staticmethod
    def get_dashboard_project_activity(*, user_id: UUID) -> dict:
        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        owner_projects = ProjectRepository.list_recent_owned_projects(user_id=user_id, limit=3)
        my_projects = ProjectRepository.list_recent_member_projects(user_id=user_id, limit=3)

        return {
            "my_projects": my_projects,
            "owner_projects": owner_projects,
        }
