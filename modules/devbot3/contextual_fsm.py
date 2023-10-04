from mas.agents.personal_agent.behaviours.contextual_fsm import AbstractContextualFSMBehaviour


class ContextualFSM(AbstractContextualFSMBehaviour):
    def __init__(self):
        super().__init__()

    async def on_start(self):
        await super().on_start()