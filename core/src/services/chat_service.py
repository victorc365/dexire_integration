from utils.metaclasses.singleton import Singleton
from mas.core_engine import CoreEngine


class ChatService(metaclass=Singleton):
    def __init__(self):
        self.bot_gateways = {}

    def register_gateway(self, gateway_id: str, bot_user_name: str):
        bot_user_name = bot_user_name.split('@')[0]
        client_id = bot_user_name.split('_')[1]
        if client_id not in self.bot_gateways.keys():
            self.bot_gateways[client_id] = {}
        self.bot_gateways[client_id][bot_user_name] = gateway_id

    async def forward_websocket(self, websocket, client_id: str, bot_user_name: str):
        gateway_id = self.bot_gateways[client_id][bot_user_name]
        gateway = CoreEngine().container.get_agent(gateway_id)
        await gateway.register_websocket(bot_user_name, websocket)
