import os
from typing import List

import yaml
from yaml.loader import SafeLoader

from enums.environment import Environment
from mas.core_engine import CoreEngine
from services.openfire.user_service import UserService
from utils.metaclasses.singleton import Singleton
from utils.string_builder import create_jid


class Bot:
    def __init__(self, data: dict) -> None:
        self.name: str = data.get('name', 'undefined')
        self.url: str = data.get('url', 'undefined')
        self.is_dev: bool = data.get('isDev', True)
        self.is_pryv_required: bool = data.get('isPryvRequired', False)
        self.has_profiling_behaviour: bool = data.get('hasProfilingBehaviour', False)
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


class BotService(metaclass=Singleton):
    def __init__(self) -> None:
        self.user_service: UserService = UserService()
        self.bots_folder = os.environ.get(
            Environment.MODULE_DIRECTORY_PATH.value)
        self.bots = []

    def get_bots(self):
        return self.bots

    def get_status(self, bot_user_name: str) -> bool:
        return CoreEngine().container.get_agent(create_jid(bot_user_name.lower())).status

    def get_bot_descriptors(self) -> list[Bot]:
        bots = os.listdir(self.bots_folder)
        bot_descriptors = []
        for bot in bots:
            descriptor_file = f'{self.bots_folder}/{bot}/descriptor.yaml'
            with open(descriptor_file) as file:
                data = yaml.load(file, Loader=SafeLoader)
                bot_descriptor = Bot(data)
                bot_descriptors.append(bot_descriptor)
                if bot_descriptor.name not in self.bots:
                    self.bots.append(bot_descriptor.name.lower())
        return bot_descriptors

    async def connect_to_bot(self, username: str, bot_name: str, token: str) -> None:
        bot_user_name = f'{bot_name}_{username}'
        bot_exists = self.user_service.bot_user_exist(bot_user_name)
        if not bot_exists:
            self.user_service.create_bot_user(bot_user_name, bot_user_name)
        await CoreEngine().create_personal_agent(bot_user_name, token)
        return self.get_status(bot_user_name)
