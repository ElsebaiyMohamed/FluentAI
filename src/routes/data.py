import logging

from fastapi import APIRouter, Depends, Request, UploadFile, status, File, Form
from fastapi.responses import JSONResponse

from src.helpers import get_settings, Settings
from src.core.pronunciation import assess_audio_file
from ..controllers import DataController
from ..models import ResponseStatus

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/fluentai/v1/data",
    tags=["api_v1", "data"],
)

@data_router.post("/upload/{lesson_id}")
async def upload_data(
    lesson_id: str,
    file: UploadFile = File(...),
    app_settings: Settings = Depends(get_settings),
):
    data_controller = DataController()
    is_valid, status_value = data_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": status_value, "lesson_id": lesson_id},
        )

    try:
        file_path, file_id = await data_controller.save_file(file, lesson_id)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": ResponseStatus.FILE_SAVE_ERROR.value, "lesson_id": lesson_id},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": status_value, "lesson_id": lesson_id, "file_id": file_id},
    )


@data_router.post("/assess/{lesson_id}")
async def assess_pronunciation(
    request: Request,
    lesson_id: str,
    audio: UploadFile = File(...),
    expected_text: str | None = Form(None),
    text: UploadFile | None = File(None),
    app_settings: Settings = Depends(get_settings),
):
    if text is not None:
        raw_text = await text.read()
        try:
            expected_text = raw_text.decode("utf-8")
        except Exception:
            expected_text = raw_text.decode("latin-1", errors="ignore")

    data_controller = DataController()
    is_valid, status_value = data_controller.validate_file(audio)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": status_value, "lesson_id": lesson_id},
        )

    try:
        audio_path, file_id = await data_controller.save_file(audio, lesson_id)
        processor = request.app.state.pronunciation_processor
        model = request.app.state.pronunciation_model
        scores = assess_audio_file(audio_path, processor, model, expected_text)
    except Exception as e:
        logger.error(f"Error processing pronunciation assessment: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": ResponseStatus.MODEL_ERROR.value, "lesson_id": lesson_id},
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": ResponseStatus.SUCCESS.value,
            "lesson_id": lesson_id,
            "file_id": file_id,
            "scores": scores,
            "expected_text": expected_text,
        },
    )

