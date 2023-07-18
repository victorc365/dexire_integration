from fastapi import APIRouter
from services.module_service import ModuleService

router = APIRouter(prefix='/bots', tags=['Bots'])
module_service = ModuleService()


@router.get('/')
def get():
    return module_service.get_module_descriptors()
