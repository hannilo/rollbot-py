import os
import logging

from dotenv import load_dotenv

import rollbot.config.log_config

from rollbot.Bot import Bot
from rollbot.CommandManager import CommandManager
from rollbot.config.BotConfig import BotConfig

logger = logging.getLogger('bot')

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')
BUILD = os.getenv('BUILD')

botConfig = BotConfig(PREFIX, BUILD)
bot = Bot(botConfig, CommandManager(botConfig))
bot.run(TOKEN)
