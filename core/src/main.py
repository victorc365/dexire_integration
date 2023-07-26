import setup
from mas.agents.dummy_agent import DummyAgent
from mas.agents.gateway_agent import GatewayAgent
from mas.core_engine import CoreEngine

setup.init_logger()
engine = CoreEngine()
gateway_agent = GatewayAgent('gateway_agent_1')
engine.add_agent(gateway_agent)
dummy_agent = DummyAgent('dummy_agent_1')
engine.add_agent(dummy_agent)
engine.start()