from api.routes.v1 import bots, feedback, messages, status, user, websocket
from fastapi import APIRouter

api_router = APIRouter(prefix='/v1')
api_router.include_router(bots.router)
api_router.include_router(feedback.router)
api_router.include_router(messages.router)
api_router.include_router(status.router)
api_router.include_router(user.router)
api_router.include_router(websocket.router)
