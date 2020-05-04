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

  def sum(self):
    return sum(self.resultList)
