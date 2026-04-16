from datetime import date, timedelta

from app.extensions import db
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.user import User


class TimeEntryRepository:
    @staticmethod
    def _build_filtered_query(
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

        return query

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
        query = TimeEntryRepository._build_filtered_query(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            search_string=search_string,
        )

        return query.order_by(TimeEntry.work_date.desc()).all()

    @staticmethod
    def get_time_entry_summary_by_user_and_date_range_and_project(
        *,
        user_id=None,
        start_date=None,
        end_date=None,
        project_id=None,
        search_string=None,
        today=None,
    ):
        current_day = today or date.today()
        start_of_week = current_day.fromordinal(current_day.toordinal() - current_day.weekday())
        start_of_month = current_day.replace(day=1)

        entries = TimeEntryRepository._build_filtered_query(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            search_string=search_string,
        ).all()

        total_entries = len(entries)
        total_minutes = sum(entry.duration_minutes for entry in entries)
        entries_today = sum(1 for entry in entries if entry.work_date == current_day)
        entries_week = sum(
            1 for entry in entries if start_of_week <= entry.work_date <= current_day
        )
        entries_month = sum(
            1 for entry in entries if start_of_month <= entry.work_date <= current_day
        )
        minutes_today = sum(
            entry.duration_minutes for entry in entries if entry.work_date == current_day
        )

        return {
            "total_entries": total_entries,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
            "entries_today": entries_today,
            "entries_current_week": entries_week,
            "entries_current_month": entries_month,
            "minutes_today": minutes_today,
            "hours_today": round(minutes_today / 60, 2),
        }

    @staticmethod
    def get_user_dashboard_activity(*, user_id, start_date, end_date):
        entries = (
            TimeEntry.query.filter(
                TimeEntry.deleted_at.is_(None),
                TimeEntry.user_id == user_id,
                TimeEntry.work_date >= start_date,
                TimeEntry.work_date <= end_date,
            )
            .order_by(TimeEntry.work_date.asc())
            .all()
        )

        minutes_by_day = {}
        for entry in entries:
            minutes_by_day[entry.work_date] = (
                minutes_by_day.get(entry.work_date, 0) + entry.duration_minutes
            )

        points = []
        current_day = start_date
        while current_day <= end_date:
            minutes = minutes_by_day.get(current_day, 0)
            points.append(
                {
                    "date": current_day.isoformat(),
                    "minutes": minutes,
                    "hours": round(minutes / 60, 2),
                }
            )
            current_day += timedelta(days=1)

        return points

    @staticmethod
    def get_recent_user_dashboard_preview_entries(*, user_id, limit=4):
        entries = (
            TimeEntry.query.join(Project, TimeEntry.project_id == Project.id)
            .filter(
                TimeEntry.deleted_at.is_(None),
                TimeEntry.user_id == user_id,
            )
            .order_by(TimeEntry.work_date.desc(), TimeEntry.created_at.desc())
            .limit(limit)
            .all()
        )

        preview = []
        for entry in entries:
            preview.append(
                {
                    "id": str(entry.id),
                    "day": entry.work_date.day,
                    "month": entry.work_date.month,
                    "title": entry.project.name,
                    "description": entry.description,
                    "time": entry.duration_minutes,
                }
            )

        return preview

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
