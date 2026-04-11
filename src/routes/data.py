import logging


from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import  aiofiles

from src.helpers import get_settings, Settings  
from ..controllers import DataController
from ..models import  ResponseStatus

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
                                    prefix="/fluentai/v1/data", 
                                    tags=["api_v1", "data"])

@data_router.post("/upload/{lesson_id}")
async def upload_data(lesson_id: str, file: UploadFile, 
                                app_settings: Settings = Depends(get_settings)
                                ):
    
    data_controller = DataController()
    is_valid, st = data_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            content={"status": st, "lesson_id": lesson_id}
            )    
    
    file_path, file_id = data_controller.gen_unique_filepath(file.filename, lesson_id)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(content)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            content={f"signal": "error", "explanation": {ResponseStatus.FILE_SAVE_ERROR.value}}
            )
    return JSONResponse(
        status_code=status.HTTP_200_OK, 
        content={"status": st, "lesson_id": lesson_id, "file_id": file_id} 
        )
