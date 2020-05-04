import logging
from typing import Dict, List

import discord

from rollbot import roller
from rollbot.model.DiceRoll import DiceRoll


class Bot(discord.Client):
  logger = logging.getLogger(__name__)
  prefix: str
  previousRoll: Dict[discord.User, DiceRoll] = {}

  def __init__(self, commandPrefix='!'):
    super(Bot, self).__init__()
    self.prefix = commandPrefix
    self.logger.info(f"Will be reacting to '{self.prefix}'")

  async def on_ready(self):
    self.logger.info(f"{self.user} has connected")
    for guild in self.guilds:
      self.logger.info(f"guild: {guild}")

  async def on_message(self, message: discord.Message):
    if message.author == self.user:
      return
    if str(message.content).startswith(self.prefix + 'roll'):  # todo add command manager, enumerate
      self.logger.info(f"Command {message.content} from {message.author} at {message.guild}.{message.channel}")
      args = str(message.content).split(' ')
      self.logger.info(f"Command args: {args}")
      args.pop(0)
      if not args:
        await message.channel.send(f"{message.author.mention}, mkm")
      elif len(args) > 1:
        await message.channel.send(f"{message.author.mention}, 1 korraga atm")
      else:
        if len(args[0]) > 100:
          await message.channel.send(f"{message.author.mention}, that command is too long")
          return

        result = roller.roll(args[0])
        self.logger.debug(f"{result}")

        if not result.valid:
          await message.channel.send(f"{message.author.mention}, invalid roll [{result.command}]")
          return

        self.previousRoll[message.author] = result
        await message.channel.send(self.buildResultMessage(result, message))
    if str(message.content).startswith(self.prefix + 'reroll'):  # todo add command manager, enumerate
      result = roller.reroll(self.previousRoll[message.author])
      await message.channel.send(self.buildResultMessage(result, message))

  def buildResultMessage(self, roll: DiceRoll, message: discord.Message):
    return f"{message.author.mention}\n" \
           f"result: {roll}\n" \
           f"sum ({roll.sum()} {'+' if roll.modifier >= 0 else '-'} {abs(roll.modifier)}) : {roll.sum() + roll.modifier}"
