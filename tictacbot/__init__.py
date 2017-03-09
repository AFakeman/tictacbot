import yaml
from redis_map import RedisUniterableMap
from .bot import TelegramBot
import os.path

if os.path.exists('config.yml'):
    with open('config.yml', 'r') as f:
        config = yaml.load(f)
else:
    print("Using default config with no api key")
    config = {
        "redis_host": "127.0.0.1",
        "redis_port": 6379,
        "api_key": None
    }
    with open('config.yml', 'w') as f:
        yaml.dump(config, f)

info = RedisUniterableMap(host=config["redis_host"], port=config["redis_port"], base_key="info")
bot = TelegramBot(config["api_key"], info=info)
from . import views
