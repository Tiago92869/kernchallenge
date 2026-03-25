from app.extensions import db
from app.models.project_member import ProjectMember
from app.models.user import User

class ProjectMemberRepository:

    @staticmethod
    def save(project_member: ProjectMember) -> ProjectMember :
        db.session.add(project_member)
        db.session.commit()
        return project_member
    
    @staticmethod
    def get_by_id(user_id, project_id):
        return ProjectMember.query.filter_by(user_id=user_id, project_id=project_id, removed_at=None).first()

    @staticmethod
    def get_by_project_and_user(project_id, user_id):
        return ProjectMember.query.filter_by(project_id=project_id, user_id=user_id).first()

    @staticmethod
    def get_currently_active_members(project_id):
        return (
            ProjectMember.query
            .join(User, ProjectMember.user_id == User.id)
            .filter(
                ProjectMember.project_id == project_id,
                ProjectMember.removed_at.is_(None),
                User.is_active.is_(True),
            )
            .all()
        )
    
