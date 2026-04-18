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
            "is_member": projects.is_member,
            "user_role": projects.user_role,
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
        return lambda projects_list: [
            ProjectSchema.serialize_project_info(project) for project in projects_list
        ]

    @staticmethod
    def serialize_project_details(project):
        return {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "visibility": project.visibility.value,
            "is_archived": project.is_archived,
            "owner_id": str(project.owner_id),
            "is_owner": project.is_owner,
            "user_role": project.user_role,
            "number_of_members": project.number_of_members,
            "created_at": project.created_at.isoformat(),
            "last_entry_at": project.last_entry_at.isoformat() if project.last_entry_at else None,
            "members": [
                {
                    "id": str(member.id),
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "email": member.email,
                }
                for member in project.members
            ],
        }

    @staticmethod
    def serialize_dashboard_project(project):
        return {
            "id": str(project.id),
            "name": project.name,
            "visibility": project.visibility.value,
            "is_archived": project.is_archived,
            "owner_id": str(project.owner_id),
            "updated_at": project.updated_at.isoformat(),
            "last_entry_at": project.last_entry_added_at.isoformat()
            if project.last_entry_added_at
            else None,
        }

    @staticmethod
    def serialize_dashboard_project_activity(payload):
        return {
            "my_projects": [
                ProjectSchema.serialize_dashboard_project(project)
                for project in payload["my_projects"]
            ],
            "owner_projects": [
                ProjectSchema.serialize_dashboard_project(project)
                for project in payload["owner_projects"]
            ],
        }
