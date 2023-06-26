from fastapi import APIRouter

router = APIRouter(prefix='/user', tags=['User'])

@router.get('/profile')
def get_profile():
    pass

@router.post('/profile')
def post_profile():
    pass

@router.patch('/profile')
def patch_profile():
    pass

@router.put('/profile')
def put_profile():
    pass

@router.get('/stats')
def get_stats():
    pass