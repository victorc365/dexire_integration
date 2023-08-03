import os
from typing import List

import yaml
from enums.environment import Environment
from yaml.loader import SafeLoader


class Bot:
    def __init__(self, data: dict) -> None:
        self.name: str = data.get('name', 'undefined')
        self.url: str = data.get('url', 'undefined')
        self.is_dev: bool = data.get('isDev', True)
        self.is_pryv_required: bool = data.get('isPryvRequired', False)
        self.required_permissions: List[Permission] = []

        for required_permission in data.get('requiredPermissions'):
            for id, permission in required_permission.items():
                stream_id = f'{self.name}_{id}'
                self.required_permissions.append(
                    Permission(stream_id, permission, id))


class Permission:
    def __init__(self, stream_id, level, default_name) -> None:
        self.stream_id = stream_id
        self.level = level
        self.default_name = default_name


class BotService:
    def __init__(self) -> None:
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