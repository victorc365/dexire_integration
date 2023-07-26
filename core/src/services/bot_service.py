import os

import yaml
from enums.environment import Environment
from yaml.loader import SafeLoader


class Bot:
    def __init__(self, data: dict) -> None:
        self.name = data.get('name', 'undefined')
        self.url = data.get('url', 'undefined')
        self.is_dev = data.get('isDev', True)


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