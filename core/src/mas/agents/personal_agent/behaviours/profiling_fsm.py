from mas.agents.generic_behaviours.dynamic_fsm import DynamicFSMBehaviour


class ProfilingFSMBehaviour(DynamicFSMBehaviour):
    """ State machine used for user profiling.

    This state machine behaviour provides to the personal agent some capabilities to profile a user.
    As different chat bot may need different information from the user, the list of questions for the profiling is
    fully customizable and the profiling behaviour is built using a list of questions provided as a yaml file coming
    with the bot module.
    """
