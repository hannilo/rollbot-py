import os
import logging
from logging.config import dictConfig

BOT_LOGLEVEL = os.getenv('BOT_LOGLEVEL') or 'DEBUG'  # 'INFO'
if BOT_LOGLEVEL == 'DEBUG':
  LOGLEVEL = logging.DEBUG

logging_config = dict(
  version=1,
  disable_existing_loggers=True,
  formatters={
    'f': {'format':
            '%(levelname)-8s %(asctime)s %(name)-18s  %(message)s'}
  },
  handlers={
    'console': {
      'class': 'logging.StreamHandler',
      'formatter': 'f',
      'level': LOGLEVEL,
    },
  },
  root={
    'handlers': ['console'],
    'level': LOGLEVEL,
  },
)

dictConfig(logging_config)

logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('websockets').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.ERROR)

logger = logging.getLogger()
logger.info(f"Logging level: {LOGLEVEL}")
