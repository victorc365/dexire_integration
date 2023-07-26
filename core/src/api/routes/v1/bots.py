from api.models.bot_model import BotModel
from fastapi import APIRouter, status
from services.bot_service import Bot, BotService

router = APIRouter(prefix='/bots', tags=['Bots'])
bot_service = BotService()


@router.get('/',
            summary='Return the list of available Bots',
            status_code=status.HTTP_200_OK,
            response_description='List of Bots',
            response_model=list[BotModel])
def get():
    bots: list[Bot] = bot_service.get_bot_descriptors()
    response = [BotModel.model_validate(bot) for bot in bots]
    return response