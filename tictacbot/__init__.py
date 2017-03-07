import redis
import yaml
import logging
from redis_map import RedisUniterableMap

with open("config.yml") as f:
    config = yaml.load(f)

REDIS_HOST = config["redis_host"]
REDIS_PORT = config["redis_port"]
REDIS_DB = config["redis_db"]

if "redis_password" in config:
    REDIS_PASSWORD = config["redis_password"]
else:
    REDIS_PASSWORD = None

redis_client = redis.Redis(host=REDIS_HOST,
                           port=REDIS_PORT,
                           db=REDIS_DB,
                           password=REDIS_PASSWORD)

from .telegram_bot import TelegramBot
telebot = TelegramBot(config["api_key"])
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
info = RedisUniterableMap(host=config["redis_host"], port=config["redis_port"], base_key="info")

from . import views

from .queue_worker import Worker
worker = Worker()