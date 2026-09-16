import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Config(BaseSettings):
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    BLOCK_SIZE: int = int(os.getenv("BLOCK_SIZE", "1600"))
    CHANNELS: int = int(os.getenv("CHANNELS", "1"))
    MINECRAFT_DIRECTORY: str = os.getenv("MINECRAFT_DIRECTORY")
    DISCORD_DIRECTORY: str = os.getenv("DISCORD_DIRECTORY")
    STEAM_DIRECTORY: str = os.getenv("STEAM_DIRECTORY")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Config()
