from dataclasses import dataclass, field
from typing import List


@dataclass
class BotConfig:
  prefix: str = '!'
  channels: List[str] = field(default_factory=lambda: list())
  shorthand: bool = True
  debug: bool = False
  build: str = 'dev'
