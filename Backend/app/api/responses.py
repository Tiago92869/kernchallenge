from flask import jsonify

# Responsible for fomatting the output sent back to the frontend
# Allows to avoid to add return jsonify... to each endpoint


def success_response(data=None, message=None, status_code=200):
    payload = {
        "success": True,
        "data": data,
    }
    if message is not None:
        payload["message"] = message
    return jsonify(payload), status_code


def error_response(code, message, details=None, status_code=400):
    payload = {"success": False, "error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["detials"] = details
    return jsonify(payload), status_code
