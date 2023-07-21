from fastapi import APIRouter
from services.module_service import ModuleService

router = APIRouter(prefix='/bots', tags=['Bots'])
module_service = ModuleService()


@router.get('/')
def get():
    modules = module_service.get_module_descriptors()
    return [module.name for module in modules]
