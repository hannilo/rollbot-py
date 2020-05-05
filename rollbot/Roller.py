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

  def roll(self, rollCommand: str) -> DiceRoll:
    if not re.fullmatch('\\d+d\\d+([+-]\\d+)?', rollCommand):
      logger.error(f"Failed to parse {rollCommand}")
      return DiceRoll(rollCommand, valid=False)
    else:
      logger.info(f"Rolling {rollCommand}")
      modifier = 0
      dice = rollCommand
      if '+' in rollCommand:
        dice, modifier = rollCommand.split('+')
        modifier = int(modifier)
      if '-' in rollCommand:
        dice, modifier = rollCommand.split('-')
        modifier = -int(modifier)
      count, faces = list(map(int, dice.split('d')))
      return DiceRoll(command=rollCommand,
                      diceCount=count,
                      diceFaces=faces,
                      resultList=self.getResults(count, faces),
                      modifier=modifier)

  def reroll(self, roll: DiceRoll) -> DiceRoll:
    return DiceRoll(command=roll.command,
                    diceCount=roll.diceCount,
                    diceFaces=roll.diceFaces,
                    resultList=self.getResults(roll.diceCount, roll.diceFaces),
                    modifier=roll.modifier)

  def getResults(self, diceCount: int, diceFaces: int) -> List[int]:
    results = []
    for _ in range(0, diceCount):
      results.append(self.randomFn(1, diceFaces))
    logger.debug(f"results: {results}")
    return results
