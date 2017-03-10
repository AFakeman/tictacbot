from telegram.ext import Dispatcher
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import Bot, Update
from .exception import ParseError, GameError
import logging
import json


def print_error(bot, update, error):
    print(error)


class TelegramBot:
    def __init__(self, token, info):
        self.token = token
        self.bot = Bot(token)
        self.info = info
        self.dispatcher = Dispatcher(self.bot, None, workers=0)
        self.help = ["/help - show this message."]
        help_handler = CommandHandler("help", self.help_func)
        self.dispatcher.add_handler(help_handler)
        logging.basicConfig(
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)

    def help_func(self, bot, update):
        print("kek")
        bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(self.help))

    def get_chat_context(self, chat_id):
        if chat_id not in self.info:
            self.info[chat_id] = {
                "another_one": "",  # whether the user was offered another game
                "board": "",  # current state of the board in str representation
                "bot": "on",  # turn the AI on or off
                "x": "",  # x's player, "#bot' is for the AI player
                "o": "",  # o's player
            }
        info_obj = self.info[chat_id]
        info_obj.decode = "UTF-8"
        return info_obj

    def command_handler(self, command, group=0, doc=None, pass_args=False, pass_context=False):
        def add_command(func):
            def processor(bot, update, args):
                try:
                    kwargs = {"upd": update}
                    if pass_context:
                        kwargs["context"] = self.get_chat_context(update.message.chat_id)
                    if pass_args:
                        result = func(args, **kwargs)
                    else:
                        result = func(**kwargs)
                except GameError as e:
                    result = str(e)
                except ParseError as e:
                    result = "Couldn't process arguments ({0}). \
                              Are you sure you are typing the command correctly?".format(str(e))
                if result:
                    self.send(bot, result, update.message.chat_id)
            handler = CommandHandler(command, processor, pass_args=True)
            self.dispatcher.add_handler(handler, group=group)
            if doc:
                self.help.append(doc)
            return func
        return add_command

    def message_handler(self, filter_func=None, group=0, doc=None, pass_context=False):
        def add_handler(func):
            def processor(bot, update):
                try:
                    kwargs = {"upd": update}
                    if pass_context:
                        kwargs["context"] = self.get_chat_context(update.message.chat_id)
                    result = func(**kwargs)
                except Exception as e:
                    result = "Error: {0}".format(str(e))
                if result:
                    self.send(bot, result, update.message.chat_id)
            handler = MessageHandler(filters=filter_func, callback=processor)
            self.dispatcher.add_handler(handler, group=group)
            return func
        return add_handler

    def cbquery_handler(self, pass_context=False):
        def add_handler(func):
            def processor(bot, update):
                kwargs = {"upd": update}
                chat_id = update.callback_query.message.chat_id
                if pass_context:
                    kwargs["context"] = self.get_chat_context(chat_id)
                try:
                    result = func(bot, **kwargs)
                except GameError as e:
                    result = str(e)
                if result:
                    self.send(bot, result, chat_id)

            handler = CallbackQueryHandler(processor)
            self.dispatcher.add_handler(handler)
            return func
        return add_handler

    def process_update(self, update):
        decoded = update.decode("UTF-8")
        jsoned = json.loads(decoded)
        de_json = Update.de_json(jsoned, bot=None)
        self.dispatcher.process_update(de_json)

    def send(self, bot, obj, chat):
        if isinstance(obj, str):
            bot.sendMessage(chat_id=chat, text=obj)
        elif isinstance(obj, tuple):
            if obj[0] == "img":
                bot.sendPhoto(chat_id=chat, photo=obj[1])
            elif obj[0] == "inline_kb":
                bot.sendMessage(chat_id=chat, text=obj[1][0], reply_markup=obj[1][1])
        else:
            for i in obj:
                if i:
                    self.send(bot, i, chat)