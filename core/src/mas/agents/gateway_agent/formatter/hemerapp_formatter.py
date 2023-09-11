from mas.agents.gateway_agent.formatter.abstract_formatter import AbstractFormatter


class HemerappFormatter(AbstractFormatter):
    def format_incoming_message(self, message):
        return message

    def format_outgoing_message(self, message):
        return message