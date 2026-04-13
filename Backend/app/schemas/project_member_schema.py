class ProjectMemberSchema:
    @staticmethod
    def serialize_project_member(project_member):
        return {
            "id": str(project_member.user.id),
            "firstname": project_member.user.first_name,
            "lastname": project_member.user.last_name,
        }
