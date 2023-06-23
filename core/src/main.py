from setup import init_fast_api, init_logger

logger = init_logger()
app = init_fast_api()
logger.debug('application initialized')

