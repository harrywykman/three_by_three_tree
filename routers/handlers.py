import fastapi_chameleon
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from config import SETTINGS


@fastapi_chameleon.template("errors/404.pt")
async def not_found_error(request: Request, exc: HTTPException):
    try:
        # Return context dictionary - decorator handles the template rendering
        return {
            "request": request,
            "title": "Page Not Found",
            "status_code": 404,
            "message": "Page not found",
            "url": str(request.url),
        }
    except Exception:
        # Fallback if template fails
        return JSONResponse(status_code=404, content={"error": "Page not found"})


@fastapi_chameleon.template("errors/500.pt")
async def internal_error(request: Request, exc: Exception):
    try:
        # Return context dictionary - decorator handles the template rendering
        return {
            "request": request,
            "title": "Server Error",
            "status_code": 500,
            "message": "Internal server error",
            "error": str(exc)
            if SETTINGS.deploy != "True"
            else None,  # Show error details only in dev
        }
    except Exception:
        # Fallback if template fails
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
