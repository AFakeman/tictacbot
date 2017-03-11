from string import ascii_lowercase
from .misc import random_string
from .config import name_length, redis_update_queue_root, redis_chat_lock_root, redis_lock_timeout
import re

_queue_regexp = redis_update_queue_root + r'(.*)'

class Worker:
    def __init__(self, redis_client, telebot):
        self.redis = redis_client
        self.telebot = telebot

    def work(self):
        match = redis_update_queue_root + '*'
        while True:
            for key in self.redis.scan_iter(match=match):
                chat_match = re.match(_queue_regexp, key)
                chat_id = chat_match.group(1)
                lock_key = redis_chat_lock_root + chat_id
                if self.redis.setnx(lock_key, 1):
                    self.redis.expire(lock_key, redis_lock_timeout)
                    update = self.redis.index(key, -1)
                    self.telebot.process_update(update)
                    self.redis.rpop(key)
                    self.redis.delete(lock_key)