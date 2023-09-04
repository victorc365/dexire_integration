from spade.behaviour import FSMBehaviour, State


class DynamicState(State):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self.name = config['name']
        self.transition = config['transition']

    def setup(self):
        pass

    async def run(self) -> None:
        pass


class DynamicFSMBehaviour(FSMBehaviour):
    def __init__(self):
        super().__init__()
        self.config = None

    async def on_start(self) -> None:
        pass

    async def on_end(self) -> None:
        pass

    def setup(self) -> None:
        for i, state_config in enumerate(self.config['states']):
            dynamic_state = DynamicState(state_config)
            self.add_state(name=dynamic_state.name, state=dynamic_state, initial=(i == 0))
            self.add_transition(dynamic_state.name, dynamic_state.transition)
