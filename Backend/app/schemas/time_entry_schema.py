class TimeEntrySchema:
    @staticmethod
    def serialize_time_entry(time_entry):
        return {
            "id": str(time_entry.id),
            "user_id": str(time_entry.user_id),
            "project_id": str(time_entry.project_id),
            "description": time_entry.description,
            "date": time_entry.work_date.isoformat(),
            "hours": time_entry.duration_minutes,
        }
