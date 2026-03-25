import pytest

from datetime import datetime
from uuid import UUID

from app.api.errors import NotFoundError
from app.models.notification import Notification, NotificationType
from app.models.project_member import ProjectMember
from app.services.project_member_service import ProjectMemberService


def test_add_member_to_project_creates_memberships(project_factory, user_factory):
    owner = user_factory(email="project-owner-one@test.com", first_name="Owner", last_name="One")
    project = project_factory(owner=owner, name="Team Project")
    user_one = user_factory(email="project-member-one@test.com")
    user_two = user_factory(email="project-member-two@test.com")

    ProjectMemberService.add_member_to_project(project.id, [user_one.id, user_two.id])

    project_members = ProjectMember.query.filter_by(project_id=project.id).all()

    assert len(project_members) == 2
    assert sorted(project_member.user_id for project_member in project_members) == sorted([user_one.id, user_two.id])
    for project_member in project_members:
        assert project_member.removed_at is None

    notifications = Notification.query.filter_by(project_id=project.id).all()
    assert len(notifications) == 2
    assert sorted(notification.recipient_user_id for notification in notifications) == sorted([user_one.id, user_two.id])
    assert all(notification.notification_type == NotificationType.ADDED for notification in notifications)
    assert all('"Owner One" just added you to "Team Project"' == notification.message for notification in notifications)


def test_add_member_to_project_reactivates_soft_deleted_membership(project_factory, user_factory, project_member_factory):
    project = project_factory()
    user = user_factory(email="reactivated-user@test.com")
    removed_by_user = user_factory(email="removed-by-user@test.com")
    removed_membership = project_member_factory(
        project=project,
        user=user,
        removed_at=datetime.now(),
        removed_by_user=removed_by_user,
    )

    ProjectMemberService.add_member_to_project(project.id, [user.id])

    refreshed_membership = ProjectMember.query.filter_by(id=removed_membership.id).first()

    assert refreshed_membership.removed_at is None
    assert refreshed_membership.removed_by_user_id is None


def test_add_member_to_project_does_not_duplicate_active_membership(project_factory, user_factory, project_member_factory):
    project = project_factory()
    user = user_factory(email="existing-member@test.com")
    existing_membership = project_member_factory(project=project, user=user)

    ProjectMemberService.add_member_to_project(project.id, [user.id])

    project_members = ProjectMember.query.filter_by(project_id=project.id, user_id=user.id).all()

    assert len(project_members) == 1
    assert project_members[0].id == existing_membership.id


def test_add_member_to_project_raises_when_project_is_archived(project_factory, user_factory):
    project = project_factory(is_archived=True)
    user = user_factory(email="archived-project-member@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.add_member_to_project(project.id, [user.id])

    assert exc_info.value.message == "Project not found or is archived"


def test_add_member_to_project_raises_when_user_is_inactive(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="inactive-project-member@test.com", is_active=False)

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.add_member_to_project(project.id, [user.id])

    assert exc_info.value.message == f"User with id {user.id} not found or is not active"


def test_add_member_to_project_raises_when_user_is_missing(project_factory):
    project = project_factory()
    missing_user_id = UUID("5540e840-e29b-41d4-a716-446655440000")

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.add_member_to_project(project.id, [missing_user_id])

    assert exc_info.value.message == f"User with id {missing_user_id} not found or is not active"


def test_remove_member_from_project_sets_removed_fields(project_factory, user_factory, project_member_factory):
    owner = user_factory(email="project-owner-two@test.com", first_name="Owner", last_name="Two")
    project = project_factory(owner=owner, name="Ops Project")
    user = user_factory(email="remove-member@test.com")
    project_member = project_member_factory(project=project, user=user)

    updated_project_member = ProjectMemberService.remove_member_from_project(project.id, user.id)

    assert updated_project_member.id == project_member.id
    assert updated_project_member.removed_at is not None
    assert updated_project_member.removed_by_user_id is None

    notification = Notification.query.filter_by(project_id=project.id, recipient_user_id=user.id).first()
    assert notification is not None
    assert notification.notification_type == NotificationType.REMOVED
    assert notification.message.startswith('"Owner Two" just removed you from "Ops Project" at "')


def test_remove_member_from_project_raises_when_membership_not_found(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="missing-membership@test.com")

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.remove_member_from_project(project.id, user.id)

    assert exc_info.value.message == "Project member not found"


def test_remove_member_from_project_raises_when_project_is_archived(project_factory, user_factory, project_member_factory):
    project = project_factory(is_archived=True)
    user = user_factory(email="archived-remove-member@test.com")
    project_member_factory(project=project, user=user)

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.remove_member_from_project(project.id, user.id)

    assert exc_info.value.message == "Project not found or is archived"


def test_remove_member_from_project_raises_when_user_is_inactive(project_factory, user_factory):
    project = project_factory()
    user = user_factory(email="inactive-remove-member@test.com", is_active=False)

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.remove_member_from_project(project.id, user.id)

    assert exc_info.value.message == f"User with id {user.id} not found or is not active"


def test_remove_member_from_project_raises_when_user_is_missing(project_factory):
    project = project_factory()
    missing_user_id = UUID("5540e840-e29b-41d4-a716-446655440000")

    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.remove_member_from_project(project.id, missing_user_id)

    assert exc_info.value.message == f"User with id {missing_user_id} not found or is not active"

def test_project_member_get_currently_active_members(project_factory, user_factory, project_member_factory):
    project = project_factory()
    active_user = user_factory(email="active-member@test.com")
    inactive_user = user_factory(email="inactive-member@test.com", is_active=False)
    removed_user = user_factory(email="removed-member@test.com")

    project_member_factory(project=project, user=active_user)
    project_member_factory(project=project, user=inactive_user)
    project_member_factory(project=project, user=removed_user, removed_at=datetime.now())

    active_members = ProjectMemberService.get_currently_active_members(project.id)

    assert len(active_members) == 1
    assert active_members[0].user_id == active_user.id

def test_project_member_get_currently_active_members_returns_empty_list_when_no_active_members(project_factory, user_factory, project_member_factory):
    project = project_factory()
    removed_user = user_factory(email="removed-member@test.com")

    project_member_factory(project=project, user=removed_user, removed_at=datetime.now())

    active_members = ProjectMemberService.get_currently_active_members(project.id)

    assert len(active_members) == 0

def test_project_member_get_currently_active_members_raises_when_project_is_archived(project_factory, user_factory):
    project = project_factory(is_archived=True)
    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.get_currently_active_members(project.id)

    assert exc_info.value.message == "Project not found or is archived"

def test_project_member_get_currently_active_members_raises_when_project_is_missing(app):
    missing_project_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    with app.app_context():
        with pytest.raises(NotFoundError) as exc_info:
            ProjectMemberService.get_currently_active_members(missing_project_id)

    assert exc_info.value.message == "Project not found or is archived"

def test_project_member_get_currently_active_members_raises_when_project_is_archived(project_factory):
    project = project_factory(is_archived=True)
    with pytest.raises(NotFoundError) as exc_info:
        ProjectMemberService.get_currently_active_members(project.id)

    assert exc_info.value.message == "Project not found or is archived"
