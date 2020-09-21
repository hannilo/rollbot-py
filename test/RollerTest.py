import unittest

from rollbot.Roller import Roller
from rollbot.model.DiceRoll import DiceRoll


class RollerTest(unittest.TestCase):
  roller = Roller(randomFn=lambda x, y: 1)

  def test_results(self):
    diceRolls = self.roller.roll('2d4')
    self.assertEqual(1, len(diceRolls))
    roll = diceRolls[0]
    self.assertEqual('2d4', roll.command)
    self.assertEqual([1, 1], roll.resultList)
    self.assertEqual(2, roll.diceCount)
    self.assertEqual(4, roll.diceFaces)
    self.assertEqual(0, roll.modifier)
    self.assertEqual(2, roll.sum())
    self.assertEqual(2, roll.total())
    self.assertTrue(roll.valid)

  def test_modifier_pos(self):
    diceRolls = self.roller.roll('2d4+2')
    self.assertEqual(1, len(diceRolls))
    roll = diceRolls[0]
    self.assertEqual('2d4+2', roll.command)
    self.assertEqual([1, 1], roll.resultList)
    self.assertEqual(2, roll.modifier)
    self.assertEqual(2, roll.sum())
    self.assertEqual(4, roll.total())

  def test_modifier_neg(self):
    diceRolls = self.roller.roll('2d4-3')
    roll = diceRolls[0]
    self.assertEqual('2d4-3', roll.command)
    self.assertEqual([1, 1], roll.resultList)
    self.assertEqual(-3, roll.modifier)
    self.assertEqual(2, roll.sum())
    self.assertEqual(-1, roll.total())

  def test_multiroll(self):
    diceRolls = self.roller.roll('3x2d4')
    self.assertEqual(3, len(diceRolls))
    self.assertEqual('3x2d4', diceRolls[1].command)
    self.assertEqual([1, 1], diceRolls[1].resultList)
    self.assertEqual(2, diceRolls[1].total())
    self.assertTrue(diceRolls[1].valid)

  def test_reroll(self):
    diceRolls = self.roller.reroll([
      DiceRoll('2d4+2', [2, 2], 2, 4, 2)
    ])
    self.assertEqual(1, len(diceRolls))
    self.assertEqual('2d4+2', diceRolls[0].command)
    self.assertEqual([1, 1], diceRolls[0].resultList)
    self.assertEqual(4, diceRolls[0].total())

  def test_single_dice(self):
    diceroll = self.roller.roll('d20')[0]
    self.assertEqual([1], diceroll.resultList)

  def test_single_dice_mod(self):
    diceroll = self.roller.roll('d20+2')[0]
    self.assertEqual([1], diceroll.resultList)
    self.assertEqual(3, diceroll.total())
