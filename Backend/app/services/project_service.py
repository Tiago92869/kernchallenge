from datetime import datetime
from types import SimpleNamespace
from uuid import UUID

from app.api.errors import ForbiddenError, NotFoundError, ValidationError
from app.models.project import Project, ProjectVisibility
from app.repositories.project_repository import ProjectRepository


class ProjectService:
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

        return ProjectRepository.save(project)

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
            members = []
            for project_member in project.project_members:
                if project_member.removed_at is not None:
                    continue

                user = project_member.user
                if not user or not user.is_active:
                    continue

                members.append(
                    SimpleNamespace(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                    )
                )

            serialized_projects.append(
                SimpleNamespace(
                    id=project.id,
                    name=project.name,
                    visibility=project.visibility,
                    is_archived=project.is_archived,
                    is_owner=project.owner_id == user_id,
                    number_of_members=len(members),
                    created_at=project.created_at,
                    last_entry_at=project.last_entry_added_at,
                    members=members,
                )
            )

        return serialized_projects
