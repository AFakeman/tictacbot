from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler
from sys import stdout
from .exception import ParseError, GameError
import logging

class TelegramBot:
    def help_func(self, bot, update):
        print("kek")
        bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(self.help))

    def __init__(self, token):
        self.token = token
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        self.help = ["/help - show this message."]
        help_handler = CommandHandler("help", self.help_func)
        self.dispatcher.add_handler(help_handler)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

    def run(self):
        self.updater.start_polling()

    def command_handler(self, command, group=0, doc=None, pass_args=False):
        def add_command(func):
            def processor(bot, update, args):
                try:
                    if pass_args:
                        result = func(update, args)
                    else:
                        result = func(update)
                except GameError as e:
                    result = str(e)
                except ParseError as e:
                    result = "Couldn't process arguments. Are you sure you are typing the command correctly?"
                except Exception as e:
                    result = "Error: {0}".format(str(e))
                if result:
                    self.send(bot, result, update.message.chat_id)
            handler = CommandHandler(command, processor, pass_args=True)
            self.dispatcher.add_handler(handler, group=group)
            if doc:
                self.help.append(doc)
            return func
        return add_command

    def message_handler(self, filter_func=None, group=0, doc=None):
        def add_handler(func):
            def processor(bot, update):
                try:
                    result = func(update)
                except Exception as e:
                    result = "Error: {0}".format(str(e))
                if result:
                    self.send(bot, result, update.message.chat_id)
            handler = MessageHandler(filters=filter_func, callback=processor)
            self.dispatcher.add_handler(handler, group=group)
            return func
        return add_handler

    def send(self, bot, obj, chat):
        if isinstance(obj, str):
            bot.sendMessage(chat_id=chat, text=obj)
        elif isinstance(obj, tuple):
            if obj[0] == "img":
                bot.sendPhoto(chat_id=chat, photo=obj[1])
        else:
            for i in obj:
                if i:
                    self.send(bot, i, chat)