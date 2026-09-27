import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class HiveConfig:
    api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    queen_model: str = "claude-opus-5-5"
    worker_model: str = "claude-haiku-4-5-20251001"
    max_retries: int = 3
    timeout: int = 30
    log_dir: str = "logs"
    enable_logging: bool = True

config = HiveConfig()
