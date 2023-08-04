from api.models.bot_model import BotModel
from fastapi import APIRouter, status
from services.bot_service import Bot, BotService
from api.models.user_info_model import UserInfoModel


router = APIRouter(prefix='/bots', tags=['Bots'])
bot_service: BotService = BotService()

@router.get('/',
            summary='Return the list of available Bots',
            status_code=status.HTTP_200_OK,
            response_description='List of Bots',
            response_model=list[BotModel])
def get():
    bots: list[Bot] = bot_service.get_bot_descriptors()
    response = [BotModel.model_validate(bot) for bot in bots]
    return response


@router.post('/{bot_name}/connect',
             summary='Connect the user to the bot corresponding to botName',
             status_code=status.HTTP_201_CREATED
             )
def connect(bot_name: str, user_info: UserInfoModel):
    bot_service.connect_to_bot(user_info.username, bot_name, user_info.token)
    return {'botname':bot_name}