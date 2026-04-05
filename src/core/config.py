from pathlib import Path
from pydantic_settings import BaseSettings
from typing import final

# get backend directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "db1" / "database.db"
COGS_PATH = BASE_DIR / "src" / "cogs"

class Settings(BaseSettings):
    DATABASE_URL: str
    BOT_TOKEN: str
    GIPHY_KEY: str
    DB_PATH: Path = DB_PATH
    COGS_PATH: Path = COGS_PATH


    @final
    class Config:
        env_file = BASE_DIR / ".env"


settings = Settings()
