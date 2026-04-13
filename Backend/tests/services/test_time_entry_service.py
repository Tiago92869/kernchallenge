from datetime import date, timedelta
from uuid import UUID

import pytest

from app.api.errors import NotFoundError, ValidationError
from app.models.time_entry import TimeEntry
from app.services.time_entry_service import TimeEntryService


def test_create_time_entry_success(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="time-entry-create@test.com")

    time_entry = TimeEntryService.create_time_entry(
        user_id=user.id,
        project_id=project.id,
        work_date=date.today(),
        duration_minutes=120,
        description="Worked on API",
    )

    assert time_entry.id is not None
    assert time_entry.user_id == user.id
    assert time_entry.project_id == project.id
    assert time_entry.work_date == date.today()
    assert time_entry.duration_minutes == 120
    assert time_entry.description == "Worked on API"


def test_create_time_entry_raises_for_invalid_hours(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="time-entry-invalid-hours@test.com")

    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.create_time_entry(
            user_id=user.id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=0,
            description="Worked on API",
        )

    assert exc_info.value.message == "Hours should be a positive number"


def test_create_time_entry_raises_for_future_date(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="time-entry-future-date@test.com")

    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.create_time_entry(
            user_id=user.id,
            project_id=project.id,
            work_date=date.today() + timedelta(days=1),
            duration_minutes=60,
            description="Worked on API",
        )

    assert exc_info.value.message == "Date should not be in the future"


def test_create_time_entry_raises_when_project_is_archived(user_factory, project_factory):
    user = user_factory(email="time-entry-archived-project@test.com")
    project = project_factory(is_archived=True)

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.create_time_entry(
            user_id=user.id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=30,
            description="Worked on API",
        )

    assert exc_info.value.message == "Project not found or is archived"


def test_create_time_entry_raises_when_user_is_inactive(user_factory, project_factory):
    user = user_factory(email="time-entry-inactive-user@test.com", is_active=False)
    project = project_factory()

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.create_time_entry(
            user_id=user.id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=30,
            description="Worked on API",
        )

    assert exc_info.value.message == f"User with id {user.id} not found or is not active"


def test_get_time_entry_by_id_success(time_entry_factory):
    time_entry = time_entry_factory(description="Fetch test")

    result = TimeEntryService.get_time_entry_by_id(time_entry.id)

    assert result.id == time_entry.id


def test_get_time_entry_by_id_not_found(app):
    with app.app_context(), pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.get_time_entry_by_id(UUID("550e8400-e29b-41d4-a716-446655440000"))

    assert exc_info.value.message == "Time entry not found"


def test_get_time_entries_by_filters_success(time_entry_factory, user_factory, project_factory):
    user = user_factory(email="time-entry-filters-user@test.com")
    project = project_factory()
    older = date.today() - timedelta(days=3)
    newer = date.today() - timedelta(days=1)

    time_entry_factory(
        user=user, project=project, work_date=older, duration_minutes=30, description="Older"
    )
    time_entry_factory(
        user=user, project=project, work_date=newer, duration_minutes=45, description="Newer"
    )

    results = TimeEntryService.get_time_entries_by_user_and_date_range_and_project(
        user_id=user.id,
        start_date=date.today() - timedelta(days=4),
        end_date=date.today(),
        project_id=project.id,
    )

    assert len(results) == 2
    assert results[0].work_date >= results[1].work_date


def test_get_time_entries_by_filters_raises_for_invalid_date_range():
    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.get_time_entries_by_user_and_date_range_and_project(
            start_date=date.today(),
            end_date=date.today() - timedelta(days=1),
        )

    assert exc_info.value.message == "Start date should be before end date"


def test_get_time_entries_by_filters_raises_when_project_is_archived(project_factory):
    project = project_factory(is_archived=True)

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.get_time_entries_by_user_and_date_range_and_project(project_id=project.id)

    assert exc_info.value.message == "Project not found or is archived"


def test_get_time_entries_by_filters_raises_when_user_is_inactive(user_factory):
    user = user_factory(email="time-entry-filter-inactive-user@test.com", is_active=False)

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.get_time_entries_by_user_and_date_range_and_project(user_id=user.id)

    assert exc_info.value.message == f"User with id {user.id} not found or is not active"


def test_update_time_entry_by_id_success(time_entry_factory, project_factory):
    time_entry = time_entry_factory(description="Before update", duration_minutes=60)
    new_project = project_factory()

    updated = TimeEntryService.update_time_entry_by_id(
        time_entry_id=time_entry.id,
        user_id=time_entry.user_id,
        project_id=new_project.id,
        work_date=date.today(),
        duration_minutes=180,
        description="After update",
    )

    assert updated.id == time_entry.id
    assert updated.user_id == time_entry.user_id
    assert updated.project_id == new_project.id
    assert updated.duration_minutes == 180
    assert updated.description == "After update"


def test_update_time_entry_by_id_not_found(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="time-entry-update-missing@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.update_time_entry_by_id(
            time_entry_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=user.id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=60,
            description="Missing",
        )

    assert exc_info.value.message == "Time entry not found"


def test_update_time_entry_by_id_raises_for_invalid_hours(time_entry_factory, project_factory):
    time_entry = time_entry_factory(description="Before invalid hours")
    project = project_factory()

    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.update_time_entry_by_id(
            time_entry_id=time_entry.id,
            user_id=time_entry.user_id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=0,
            description="After update",
        )

    assert exc_info.value.message == "Hours should be a positive number"


def test_update_time_entry_by_id_raises_for_future_date(time_entry_factory, project_factory):
    time_entry = time_entry_factory(description="Before future date")
    project = project_factory()

    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.update_time_entry_by_id(
            time_entry_id=time_entry.id,
            user_id=time_entry.user_id,
            project_id=project.id,
            work_date=date.today() + timedelta(days=1),
            duration_minutes=60,
            description="After update",
        )

    assert exc_info.value.message == "Date should not be in the future"


def test_update_time_entry_by_id_raises_when_project_is_archived(
    time_entry_factory, project_factory
):
    time_entry = time_entry_factory(description="Before archived project")
    project = project_factory(is_archived=True)

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.update_time_entry_by_id(
            time_entry_id=time_entry.id,
            user_id=time_entry.user_id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=60,
            description="After update",
        )

    assert exc_info.value.message == "Project not found or is archived"


def test_update_time_entry_by_id_denies_when_different_user(
    time_entry_factory, user_factory, project_factory
):
    time_entry = time_entry_factory(description="Before different user")
    different_user = user_factory(email="time-entry-different-user@test.com")
    project = project_factory()

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.update_time_entry_by_id(
            time_entry_id=time_entry.id,
            user_id=different_user.id,
            project_id=project.id,
            work_date=date.today(),
            duration_minutes=60,
            description="After update",
        )

    assert exc_info.value.message == "You do not have permission to update this time entry"


def test_delete_time_entry_by_id_success(time_entry_factory):
    time_entry = time_entry_factory(description="Delete me")

    TimeEntryService.delete_time_entry_by_id(time_entry.id, time_entry.user_id)

    db_time_entry = TimeEntry.query.filter_by(id=time_entry.id).first()
    assert db_time_entry.deleted_at is not None


def test_delete_time_entry_by_id_not_found(app, user_factory):
    user = user_factory(email="time-entry-delete-not-found@test.com")
    with app.app_context():
        with pytest.raises(NotFoundError) as exc_info:
            TimeEntryService.delete_time_entry_by_id(
                UUID("550e8400-e29b-41d4-a716-446655440000"), user.id
            )

    assert exc_info.value.message == "Time entry not found"


def test_delete_time_entry_by_id_denies_when_different_user(time_entry_factory, user_factory):
    time_entry = time_entry_factory(description="Delete me")
    different_user = user_factory(email="time-entry-delete-different-user@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.delete_time_entry_by_id(time_entry.id, different_user.id)

    assert exc_info.value.message == "You do not have permission to delete this time entry"
