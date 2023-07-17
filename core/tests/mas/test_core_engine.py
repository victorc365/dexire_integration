from src.enums.status import Status
from src.mas.core_engine import CoreEngine
from tests.mas.utils.factories import MockedGatewayAgentFactory


class TestCoreEngine():
    def test_init(self):
        core_engine = CoreEngine()
        assert core_engine._status == Status.TURNED_OFF.value

    def test_add_agent(self):
        core_engine = CoreEngine()
        gateway_agent = MockedGatewayAgentFactory()

        assert len(core_engine.agents) == 0

        core_engine.add_agent(gateway_agent)
        assert len(core_engine.agents) == 1

    def test_running(self):
        core_engine = CoreEngine()
        gateway_agent = MockedGatewayAgentFactory()

        core_engine.add_agent(gateway_agent)
        core_engine.start()
        assert core_engine._status == Status.RUNNING.value
