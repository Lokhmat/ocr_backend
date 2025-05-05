from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .routers.read_router import read_router

app = FastAPI(title="Readonly Backend")
router = APIRouter(prefix="/api")

@router.get("/")
async def root():
    return {"message": "Readonly Backend API"}

app = FastAPI(title="Readonly Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(read_router)