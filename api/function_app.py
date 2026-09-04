"""
NUST Alumni Voting Portal - Azure Functions Backend
Handles election management and voting operations
"""
import azure.functions as func
import json
import os
import base64
import logging
from datetime import datetime
from typing import Optional
from repositories.election_repository import ElectionRepository
from repositories.user_repository import UserRepository
from services.election_service import ElectionService
from shared.response_utils import success_response, error_response, created_response
from shared.jwt_utils import verify_token, get_user_from_token, generate_token
from shared.password_utils import hash_password, verify_password
from shared.storage_client import StorageClient

app = func.FunctionApp()


@app.function_name(name="DebugVerify")
@app.route(route="_debug/verify", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def debug_verify(req: func.HttpRequest) -> func.HttpResponse:
    """TEMPORARY diagnostic endpoint - remove once the 403 root cause is confirmed."""
    import jwt as jwt_lib
    import hashlib
    import socket
    from shared.jwt_utils import JWT_SECRET, JWT_ALGORITHM

    token = (req.headers.get('Authorization') or '').replace('Bearer ', '')
    info = {
        "pyjwt_version": getattr(jwt_lib, "__version__", "unknown"),
        "algorithm": JWT_ALGORITHM,
        "secret_len": len(JWT_SECRET) if JWT_SECRET else 0,
        "secret_present": bool(JWT_SECRET),
        "secret_fingerprint": hashlib.sha256(JWT_SECRET.encode()).hexdigest()[:12] if JWT_SECRET else None,
        "instance_hostname": socket.gethostname(),
        "token_received": bool(token),
    }
    try:
        self_signed = jwt_lib.encode({"self_test": True}, JWT_SECRET, algorithm=JWT_ALGORITHM)
        jwt_lib.decode(self_signed, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        info["self_roundtrip"] = "success"
    except Exception as e:
        info["self_roundtrip"] = f"failed: {type(e).__name__}: {str(e)}"
    if token:
        try:
            payload = jwt_lib.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            info["decode_result"] = "success"
            info["payload"] = payload
        except Exception as e:
            info["decode_result"] = "failed"
            info["error_type"] = type(e).__name__
            info["error_message"] = str(e)
    return func.HttpResponse(json.dumps(info, default=str), mimetype="application/json", status_code=200)


# Initialize repository and service
MONGO_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
if not MONGO_CONNECTION_STRING:
    raise ValueError("MONGODB_CONNECTION_STRING environment variable not set")

election_repo = ElectionRepository(MONGO_CONNECTION_STRING)
election_service = ElectionService(election_repo)
user_repo = UserRepository(MONGO_CONNECTION_STRING)

logger = logging.getLogger(__name__)


def _ensure_candidate_profile(user_id: str, email: str, name: Optional[str] = None) -> None:
    """Ensure a candidate-role user has a candidate profile.

    A candidate is just a user with role="candidate" plus an extended profile
    document in the candidates collection, created 1:1 at registration time
    and keyed by user_id - there is no separate admin pre-creation step to
    link up by email.
    """
    try:
        if election_repo.get_candidate_by_user_id(user_id):
            return

        elections = election_repo.get_all_elections()
        if not elections:
            return
        election_id = str(elections[0]['_id'])
        election_service.self_register_candidate(election_id, user_id, name or email, email)
    except Exception as e:
        logger.warning(f"Candidate profile creation skipped: {str(e)}")


# ==================== ELECTION ENDPOINTS ====================

@app.function_name(name="CreateElection")
@app.route(route="elections", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_election(req: func.HttpRequest) -> func.HttpResponse:
    """Create a new election (Admin only)"""
    try:
        # Verify admin token
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)
        
        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)
        
        data = req.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        result = election_service.create_election(
            title=data['title'],
            description=data['description'],
            total_seats=data.get('total_seats', 10),
            start_date=datetime.fromisoformat(data['start_date']) if 'start_date' in data else None,
            end_date=datetime.fromisoformat(data['end_date']) if 'end_date' in data else None
        )
        
        if result['success']:
            return created_response(result, f"/api/elections/{result['election_id']}")
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error creating election: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetElections")
@app.route(route="elections", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_elections(req: func.HttpRequest) -> func.HttpResponse:
    """Get all elections"""
    try:
        status = req.params.get('status')
        elections = election_repo.get_all_elections(status=status)
        
        elections_data = [
            {
                "_id": str(e["_id"]),
                "title": e.get("title"),
                "description": e.get("description"),
                "status": e.get("status"),
                "total_seats": e.get("total_seats"),
                "start_date": e.get("start_date"),
                "end_date": e.get("end_date"),
                "created_at": e.get("created_at")
            }
            for e in elections
        ]
        
        return success_response({
            "count": len(elections_data),
            "elections": elections_data
        })
    
    except Exception as e:
        logger.error(f"Error getting elections: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetElectionDetails")
@app.route(route="elections/{election_id}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_election_details(req: func.HttpRequest) -> func.HttpResponse:
    """Get detailed election information"""
    try:
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        result = election_service.get_election_details(election_id)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 404)
    
    except Exception as e:
        logger.error(f"Error getting election details: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UpdateElection")
@app.route(route="elections/{election_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_election(req: func.HttpRequest) -> func.HttpResponse:
    """Update an election (Admin only)"""
    try:
        # Verify admin token
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)
        
        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)
        
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        data = req.get_json()
        for date_field in ('start_date', 'end_date'):
            if data.get(date_field):
                try:
                    parsed = datetime.fromisoformat(data[date_field].replace('Z', '+00:00'))
                    data[date_field] = parsed.replace(tzinfo=None)
                except ValueError:
                    return error_response(f"Invalid {date_field} format", 400)

        success = election_repo.update_election(election_id, data)

        if success:
            return success_response({"message": "Election updated successfully"})
        else:
            return error_response("Failed to update election", 400)
    
    except Exception as e:
        logger.error(f"Error updating election: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="OpenNominations")
@app.route(route="elections/{election_id}/open-nominations", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def open_nominations(req: func.HttpRequest) -> func.HttpResponse:
    """Allow candidates to select their seats again (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        result = election_service.open_nominations(election_id)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error opening nominations: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="ActivateElection")
@app.route(route="elections/{election_id}/activate", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def activate_election(req: func.HttpRequest) -> func.HttpResponse:
    """Activate an election (Admin only)"""
    try:
        # Verify admin token
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)
        
        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)
        
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        result = election_service.activate_election(election_id)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error activating election: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="CloseElection")
@app.route(route="elections/{election_id}/close", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def close_election(req: func.HttpRequest) -> func.HttpResponse:
    """Close an election (Admin only)"""
    try:
        # Verify admin token
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)
        
        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)
        
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        force = bool((req.get_json() or {}).get('force')) if req.get_body() else False
        result = election_service.close_election(election_id, force=force)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error closing election: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="DeleteElection")
@app.route(route="elections/{election_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_election(req: func.HttpRequest) -> func.HttpResponse:
    """Delete an election and its related data (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        success = election_repo.delete_election(election_id)

        if success:
            return success_response({"message": "Election deleted successfully"})
        else:
            return error_response("Failed to delete election", 400)

    except Exception as e:
        logger.error(f"Error deleting election: {str(e)}")
        return error_response(str(e), 500)


# ==================== POSITION (SEAT) ENDPOINTS ====================

@app.function_name(name="CreatePosition")
@app.route(route="elections/{election_id}/positions", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_position(req: func.HttpRequest) -> func.HttpResponse:
    """Create a position/seat for an election (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        data = req.get_json()
        if 'name' not in data:
            return error_response("Missing required field: name", 400)

        result = election_service.create_position(
            election_id=election_id,
            name=data['name'],
            region=data.get('region'),
            description=data.get('description')
        )

        if result['success']:
            return created_response(result, f"/api/positions/{result['position_id']}")
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error creating position: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetPositions")
@app.route(route="elections/{election_id}/positions", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_positions(req: func.HttpRequest) -> func.HttpResponse:
    """List positions/seats for an election"""
    try:
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        result = election_service.get_positions(election_id)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error listing positions: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UpdatePosition")
@app.route(route="positions/{position_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_position(req: func.HttpRequest) -> func.HttpResponse:
    """Update a position/seat's name, region or description (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        position_id = req.route_params.get('position_id')
        if not position_id:
            return error_response("Missing position_id", 400)

        data = req.get_json()
        result = election_service.update_position(position_id, data)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error updating position: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="DeletePosition")
@app.route(route="positions/{position_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_position(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a position/seat (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        position_id = req.route_params.get('position_id')
        if not position_id:
            return error_response("Missing position_id", 400)

        result = election_service.delete_position(position_id)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error deleting position: {str(e)}")
        return error_response(str(e), 500)


# ==================== CANDIDATE ENDPOINTS ====================

@app.function_name(name="GetCandidates")
@app.route(route="elections/{election_id}/candidates", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_candidates(req: func.HttpRequest) -> func.HttpResponse:
    """Get candidates for an election"""
    try:
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        position = req.params.get('position')
        
        result = election_service.get_candidates(election_id, position=position)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error getting candidates: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UpdateCandidate")
@app.route(route="candidates/{candidate_id:length(24)}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_candidate(req: func.HttpRequest) -> func.HttpResponse:
    """Update any field on a candidate (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        candidate_id = req.route_params.get('candidate_id')
        if not candidate_id:
            return error_response("Missing candidate_id", 400)

        data = req.get_json()
        editable_fields = {
            'name', 'positions', 'bio', 'image_url', 'batch_year', 'department',
            'contact_email', 'platform', 'profile_url', 'linkedin_url', 'social_url'
        }
        updates = {k: v for k, v in data.items() if k in editable_fields}
        if not updates:
            return error_response("No editable fields provided", 400)

        if 'positions' in updates:
            if not updates['positions'] or len(updates['positions']) == 0:
                return error_response("A candidate must run for at least one position", 400)
            if len(updates['positions']) > 3:
                return error_response("A candidate can run for at most 3 positions", 400)

        if updates.get('contact_email'):
            updates['contact_email'] = updates['contact_email'].strip().lower()

        success = election_repo.update_candidate(candidate_id, updates)

        if success:
            return success_response({"message": "Candidate updated successfully"})
        else:
            return error_response("Failed to update candidate", 400)

    except Exception as e:
        logger.error(f"Error updating candidate: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="DeleteCandidate")
@app.route(route="candidates/{candidate_id:length(24)}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_candidate(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a candidate and its related votes (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        candidate_id = req.route_params.get('candidate_id')
        if not candidate_id:
            return error_response("Missing candidate_id", 400)

        success = election_repo.delete_candidate(candidate_id)

        if success:
            return success_response({"message": "Candidate deleted successfully"})
        else:
            return error_response("Failed to delete candidate", 400)

    except Exception as e:
        logger.error(f"Error deleting candidate: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetMyCandidateProfile")
@app.route(route="candidates/me", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_my_candidate_profile(req: func.HttpRequest) -> func.HttpResponse:
    """Get the candidate profile linked to the signed-in candidate account"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'candidate':
            return error_response("Unauthorized access", 403)

        result = election_service.get_my_candidate_profile(user.get('user_id'))

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 404)

    except Exception as e:
        logger.error(f"Error getting candidate profile: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UpdateMyCandidateProfile")
@app.route(route="candidates/me", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_my_candidate_profile(req: func.HttpRequest) -> func.HttpResponse:
    """Let a signed-in candidate edit their own photo, bio and profile URL"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'candidate':
            return error_response("Unauthorized access", 403)

        data = req.get_json()
        result = election_service.update_my_candidate_profile(user.get('user_id'), data)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)

    except Exception as e:
        logger.error(f"Error updating candidate profile: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UploadMyCandidatePhoto")
@app.route(route="candidates/me/photo", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_my_candidate_photo(req: func.HttpRequest) -> func.HttpResponse:
    """Upload a photo for the signed-in candidate to Azure Blob Storage"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'candidate':
            return error_response("Unauthorized access", 403)

        candidate = election_repo.get_candidate_by_user_id(user.get('user_id'))
        if not candidate:
            return error_response("No candidate profile is linked to this account yet", 404)

        data = req.get_json()
        image_base64 = data.get('image_base64')
        content_type = data.get('content_type', 'image/jpeg')
        if not image_base64:
            return error_response("Missing image_base64", 400)

        try:
            file_bytes = base64.b64decode(image_base64.split(',')[-1])
        except Exception:
            return error_response("Invalid base64 image data", 400)

        if len(file_bytes) > 5 * 1024 * 1024:
            return error_response("Image must be smaller than 5MB", 400)

        storage_client = StorageClient()
        image_url = storage_client.upload_image(file_bytes, content_type)

        election_repo.update_candidate(str(candidate['_id']), {"image_url": image_url})

        return success_response({"image_url": image_url})

    except ValueError as e:
        logger.error(f"Storage not configured: {str(e)}")
        return error_response("Photo storage is not configured on the server", 500)
    except Exception as e:
        logger.error(f"Error uploading candidate photo: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UploadMyCampaignMedia")
@app.route(route="candidates/me/media", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def upload_my_campaign_media(req: func.HttpRequest) -> func.HttpResponse:
    """Upload a campaign image or video for the signed-in candidate's media gallery"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'candidate':
            return error_response("Unauthorized access", 403)

        candidate = election_repo.get_candidate_by_user_id(user.get('user_id'))
        if not candidate:
            return error_response("No candidate profile is linked to this account yet", 404)

        data = req.get_json()
        media_base64 = data.get('media_base64')
        content_type = data.get('content_type', 'image/jpeg')
        if not media_base64:
            return error_response("Missing media_base64", 400)

        if not (content_type.startswith('image/') or content_type.startswith('video/')):
            return error_response("Only image or video files are allowed", 400)

        try:
            file_bytes = base64.b64decode(media_base64.split(',')[-1])
        except Exception:
            return error_response("Invalid base64 media data", 400)

        max_size = 20 * 1024 * 1024 if content_type.startswith('video/') else 5 * 1024 * 1024
        if len(file_bytes) > max_size:
            return error_response(f"File must be smaller than {max_size // (1024 * 1024)}MB", 400)

        storage_client = StorageClient()
        media_url = storage_client.upload_image(file_bytes, content_type)

        media_item = {
            "url": media_url,
            "media_type": "video" if content_type.startswith('video/') else "image",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        election_repo.add_campaign_media(str(candidate['_id']), media_item)

        return success_response({"media": media_item})

    except ValueError as e:
        logger.error(f"Storage not configured: {str(e)}")
        return error_response("Media storage is not configured on the server", 500)
    except Exception as e:
        logger.error(f"Error uploading campaign media: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="DeleteMyCampaignMedia")
@app.route(route="candidates/me/media", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_my_campaign_media(req: func.HttpRequest) -> func.HttpResponse:
    """Remove a campaign image or video from the signed-in candidate's media gallery"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'candidate':
            return error_response("Unauthorized access", 403)

        candidate = election_repo.get_candidate_by_user_id(user.get('user_id'))
        if not candidate:
            return error_response("No candidate profile is linked to this account yet", 404)

        data = req.get_json()
        media_url = data.get('url')
        if not media_url:
            return error_response("Missing url", 400)

        election_repo.remove_campaign_media(str(candidate['_id']), media_url)

        return success_response({"message": "Media removed"})

    except Exception as e:
        logger.error(f"Error removing campaign media: {str(e)}")
        return error_response(str(e), 500)


# ==================== USER (VOTER) MANAGEMENT ENDPOINTS ====================

@app.function_name(name="GetUsers")
@app.route(route="users", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_users(req: func.HttpRequest) -> func.HttpResponse:
    """List user accounts, optionally filtered by role (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user or user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        role = req.params.get('role')
        users = user_repo.get_all_users(role)

        return success_response({
            "users": [
                {
                    "_id": str(u["_id"]),
                    "name": u.get("name"),
                    "email": u.get("email"),
                    "role": u.get("role"),
                    "created_at": u.get("created_at")
                }
                for u in users
            ]
        })

    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="CreateUser")
@app.route(route="users", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    """Create a voter or candidate account directly (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        admin_user = verify_token(token)
        if not admin_user or admin_user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        data = req.get_json()
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        role = data.get('role', 'voter')
        if role not in ('voter', 'candidate'):
            return error_response("Role must be voter or candidate", 400)

        if user_repo.get_user_by_email(data['email']):
            return error_response("A user with this email already exists", 400)

        user_id = user_repo.create_user({
            "email": data['email'],
            "password_hash": hash_password(data['password']),
            "name": data['name'],
            "role": role,
            "created_at": datetime.utcnow()
        })

        if role == 'candidate':
            _ensure_candidate_profile(user_id, data['email'], data.get('name'))

        return created_response({"user_id": user_id}, f"/api/users/{user_id}")

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="UpdateUser")
@app.route(route="users/{user_id}", methods=["PUT"], auth_level=func.AuthLevel.ANONYMOUS)
def update_user(req: func.HttpRequest) -> func.HttpResponse:
    """Update a user's name, email or role (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        admin_user = verify_token(token)
        if not admin_user or admin_user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        user_id = req.route_params.get('user_id')
        if not user_id:
            return error_response("Missing user_id", 400)

        data = req.get_json()
        editable_fields = {'name', 'email', 'role'}
        updates = {k: v for k, v in data.items() if k in editable_fields}

        if 'role' in updates and updates['role'] not in ('admin', 'voter', 'candidate'):
            return error_response("Invalid role", 400)

        if 'password' in data and data['password']:
            updates['password_hash'] = hash_password(data['password'])

        if not updates:
            return error_response("No editable fields provided", 400)

        success = user_repo.update_user(user_id, updates)

        if success:
            return success_response({"message": "User updated successfully"})
        else:
            return error_response("Failed to update user", 400)

    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="DeleteUser")
@app.route(route="users/{user_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
def delete_user(req: func.HttpRequest) -> func.HttpResponse:
    """Delete a user account (Admin only)"""
    try:
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)

        token = token.replace('Bearer ', '')
        admin_user = verify_token(token)
        if not admin_user or admin_user.get('role') != 'admin':
            return error_response("Unauthorized access", 403)

        user_id = req.route_params.get('user_id')
        if not user_id:
            return error_response("Missing user_id", 400)

        success = user_repo.delete_user(user_id)

        if success:
            return success_response({"message": "User deleted successfully"})
        else:
            return error_response("Failed to delete user", 400)

    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return error_response(str(e), 500)


# ==================== VOTING ENDPOINTS ====================

@app.function_name(name="CastVote")
@app.route(route="elections/{election_id}/vote", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def cast_vote(req: func.HttpRequest) -> func.HttpResponse:
    """Cast a vote"""
    try:
        # Verify user token
        token = req.headers.get('Authorization')
        if not token:
            return error_response("Missing authorization token", 401)
        
        token = token.replace('Bearer ', '')
        user = verify_token(token)
        if not user:
            return error_response("Invalid token", 401)

        if user.get('role') == 'candidate':
            return error_response("Candidate accounts cannot cast votes", 403)

        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        data = req.get_json()

        if 'candidate_id' not in data:
            return error_response("Missing candidate_id", 400)
        if 'position' not in data:
            return error_response("Missing position", 400)

        result = election_service.cast_vote(
            election_id=election_id,
            candidate_id=data['candidate_id'],
            voter_id=user.get('user_id'),
            voter_email=user.get('email'),
            position=data['position']
        )
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error casting vote: {str(e)}")
        return error_response(str(e), 500)


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.function_name(name="RegisterUser")
@app.route(route="auth/register", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def register_user(req: func.HttpRequest) -> func.HttpResponse:
    """Register a new voter account"""
    try:
        data = req.get_json()

        required_fields = ['email', 'password', 'name']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)

        if len(data['password']) < 6:
            return error_response("Password must be at least 6 characters", 400)

        if user_repo.get_user_by_email(data['email']):
            return error_response("A user with this email already exists", 400)

        requested_role = data.get('role', 'voter')
        if requested_role not in ('voter', 'candidate'):
            requested_role = 'voter'

        role = 'admin' if data['email'].lower() == (os.getenv('ADMIN_EMAIL') or '').lower() else requested_role

        user_id = user_repo.create_user({
            "email": data['email'],
            "password_hash": hash_password(data['password']),
            "name": data['name'],
            "role": role,
            "created_at": datetime.utcnow()
        })

        if role == 'candidate':
            _ensure_candidate_profile(user_id, data['email'], data.get('name'))

        token = generate_token(user_id, data['email'], role)

        return created_response({
            "token": token,
            "user": {
                "user_id": user_id,
                "email": data['email'],
                "name": data['name'],
                "role": role
            }
        }, "/api/auth/login")

    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="LoginUser")
@app.route(route="auth/login", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def login_user(req: func.HttpRequest) -> func.HttpResponse:
    """Authenticate a user and issue a JWT"""
    try:
        data = req.get_json()

        if 'email' not in data or 'password' not in data:
            return error_response("Missing email or password", 400)

        user = user_repo.get_user_by_email(data['email'])
        if not user or not verify_password(data['password'], user.get('password_hash', '')):
            return error_response("Invalid email or password", 401)

        user_id = str(user['_id'])
        role = user.get('role', 'voter')

        if role == 'candidate':
            _ensure_candidate_profile(user_id, user['email'], user.get('name'))

        token = generate_token(user_id, user['email'], role)

        return success_response({
            "token": token,
            "user": {
                "user_id": user_id,
                "email": user['email'],
                "name": user.get('name'),
                "role": role
            }
        })

    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return error_response(str(e), 500)


# ==================== RESULTS ENDPOINTS ====================

@app.function_name(name="GetLiveResults")
@app.route(route="elections/{election_id}/results", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_live_results(req: func.HttpRequest) -> func.HttpResponse:
    """Get live election results"""
    try:
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        result = election_service.get_live_results(election_id)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 404)
    
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetElectionStats")
@app.route(route="elections/{election_id}/stats", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_election_stats(req: func.HttpRequest) -> func.HttpResponse:
    """Get headline dashboard numbers (seats, candidates, registered voters) - public"""
    try:
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)

        total_registered_voters = user_repo.count_users('voter')
        result = election_service.get_stats(election_id, total_registered_voters)

        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 404)

    except Exception as e:
        logger.error(f"Error getting election stats: {str(e)}")
        return error_response(str(e), 500)


@app.function_name(name="GetPositionResults")
@app.route(route="elections/{election_id}/results/{position}", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def get_position_results(req: func.HttpRequest) -> func.HttpResponse:
    """Get results for a specific position"""
    try:
        election_id = req.route_params.get('election_id')
        position = req.route_params.get('position')
        
        if not election_id or not position:
            return error_response("Missing election_id or position", 400)
        
        result = election_service.get_position_results(election_id, position)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 404)
    
    except Exception as e:
        logger.error(f"Error getting position results: {str(e)}")
        return error_response(str(e), 500)
