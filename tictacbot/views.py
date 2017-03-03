from telegram.ext import Filters
from . import bot, info
from .tictactoe import TicTacToe
from .tictactoebot import TicTacPlayer
from .exception import ParseError, GameError
from io import BytesIO, BufferedReader
from random import choice

def arguments(*arg_types):
    types = {len(pair):pair for pair in arg_types}
    def decorator(func):
        def wrapper(update, args):
            if len(args) not in types:
                raise ParseError("Not enough or too many arguments")
            parsed = []
            for i in range(len(args)):
                try:
                    if types[len(args)][i]:
                        parsed.append(types[len(args)][i](args[i]))
                    else:
                        parsed.append(args[i])
                except:
                    raise ParseError(str(args[i]))
            return func(update, tuple(parsed))
        return wrapper
    return decorator

def get_client(client):
    if client not in info:
        info[client] = {
            "another_one": "",
            "board": "",
            "bot": "on"
        }
    return info[client]

@bot.command_handler(
    command='start',
    doc="/start <size> <side> - start with a <size> cell field (between 3 and 50), <side> is x or o. X's go first!",
    pass_args=True
)
@arguments((int, str), (int,), ())
def start_game(update, args):
    if not args:
        return "Hello! Type start <size> <side> to play the game, or use /help!"
    size = args[0]
    if len(args) == 2:
        start = args[1]
    else:
        start = "x"
    client = get_client(update.message.chat_id)
    if client["board"]:
        return "You still have a game playing."
    if client["another_one"]:
        client["another_one"] = ""
    if start not in ['o', 'x']:
        raise ValueError("Invalid starting piece")
    board = TicTacToe(field_size=size)
    if start == 'o' and client["bot"] == 'on':
        TicTacPlayer.move(board)
    print(client)
    client["board"] = repr(board)
    return [("img", board.img())]



@bot.command_handler(
    command='move',
    doc="/move <x> <y> - place a tile at coordinates",
    pass_args=True
)
@arguments((int, int))
def process_move(update, args):
    x = args[0]
    y = args[1]
    client = get_client(update.message.chat_id)
    if not client["board"]:
        raise GameError("You are not playing. Care to /start another one?")
    board = TicTacToe(client["board"].decode('ascii'))
    if board.end:
        raise GameError("Game is over, let it go. Or /start another one.")
    board.move(x - 1, y - 1)
    if not board.end and client["bot"] == "on":
        TicTacPlayer.move(board)
    client["board"] = repr(board)
    img = board.img()
    reply = [("img", img)]
    if board.end:
        game_result, param = board.check_win()
        if game_result == "tie":
            reply.append("It's a tie!")
        else:
            reply.append("Game is over! {0}'s won!".format(board.opposite(board.turn)))
        reply.append("Another one (/yes or /no)?")
        client["another_one"] = "yes"
    return reply


@bot.command_handler(
    command='end_game',
    doc="/end_game - stop current game.",
    pass_args=True
)
def end_game(update, args):
    client = get_client(update.message.chat_id)
    if client["board"]:
        client["board"] = ""
        return "You must be busy. Maybe other time."
    else:
        return "You were not playing in the first place..."


@bot.command_handler('yes')
def agree(update):
    client = get_client(update.message.chat_id)
    if client["another_one"]:
        client["another_one"] = ""
        board = client["board"]
        size = int(len(board) ** 0.5)
        return start_game(update, (size, choice(['x','o'])))
    else:
        return "Huh?"


@bot.command_handler('no')
def disagree(update):
    client = get_client(update.message.chat_id)
    if client["another_one"]:
        client["another_one"] = ""
        return "You must be busy. Maybe other time."
    else:
        return "Huh?"


@bot.command_handler(
    command='bot',
    pass_args=True,
    doc="/bot <on/off> - turn bot on and off. You cannot start the game as o's when the bot is off!"
)
@arguments((str,))
def toggle_bot(update, args):
    client = get_client(update.message.chat_id)
    mode = args[0]
    if mode not in ["on", "off"]:
        raise ParseError("Bot can be either on or off.")
    if mode == client["bot"]:
        return "Bot is already {0}.".format(mode)
    else:
        client["bot"] = mode
        return "Bot is {0} now.".format(mode)


@bot.message_handler(Filters.command)
def process_unknown(update):
    return "Unknown command. Type /help for available commands."
