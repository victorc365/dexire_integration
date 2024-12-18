from mas.agents.generic_behaviours.dynamic_fsm import DynamicFSMBehaviour
from services.bot_service import BotProfilingConfig
from mas.enums.message import MessageContext
from utils.communication_utils import get_contextual_fsm_template

class ProfilingFSMBehaviour(DynamicFSMBehaviour):
    """ State machine used for user profiling.

    This state machine behaviour provides to the personal agent some capabilities to profile a user.
    As different chat bot may need different information from the user, the list of questions for the profiling is
    fully customizable and the profiling behaviour is built using a list of questions provided as a yaml file coming
    with the bot module.
    """

    def __init__(self, config: BotProfilingConfig) -> None:
        if config is None:
            self.logger.debug('No profiling Configuration to load.')
            return

        if config.states is None:
            self.logger.error('Profiling configuration exists but no state has been defined. Skipping profiling FSM')
            return
        self.config = config

        super().__init__()

    def setup(self) -> None:
        super().setup()

    async def on_end(self) -> None:
        profile = self.agent.profile
        persistence_service = self.agent.persistence_service
        persistence_service.save_data(profile, 'profiling')

        self.agent.add_contextual_behaviour(MessageContext.CONTEXTUAL.value, self.agent.contextual_module(), get_contextual_fsm_template())

