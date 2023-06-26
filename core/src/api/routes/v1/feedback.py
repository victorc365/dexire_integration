from fastapi import APIRouter

router = APIRouter(prefix='/feedback', tags=['Feedback'])


@router.get('/')
def get():
    pass

@router.post('/')
def post():
    pass

@router.get('/questions')
def get_questions():
    pass