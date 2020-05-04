import unittest

from rollbot import roller


class TestRoller(unittest.TestCase):
  def test_results(self):
    diceRoll = roller.roll('1d4')
    self.assertEqual('1d4', diceRoll.command)
