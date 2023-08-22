from mas.agents.basic_agent import BasicAgent


class PersonalAgent(BasicAgent):
    def __init__(self, bot_user_name: str, password: str, token: str):
        super().__init__(bot_user_name)
        self.password = password
        self.token = token

    async def setup(self):
        self.logger.debug('Setup and ready!')
        return await super().setup()