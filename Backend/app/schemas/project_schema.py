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
