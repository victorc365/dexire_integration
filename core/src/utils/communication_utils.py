from spade.template import Template

from mas.enums.message import MessageThread, MessageMetadata, MessageContext


def get_internal_thread_template():
    internal_communication_template = Template()
    internal_communication_template.thread = MessageThread.INTERNAL_THREAD.value
    return internal_communication_template


def get_user_thread_template():
    user_communication_template = Template()
    user_communication_template.thread = MessageThread.USER_THREAD.value
    return user_communication_template


def get_contextual_fsm_template():
    user_communication_template = Template()
    user_communication_template.thread = MessageThread.USER_THREAD.value
    user_communication_template.metadata = {MessageMetadata.CONTEXT.value: MessageContext.CONTEXTUAL.value}
    return user_communication_template


def get_profiling_fsm_template():
    user_communication_template = Template()
    user_communication_template.thread = MessageThread.USER_THREAD.value
    user_communication_template.metadata = {MessageMetadata.CONTEXT.value: MessageContext.PROFILING.value}
    return user_communication_template
