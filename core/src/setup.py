import logging
import os

from api.v1 import router
from enums.environment import Environment
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def init_logger():
    LOG_DIRECTORY_PATH = os.environ.get(Environment.LOG_DIRECTORY_PATH.value)
    LOG_LEVEL = os.environ.get(Environment.LOG_LEVEL.value)
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                        filename=f'{LOG_DIRECTORY_PATH}/logs.txt')
    return logging.getLogger(__name__)

def init_fast_api():
    app = FastAPI(docs_url='/docs', redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router.api_router)
    return app