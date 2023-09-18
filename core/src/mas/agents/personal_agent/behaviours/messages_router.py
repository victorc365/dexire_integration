from spade.behaviour import CyclicBehaviour
from mas.enums.message import MessageMetadata, MessagePerformative, MessageContext


class MessagesRouterBehaviour(CyclicBehaviour):
    """ Personal Agent's internal message routing services.

    Personal Agents require a router as entry point for all incoming messages. The router waits for incoming messages
    and process them by using the metadata "action" attached to the received message. The router serves two main
    purposes. First, it is in charge to route the message to the internal queue of the correct agent's behaviour.
    Second, if the action to perform requires to start a new behaviour (ie: a OneShotBehaviour), the router can
    attach the behaviour to the agent and start it.

    """

    def __init__(self) -> None:
        super().__init__()
        self.addresses = {
            MessageContext.PROFILING.value: None,
            MessageContext.CONTEXTUAL.value: None,
            MessageContext.PERSUASION.value: None
        }

    def set_address(self, context: str, behaviour):
        self.addresses[context] = behaviour

    async def run(self) -> None:
        message = await self.receive(timeout=1)

        if message is None:
            return

        performative = message.metadata[MessageMetadata.PERFORMATIVE.value]
        if performative == MessagePerformative.INFORM.value:
            context = message.metadata[MessageMetadata.CONTEXT.value]
            behaviour = self.addresses[context]

            if behaviour is None:
                self.agent.logger.error(
                    f'No behaviour assigned to context ({context}) but received message for it: {message}')
            if behaviour.is_done():
                self.agent.logger.error(
                    f'A message has been sent for an ended context. Context: {context}, Message: {message}')
                return
            await behaviour.get_state(behaviour.current_state).enqueue(message)
