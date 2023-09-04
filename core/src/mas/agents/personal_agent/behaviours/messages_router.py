from spade.behaviour import CyclicBehaviour


class MessagesRouterBehaviour(CyclicBehaviour):
    """ Personal Agent's internal message routing services.

    Personal Agents require a router as entry point for all incoming messages. The router waits for incoming messages
    and process them by using the metadata "action" attached to the received message. The router serves two main
    purposes. First, it is in charge to route the message to the internal queue of the correct agent's behaviour.
    Second, if the action to perform requires to start a new behaviour (ie: a OneShotBehaviour), the router can
    attach the behaviour to the agent and start it.
    """

    async def run(self) -> None:
        msg = await self.receive(timeout=1)
        if msg is not None:
            self.agent.save_message(message=msg)
            action = msg.get_metadata('action')
