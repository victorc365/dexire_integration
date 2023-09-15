from spade.behaviour import CyclicBehaviour

from mas.agents.generic_behaviours.send_message_behaviour import SendHemerappOutgoingMessageBehaviour
from mas.enums.message import MessageMetadata, MessagePerformative


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

    async def run(self) -> None:
        message = await self.receive(timeout=1)

        if message is None:
            return

        if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.INFORM.value:
            # TODO - forward to correct FSM when personal agent FSM are implemented
            self.agent.add_behaviour(SendHemerappOutgoingMessageBehaviour(
                to=str(message.sender),
                sender=str(message.to),
                body=message.body,
                performative=MessagePerformative.INFORM.value
            ))
