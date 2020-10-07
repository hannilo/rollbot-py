import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

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


class CommandHandler:
  logger = logging.getLogger(__name__)

  prefix: str
  config: BotConfig
  roller: Roller

  previousRoll: Dict[discord.User, List[DiceRoll]] = {}

  def __init__(self, botConfig: BotConfig, roller: Roller):
    self.prefix = botConfig.prefix
    self.config = botConfig
    self.roller = roller

  def parseBotCommand(self, userCommand: str) -> Command:
    for cmd in Command:
      if userCommand == f"{self.prefix}{cmd.value}":
        return cmd

  def handle(self, message: discord.Message) -> CommandResult:
    self.logger.info(f"Command {message.content} from {message.author} at {message.guild}.{message.channel}")
    args = str(message.content).split(' ')

    userCommand = args.pop(0)
    botCommand = self.parseBotCommand(userCommand)
    if not botCommand:
      if self.config.shorthand:
        botCommand = Command.ROLL
      else:
        return VoidResult(message.content, False)

    self.logger.debug(f"Got [{botCommand}]")
    if args:
      self.logger.debug(f"Command args: {args}")

    if botCommand == Command.ROLL:
      return self.roll(userCommand, args, message)
    if botCommand == Command.REROLL:
      return self.reroll(message)
    if botCommand == Command.HELP:
      shorthandMessage = f', using `{self.prefix} <dice>` will default to `!roll <dice>`' if self.config.shorthand else ''
      return ReplyResult(message.content, True,
                         f"`{self.prefix}roll 2d4+1` - roll 2 d4 dice and add 1{shorthandMessage}\n"
                         f"`{self.prefix}reroll`         - reroll your last roll\n"
                         f"`{self.prefix}about`           - general info")
    if botCommand == Command.ABOUT:
      return ReplyResult(message.content, True, f"Build: **{self.config.build}**\n"
                                                f"Source: https://github.com/hannilo/rollbot-py")

  def roll(self, userCommand: str, args: [str], message: discord.Message):
    if not args:
      self.logger.debug(f"missing args : {userCommand}")
      if userCommand == f'{self.prefix}roll' or userCommand == self.prefix + self.prefix:
        self.logger.debug(f"defaulting {userCommand} to d20")
        args = ['d20']
      else:
        return VoidResult(message.content, False)
    elif len(args) > 1:
      return ReplyResult(message.content, False, f"{message.author.mention}, one at a time please, sorry")
    elif len(args[0]) > 100:
      return ReplyResult(message.content, False, f"{message.author.mention}, that command is too long")

    result = self.roller.roll(args[0])
    self.logger.debug(f"{result}")

    if not result[0].valid:
      return ReplyResult(message.content, False, f"{message.author.mention}, invalid roll [{result[0].command}]")

    self.previousRoll[message.author] = result
    return ReplyResult(message.content, True, self.buildResultMessage(result, message))

  def reroll(self, message):
    previous = self.previousRoll.get(message.author)
    if previous is None:
      message = f"No previous roll for {message.author}"
      self.logger.info(message)
      return VoidResult(message, False)
    result = self.roller.reroll(previous)
    return ReplyResult(message.content, True, self.buildResultMessage(result, message))

  def buildResultMessage(self, rolls: List[DiceRoll], message: discord.Message) -> str:
    reply = f"{message.author.mention}"
    if len(rolls) == 1:
      roll = rolls[0]
      return f"{reply} rolling `{roll.command}`\n" \
             f"result: {f'`{roll}`' if self.config.debug else f'{roll.resultList}'}\n" \
             f"sum ({roll.sum()} {'+' if roll.modifier >= 0 else '-'} {abs(roll.modifier)}) : **{roll.total()}**"
    else:
      grandTotal = sum(map(lambda r: r.total(), rolls))
      totalList = '('
      for i in range(len(rolls)):
        if i != 0:
          totalList += ' + '
        totalList += str(rolls[i].total())
      totalList += ')'
      return f"{reply} rolling `{rolls[0].command}`\n" \
             f"result: {f'`{rolls}`' if self.config.debug else [roll.resultList for roll in rolls]}\n" \
             f"grand total {totalList}: **{grandTotal}**"
