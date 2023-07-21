from fastapi import APIRouter

router = APIRouter(prefix='/status', tags=['Status'])


@router.get('/')
def get():
    pass
