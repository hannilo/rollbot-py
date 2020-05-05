import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict

import discord

from rollbot.Roller import Roller
from rollbot.config.BotConfig import BotConfig
from rollbot.model.DiceRoll import DiceRoll


class Command(Enum):
  ABOUT = 'about'
  HELP = 'help'
  REROLL = 'reroll'
  ROLL = 'roll'


@dataclass
class CommandResult:
  command: str
  successful: bool


@dataclass
class VoidResult(CommandResult):
  pass


@dataclass
class ReplyResult(CommandResult):
  reply: str


class CommandManager:
  logger = logging.getLogger(__name__)

  prefix: str
  config: BotConfig
  roller: Roller

  previousRoll: Dict[discord.User, DiceRoll] = {}

  def __init__(self, botConfig: BotConfig, roller: Roller):
    self.prefix = botConfig.prefix
    self.config = botConfig
    self.roller = roller

  def handle(self, message: discord.Message) -> CommandResult:
    messageContent = str(message.content)

    self.logger.info(f"Command {message.content} from {message.author} at {message.guild}.{message.channel}")
    args = str(message.content).split(' ')

    userCommand = args.pop(0)
    botCommand = self.parseBotCommand(userCommand)
    if not botCommand:
      return VoidResult(messageContent, False)

    self.logger.debug(f"Got {userCommand} [{botCommand}]")
    if args:
      self.logger.debug(f"Command args: {args}")

    if botCommand == Command.ROLL:
      if not args:
        return ReplyResult(messageContent, False, f"{message.author.mention}, mkm")
      elif len(args) > 1:
        return ReplyResult(messageContent, False, f"{message.author.mention}, 1 korraga atm")
      elif len(args[0]) > 100:
        return ReplyResult(messageContent, False, f"{message.author.mention}, that command is too long")

      result = self.roller.roll(args[0])
      self.logger.debug(f"{result}")

      if not result.valid:
        return ReplyResult(messageContent, False, f"{message.author.mention}, invalid roll [{result.command}]")

      self.previousRoll[message.author] = result
      return ReplyResult(messageContent, True, buildResultMessage(result, message))

    if botCommand == Command.REROLL:
      previous = self.previousRoll.get(message.author)
      if previous is None:
        self.logger.info(f"No previous roll for {message.author}")
        return VoidResult(userCommand, False)
      result = self.roller.reroll(previous)
      return ReplyResult(messageContent, True, buildResultMessage(result, message))

    if botCommand == Command.HELP:
      return ReplyResult(messageContent, True, f"`{self.prefix}roll 2d4+1` - roll 2 d4 dice and add 1\n"
                                               f"`{self.prefix}reroll`         - reroll your last roll\n"
                                               f"`{self.prefix}about`           - general info")

    if botCommand == Command.ABOUT:
      return ReplyResult(messageContent, True, f"Build: **{self.config.build}**\n"
                                               f"Source: https://github.com/hannilo/rollbot-py")

  def parseBotCommand(self, userCommand: str) -> Command:
    for cmd in Command:
      if userCommand == f"{self.prefix}{cmd.value}":
        return cmd


def buildResultMessage(roll: DiceRoll, message: discord.Message):
  return f"{message.author.mention}\n" \
         f"result: {roll}\n" \
         f"sum ({roll.sum()} {'+' if roll.modifier >= 0 else '-'} {abs(roll.modifier)}) : **{roll.sum() + roll.modifier}**"
