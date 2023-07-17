import nest_asyncio
import setup

# https://medium.com/@vyshali.enukonda/how-to-get-around-runtimeerror-this-event-loop-is-already-running-3f26f67e762e
# Spade and unicorn are both using asyncio and this create a conflict because asyncio does not allow nested event loops.
# nest_asyncio is a patch for this.
# TODO - Remove this library when the official asyncio library is patched.
nest_asyncio.apply()

setup.init_logger()
app = setup.init_fast_api()
setup.init_mas()
