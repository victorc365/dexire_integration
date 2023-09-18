from spade.behaviour import FSMBehaviour

class ContextualFSMBehaviour(FSMBehaviour):
    """ Main state machine behaviour of a module (bot).

    A Personal Agent must have a ContextualFSMBehaviour. It is the state machine that is in charge to execute the module
    main purpose. It defines the main behaviour of the bot. This state machine is loaded dynamically from the
    installation directory of the module and will be executed by all Personal Agents created for this specific module.
    """

    def __init__(self) -> None:
        super().__init__()
