import logging

from aiomisc.log import basic_config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.auth_router import auth_router
from .routers.process_router import process_router
from .routers.image_router import image_router
from .routers.token_router import token_router
from .routers.user_router import user_router

try:
    from . import bucket_init
except Exception as e:
    print(f"❌ Failed to initialize bucket: {e}")

tags_metadata = [
    {
        "name": "FastApi template",
        "description": "Main API schema.",
    },
]

app = FastAPI(openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(process_router)
app.include_router(image_router)
app.include_router(token_router)
app.include_router(user_router)

basic_config(logging.DEBUG, buffered=True)
