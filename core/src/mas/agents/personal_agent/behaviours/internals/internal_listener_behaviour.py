import json

from spade.behaviour import CyclicBehaviour
from enums.status import Status
from mas.agents.generic_behaviours.send_message_behaviour import SendHemerappOutgoingMessageBehaviour
from mas.agents.personal_agent.behaviours.internals.register_to_gateway_behaviour import FreeSlotGatewayRequestMessage
from mas.agents.personal_agent.behaviours.profiling_fsm import ProfilingFSMBehaviour
from mas.enums.message import MessagePerformative, MessageType, MessageMetadata, MessageContext, MessageBodyFormat
from services.bot_service import BotService
from services.chat_service import ChatService
from utils.communication_utils import get_profiling_fsm_template
from spade.message import Message
from utils.communication_utils import get_contextual_fsm_template

class InternalListenerBehaviour(CyclicBehaviour):
    def __init__(self) -> None:
        super().__init__()

    async def _process_free_slots_message(self, message):
        message_performative = message.get_metadata(MessageMetadata.PERFORMATIVE.value)
        match message_performative:
            case MessagePerformative.AGREE.value:
                ChatService().register_gateway(str(message.sender), self.agent.id)
                self.agent.status = Status.RUNNING.value
            case MessagePerformative.REFUSE.value:
                message = FreeSlotGatewayRequestMessage(self.agent.id, self.agent.subscribed_gateways.pop())
                await self.send(message)

    async def _process_available_gateways_message(self, message):
        message_performative = message.get_metadata(MessageMetadata.PERFORMATIVE.value)
        match message_performative:
            case MessagePerformative.AGREE.value:
                gateways = json.loads(message.body)
                self.agent.last_gateway = gateways[-1]
                for gateway in gateways:
                    if any(gateway == str(contact) for contact in self.presence.get_contacts()):
                        self.agent.subscribed_gateways.append(gateway)
                if len(self.agent.subscribed_gateways) > 0:
                    message = FreeSlotGatewayRequestMessage(self.agent.id, self.agent.subscribed_gateways.pop())
                    await self.send(message)
                else:
                    # Use the most recent gateway as it should have available space
                    self.presence.subscribe(self.agent.last_gateway)

    async def run(self) -> None:
        message: Message = await self.receive(timeout=1)

        if message is None:
            return
        message_type = message.get_metadata(MessageMetadata.TYPE.value)

        match message_type:
            case MessageType.FREE_SLOTS.value:
                await self._process_free_slots_message(message)
            case MessageType.AVAILABLE_GATEWAYS.value:
                await self._process_available_gateways_message(message)
            case MessageType.OPENED_WEBSOCKET.value:
                gateway = message.sender
                history = self.agent.persistence_service.get_history()
                message = json.dumps(history)
                metadata = {MessageMetadata.CONTEXT.value: MessageContext.HISTORY.value}
                if len(history) == 0:
                    # send welcome message
                    message = BotService().get_welcome_message(self.agent.bot_name)
                    metadata = {MessageMetadata.CONTEXT.value: MessageContext.WELCOMING.value,
                                MessageMetadata.BODY_FORMAT.value: MessageBodyFormat.TEXT.value}

                self.agent.add_behaviour(SendHemerappOutgoingMessageBehaviour(
                    to=gateway,
                    sender=self.agent.id,
                    body=str(message),
                    performative=MessagePerformative.INFORM.value,
                    metadata=metadata
                ))

                metadata = {MessageMetadata.CONTEXT.value: MessageContext.KEYBOARD.value,
                            MessageMetadata.BODY_FORMAT.value: MessageBodyFormat.TEXT.value}
                if self.agent.custom_keyboard is not None:
                    self.agent.add_behaviour(SendHemerappOutgoingMessageBehaviour(
                        to=gateway,
                        sender=self.agent.id,
                        body=json.dumps(self.agent.custom_keyboard),
                        performative=MessagePerformative.INFORM.value,
                        metadata=metadata
                    ))

                profiling_configuration = BotService().get_bot_profiling(self.agent.bot_name)
                if profiling_configuration is not None:
                    if len(self.agent.profile) == 0:
                        self.agent.add_contextual_behaviour(MessageContext.PROFILING.value,
                                                            ProfilingFSMBehaviour(profiling_configuration),
                                                            get_profiling_fsm_template())
                        return
                self.agent.add_contextual_behaviour(MessageContext.CONTEXTUAL.value, self.agent.contextual_module(), get_contextual_fsm_template())

