import unittest
from unittest.mock import Mock

import discord

from rollbot.CommandHandler import CommandHandler, CommandResult, ReplyResult
from rollbot.Roller import Roller
from rollbot.config.BotConfig import BotConfig


class HandlerTest(unittest.TestCase):

  def test_default(self):
    handler = CommandHandler(BotConfig(shorthand=True), Roller(randomFn=lambda x, y: 1))

    mockMessage = Mock(discord.Message)
    mockMessage.content = '!roll'

    result: ReplyResult = handler.handle(mockMessage)
    self.assertEqual('!roll', result.command)
    self.assertIn('result: [1]\nsum (1 + 0) : **1**', result.reply)

  def test_shorthand(self):
    handler = CommandHandler(BotConfig(shorthand=True), Roller(randomFn=lambda x, y: 1))

    mockMessage = Mock(discord.Message)
    mockMessage.content = '! 2d4'

    result: ReplyResult = handler.handle(mockMessage)
    self.assertEqual('! 2d4', result.command)
    self.assertIn('result: [1, 1]\nsum (2 + 0) : **2**', result.reply)

  def test_default_multiple_rolls(self):
    handler = CommandHandler(BotConfig(shorthand=True), Roller(randomFn=lambda x, y: 1))

    mockMessage = Mock(discord.Message)
    mockMessage.content = '! 2x3d4+5'

    result: ReplyResult = handler.handle(mockMessage)
    self.assertEqual('! 2x3d4+5', result.command)
    self.assertIn('result: [[1, 1, 1], [1, 1, 1]]\ngrand total (8 + 8): **16**', result.reply)
