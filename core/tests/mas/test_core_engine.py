from src.enums.status import Status
from src.mas.core_engine import CoreEngine
from tests.mas.utils.factories import (MockedDummyAgentFactory,
                                       MockedGatewayAgentFactory)


class TestCoreEngine():
    def test_init(self):
        core_engine = CoreEngine()
        assert core_engine._status == Status.TURNED_OFF.value

    def test_add_agent(self):
        core_engine = CoreEngine(run_api=False)
        gateway_agent = MockedGatewayAgentFactory()

        assert len(core_engine.agents) == 0

        core_engine.add_agent(gateway_agent)
        assert len(core_engine.agents) == 1

    def test_running(self):
        core_engine = CoreEngine(run_api=False)
        dummy_agent = MockedDummyAgentFactory()
        core_engine.add_agent(dummy_agent)
        core_engine.start()
        assert core_engine._status == Status.RUNNING.value
