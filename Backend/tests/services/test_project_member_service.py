import pytest

from datetime import datetime
from uuid import UUID

from app.api.errors import NotFoundError
from app.models.project_member import ProjectMember
from app.services.project_member_service import ProjectMemberService


def test_add_member_to_project_creates_memberships(project_factory, user_factory):
    project = project_factory()
    user_one = user_factory(email="project-member-one@test.com")
    user_two = user_factory(email="project-member-two@test.com")

    ProjectMemberService.add_member_to_project(project.id, [user_one.id, user_two.id])

    project_members = ProjectMember.query.filter_by(project_id=project.id).all()

    assert len(project_members) == 2
    assert sorted(project_member.user_id for project_member in project_members) == sorted([user_one.id, user_two.id])
    for project_member in project_members:
        assert project_member.removed_at is None


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
