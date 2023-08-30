import os
from typing import List

import yaml
from yaml.loader import SafeLoader

from enums.environment import Environment
from mas.core_engine import CoreEngine
from services.openfire.user_service import UserService


class Bot:
    def __init__(self, data: dict) -> None:
        self.name: str = data.get('name', 'undefined')
        self.url: str = data.get('url', 'undefined')
        self.is_dev: bool = data.get('isDev', True)
        self.is_pryv_required: bool = data.get('isPryvRequired', False)
        self.required_permissions: List[Permission] = []

        for required_permission in data.get('requiredPermissions'):
            for name, permission in required_permission.items():
                stream_id = f'{self.name}_{name}'
                self.required_permissions.append(
                    Permission(stream_id, permission, name))


class Permission:
    def __init__(self, stream_id, level, default_name) -> None:
        self.stream_id = stream_id
        self.level = level
        self.default_name = default_name


class BotService:
    def __init__(self) -> None:
        self.user_service: UserService = UserService()
        self.bots_folder = os.environ.get(
            Environment.MODULE_DIRECTORY_PATH.value)

    def get_bot_descriptors(self) -> list[Bot]:
        bots = os.listdir(self.bots_folder)
        bot_descriptors = []
        for bot in bots:
            descriptor_file = f'{self.bots_folder}/{bot}/descriptor.yaml'
            with open(descriptor_file) as file:
                data = yaml.load(file, Loader=SafeLoader)
                bot_descriptors.append(Bot(data))
        return bot_descriptors

    async def connect_to_bot(self, username: str, bot_name: str, token: str) -> None:
        bot_user_name = f'{bot_name}_{username}'
        bot_exists = self.user_service.bot_user_exist(bot_user_name)
        if not bot_exists:
            self.user_service.create_bot_user(bot_user_name, bot_user_name)
        await CoreEngine().create_personal_agent(bot_user_name, token)
