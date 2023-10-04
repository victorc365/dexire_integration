from enum import Enum


class Environment(Enum):
    LOG_DIRECTORY_PATH = 'LOG_DIRECTORY_PATH'
    LOG_LEVEL = 'LOG_LEVEL'
    MODULE_DIRECTORY_PATH = 'MODULE_DIRECTORY_PATH'
    XMPP_ADMIN_PORT = 'XMPP_ADMIN_PORT'
    XMPP_SECRET_KEY = 'XMPP_SECRET_KEY'
    XMPP_SERVER_URL = 'XMPP_SERVER_URL'
    MAXIMUM_CLIENTS_PER_GATEWAY = 'MAXIMUM_CLIENTS_PER_GATEWAY'
    PRYV_SERVER_URL = 'PRYV_SERVER_URL'
