import setup
import sys
from mas.core_engine import CoreEngine

from dotenv import load_dotenv

sys.path.insert(0, ".")

load_dotenv('../../.env')

setup.init_logger()
engine = CoreEngine()
engine.start()