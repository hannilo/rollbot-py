import unittest

from rollbot.Roller import Roller


class TestRoller(unittest.TestCase):

  def test_results(self):
    roller = Roller(randomFn=lambda x, y: 1)
    diceRoll = roller.roll('2d4')
    self.assertEqual('2d4', diceRoll.command)
    self.assertEqual([1, 1], diceRoll.resultList)
