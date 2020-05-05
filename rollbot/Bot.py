import logging
import discord
from rollbot.CommandManager import CommandManager, ReplyResult
from rollbot.config.BotConfig import BotConfig


class Bot(discord.Client):
  """
  The base of the Bot. Only concerns itself with discord.Client events and delegates handling
  """
  logger = logging.getLogger(__name__)
  prefix: str
  build: str

  manager: CommandManager

  def __init__(self, config: BotConfig, commandManager: CommandManager):
    super(Bot, self).__init__()
    self.prefix = config.prefix
    self.build = config.build
    self.manager = commandManager
    self.logger.info(f"Will be reacting to '{self.prefix}'")

  async def on_ready(self):
    self.logger.info(f"{self.user} has connected")
    for guild in self.guilds:
      self.logger.info(f"guild: {guild}")

  async def on_message(self, message: discord.Message):
    if message.author == self.user:
      return

    if str(message.content).startswith(self.prefix):
      result = self.manager.handle(message)
      if isinstance(result, ReplyResult):
        await message.channel.send(result.reply)
