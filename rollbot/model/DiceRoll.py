from dataclasses import dataclass
from typing import List


@dataclass
class DiceRoll:
  command: str
  diceCount: int
  diceFaces: int
  resultList: List[int]
  modifier: int = 0
  valid: bool = True

  def sum(self):
    return sum(self.resultList)
