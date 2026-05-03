import logging
from typing import Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.interfaces.llm_interface import LLMInterface
from backend.services.formatter import parse_and_format_response
from backend.services.gemini_service import get_llm_service
from backend.services.validator import QueryValidator

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    """
    Schema for the incoming user query.
    """

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The user's election-related question.",
    )


class QueryResponse(BaseModel):
    """
    Schema for the structured AI response.
    """

    title: str = Field(..., description="The title of the insight.")
    summary: str = Field(..., description="A brief summary of the response.")
    detailed: str = Field(..., description="Detailed explanation or steps.")


@router.post("/ask", response_model=QueryResponse)
async def ask_election_assistant(
    request: Request,
    payload: QueryRequest,
    llm_service: LLMInterface = Depends(get_llm_service),
) -> Union[QueryResponse, JSONResponse]:
    """
    Endpoint to ask election-related questions.

    Args:
        request (Request): The raw incoming request.
        payload (QueryRequest): The validated query payload.
        llm_service (LLMInterface): The injected LLM service.

    Returns:
        Union[QueryResponse, JSONResponse]: A structured AI response or an error JSON.
    """
    await _log_request_details(request, payload)

    if not payload.query or not payload.query.strip():
        logger.error("Validation failed: Empty query")
        return JSONResponse(
            status_code=400, content={"detail": "Query cannot be empty"}
        )

    # 1. Validate Input
    validation_result = _validate_query_content(payload.query)
    if isinstance(validation_result, JSONResponse):
        return validation_result
    if isinstance(validation_result, QueryResponse):
        return validation_result

    # 2. Generate and Format Response
    return _process_llm_request(payload.query, llm_service)


async def _log_request_details(request: Request, payload: QueryRequest) -> None:
    """Logs the incoming request body and extracted query."""
    try:
        body_bytes = await request.body()
        logger.info(f"Received API request body: {body_bytes.decode('utf-8')}")
    except Exception as e:
        logger.warning(f"Could not read request body: {e}")
    logger.info(f"Extracted query: {payload.query}")


def _validate_query_content(query: str) -> Union[None, QueryResponse, JSONResponse]:
    """Validates the query for safety and relevance."""
    try:
        is_safe, error_message = QueryValidator.is_safe(query)
        if not is_safe:
            logger.error(f"Query validation failed: {error_message}")
            if "security reasons" in error_message:
                return JSONResponse(status_code=400, content={"detail": error_message})

            return QueryResponse(
                title="Topic Restriction",
                summary="Election-related queries only.",
                detailed=error_message,
            )
        return None
    except Exception as e:
        logger.error("Error during validation", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)},
        )


def _process_llm_request(
    query: str, llm_service: LLMInterface
) -> Union[QueryResponse, JSONResponse]:
    """Handles the LLM call and response formatting."""
    try:
        raw_response = llm_service.get_response(query)
        logger.info("Received raw response from LLM service")

        formatted_content = parse_and_format_response(raw_response)
        logger.info("Sending structured response back to client")

        return QueryResponse(**formatted_content)

    except ValueError as ve:
        logger.error(f"ValueError in LLM service: {ve}", exc_info=True)
        return JSONResponse(status_code=400, content={"detail": str(ve)})
    except Exception as e:
        logger.error("Exception in LLM service", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)},
        )
