from datetime import date
from uuid import UUID

from flask import Blueprint, request

from app.api.errors import ValidationError
from app.api.responses import success_response
from app.schemas.notification_schema import NotificationSchema
from app.services.notification_service import NotificationService


notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(message=f"Invalid {field_name} format, expected YYYY-MM-DD") from exc


@notification_bp.get("")
def get_notifications_by_recipient():
    recipient_user_id = request.args.get("recipient_user_id")
    search = request.args.get("search")
    created_date = request.args.get("date")
    project_id = request.args.get("project_id")

    notifications = NotificationService.get_notifications_by_recipient(
        recipient_user_id=UUID(recipient_user_id),
        search=search,
        created_date=_parse_date(created_date, "date") if created_date else None,
        project_id=UUID(project_id) if project_id else None,
    )

    return success_response(
        data=[
            NotificationSchema.serialize_notification(notification)
            for notification in notifications
        ]
    )


@notification_bp.patch("/<notification_id>/read")
def mark_notification_as_read(notification_id):
    notification = NotificationService.mark_notification_as_read(UUID(notification_id))

    return success_response(data=NotificationSchema.serialize_notification(notification))
