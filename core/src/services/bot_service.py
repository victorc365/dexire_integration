import os

import yaml
import json
from yaml.loader import SafeLoader

from enums.environment import Environment
from mas.core_engine import CoreEngine
from services.openfire.user_service import UserService
from utils.metaclasses.singleton import Singleton
from utils.string_builder import create_jid


class BotProfilingConfig:
    def __init__(self, data: dict) -> None:
        self.name: str = data.get('name', 'undefined')
        self.version: str = data.get('version', 'undefined')
        self.description: str = data.get('description', 'undefined')
        self.invalid_answer_message: str = data.get('invalid_answer_message', None)
        self.states: dict = data.get('states', 'undefined')


class Bot:
    def __init__(self, data: dict) -> None:
        self.name: str = data.get('name', 'undefined')
        self.description: str = data.get('description', 'No description')
        self.url: str = data.get('url', 'undefined')
        self.is_dev: bool = data.get('isDev', True)
        self.is_pryv_required: bool = data.get('isPryvRequired', False)
        self.has_profiling_behaviour: bool = data.get('hasProfilingBehaviour', False)
        self.required_permissions: list[Permission] = []
        self.required_streams: list[Stream] = []
        self.is_update_required: bool = data.get('isUpdateRequired', False)

        for required_permission in data.get('requiredPermissions'):
            for name, permission in required_permission.items():
                self.required_permissions.append(
                    Permission(name, permission, name))
        for required_stream in data.get('requiredStreams'):
            for stream in required_stream.values():
                self.required_streams.append(Stream(stream['id'], stream['parent'], stream['name']))


class Stream:
    def __init__(self, stream_id, parent, default_name) -> None:
        self.stream_id = stream_id
        self.default_name = default_name
        self.parent = parent


class Permission:
    def __init__(self, stream_id, level, default_name) -> None:
        self.stream_id = stream_id
        self.level = level
        self.default_name = default_name


class BotService(metaclass=Singleton):
    def __init__(self) -> None:
        import dotenv
        dotenv.load_dotenv(".env")
        self.user_service: UserService = UserService()
        self.bots_folder = os.environ.get(
            Environment.MODULE_DIRECTORY_PATH.value)
        self.bots = []

    def get_bots(self):
        return self.bots

    def get_status(self, bot_user_name: str) -> bool:
        return CoreEngine().container.get_agent(create_jid(bot_user_name.lower())).status

    def get_bot_descriptor(self, bot_name: str) -> Bot:
        descriptor_file = f'{self.bots_folder}/{bot_name}/descriptor.yaml'
        with open(descriptor_file) as file:
            data = yaml.load(file, Loader=SafeLoader)
            bot_descriptor = Bot(data)
        return bot_descriptor

    def get_bot_descriptors(self) -> list[Bot]:
        bots = os.listdir(self.bots_folder)
        bot_descriptors = []
        for bot in bots:
            bot_descriptor = self.get_bot_descriptor(bot)
            bot_descriptors.append(bot_descriptor)
            if bot_descriptor.name not in self.bots:
                self.bots.append(bot_descriptor.name.lower())
        return bot_descriptors

    async def connect_to_bot(self, username: str, bot_name: str, token: str) -> bool:
        bot_user_name = f'{bot_name}_{username}'
        bot_exists = self.user_service.bot_user_exist(bot_user_name)
        descriptor = self.get_bot_descriptor(bot_name)
        if not bot_exists:
            self.user_service.create_bot_user(bot_user_name, bot_user_name)
            descriptor.is_update_required = True

        await CoreEngine().create_personal_agent(bot_user_name, token, descriptor)
        return self.get_status(bot_user_name)

    def search_user_bots(self, username: str) -> list[Bot] | None:
        if username is None:
            return
        users: list = self.user_service.search_bots(username)['users']
        bot_names = [user['username'].split('_')[0] for user in users]
        bots = []
        for bot_name in bot_names:
            descriptor = self.get_bot_descriptor(bot_name)
            bots.append(descriptor)
        return bots

    def get_bot_profiling(self, bot_name: str) -> BotProfilingConfig | None:
        profiling_file = f'{self.bots_folder}/{bot_name}/profiling.yaml'
        try:
            with open(profiling_file) as file:
                data = yaml.load(file, Loader=SafeLoader)
                bot_profiling = BotProfilingConfig(data)
                return bot_profiling
        except FileNotFoundError:
            return None

    def get_welcome_message(self, bot_name: str) -> str:
        welcome_file = f'{self.bots_folder}/{bot_name}/welcome.txt'
        try:
            with open(welcome_file) as file:
                message = file.read()
                return message
        except FileNotFoundError:
            return None

    def get_custom_keyboard(self, bot_name: str) -> str:
        custom_keyboard_file = f'{self.bots_folder}/{bot_name}/custom_keyboard.json'
        try:
            with open(custom_keyboard_file) as file:
                keyboard = json.load(file)
        except FileNotFoundError:
            return None
        return keyboard
