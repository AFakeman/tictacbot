from string import ascii_lowercase
from .misc import random_string
from . import redis_client, telebot
from .config import name_length, redis_workers, redis_worker_queue_root, redis_workers_alive_root

class Worker:
    def __init__(self):
        self.name = None
        self._register()
        self.queue = redis_worker_queue_root.format(self.name)
        self.alive_key = redis_workers_alive_root.format(self.name)

    def _register(self):
        name = random_string(ascii_lowercase, name_length)
        while redis_client.sadd(redis_workers, name) == 0:
            name = random_string(ascii_lowercase, name_length)
        self.name = name

    def _keep_alive(self):
        redis_client.setex(self.alive_key, "1", 1)

    def work(self):
        print("Registered as {0}".format(self.name))
        while True:
            update = redis_client.rpop(self.queue)
            if update:
                telebot.process_update(update)
            else:
                self._keep_alive()