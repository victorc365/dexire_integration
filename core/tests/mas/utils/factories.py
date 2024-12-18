from unittest.mock import AsyncMock, Mock

import factory
from src.mas.agents.dummy_agent import DummyAgent
from mas.agents.gateway_agent.gateway_agent import GatewayAgent


class MockedGatewayAgent(GatewayAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = AsyncMock()
        self._async_register = AsyncMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = AsyncMock()
        self.stream = Mock()


class MockedGatewayAgentFactory(factory.Factory):
    class Meta:
        model = MockedGatewayAgent

    name = "fake"


class MockedDummyAgent(DummyAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._async_connect = AsyncMock()
        self._async_register = AsyncMock()
        self.conn_coro = Mock()
        self.conn_coro.__aexit__ = AsyncMock()
        self.stream = Mock()


class MockedDummyAgentFactory(factory.Factory):
    class Meta:
        model = MockedDummyAgent

    name = "dummy"