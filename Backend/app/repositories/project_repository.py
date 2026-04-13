from app.extensions import db
from app.models.project import Project


class ProjectRepository:
    @staticmethod
    def save(project: Project) -> Project:
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_by_id(project_id):
        return db.session.get(Project, project_id)
