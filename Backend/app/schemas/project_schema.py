class ProjectSchema:
    @staticmethod
    def serialize_project(project):
        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "visibility": project.visibility.value,
            "is_archived": project.is_archived,
            "owner_id": str(project.owner_id),
        }
    
    @staticmethod
    def serialize_project_info(projects):
        return {
            "id": str(projects.id),
            "name": projects.name,
            "visibility": projects.visibility.value,
            "is_archived": projects.is_archived,
            "is_owner": projects.is_owner,
            "number_of_members": projects.number_of_members,
            "created_at": projects.created_at.isoformat(),
            "last_entry_at": projects.last_entry_at.isoformat() if projects.last_entry_at else None,
            "members": [
                {
                    "id": str(member.id),
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "email": member.email,
                }
                for member in projects.members
            ],
        }
    
    @staticmethod
    def serialize_project_infos_list():
        return lambda projects_list: [ProjectSchema.serialize_project_info(project) for project in projects_list]
