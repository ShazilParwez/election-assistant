import logging
import traceback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from services.validator import QueryValidator
from services.gemini_service import get_response

logger = logging.getLogger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="The user's election-related question.")

class QueryResponse(BaseModel):
    response: str

@router.post("/ask", response_model=QueryResponse)
async def ask_election_assistant(request: Request, payload: QueryRequest) -> QueryResponse | JSONResponse:
    """
    Endpoint to ask election-related questions.

    Args:
        request (Request): The raw incoming request.
        payload (QueryRequest): The validated query payload.

    Returns:
        QueryResponse | JSONResponse: A structured AI response or an error JSON.
    """
    try:
        body_bytes = await request.body()
        logger.info(f"Received API request body: {body_bytes.decode('utf-8')}")
    except Exception as e:
        logger.warning(f"Could not read request body: {e}")

    logger.info(f"Extracted query: {payload.query}")
    
    if not payload.query or not payload.query.strip():
        logger.error("Validation failed: Empty query")
        return JSONResponse(status_code=400, content={"detail": "Query cannot be empty"})
    
    # 1. Validate Input
    try:
        is_safe, error_message = QueryValidator.is_safe(payload.query)
        if not is_safe:
            logger.error(f"Query validation failed: {error_message}")
            if "security reasons" in error_message:
                return JSONResponse(status_code=400, content={"detail": error_message})
            return QueryResponse(response=error_message)
    except Exception as e:
        logger.error("Error during validation", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "error": str(e)})

    # 2. Generate Response using Gemini
    try:
        response_content = get_response(payload.query)
        logger.info("Sending Gemini response back to client")
        return QueryResponse(response=response_content)
    except ValueError as ve:
        logger.error(f"ValueError in LLM service: {ve}", exc_info=True)
        return JSONResponse(status_code=400, content={"detail": str(ve)})
    except Exception as e:
        logger.error("Exception in LLM service", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error", "error": str(e)})
