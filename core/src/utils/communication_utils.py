from spade.template import Template

from mas.enums.message import MessageThread


def get_internal_thread_template():
    internal_communication_template = Template()
    internal_communication_template.thread = MessageThread.INTERNAL_THREAD.value
    return internal_communication_template


def get_user_thread_template():
    user_communication_template = Template()
    user_communication_template.thread = MessageThread.USER_THREAD.value
    return user_communication_template
