from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler
from io import BytesIO, BufferedReader

class TicTacBot:
    def help_func(self, bot, update):
        print("kek")
        bot.sendMessage(chat_id=update.message.chat_id, text="\n".join(self.help))

    def __init__(self, token):
        self.token = token
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        self.help = ["help"]
        help_handler = CommandHandler("help", self.help_func)
        self.dispatcher.add_handler(help_handler)

    def run(self):
        self.updater.start_polling()

    def command_handler(self, command, group=0, doc=None):
        def add_command(func):
            def processor(bot, update, args):
                try:
                    result = func(update, args)
                except Exception as e:
                    result = "Error: {0}".format(str(e))
                if isinstance(result, str):
                    bot.sendMessage(chat_id=update.message.chat_id, text=result)
                elif isinstance(result, tuple):
                    if result[0] == "img":
                        bot.sendPhoto(chat_id=update.message.chat_id, photo=result[1])
                else:
                    for i in result:
                        if isinstance(i, str):
                            bot.sendMessage(chat_id=update.message.chat_id, text=i)
                        elif isinstance(i, tuple):
                            if i[0] == "img":
                                bot.sendPhoto(chat_id=update.message.chat_id, photo=i[1])
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
                if isinstance(result, str):
                    bot.sendMessage(chat_id=update.message.chat_id, text=result)
                elif isinstance(result, tuple):
                    if result[0] == "img":
                        bot.sendPhoto(chat_id=update.message.chat_id, photo=result[1])
                else:
                    for i in result:
                        if isinstance(i, str):
                            bot.sendMessage(chat_id=update.message.chat_id, text=i)
                        elif isinstance(i, tuple):
                            if i[0] == "img":
                                bot.sendPhoto(chat_id=update.message.chat_id, photo=i[1])
            handler = MessageHandler(filters=filter_func, callback=processor)
            self.dispatcher.add_handler(handler, group=group)
            if doc:
                self.help.append(doc)
            return func
        return add_handler
