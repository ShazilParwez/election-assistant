import logging
import traceback
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from core.config import settings
from routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for the Interactive Election Education Assistant"
)

@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    Middleware to log incoming requests and their status codes.

    Args:
        request (Request): The incoming FastAPI request.
        call_next: The next middleware or route handler.

    Returns:
        Response: The generated HTTP response.
    """
    logger.info(f"Incoming Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response Status Code: {response.status_code}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler to safely catch and log all unhandled errors.

    Args:
        request (Request): The incoming request.
        exc (Exception): The unhandled exception.

    Returns:
        JSONResponse: A 500 status response with error details.
    """
    logger.error("Unhandled Exception occurred", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "error": str(exc)}
    )

# Include the router
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
async def root() -> dict[str, str]:
    """
    Health check and root welcome endpoint.

    Returns:
        dict: A welcome message.
    """
    return {"message": f"Welcome to the {settings.PROJECT_NAME} API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
