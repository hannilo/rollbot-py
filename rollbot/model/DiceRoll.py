from dataclasses import dataclass
from typing import List


@dataclass
class DiceRoll:
  command: str
  resultList: List[int] = List
  diceCount: int = 0
  diceFaces: int = 1
  modifier: int = 0
  valid: bool = True

  def sum(self) -> int:
    """
    :return: The sum of the raw resultList, without the modifier
    """
    return sum(self.resultList)

  def total(self) -> int:
    """
    :return: The sum of the whole roll, including the modifier
    """
    return sum(self.resultList) + self.modifier
