from spade.behaviour import OneShotBehaviour


class SetupPresenceListener(OneShotBehaviour):
    def on_available(self, jid, stanza):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} is available.')

    def on_subscribed(self, jid):
        self.agent.logger.debug(f'Agent {jid.split("@")[0]} has accepted the subscription.')

    async def run(self):
        self.presence.on_available = self.on_available
        self.presence.on_unavailable = self.on_unavailable
        self.presence.on_subscribed = self.on_subscribed
