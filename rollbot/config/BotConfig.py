from dataclasses import dataclass


@dataclass
class BotConfig:
  prefix: str = '!'
  shorthand: bool = True
  debug: bool = False
  build: str = 'dev'
