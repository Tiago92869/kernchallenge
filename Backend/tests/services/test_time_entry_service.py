from datetime import date, timedelta
from uuid import UUID

import pytest

from app.api.errors import ForbiddenError, NotFoundError, ValidationError
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


def test_get_time_entries_by_project_owner_sees_all(
    time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="project-owner-all@test.com")
    member1 = user_factory(email="project-member1-all@test.com")
    member2 = user_factory(email="project-member2-all@test.com")
    project = project_factory(owner=owner)

    project_member_factory(project=project, user=member1)
    project_member_factory(project=project, user=member2)

    time_entry_factory(user=owner, project=project, description="Owner entry")
    time_entry_factory(user=member1, project=project, description="Member1 entry")
    time_entry_factory(user=member2, project=project, description="Member2 entry")

    results = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=project.id,
        user_id=owner.id,
    )

    assert len(results) == 3
    descriptions = {e.description for e in results}
    assert "Owner entry" in descriptions
    assert "Member1 entry" in descriptions
    assert "Member2 entry" in descriptions


def test_get_time_entries_by_project_member_sees_own_only(
    time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="project-owner-member@test.com")
    member1 = user_factory(email="project-member1-view@test.com")
    member2 = user_factory(email="project-member2-view@test.com")
    project = project_factory(owner=owner)

    project_member_factory(project=project, user=member1)
    project_member_factory(project=project, user=member2)

    time_entry_factory(user=owner, project=project, description="Owner entry")
    time_entry_factory(user=member1, project=project, description="Member1 entry 1")
    time_entry_factory(user=member1, project=project, description="Member1 entry 2")
    time_entry_factory(user=member2, project=project, description="Member2 entry")

    results = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=project.id,
        user_id=member1.id,
    )

    assert len(results) == 2
    descriptions = {e.description for e in results}
    assert "Member1 entry 1" in descriptions
    assert "Member1 entry 2" in descriptions
    assert "Owner entry" not in descriptions
    assert "Member2 entry" not in descriptions


def test_get_time_entries_by_project_denies_non_member(user_factory, project_factory):
    owner = user_factory(email="project-owner-deny@test.com")
    non_member = user_factory(email="project-non-member@test.com")
    project = project_factory(owner=owner)

    with pytest.raises(ForbiddenError) as exc_info:
        TimeEntryService.get_time_entries_by_project_with_role_visibility(
            project_id=project.id,
            user_id=non_member.id,
        )

    assert exc_info.value.message == "User does not have access to this project"


def test_get_time_entries_by_project_with_date_filter(
    time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="project-owner-date@test.com")
    member = user_factory(email="project-member-date@test.com")
    project = project_factory(owner=owner)

    project_member_factory(project=project, user=member)

    early = date.today() - timedelta(days=5)
    middle = date.today() - timedelta(days=2)
    recent = date.today()

    time_entry_factory(user=member, project=project, work_date=early, description="Early entry")
    time_entry_factory(user=member, project=project, work_date=middle, description="Middle entry")
    time_entry_factory(user=member, project=project, work_date=recent, description="Recent entry")

    results = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=project.id,
        user_id=member.id,
        start_date=date.today() - timedelta(days=3),
        end_date=date.today(),
    )

    assert len(results) == 2
    descriptions = {e.description for e in results}
    assert "Middle entry" in descriptions
    assert "Recent entry" in descriptions
    assert "Early entry" not in descriptions


def test_get_time_entries_by_project_with_search_filter(
    time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="project-owner-search@test.com")
    member = user_factory(email="project-member-search@test.com")
    project = project_factory(owner=owner)

    project_member_factory(project=project, user=member)

    time_entry_factory(user=member, project=project, description="Fixed bug in dashboard")
    time_entry_factory(user=member, project=project, description="Implemented new API endpoint")
    time_entry_factory(user=member, project=project, description="Updated documentation")

    results = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=project.id,
        user_id=member.id,
        search_string="dashboard",
    )

    assert len(results) == 1
    assert results[0].description == "Fixed bug in dashboard"


def test_get_time_entries_by_project_excludes_deleted(
    time_entry_factory, user_factory, project_factory, project_member_factory
):
    owner = user_factory(email="project-owner-deleted@test.com")
    member = user_factory(email="project-member-deleted@test.com")
    project = project_factory(owner=owner)

    project_member_factory(project=project, user=member)

    active_entry = time_entry_factory(user=member, project=project, description="Active entry")
    deleted_entry = time_entry_factory(user=member, project=project, description="Deleted entry")
    TimeEntryService.delete_time_entry_by_id(deleted_entry.id, member.id)

    results = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=project.id,
        user_id=member.id,
    )

    assert len(results) == 1
    assert results[0].description == "Active entry"


def test_get_time_entries_by_project_raises_for_archived_project(user_factory, project_factory):
    owner = user_factory(email="project-owner-archived@test.com")
    project = project_factory(owner=owner, is_archived=True)

    with pytest.raises(NotFoundError) as exc_info:
        TimeEntryService.get_time_entries_by_project_with_role_visibility(
            project_id=project.id,
            user_id=owner.id,
        )

    assert exc_info.value.message == "Project not found or is archived"


def test_get_time_entries_by_project_raises_for_invalid_date_range(user_factory, project_factory):
    owner = user_factory(email="project-owner-invalid-date@test.com")
    project = project_factory(owner=owner)

    with pytest.raises(ValidationError) as exc_info:
        TimeEntryService.get_time_entries_by_project_with_role_visibility(
            project_id=project.id,
            user_id=owner.id,
            start_date=date.today(),
            end_date=date.today() - timedelta(days=1),
        )

    assert exc_info.value.message == "Start date should be before end date"
