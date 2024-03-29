import logging
import discord
from rollbot.CommandHandler import CommandHandler, ReplyResult
from rollbot.config.BotConfig import BotConfig


class Bot(discord.Client):
  """
  The base of the Bot. Only concerns itself with discord.Client events and delegates handling
  """
  logger = logging.getLogger(__name__)
  prefix: str
  build: str

  handler: CommandHandler

  def __init__(self, config: BotConfig, commandHandler: CommandHandler):
    intents = discord.Intents.all()  # yolo
    super(Bot, self).__init__(intents=intents)
    self.prefix = config.prefix
    self.build = config.build
    self.handler = commandHandler
    self.logger.info(f"Will be reacting to '{self.prefix}'")

  async def on_ready(self):
    self.logger.info(f"{self.user} has connected")
    self.logger.info(f"guilds: {[guild.name for guild in self.guilds]}")

  async def on_message(self, message: discord.Message):
    if message.author == self.user:
      return

    if str(message.content).startswith(self.prefix):
      result = self.handler.handle(message)
      if isinstance(result, ReplyResult):
        await message.channel.send(result.reply)
