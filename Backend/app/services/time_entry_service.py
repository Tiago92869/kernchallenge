from datetime import date, datetime, timedelta
from uuid import UUID

from app.api.errors import ForbiddenError, NotFoundError, ValidationError
from app.models.time_entry import TimeEntry
from app.repositories.project_member_repository import ProjectMemberRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.time_entry_repository import TimeEntryRepository
from app.services.project_service import ProjectService
from app.services.user_service import UserService


class TimeEntryService:
    @staticmethod
    def create_time_entry(
        user_id: UUID, project_id: UUID, work_date: date, duration_minutes: int, description: str
    ) -> TimeEntry:

        if duration_minutes <= 0:
            raise ValidationError(message="Hours should be a positive number")

        if work_date > date.today():
            raise ValidationError(message="Date should not be in the future")

        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        time_entry = TimeEntry(
            user_id=user_id,
            project_id=project_id,
            description=description,
            work_date=work_date,
            duration_minutes=duration_minutes,
        )

        return TimeEntryRepository.save(time_entry)

    @staticmethod
    def get_time_entry_by_id(time_entry_id: UUID) -> TimeEntry:

        time_entry = TimeEntryRepository.get_time_entry_by_id(time_entry_id)

        if not time_entry:
            raise NotFoundError(message="Time entry not found")

        return time_entry

    @staticmethod
    def get_time_entries_by_user_and_date_range_and_project(
        user_id=None, start_date=None, end_date=None, project_id=None, search_string=None
    ) -> list[TimeEntry]:

        if project_id and not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if user_id and not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        if start_date and end_date and start_date > end_date:
            raise ValidationError(message="Start date should be before end date")

        return TimeEntryRepository.get_time_entries_by_user_and_date_range_and_project(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            search_string=search_string,
        )

    @staticmethod
    def get_time_entry_summary_by_user_and_date_range_and_project(
        user_id=None, start_date=None, end_date=None, project_id=None, search_string=None
    ) -> dict:
        if project_id and not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if user_id and not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        if start_date and end_date and start_date > end_date:
            raise ValidationError(message="Start date should be before end date")

        return TimeEntryRepository.get_time_entry_summary_by_user_and_date_range_and_project(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            project_id=project_id,
            search_string=search_string,
        )

    @staticmethod
    def update_time_entry_by_id(
        time_entry_id: UUID,
        user_id: UUID,
        project_id: UUID,
        work_date: date,
        duration_minutes: int,
        description: str,
    ) -> TimeEntry:
        time_entry = TimeEntryRepository.get_time_entry_by_id(time_entry_id)

        if not time_entry:
            raise NotFoundError(message="Time entry not found")

        if time_entry.user_id != user_id:
            raise NotFoundError(message="You do not have permission to update this time entry")

        if duration_minutes <= 0:
            raise ValidationError(message="Hours should be a positive number")

        if work_date > date.today():
            raise ValidationError(message="Date should not be in the future")

        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        time_entry.project_id = project_id
        time_entry.description = description
        time_entry.work_date = work_date
        time_entry.duration_minutes = duration_minutes

        return TimeEntryRepository.save(time_entry)

    @staticmethod
    def delete_time_entry_by_id(time_entry_id: UUID, user_id: UUID) -> None:
        time_entry = TimeEntryRepository.get_time_entry_by_id(time_entry_id)

        if not time_entry:
            raise NotFoundError(message="Time entry not found")

        if time_entry.user_id != user_id:
            raise NotFoundError(message="You do not have permission to delete this time entry")

        time_entry.deleted_at = datetime.now()
        # TODO missing deleted_by_user_id once auth context exists.

        TimeEntryRepository.save(time_entry)

    @staticmethod
    def get_time_entries_by_project_with_role_visibility(
        project_id: UUID,
        user_id: UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        search_string: str | None = None,
    ) -> list[TimeEntry]:
        """Get project time entries respecting role-based visibility rules.

        Owner: sees all entries
        Regular member: sees only their own entries
        Non-member: denied
        """
        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        project = ProjectRepository.get_by_id(project_id)

        is_owner = project.owner_id == user_id
        is_member = ProjectMemberRepository.get_by_id(user_id, project_id) is not None

        if not is_owner and not is_member:
            raise ForbiddenError(message="User does not have access to this project")

        owner_sees_all = is_owner
        member_filter_user_id = None if owner_sees_all else user_id

        if start_date and end_date and start_date > end_date:
            raise ValidationError(message="Start date should be before end date")

        return TimeEntryRepository.get_time_entries_by_project(
            project_id=project_id,
            user_id_filter=member_filter_user_id,
            start_date=start_date,
            end_date=end_date,
            search_string=search_string,
        )

    @staticmethod
    def get_member_time_aggregation_by_project(
        project_id: UUID,
        user_id: UUID,
        period: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict]:
        if period not in {"week", "month"}:
            raise ValidationError(message="Invalid period, expected 'week' or 'month'")

        if not ProjectService.does_project_exist_and_active(project_id):
            raise NotFoundError(message="Project not found or is archived")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        if start_date and end_date and start_date > end_date:
            raise ValidationError(message="Start date should be before end date")

        project = ProjectRepository.get_by_id(project_id)
        if project.owner_id != user_id:
            raise ForbiddenError(message="Only project owner can access member aggregation")

        return TimeEntryRepository.get_member_time_aggregation_by_project(
            project_id=project_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def get_dashboard_activity_for_user(*, user_id: UUID, period: str) -> dict:
        if period not in {"7d", "30d"}:
            raise ValidationError(message="Invalid period, expected '7d' or '30d'")

        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        end_date = date.today()
        days = 7 if period == "7d" else 30
        start_date = end_date - timedelta(days=days - 1)

        points = TimeEntryRepository.get_user_dashboard_activity(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )

        total_minutes = sum(point["minutes"] for point in points)
        return {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "points": points,
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 2),
        }

    @staticmethod
    def get_dashboard_preview_for_user(*, user_id: UUID) -> list[dict]:
        if not UserService.does_user_exist_and_active(user_id):
            raise NotFoundError(message=f"User with id {user_id} not found or is not active")

        return TimeEntryRepository.get_recent_user_dashboard_preview_entries(
            user_id=user_id,
            limit=4,
        )
