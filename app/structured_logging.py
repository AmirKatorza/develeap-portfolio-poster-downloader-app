import logging
import json

class StructuredMessage:
    def __init__(self, message, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def to_json(self):
        return json.dumps({'message': self.message, **self.kwargs})

def structured_log(level, message, **kwargs):
    logger = logging.getLogger(__name__)
    log_method = getattr(logger, level)
    log_method(StructuredMessage(message, **kwargs).to_json())

# Configure the logging at the root level of your application
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')