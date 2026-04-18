from datetime import date
from uuid import UUID

from app.api.errors import ValidationError
from app.api.responses import success_response
from app.schemas.notification_schema import NotificationSchema
from app.services.notification_service import NotificationService
from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


def _parse_date(value, field_name):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(message=f"Invalid {field_name} format, expected YYYY-MM-DD") from exc


@notification_bp.get("")
@jwt_required()
def get_notifications_by_recipient():
    """List notifications for a recipient user.
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: query
        name: search
        type: string
        required: false
        description: Search in notification message
      - in: query
        name: date
        type: string
        format: date
        required: false
        example: "2026-04-16"
      - in: query
        name: project_id
        type: string
        format: uuid
        required: false
    responses:
      200:
        description: Notification list returned
      401:
        description: Missing or invalid auth token
      400:
        description: Validation error
    """
    search = request.args.get("search")
    created_date = request.args.get("date")
    project_id = request.args.get("project_id")

    notifications = NotificationService.get_notifications_by_recipient(
        recipient_user_id=UUID(get_jwt_identity()),
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
    """Mark a notification as read.
    ---
    tags:
      - Notifications
    parameters:
      - in: path
        name: notification_id
        type: string
        format: uuid
        required: true
    responses:
      200:
        description: Notification marked as read
      404:
        description: Notification not found
    """
    notification = NotificationService.mark_notification_as_read(UUID(notification_id))

    return success_response(data=NotificationSchema.serialize_notification(notification))


@notification_bp.patch("/read-all")
@jwt_required()
def mark_all_notifications_as_read():
    """Mark all notifications as read for the authenticated user.
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        description: All notifications marked as read
      401:
        description: Missing or invalid auth token
    """
    NotificationService.mark_all_notifications_as_read(recipient_user_id=UUID(get_jwt_identity()))
    return success_response(message="All notifications marked as read")
