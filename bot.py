import os
import logging

from dotenv import load_dotenv

import rollbot.config.log_config

from rollbot.Bot import Bot
from rollbot.CommandHandler import CommandHandler
from rollbot.Roller import Roller
from rollbot.config.BotConfig import BotConfig

logger = logging.getLogger('bot')

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')
SHORTHAND = os.getenv('ALLOW_SHORTHAND') == 'true'
DEBUG = os.getenv('BUILD') == 'true'
BUILD = os.getenv('BUILD')

botConfig = BotConfig(PREFIX, SHORTHAND, DEBUG, BUILD)
roller = Roller()

bot = Bot(botConfig, CommandHandler(botConfig, roller))
bot.run(TOKEN)
