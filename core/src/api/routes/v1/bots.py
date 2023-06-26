from fastapi import APIRouter

router = APIRouter(prefix='/bots', tags=['Bots'])


@router.get('/')
def get():
    pass