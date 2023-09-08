from fastapi import APIRouter, WebSocket
from services.chat_service import ChatService

router = APIRouter(prefix='/ws', tags=['Websocket'])
chat_service = ChatService()


@router.websocket('/{client_name}/{bot_name}')
async def websocket_endpoint(websocket: WebSocket, client_name: str, bot_name: str):
    bot_user_name = f'{bot_name}_{client_name}'
    await chat_service.forward_websocket(websocket, client_name, bot_user_name)
