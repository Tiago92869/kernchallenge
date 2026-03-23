from uuid import UUID
from app.models.project import Project, ProjectVisibility
from app.repositories.project_repository import ProjectRepository
from app.api.errors import NotFoundError, ValidationError

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
            owner_id=owner_id
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

        return ProjectRepository.save(project
    )


            