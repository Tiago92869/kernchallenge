from datetime import datetime, timedelta
from uuid import UUID

import pytest

from app.api.errors import ForbiddenError, NotFoundError, ValidationError
from app.extensions import db
from app.models.project import ProjectVisibility
from app.models.project_member import ProjectMember
from app.services.project_service import ProjectService


def test_create_project_sucess(user_factory):
    owner = user_factory()

    project = ProjectService.create_project(
        owner_id=owner.id,
        name=" TimeSync ",
        description=" This is a project ",
        visibility="PRIVATE",
    )

    assert project.id is not None
    assert project.name == "TimeSync"
    assert project.description == "This is a project"
    assert project.visibility == ProjectVisibility.PRIVATE
    assert project.owner_id == owner.id
    assert project.is_archived is False


def test_create_project_reject_blank_name(user_factory):
    owner = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.create_project(
            owner_id=owner.id, name="  ", description=" This is a project ", visibility="PRIVATE"
        )

    assert exc_info.value.message == "Project name is required"


def test_create_project_rejects_invalid_visibility(user_factory):
    owner = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.create_project(
            owner_id=owner.id, name="TimeSync", description="Main project", visibility="ERROR"
        )

    assert exc_info.value.message == "Invalid project visibility"


def test_update_project_success(project_factory):
    project = project_factory()

    project = ProjectService.updateProject(
        project_id=project.id,
        name=" TimeSyncProject ",
        description=" This is a project one ",
        visibility="PUBLIC",
    )

    assert project.id is not None
    assert project.name == "TimeSyncProject"
    assert project.description == "This is a project one"
    assert project.visibility == ProjectVisibility.PUBLIC
    assert project.is_archived is False


def test_update_project_invalid_id_project_not_found(project_factory):
    project = project_factory()

    with pytest.raises(NotFoundError) as exc_info:
        ProjectService.updateProject(
            project_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            name=" TimeSyncProject ",
            description=" This is a project one ",
            visibility="PUBLIC",
        )

    assert exc_info.value.message == "Project not found"


def test_update_project_rejects_invalid_visibility(project_factory):
    project = project_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.updateProject(
            project_id=project.id,
            name=" TimeSyncProject ",
            description=" This is a project one ",
            visibility="ERROR",
        )

    assert exc_info.value.message == "Invalid project visibility"


def test_does_project_exist_and_active_returns_true(project_factory):
    project = project_factory()

    project_exists = ProjectService.does_project_exist_and_active(project.id)

    assert project_exists is True


def test_does_project_exist_and_active_returns_false_for_archived_project(project_factory):
    project = project_factory(is_archived=True)

    project_exists = ProjectService.does_project_exist_and_active(project.id)

    assert project_exists is False


def test_does_project_exist_and_active_returns_false_for_missing_project(app):
    with app.app_context():
        project_exists = ProjectService.does_project_exist_and_active(
            UUID("550e8400-e29b-41d4-a716-446655440000")
        )

    assert project_exists is False


def test_change_archive_status_archives_project(project_factory):
    project = project_factory()

    archived_project = ProjectService.change_archive_status(
        project_id=project.id,
        user_id=project.owner_id,
        action="archive",
    )

    assert archived_project.is_archived is True
    assert archived_project.archived_at is not None
    assert archived_project.archived_by_user_id == project.owner_id


def test_change_archive_status_unarchives_project(project_factory):
    project = project_factory(is_archived=True)

    unarchived_project = ProjectService.change_archive_status(
        project_id=project.id,
        user_id=project.owner_id,
        action="unarchive",
    )

    assert unarchived_project.is_archived is False
    assert unarchived_project.archived_at is None
    assert unarchived_project.archived_by_user_id is None


def test_change_archive_status_project_not_found(project_factory):
    project = project_factory()

    with pytest.raises(NotFoundError) as exc_info:
        ProjectService.change_archive_status(
            project_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            user_id=project.owner_id,
            action="archive",
        )

    assert exc_info.value.message == "Project not found"


def test_change_archive_status_rejects_invalid_action(project_factory):
    project = project_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.change_archive_status(
            project_id=project.id,
            user_id=project.owner_id,
            action="invalid",
        )

    assert exc_info.value.message == "Invalid action. Use 'archive' or 'unarchive'"


def test_change_archive_status_rejects_same_state(project_factory):
    project = project_factory(is_archived=True)

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.change_archive_status(
            project_id=project.id,
            user_id=project.owner_id,
            action="archive",
        )

    assert exc_info.value.message == "Project already in requested state"


def test_change_archive_status_rejects_when_user_not_owner(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="not-owner@test.com")

    with pytest.raises(ForbiddenError) as exc_info:
        ProjectService.change_archive_status(
            project_id=project.id,
            user_id=user.id,
            action="archive",
        )

    assert exc_info.value.message == "User is not the project owner"


def test_list_available_projects_returns_public_and_owned(
    user_factory, project_factory, project_member_factory
):
    current_user = user_factory(email="current-user@test.com")
    another_user = user_factory(email="another-user@test.com")

    owned_private_project = project_factory(owner=current_user, name="Owned Private")
    public_project = project_factory(
        owner=another_user,
        name="Public Project",
        visibility="PUBLIC",
    )
    project_factory(owner=another_user, name="Other Private", visibility="PRIVATE")

    active_member = user_factory(email="member-active@test.com")
    removed_member = user_factory(email="member-removed@test.com")

    project_member_factory(project=public_project, user=active_member)

    removed_project_member = ProjectMember(
        project_id=public_project.id,
        user_id=removed_member.id,
    )
    db.session.add(removed_project_member)
    db.session.flush()
    removed_project_member.removed_at = owned_private_project.created_at
    db.session.commit()

    projects = ProjectService.list_available_projects(user_id=current_user.id)

    project_names = [project.name for project in projects]
    assert "Owned Private" in project_names
    assert "Public Project" in project_names
    assert "Other Private" not in project_names

    owned_project_info = next(project for project in projects if project.name == "Owned Private")
    assert owned_project_info.is_owner is True

    public_project_info = next(project for project in projects if project.name == "Public Project")
    assert public_project_info.is_owner is False
    assert public_project_info.number_of_members == 1
    assert public_project_info.members[0].email == "member-active@test.com"


def test_list_available_projects_filters_by_search_and_my_projects(user_factory, project_factory):
    current_user = user_factory(email="owner-search@test.com")
    other_user = user_factory(email="other-search@test.com")

    project_factory(owner=current_user, name="Alpha Owned", visibility="PRIVATE")
    project_factory(owner=current_user, name="Beta Owned", visibility="PUBLIC")
    project_factory(owner=other_user, name="Alpha Public", visibility="PUBLIC")

    my_filtered_projects = ProjectService.list_available_projects(
        user_id=current_user.id,
        search="Alpha",
        my_projects=True,
    )

    assert len(my_filtered_projects) == 1
    assert my_filtered_projects[0].name == "Alpha Owned"
    assert my_filtered_projects[0].is_owner is True


def test_get_dashboard_project_activity_splits_owned_and_member_projects(
    user_factory, project_factory, project_member_factory
):
    current_user = user_factory(email="dashboard-projects-current@test.com")
    other_owner = user_factory(email="dashboard-projects-other-owner@test.com")

    owner_projects = [project_factory(owner=current_user, name=f"Owned {i}") for i in range(4)]
    member_projects = [project_factory(owner=other_owner, name=f"Member {i}") for i in range(4)]

    for index, project in enumerate(owner_projects):
        project.updated_at = datetime.now() - timedelta(days=index)
    for index, project in enumerate(member_projects):
        project.updated_at = datetime.now() - timedelta(days=index)
        project_member_factory(project=project, user=current_user)
    db.session.commit()

    payload = ProjectService.get_dashboard_project_activity(user_id=current_user.id)

    assert len(payload["owner_projects"]) == 3
    assert len(payload["my_projects"]) == 3
    assert all(project.owner_id == current_user.id for project in payload["owner_projects"])
    assert all(project.owner_id != current_user.id for project in payload["my_projects"])


def test_get_dashboard_project_activity_keeps_archived_projects_visible(
    user_factory, project_factory, project_member_factory
):
    current_user = user_factory(email="dashboard-projects-archived-current@test.com")
    other_owner = user_factory(email="dashboard-projects-archived-owner@test.com")

    owned_archived = project_factory(owner=current_user, name="Owned Archived", is_archived=True)
    member_archived = project_factory(owner=other_owner, name="Member Archived", is_archived=True)
    project_member_factory(project=member_archived, user=current_user)

    payload = ProjectService.get_dashboard_project_activity(user_id=current_user.id)

    owner_names = [project.name for project in payload["owner_projects"]]
    member_names = [project.name for project in payload["my_projects"]]
    assert "Owned Archived" in owner_names
    assert "Member Archived" in member_names
