"""
NUST Alumni Voting Portal - Azure Functions Backend
Handles election management and voting operations
"""
import azure.functions as func
import json
import os
import logging
from datetime import datetime
from typing import Optional
from repositories.election_repository import ElectionRepository
from services.election_service import ElectionService
from shared.response_utils import success_response, error_response, created_response
from shared.jwt_utils import verify_token, get_user_from_token

app = func.FunctionApp()

# Initialize repository and service
MONGO_CONNECTION_STRING = os.getenv('MONGODB_CONNECTION_STRING')
if not MONGO_CONNECTION_STRING:
    raise ValueError("MONGODB_CONNECTION_STRING environment variable not set")

election_repo = ElectionRepository(MONGO_CONNECTION_STRING)
election_service = ElectionService(election_repo)

logger = logging.getLogger(__name__)


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
        success = election_repo.update_election(election_id, data)
        
        if success:
            return success_response({"message": "Election updated successfully"})
        else:
            return error_response("Failed to update election", 400)
    
    except Exception as e:
        logger.error(f"Error updating election: {str(e)}")
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
        
        result = election_service.close_election(election_id)
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error closing election: {str(e)}")
        return error_response(str(e), 500)


# ==================== CANDIDATE ENDPOINTS ====================

@app.function_name(name="AddCandidate")
@app.route(route="elections/{election_id}/candidates", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
def add_candidate(req: func.HttpRequest) -> func.HttpResponse:
    """Add a candidate to an election (Admin only)"""
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
        
        # Validate required fields
        required_fields = ['name', 'position', 'bio']
        for field in required_fields:
            if field not in data:
                return error_response(f"Missing required field: {field}", 400)
        
        result = election_service.add_candidate(
            election_id=election_id,
            name=data['name'],
            position=data['position'],
            bio=data['bio'],
            image_url=data.get('image_url'),
            batch_year=data.get('batch_year'),
            department=data.get('department'),
            contact_email=data.get('contact_email'),
            platform=data.get('platform')
        )
        
        if result['success']:
            return created_response(result, f"/api/candidates/{result['candidate_id']}")
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error adding candidate: {str(e)}")
        return error_response(str(e), 500)


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
        
        election_id = req.route_params.get('election_id')
        if not election_id:
            return error_response("Missing election_id", 400)
        
        data = req.get_json()
        
        if 'candidate_id' not in data:
            return error_response("Missing candidate_id", 400)
        
        result = election_service.cast_vote(
            election_id=election_id,
            candidate_id=data['candidate_id'],
            voter_id=user.get('user_id'),
            voter_email=user.get('email')
        )
        
        if result['success']:
            return success_response(result)
        else:
            return error_response(result['error'], 400)
    
    except Exception as e:
        logger.error(f"Error casting vote: {str(e)}")
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
