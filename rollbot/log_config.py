import os
import logging
from logging.config import dictConfig

BOT_LOGLEVEL = os.getenv('BOT_LOGLEVEL') or 'DEBUG'  # 'INFO'
if BOT_LOGLEVEL == 'DEBUG':
  LOGLEVEL = logging.DEBUG

logging_config = dict(
  version=1,
  formatters={
    'f': {'format':
            '%(levelname)-8s %(asctime)s %(name)-18s  %(message)s'}
  },
  handlers={
    'console': {
      'class': 'logging.StreamHandler',
      'formatter': 'f',
      'level': LOGLEVEL
    },
    'file': {
      'class': 'logging.handlers.RotatingFileHandler',
      'formatter': 'f',
      'filename': 'bot.log',
      'level': LOGLEVEL
    }
  },
  root={
    'handlers': ['console', 'file'],
    'level': LOGLEVEL,
  },
)

dictConfig(logging_config)

logger = logging.getLogger()
logger.info(f"Logging level: {LOGLEVEL}")
