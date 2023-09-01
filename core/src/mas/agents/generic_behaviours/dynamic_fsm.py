from spade.behaviour import FSMBehaviour, State


class DynamicState(State):
    def __init__(self):
        super().__init__()

    def setup(self):
        pass

    async def run(self) -> None:
        pass


class DynamicFSMBehaviour(FSMBehaviour):
    def __init__(self):
        super().__init__()

    async def on_start(self) -> None:
        pass

    async def on_end(self) -> None:
        pass

    def setup(self) -> None:
        pass
