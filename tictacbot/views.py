from telegram.ext import Filters
from . import bot, info
from .tictactoe import TicTacToe
from .tictactoebot import TicTacPlayer
from .exception import ParseError, GameError
from io import BytesIO, BufferedReader
from random import choice
import logging



def arguments(*arg_types):
    types = {len(pair):pair for pair in arg_types}
    def decorator(func):
        def wrapper(update, args, **kwargs):
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
            return func(update, tuple(parsed), **kwargs)
        return wrapper
    return decorator

def get_client(client):
    if client not in info:
        info[client] = {
            "another_one": "",  # whether the user was offered another game
            "board": "",  # current state of the board in str representation
            "bot": "on",  # turn the AI on or off
            "x": "",  # x's player, "#bot' is for the AI player
            "o": "",  # o's player
        }
    info_obj = info[client]
    info_obj.decode = "UTF-8"
    return info_obj

@bot.command_handler(
    command='start',
    doc="/start <size> (<side>) - start with a <size> cell field "
        "(between 3 and 50), <side> is x or o. X's go first!",
    pass_args=True
)
@arguments((int, str), (int,), ())
def start_game(update, args, restart=False):
    size = args[0]
    if len(args) == 2:
        start = args[1]
    else:
        start = choice(["x", "o"])

    client = get_client(update.message.chat_id)

    if client["board"] and not restart:
        return "You still have a game playing."

    if client["another_one"]:
        client["another_one"] = ""

    if start not in ['o', 'x']:
        raise ValueError("Invalid starting piece")

    board = TicTacToe(field_size=size)
    opposite = board.opposite(start)
    after_img = []

    if not restart:
        if client["bot"] == 'on':
            client[start] = '#any'
            client[opposite] = "#bot"
        else:
            client[start] = update.message.from_user.username
            client[opposite] = "#undefined"
    else:
        after_img.append("{0} goes first!".format(client["x"]))

    response = []
    if client["x"] == "#bot":
        TicTacPlayer.move(board)
    elif client["x"] == "#undefined":
        after_img.append("The first turn is the other player's! /join to play!")
    response.append(("img", board.img()))
    client["board"] = repr(board)
    return response+after_img



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
    response = []
    if not client["board"]:
        raise GameError("You are not playing. Care to /start another one?")
    board = TicTacToe(client["board"])
    if board.end:
        raise GameError("Game is over, let it go. Or /start another one.")
    if client[board.turn] != update.message.from_user.username and client[board.turn] != "#any":
        if client[board.opposite(board.turn)] == update.message.from_user.username:
            return "It's not your turn!"
        else:
            return "Only the player who /start and who /join may play"
    board.move(x - 1, y - 1)
    if client[board.turn] == "#bot":
        TicTacPlayer.move(board)
    client["board"] = repr(board)
    img = board.img()
    reply = [("img", img)]
    if board.end:
        game_result, param = board.check_win(board.field)
        if game_result == "tie":
            reply.append("It's a tie!")
        else:
            reply.append("Game is over! {0}'s won!".format(board.opposite(board.turn)))
        reply.append("Another one (/yes or /no)?")
        client["another_one"] = "yes"
    return reply

@bot.command_handler(
    command='join',
    doc='/join - join the game created by another player. '
        'Works only if the bot is off.',
)
def process_join(update):
    client = get_client(update.message.chat_id)
    if client["bot"] == "on":
        return "You have to turn the bot off to join the game."
    if client["x"] == "#undefined":
        client["x"] = update.message.from_user.username
        return "You play as x's!"
    elif client["o"] == "#undefined":
        client["o"] = update.message.from_user.username
        return "You play as o's!"
    else:
        return "Both players seem to be present."

@bot.command_handler(
    command='end_game',
    doc="/end_game - stop current game.",
    pass_args=True
)
def end_game(update, args):
    client = get_client(update.message.chat_id)
    if client["board"]:
        client["board"] = ""
        client["x"] = ""
        client["y"] = ""
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
        client["board"] = ""
        return start_game(update, (size, choice(['x','o'])), restart=True)
    else:
        return "Huh?"


@bot.command_handler('no')
def disagree(update):
    client = get_client(update.message.chat_id)
    if client["another_one"]:
        client["another_one"] = ""
        client["board"] = ""
        client["x"] = ""
        client["y"] = ""
        return "You must be busy. Maybe other time."
    else:
        return "Huh?"


@bot.command_handler(
    command='bot',
    pass_args=True,
    doc="/bot <on/off> - turn bot on and off."
)
@arguments((str,), ())
def toggle_bot(update, args):
    client = get_client(update.message.chat_id)
    if not args:
        return "Bot is {0} now.".format(client["bot"])
    mode = args[0]
    if mode not in ["on", "off"]:
        raise ParseError("Bot can be either on or off.")
    if mode == client["bot"]:
        return "Bot is already {0}.".format(mode)
    else:
        if client["board"] != "":
            return "You can't toggle the bot during the game!"
        client["bot"] = mode
        return "Bot is {0} now.".format(mode)


@bot.message_handler(Filters.command)
def process_unknown(update):
    return "Unknown command. Type /help for available commands."
