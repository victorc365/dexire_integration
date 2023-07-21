import os

from enums.environment import Environment


class ModuleService:
    def __init__(self) -> None:
        self.modules_folder = os.environ.get(
            Environment.MODULE_DIRECTORY_PATH.value)
        self.module_descriptors = self.get_module_descriptors()

    def get_module_descriptors(self):
        modules = os.listdir(self.modules_folder)
        return modules
