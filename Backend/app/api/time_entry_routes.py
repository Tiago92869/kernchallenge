from datetime import date
from uuid import UUID

from app.api.errors import ValidationError
from app.api.responses import success_response
from app.schemas.time_entry_schema import TimeEntrySchema
from app.services.time_entry_service import TimeEntryService
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

time_entry_bp = Blueprint("time_entries", __name__, url_prefix="/time-entries")


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(message=f"Invalid {field_name} format, expected YYYY-MM-DD") from exc


@time_entry_bp.post("")
def create_time_entry():
    """Create a new time entry.
    ---
    tags:
      - Time Entries
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - project_id
            - date
            - hours
          properties:
            user_id:
              type: string
              format: uuid
            project_id:
              type: string
              format: uuid
            date:
              type: string
              format: date
              example: "2026-04-16"
            hours:
              type: integer
              description: Duration in minutes
            description:
              type: string
    responses:
      201:
        description: Time entry created
      400:
        description: Validation error
    """
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


@time_entry_bp.get("/project/<project_id>")
def get_time_entries_by_project(project_id):
    """Get project time entries with role-based visibility.
    ---
    tags:
      - Time Entries
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
      - in: query
        name: user_id
        type: string
        format: uuid
        required: true
        description: Current user id (owner sees all entries, members see only their own)
      - in: query
        name: start_date
        type: string
        format: date
        required: false
        example: "2026-04-01"
      - in: query
        name: end_date
        type: string
        format: date
        required: false
        example: "2026-04-30"
      - in: query
        name: search
        type: string
        required: false
        description: Search in description
    responses:
      200:
        description: Time entries list returned
      400:
        description: Validation error
      403:
        description: User does not have access to this project
      404:
        description: Project or user not found
    """
    user_id = request.args.get("user_id")
    if not user_id:
        raise ValidationError(message="Query param 'user_id' is required")

    try:
        parsed_user_id = UUID(user_id)
    except ValueError as exc:
        raise ValidationError(message="Invalid user_id") from exc

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    search_string = request.args.get("search")

    time_entries = TimeEntryService.get_time_entries_by_project_with_role_visibility(
        project_id=UUID(project_id),
        user_id=parsed_user_id,
        start_date=_parse_date(start_date, "start_date") if start_date else None,
        end_date=_parse_date(end_date, "end_date") if end_date else None,
        search_string=search_string,
    )

    return success_response(
        data=[TimeEntrySchema.serialize_time_entry(time_entry) for time_entry in time_entries]
    )


@time_entry_bp.get("/project/<project_id>/aggregation")
def get_project_member_time_aggregation(project_id):
    """Get owner-only member time aggregation by week or month.
    ---
    tags:
      - Time Entries
    parameters:
      - in: path
        name: project_id
        type: string
        format: uuid
        required: true
      - in: query
        name: user_id
        type: string
        format: uuid
        required: true
        description: Project owner id
      - in: query
        name: period
        type: string
        enum:
          - week
          - month
        required: true
      - in: query
        name: start_date
        type: string
        format: date
        required: false
      - in: query
        name: end_date
        type: string
        format: date
        required: false
    responses:
      200:
        description: Aggregated member totals returned
      400:
        description: Validation error
      403:
        description: Only owner can access this report
      404:
        description: Project or user not found
    """
    user_id = request.args.get("user_id")
    if not user_id:
        raise ValidationError(message="Query param 'user_id' is required")

    period = request.args.get("period")
    if not period:
        raise ValidationError(message="Query param 'period' is required")

    try:
        parsed_user_id = UUID(user_id)
    except ValueError as exc:
        raise ValidationError(message="Invalid user_id") from exc

    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    aggregated = TimeEntryService.get_member_time_aggregation_by_project(
        project_id=UUID(project_id),
        user_id=parsed_user_id,
        period=period,
        start_date=_parse_date(start_date, "start_date") if start_date else None,
        end_date=_parse_date(end_date, "end_date") if end_date else None,
    )

    return success_response(data=aggregated)


@time_entry_bp.get("/<time_entry_id>")
def get_time_entry_by_id(time_entry_id):
    """Get a single time entry by id.
    ---
    tags:
      - Time Entries
    parameters:
      - in: path
        name: time_entry_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Time entry found
      404:
        description: Time entry not found
    """
    time_entry = TimeEntryService.get_time_entry_by_id(UUID(time_entry_id))

    return success_response(data=TimeEntrySchema.serialize_time_entry(time_entry))


@time_entry_bp.get("")
def get_time_entries_by_user_and_date_range_and_project():
    """List time entries with optional filters.
    ---
    tags:
      - Time Entries
    parameters:
      - in: query
        name: user_id
        type: string
        format: uuid
        required: false
      - in: query
        name: start_date
        type: string
        format: date
        required: false
        example: "2026-04-01"
      - in: query
        name: end_date
        type: string
        format: date
        required: false
        example: "2026-04-30"
      - in: query
        name: project_id
        type: string
        format: uuid
        required: false
      - in: query
        name: search
        type: string
        required: false
        description: Search in description
    responses:
      200:
        description: Time entries list returned
      400:
        description: Validation error
    """
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
        data=[TimeEntrySchema.serialize_time_entry(time_entry) for time_entry in time_entries]
    )


@time_entry_bp.get("/summary")
def get_time_entry_summary_by_user_and_date_range_and_project():
    """Get summary totals for time entries using the same filters as list endpoint.
    ---
    tags:
      - Time Entries
    parameters:
      - in: query
        name: user_id
        type: string
        format: uuid
        required: false
      - in: query
        name: start_date
        type: string
        format: date
        required: false
      - in: query
        name: end_date
        type: string
        format: date
        required: false
      - in: query
        name: project_id
        type: string
        format: uuid
        required: false
      - in: query
        name: search
        type: string
        required: false
        description: Search in description
    responses:
      200:
        description: Summary returned
      400:
        description: Validation error
      404:
        description: Related project or user not found
    """
    user_id = request.args.get("user_id")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    project_id = request.args.get("project_id")
    search_string = request.args.get("search")

    summary = TimeEntryService.get_time_entry_summary_by_user_and_date_range_and_project(
        user_id=UUID(user_id) if user_id else None,
        start_date=_parse_date(start_date, "start_date") if start_date else None,
        end_date=_parse_date(end_date, "end_date") if end_date else None,
        project_id=UUID(project_id) if project_id else None,
        search_string=search_string,
    )

    return success_response(data=summary)


@time_entry_bp.get("/dashboard/activity")
@jwt_required()
def get_dashboard_activity():
    """Get chart-ready activity data for the authenticated user.
    ---
    tags:
      - Time Entries
    security:
      - Bearer: []
    parameters:
      - in: query
        name: period
        type: string
        enum:
          - 7d
          - 30d
        required: true
        description: Last 7 or 30 days
    responses:
      200:
        description: Dashboard activity returned
      400:
        description: Validation error
      401:
        description: Missing or invalid auth token
      404:
        description: Authenticated user not found or inactive
    """
    period = request.args.get("period")
    if not period:
        raise ValidationError(message="Query param 'period' is required")

    user_id = UUID(get_jwt_identity())

    activity = TimeEntryService.get_dashboard_activity_for_user(
        user_id=user_id,
        period=period,
    )

    return success_response(data=activity)


@time_entry_bp.put("/<time_entry_id>")
def update_time_entry(time_entry_id):
    """Update a time entry.
    ---
    tags:
      - Time Entries
    parameters:
      - in: path
        name: time_entry_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
            - project_id
            - date
            - hours
          properties:
            user_id:
              type: string
              format: uuid
            project_id:
              type: string
              format: uuid
            date:
              type: string
              format: date
              example: "2026-04-16"
            hours:
              type: integer
              description: Duration in minutes
            description:
              type: string
    responses:
      200:
        description: Time entry updated
      400:
        description: Validation error
      404:
        description: Time entry not found
    """
    data = request.get_json() or {}

    time_entry = TimeEntryService.update_time_entry_by_id(
        time_entry_id=UUID(time_entry_id),
        user_id=UUID(data.get("user_id")),
        project_id=UUID(data.get("project_id")),
        work_date=_parse_date(data.get("date"), "date"),
        duration_minutes=int(data.get("hours")),
        description=data.get("description", "No description"),
    )

    return success_response(data=TimeEntrySchema.serialize_time_entry(time_entry))


@time_entry_bp.delete("/<time_entry_id>")
def delete_time_entry_by_id(time_entry_id):
    """Delete a time entry.
    ---
    tags:
      - Time Entries
    parameters:
      - in: path
        name: time_entry_id
        type: string
        format: uuid
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - user_id
          properties:
            user_id:
              type: string
              format: uuid
              description: User performing the delete (must be the entry owner)
    responses:
      200:
        description: Time entry deleted
      403:
        description: User is not the entry owner
      404:
        description: Time entry not found
    """
    data = request.get_json() or {}

    TimeEntryService.delete_time_entry_by_id(
        time_entry_id=UUID(time_entry_id), user_id=UUID(data.get("user_id"))
    )

    return success_response(data={"message": "Time entry deleted successfully"})
