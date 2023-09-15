from spade.behaviour import CyclicBehaviour, OneShotBehaviour
from spade.message import Message

from mas.enums.message import MessageMetadata, MessagePerformative, MessageThread


class EchoBehaviour(OneShotBehaviour):
    def __init__(self, message) -> None:
        super().__init__()
        self.message = message

    async def run(self) -> None:
        # TODO - remove this dummy behaviour when FSM is implemented
        message = Message()
        message.to = str(self.message.sender)
        message.sender = str(self.message.to)
        message.metadata = {'performative': 'inform', 'direction': 'outgoing', 'target': 'hemerapp'}
        message.body = self.message.body
        message.thread = MessageThread.USER_THREAD.value
        await self.send(message)


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
        print(message)

        if message.metadata[MessageMetadata.PERFORMATIVE.value] == MessagePerformative.INFORM.value:
            # TODO - forward to correct FSM when personal agent FSM are implemented
            self.agent.add_behaviour(EchoBehaviour(message))
