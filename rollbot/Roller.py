import logging
import re
import random
from typing import List, Callable

from rollbot.model.DiceRoll import DiceRoll

logger = logging.getLogger(__name__)


class Roller:
  randomFn: Callable[[int, int], int]

  def __init__(self, randomFn: Callable[[int, int], int] = random.randint):
    self.randomFn = randomFn

  def roll(self, rollCommand: str) -> List[DiceRoll]:
    """
    rollCommand - in the form of LxMdN[+-]P where

    | L(optional) = times to complete
    | M - count of dice in a roll
    | N - dice faces
    | [+-]P(Optional) - modifier to add to each MdN roll
    """
    if not re.fullmatch('(\\dx)?\\d+d\\d+([+-]\\d+)?', rollCommand):
      logger.error(f"Failed to parse {rollCommand}")
      return [DiceRoll(rollCommand, valid=False)]

    logger.info(f"Rolling {rollCommand}")
    times = 1
    modifier = 0
    dice = rollCommand

    if re.match('\\dx', rollCommand):
      times, dice = dice.split('x')
      times = int(times)
    if '+' in rollCommand:
      dice, modifier = dice.split('+')
      modifier = int(modifier)
    if '-' in rollCommand:
      dice, modifier = dice.split('-')
      modifier = -int(modifier)
    count, faces = list(map(int, dice.split('d')))
    result = []
    for _ in range(times):
      result.append(DiceRoll(command=rollCommand,
                             diceCount=count,
                             diceFaces=faces,
                             resultList=self.generateResults(count, faces),
                             modifier=modifier))
    return result

  def reroll(self, rolls: List[DiceRoll]) -> List[DiceRoll]:
    return list(map(lambda r: self.rerollOnce(r), rolls))

  def rerollOnce(self, roll: DiceRoll) -> DiceRoll:
    return DiceRoll(command=roll.command,
                    diceCount=roll.diceCount,
                    diceFaces=roll.diceFaces,
                    resultList=self.generateResults(roll.diceCount, roll.diceFaces),
                    modifier=roll.modifier)

  def generateResults(self, diceCount: int, diceFaces: int) -> List[int]:
    results = []
    for _ in range(diceCount):
      results.append(self.randomFn(1, diceFaces))
    logger.debug(f"results: {results}")
    return results
