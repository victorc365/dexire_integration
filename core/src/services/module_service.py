import os

import yaml
from enums.environment import Environment
from yaml.loader import SafeLoader


class ModuleService:
    def __init__(self) -> None:
        self.modules_folder = os.environ.get(
            Environment.MODULE_DIRECTORY_PATH.value)

    def get_module_descriptors(self):
        modules = os.listdir(self.modules_folder)
        module_descriptors = []
        for module in modules:
            descriptor_file = f'{self.modules_folder}/{module}/descriptor.yaml'
            with open(descriptor_file) as file:
                data = yaml.load(file, Loader=SafeLoader)
                module_descriptors.append(Module(data))
        return module_descriptors


class Module:
    def __init__(self, data: dict) -> None:
        self.name = data.get('name', 'undefined')
        self.url = data.get('url', 'undefined')
        self.dev = data.get('dev', True)
