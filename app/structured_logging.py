import logging
import sys
from pythonjsonlogger import jsonlogger

# Configure the logger at the module level
logger = logging.getLogger("json_logger")
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter('%(asctime)s - %(levelname)s - %(message)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

def structured_log(level, message, **kwargs):
    log_method = getattr(logger, level)
    log_method(message, extra=kwargs)