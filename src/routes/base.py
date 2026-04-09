from fastapi import FastAPI, APIRouter

base_router = APIRouter()

@base_router.get("/")
async def root(): 
    return {"message": "Hello World"}



