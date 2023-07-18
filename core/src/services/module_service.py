import os


class ModuleService:
    def __init__(self) -> None:
        self.modules_folder = '/opt/modules'
        self.module_descriptors = self.get_module_descriptors()

    def get_module_descriptors(self):
        modules = os.listdir(self.modules_folder)
        return modules
