from mas.agents.personal_agent.behaviours.contextual_fsm import ContextualFSMBehaviour


class ContextualFSM(ContextualFSMBehaviour):
    def __init__(self):
        super().__init__()


    async def on_start(self):
        await super().on_start()
        print(f"CA MARCHE!!!!!!!!: {self.agent.bot_username}")