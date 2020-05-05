import logging
import re
import random

from rollbot.model.DiceRoll import DiceRoll

logger = logging.getLogger(__name__)


def roll(rollCommand: str):
  if not re.fullmatch('(\\d+)?d\\d+([+-]\\d+)?', rollCommand):
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
    if re.fullmatch('d\\d+', dice):
        dice = '1' + dice
    count, faces = list(map(int, dice.split('d')))
    return DiceRoll(command=rollCommand,
                    diceCount=count,
                    diceFaces=faces,
                    resultList=getResults(count, faces),
                    modifier=modifier)


def reroll(roll: DiceRoll):
  return DiceRoll(command=roll.command,
                  diceCount=roll.diceCount,
                  diceFaces=roll.diceFaces,
                  resultList=getResults(roll.diceCount, roll.diceFaces),
                  modifier=roll.modifier)


def getResults(diceCount: int, diceFaces: int):
  results = []
  for i in range(0, diceCount):
    results.append(random.randint(1, diceFaces))  # todo inject random function
  logger.debug(f"results: {results}")
  return results
