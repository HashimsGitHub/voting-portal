"""
Response Utilities
Standardized JSON HTTP responses for Azure Functions
"""
import json
import azure.functions as func
from bson import ObjectId
from datetime import datetime


class JSONEncoder(json.JSONEncoder):
    """JSON encoder that handles MongoDB ObjectId and datetime values"""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _json_response(payload: dict, status_code: int) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(payload, cls=JSONEncoder),
        status_code=status_code,
        mimetype="application/json"
    )


def success_response(data=None, status_code: int = 200) -> func.HttpResponse:
    """Build a 2xx success response. Dict data is merged into the payload root."""
    payload = {"success": True}
    if isinstance(data, dict):
        payload.update(data)
    elif data is not None:
        payload["data"] = data
    return _json_response(payload, status_code)


def created_response(data=None, location: str = None) -> func.HttpResponse:
    """Build a 201 Created response, optionally with a Location header"""
    response = success_response(data, status_code=201)
    if location:
        response.headers["Location"] = location
    return response


def error_response(message: str, status_code: int = 400) -> func.HttpResponse:
    """Build an error response"""
    return _json_response({"success": False, "error": message}, status_code)
