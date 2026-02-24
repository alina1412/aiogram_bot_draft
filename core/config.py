import logging
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml


@dataclass
class AppConfig:
    debug: str


@dataclass
class BotConfig:
    token: str
    group_id: int


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"
    db_driver: str = "postgresql+asyncpg"


@dataclass
class RabbitmqConfig:
    user: str
    password: str
    host: str
    queue_title: str


@dataclass
class Config:
    app: AppConfig | None = None
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None
    rabbit: RabbitmqConfig | None = None
    logger: logging.Logger | None = None


def get_logger(DEBUG=True):
    logging.basicConfig(
        filename=("logs.log" if DEBUG else None),
        level=(logging.INFO if DEBUG else logging.WARNING),
        format=(
            "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"
        ),
        datefmt=("%H:%M:%S" if DEBUG else "%Y-%m-%d %H:%M:%S"),
    )
    logger = logging.getLogger(__name__)
    return logger


def setup_config(config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    config = Config(
        app=AppConfig(debug=raw_config["app"]["debug"]),
        bot=BotConfig(
            token=raw_config["bot"]["token"],
            group_id=int(raw_config["bot"]["group_id"]),
        ),
        database=DatabaseConfig(**raw_config["database"]),
        rabbit=RabbitmqConfig(**raw_config["rabbitmq"]),
        logger=get_logger(raw_config["app"]["debug"] is True),
    )
    return config


@lru_cache
def get_config():
    config_path = Path(__file__).parent.parent / "config.yml"
    config = setup_config(config_path)
    return config


config = get_config()
logger = config.logger
