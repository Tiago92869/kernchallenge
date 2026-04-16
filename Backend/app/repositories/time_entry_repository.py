from app.extensions import db
from app.models.time_entry import TimeEntry
from app.models.user import User


class TimeEntryRepository:
    @staticmethod
    def save(time_entry: TimeEntry) -> TimeEntry:
        db.session.add(time_entry)
        db.session.commit()
        return time_entry

    @staticmethod
    def get_time_entry_by_id(time_entry_id):
        return db.session.get(TimeEntry, time_entry_id)

    @staticmethod
    def get_time_entries_by_user_and_date_range_and_project(
        user_id=None, start_date=None, end_date=None, project_id=None, search_string=None
    ):
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

    @staticmethod
    def get_time_entries_by_project(
        project_id,
        user_id_filter=None,
        start_date=None,
        end_date=None,
        search_string=None,
    ):
        """Get time entries for a project without visibility checks (caller responsible)."""
        query = TimeEntry.query.filter(
            TimeEntry.project_id == project_id, TimeEntry.deleted_at.is_(None)
        )

        if user_id_filter:
            query = query.filter(TimeEntry.user_id == user_id_filter)

        if start_date:
            query = query.filter(TimeEntry.work_date >= start_date)

        if end_date:
            query = query.filter(TimeEntry.work_date <= end_date)

        if search_string:
            query = query.filter(TimeEntry.description.ilike(f"%{search_string}%"))

        return query.order_by(TimeEntry.work_date.desc()).all()

    @staticmethod
    def get_member_time_aggregation_by_project(
        project_id,
        period,
        start_date=None,
        end_date=None,
    ):
        query = TimeEntry.query.join(User, TimeEntry.user_id == User.id).filter(
            TimeEntry.project_id == project_id,
            TimeEntry.deleted_at.is_(None),
        )

        if start_date:
            query = query.filter(TimeEntry.work_date >= start_date)

        if end_date:
            query = query.filter(TimeEntry.work_date <= end_date)

        entries = query.order_by(TimeEntry.work_date.asc()).all()

        totals = {}
        member_info = {}

        for entry in entries:
            if period == "week":
                period_start = entry.work_date.fromordinal(
                    entry.work_date.toordinal() - entry.work_date.weekday()
                )
            else:
                period_start = entry.work_date.replace(day=1)

            key = (entry.user_id, period_start)
            totals[key] = totals.get(key, 0) + entry.duration_minutes
            member_info[entry.user_id] = {
                "member_id": str(entry.user.id),
                "first_name": entry.user.first_name,
                "last_name": entry.user.last_name,
            }

        aggregated = []
        for (member_id, period_start), total_minutes in sorted(
            totals.items(), key=lambda item: (item[0][1], item[0][0]), reverse=True
        ):
            aggregated.append(
                {
                    "period_start": period_start.isoformat(),
                    "period": period,
                    **member_info[member_id],
                    "total_minutes": total_minutes,
                }
            )

        return aggregated
