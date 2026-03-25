import pytest

from uuid import UUID
from app.api.errors import ForbiddenError, NotFoundError, ValidationError
from app.models.project import ProjectVisibility
from app.services.project_service import ProjectService

def test_create_project_sucess(user_factory):
    owner = user_factory()

    project = ProjectService.create_project(
        owner_id = owner.id,
        name=" TimeSync ",
        description=" This is a project ",
        visibility="PRIVATE"
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
            owner_id=owner.id,
            name="  ",
            description=" This is a project ",
            visibility="PRIVATE"
        )
    
    assert exc_info.value.message == "Project name is required"

def test_create_project_rejects_invalid_visibility(user_factory):
    owner = user_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.create_project(
            owner_id=owner.id,
            name="TimeSync",
            description="Main project",
            visibility="ERROR"
        )

    assert exc_info.value.message == "Invalid project visibility"

def test_update_project_success(project_factory):
    project = project_factory()

    project = ProjectService.updateProject(
        project_id = project.id,
        name = " TimeSyncProject ",
        description = " This is a project one ",
        visibility = "PUBLIC"
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
            project_id = UUID("550e8400-e29b-41d4-a716-446655440000"),
            name = " TimeSyncProject ",
            description = " This is a project one ",
            visibility = "PUBLIC"
        )

    assert exc_info.value.message == "Project not found"

def test_update_project_rejects_invalid_visibility(project_factory):
    project = project_factory()

    with pytest.raises(ValidationError) as exc_info:
        ProjectService.updateProject(
            project_id = project.id,
            name = " TimeSyncProject ",
            description = " This is a project one ",
            visibility = "ERROR"
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
        project_exists = ProjectService.does_project_exist_and_active(UUID("550e8400-e29b-41d4-a716-446655440000"))

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
