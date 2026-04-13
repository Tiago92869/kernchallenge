from app.extensions import db
from app.models.project import Project, ProjectVisibility
from app.models.project_member import ProjectMember
from sqlalchemy import or_
from sqlalchemy.orm import joinedload


class ProjectRepository:
    @staticmethod
    def save(project: Project) -> Project:
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_by_id(project_id):
        return db.session.get(Project, project_id)

    @staticmethod
    def list_available_projects(*, user_id, search: str | None = None, my_projects: bool = False):
        query = Project.query.options(
            joinedload(Project.project_members).joinedload(ProjectMember.user)
        )

        if my_projects:
            query = query.filter(Project.owner_id == user_id)
        else:
            query = query.filter(
                or_(
                    Project.visibility == ProjectVisibility.PUBLIC,
                    Project.owner_id == user_id,
                )
            )

        normalized_search = (search or "").strip()
        if normalized_search:
            query = query.filter(Project.name.ilike(f"%{normalized_search}%"))

        return query.order_by(Project.created_at.desc()).all()
