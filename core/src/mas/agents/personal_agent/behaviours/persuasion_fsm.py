from spade.behaviour import FSMBehaviour


class PersuasionFSMBehaviour(FSMBehaviour):
    """ Custom state machine configurable in a per user fashion.

    Each module (bot) can have a persuasion state machine that is configurable per user. In addition to the contextual
    state machine (main behaviour of a module), it is sometimes required that the module achieve some specific tasks
    for a specific user. The persuasion state machine serves this purpose. It is usually configured from the admin
    dashboard of erebots 3 and is executed only by the Personal Agent of the user it has been configured for.
    """
    pass
