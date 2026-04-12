from fastapi import FastAPI, APIRouter, Depends, Request
from src.helpers import get_settings, Settings

base_router = APIRouter(
    prefix="/fluentai/v1",
    tags=["api_v1"]
)


@base_router.get("/info")
async def data_info(app_settings: Settings = Depends(get_settings)):
    return {
        "data_endpoint": "This endpoint provides information about the data used in the application.",
        "app_name": app_settings.APP_NAME,
        "app_version": app_settings.APP_VERSION,
        "author": app_settings.AUTHOR,
    }


@base_router.get("/health")
async def health_check(request: Request):
    model_loaded = hasattr(request.app.state, "pronunciation_model") and request.app.state.pronunciation_model is not None
    processor_loaded = hasattr(request.app.state, "pronunciation_processor") and request.app.state.pronunciation_processor is not None

    return {
        "status": "ok" if model_loaded and processor_loaded else "degraded",
        "model_loaded": model_loaded,
        "processor_loaded": processor_loaded,
    }




