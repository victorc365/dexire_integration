import os

from enums.environment import Environment


class StringBuilder():
    pass


def create_jid(name: str) -> str:
    return f'{name}@{Environment.XMPP_SERVER_URL.value}'
