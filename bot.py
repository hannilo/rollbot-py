import os
import discord
import logging

import rollbot.log_config
from dotenv import load_dotenv

from rollbot.Bot import Bot

logger = logging.getLogger('bot')

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')
BUILD = os.getenv('BUILD')

bot = Bot(commandPrefix=PREFIX, build=BUILD)
bot.run(TOKEN)
