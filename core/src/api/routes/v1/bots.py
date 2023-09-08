from fastapi import APIRouter, status

from api.models.bot_model import BotModel
from api.models.user_info_model import UserInfoModel
from services.bot_service import Bot, BotService

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
async def connect(bot_name: str, user_info: UserInfoModel):
    bot_status = await bot_service.connect_to_bot(user_info.username, bot_name, user_info.token)
    return bot_status


@router.get('/{bot_user_name}/status',
            summary='Get the status of the bot corresponding to bot_user_name in format {bot_name}_{username}',
            status_code=status.HTTP_200_OK)
async def get_status(bot_user_name: str):
    bot_status = bot_service.get_status(bot_user_name)
    return bot_status
