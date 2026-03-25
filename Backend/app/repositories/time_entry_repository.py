from app.extensions import db
from app.models.time_entry import TimeEntry

class TimeEntryRepository:

    @staticmethod
    def save(time_entry: TimeEntry) -> TimeEntry :
        db.session.add(time_entry)
        db.session.commit()
        return time_entry
    
    @staticmethod
    def get_time_entry_by_id(time_entry_id):
        return db.session.get(TimeEntry, time_entry_id)
    
    @staticmethod
    def get_time_entries_by_user_and_date_range_and_project(user_id=None, start_date=None, end_date=None, project_id=None, search_string=None):
        query = TimeEntry.query.filter(TimeEntry.deleted_at.is_(None))

        if user_id:
            query = query.filter(TimeEntry.user_id == user_id)

        if start_date:
            query = query.filter(TimeEntry.work_date >= start_date)

        if end_date:
            query = query.filter(TimeEntry.work_date <= end_date)

        if project_id:
            query = query.filter(TimeEntry.project_id == project_id)

        if search_string:
            query = query.filter(TimeEntry.description.ilike(f"%{search_string}%"))

        return query.order_by(TimeEntry.work_date.desc()).all()