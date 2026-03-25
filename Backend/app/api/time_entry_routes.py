from flask import Blueprint, request
from datetime import date
from uuid import UUID
from app.api.errors import ValidationError
from app.api.responses import success_response
from app.services.time_entry_service import TimeEntryService
from app.schemas.time_entry_schema import TimeEntrySchema

time_entry_bp = Blueprint("time_entries", __name__, url_prefix="/time-entries")


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(message=f"Invalid {field_name} format, expected YYYY-MM-DD") from exc

@time_entry_bp.post("")
def create_time_entry():
    data = request.get_json() or {}

    time_entry = TimeEntryService.create_time_entry(
        user_id=UUID(data.get("user_id")),
        project_id=UUID(data.get("project_id")),
        work_date=_parse_date(data.get("date"), "date"),
        duration_minutes=int(data.get("hours")),
        description=data.get("description", "No description"),
    )

    return success_response(
        data=TimeEntrySchema.serialize_time_entry(time_entry),
        status_code=201,
    )

@time_entry_bp.get("/<time_entry_id>")
def get_time_entry_by_id(time_entry_id):
    time_entry = TimeEntryService.get_time_entry_by_id(UUID(time_entry_id))

    return success_response(
        data=TimeEntrySchema.serialize_time_entry(time_entry)
    )

@time_entry_bp.get("")
def get_time_entries_by_user_and_date_range_and_project():
    user_id = request.args.get("user_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    project_id = request.args.get("project_id")
    search_string = request.args.get("search")

    time_entries = TimeEntryService.get_time_entries_by_user_and_date_range_and_project(
        user_id=UUID(user_id) if user_id else None,
        start_date=_parse_date(start_date, "start_date") if start_date else None,
        end_date=_parse_date(end_date, "end_date") if end_date else None,
        project_id=UUID(project_id) if project_id else None,
        search_string=search_string,
    )

    return success_response(
        data=[
            TimeEntrySchema.serialize_time_entry(time_entry)
            for time_entry in time_entries
        ]
    )

@time_entry_bp.put("/<time_entry_id>")
def update_time_entry(time_entry_id):
    data = request.get_json() or {}

    time_entry = TimeEntryService.update_time_entry_by_id(
        time_entry_id=UUID(time_entry_id),
        user_id=UUID(data.get("user_id")),
        project_id=UUID(data.get("project_id")),
        work_date=_parse_date(data.get("date"), "date"),
        duration_minutes=int(data.get("hours")),
        description=data.get("description", "No description"),
    )

    return success_response(
        data=TimeEntrySchema.serialize_time_entry(time_entry)
    )

@time_entry_bp.delete("/<time_entry_id>")
def delete_time_entry_by_id(time_entry_id):
    data = request.get_json() or {}
    
    TimeEntryService.delete_time_entry_by_id(
        time_entry_id=UUID(time_entry_id),
        user_id=UUID(data.get("user_id"))
    )
    
    return success_response(
        data={"message": "Time entry deleted successfully"}
    )