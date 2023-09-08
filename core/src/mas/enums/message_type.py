from enum import Enum


class MessageType(Enum):
    FREE_SLOTS = 'free_slots'
    AVAILABLE_GATEWAYS = 'available_gateways'