import unittest
from unittest.mock import Mock

import discord

from rollbot.CommandHandler import CommandHandler, CommandResult, ReplyResult, RollResult
from rollbot.Roller import Roller
from rollbot.config.BotConfig import BotConfig


class HandlerTest(unittest.TestCase):
  handler = CommandHandler(BotConfig(shorthand=True), Roller(randomFn=lambda x, y: 1))

  def test_default(self):

    mockMessage = Mock(discord.Message)
    mockMessage.content = '!roll'

    result: ReplyResult = self.handler.handle(mockMessage)
    self.assertEqual('!roll', result.command)
    self.assertIn('result: [1]\nsum (1 + 0) : **1**', result.reply)

  def test_shorthand(self):

    mockMessage = Mock(discord.Message)
    mockMessage.content = '! 2d4'

    result: ReplyResult = self.handler.handle(mockMessage)
    self.assertEqual('! 2d4', result.command)
    self.assertIn('result: [1, 1]\nsum (2 + 0) : **2**', result.reply)

  def test_default_multiple_rolls(self):

    mockMessage = Mock(discord.Message)
    mockMessage.content = '! 2x3d4+5'

    result: ReplyResult = self.handler.handle(mockMessage)
    self.assertEqual('! 2x3d4+5', result.command)
    self.assertIn('result: [[1, 1, 1], [1, 1, 1]]\ngrand total (8 + 8): **16**', result.reply)

  def test_double(self):

    mockMessage = Mock(discord.Message)
    mockMessage.content = '!!'

    result = self.handler.handle(mockMessage)

    self.assertTrue(isinstance(result, ReplyResult))
    self.assertTrue(isinstance(result, RollResult))
    self.assertEqual(20, result.rolls[0].diceFaces)
