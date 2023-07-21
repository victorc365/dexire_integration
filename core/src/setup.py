import logging
import os

from api import router
from enums.environment import Environment
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mas.agents.dummy_agent import DummyAgent
from mas.agents.gateway_agent import GatewayAgent
from mas.core_engine import CoreEngine
from uvicorn import Config, Server


def init_logger() -> None:
    LOG_DIRECTORY_PATH = os.environ.get(Environment.LOG_DIRECTORY_PATH.value)
    LOG_LEVEL = os.environ.get(Environment.LOG_LEVEL.value)
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                        filename=f'{LOG_DIRECTORY_PATH}/logs.txt')


def init_api(loop) -> Server:
    api = FastAPI(docs_url='/docs', redoc_url=None)
    api.add_middleware(CORSMiddleware,
                       allow_origins=['*'],
                       allow_credentials=True,
                       allow_methods=['*'],
                       allow_headers=['*'])
    api.include_router(router.api_router)
    config = Config(app=api,
                    loop=loop,
                    host='0.0.0.0',
                    port=8080)
    server = Server(config)
    return server


def init_engine() -> None:
    engine = CoreEngine()
    gateway_agent = GatewayAgent('gateway_agent_1')
    engine.add_agent(gateway_agent)
    dummy_agent = DummyAgent('dummy_agent_1')
    engine.add_agent(dummy_agent)
    engine.start()
