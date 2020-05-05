from dataclasses import dataclass


@dataclass
class BotConfig:
  prefix: str = '!'
  build: str = 'dev'
