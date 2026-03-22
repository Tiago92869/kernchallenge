import pytest

from app.api.errors import ValidationError
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