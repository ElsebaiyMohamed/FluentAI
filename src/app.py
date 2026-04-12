from fastapi import FastAPI
from src.routes import base_router, data_router
from src.core.pronunciation import load_model_components

app = FastAPI()
app.include_router(base_router)
app.include_router(data_router)


@app.on_event("startup")
async def startup_event():
    processor, model = load_model_components()
    app.state.pronunciation_processor = processor
    app.state.pronunciation_model = model

