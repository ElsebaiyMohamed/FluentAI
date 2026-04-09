from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
from src.helpers import get_settings, Settings  
from ..controllers import DataController

data_router = APIRouter(
    prefix="/fluentai/v1/data", 
    tags=["api_v1", "data"]
)

@data_router.post("/upload/{lesson_id}")
async def upload_data(lesson_id: str, file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    is_valid, st, explain = DataController().validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"signal": st, "explanation": explain}
            )   
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content={"signal": st, "explanation": explain}
        )
