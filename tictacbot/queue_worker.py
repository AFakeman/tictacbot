from string import ascii_lowercase
from .misc import random_string
from .config import name_length, redis_workers, redis_worker_queue_root, redis_workers_alive_root

class Worker:
    def __init__(self, redis_client, telebot):
        self.name = None
        self.queue = redis_worker_queue_root.format(self.name)
        self.alive_key = redis_workers_alive_root.format(self.name)
        self.redis_client = redis_client
        self.telebot = telebot
        self._register()

    def _register(self):
        name = random_string(ascii_lowercase, name_length)
        while self.redis_client.sadd(redis_workers, name) == 0:
            name = random_string(ascii_lowercase, name_length)
        self.name = name

    def _keep_alive(self):
        self.redis_client.setex(self.alive_key, "1", 1)

    def work(self):
        print("Registered as {0}".format(self.name))
        while True:
            update = self.redis_client.rpop(self.queue)
            if update:
                self.telebot.process_update(update)
            else:
                self._keep_alive()