from fastapi import FastAPI, APIRouter, Depends
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
        "author": app_settings.AUTHOR
    }   



