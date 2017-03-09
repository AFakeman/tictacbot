from telegram.ext import Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from . import bot, info
from .tictactoe import TicTacToe
from .tictactoebot import TicTacPlayer
from .exception import ParseError, GameError
from io import BytesIO, BufferedReader
import random
import logging
import time


def arguments(*arg_types):
    types = {len(pair):pair for pair in arg_types}
    def decorator(func):
        def wrapper(args, **kwargs):
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
            return func(*tuple(parsed), **kwargs)
        return wrapper
    return decorator



@bot.command_handler(
    command='start',
    doc="/start <size> (<side>) - start with a <size> cell field "
        "(between 3 and 50), <side> is x or o. X's go first!",
    pass_args=True,
    pass_context=True
)
@arguments((int, str), (int,), ())
def start_game(*args, restart=False, upd=None, context=None, cbq=False):
    if not cbq:
        username = upd.message.from_user.username
    else:
        username = upd.callback_query.from_user.username
    size = args[0]
    if len(args) == 2:
        start = args[1]
    else:
        start = random.choice(["x", "o"])

    if context["board"] and not restart:
        return "You still have a game playing."

    if context["another_one"]:
        context["another_one"] = ""

    if start not in ['o', 'x']:
        raise ValueError("Invalid starting piece")

    board = TicTacToe(field_size=size)
    opposite = board.opposite(start)
    after_img = []

    if not restart:
        if context["bot"] == 'on':
            context[start] = '#any'
            context[opposite] = "#bot"
        else:
            context[start] = username
            context[opposite] = "#undefined"
    else:
        old_x = context["x"]
        old_o = context["o"]
        context[start] = old_x
        context[opposite] = old_o

    response = []
    if context["x"] == "#bot":
        TicTacPlayer.move(board)
    elif context["x"] == "#undefined":
        after_img.append("The first turn is the other player's! /join to play!")
    else:
        name = "Anyone" if context["x"] == "#any" else context["x"]
        after_img.append("{0} goes first!".format(name))
    response.append(print_game_board(board))
    response.append(print_controls(board))
    context["board"] = repr(board)
    return response+after_img




@bot.command_handler(
    command='move',
    doc="/move <x> <y> - place a tile at coordinates",
    pass_args=True,
    pass_context=True
)
@arguments((int, int))
def process_move(x, y, upd=None, context=None, cbq=False):
    response = []
    if not cbq:
        username = upd.message.from_user.username
    else:
        username = upd.callback_query.from_user.username
    if not context["board"]:
        return "You are not playing. Care to /start another one?"
    board = TicTacToe(context["board"])
    if board.end:
        return "Game is over, let it go. Or /start another one."

    if context[board.turn] != username and context[board.turn] != "#any":
        if context[board.opposite(board.turn)] == username:
            raise GameError("It's not your turn!")
        else:
            raise GameError("Only the player who /start and who /join may play")

    board.move(x - 1, y - 1)
    if context[board.turn] == "#bot" and not board.end:
        TicTacPlayer.move(board)
    context["board"] = repr(board)
    reply = []
    if board.end:
        reply.append(print_game_board(board))
        game_result, param = board.check_win(board.field)
        if game_result == "tie":
            reply.append("It's a tie!")
        else:
            reply.append("Game is over! {0}'s won!".format(board.opposite(board.turn)))
        reply.append("Another one (/yes or /no)?")
        context["another_one"] = "yes"
    else:
        reply.append(print_game_board(board))
        reply.append(print_controls(board))
    return reply


@bot.command_handler(
    command='join',
    doc='/join - join the game created by another player. '
        'Works only if the bot is off.',
    pass_context=True
)
def process_join(upd=None, context=None, cbq=False):
    if not cbq:
        username = upd.message.from_user.username
    else:
        username = upd.callback_query.from_user.username
    if context["bot"] == "on":
        return "You have to turn the bot off to join the game."
    if context["x"] == "#undefined":
        context["x"] = username
        board = TicTacToe(context["board"])
        return [
            print_game_board(board),
            "You play as x's!"
        ]
    elif context["o"] == "#undefined":
        context["o"] = username
        board = TicTacToe(context["board"])
        return [
            print_game_board(board),
            "You play as o's!"
        ]
    else:
        return "Both players seem to be present."

@bot.command_handler(
    command='end_game',
    doc="/end_game - stop current game.",
    pass_context=True
)
def end_game(upd=None, context=None):
    if context["board"]:
        context["board"] = ""
        context["x"] = ""
        context["y"] = ""
        context["another_one"] = ""
        return "You must be busy. Maybe other time."
    else:
        return "You were not playing in the first place..."


def print_game_board(board):
    reply = [("img", board.img())]
    return reply

def print_controls(board):
    if board.field_size <= 5:
        markup_list = []
        for y in range(board.field_size):
            markup_row = []
            for x in range(board.field_size):
                if (x, y) == board.last_x:
                    tile = "X"
                elif (x,y) == board.last_o:
                    tile = "O"
                else:
                    tile = board[(x, y)]
                button = InlineKeyboardButton(tile,
                                              callback_data="{0} {1}".format(x + 1, y + 1))
                markup_row.append(button)
            markup_list.append(markup_row)
        markup = InlineKeyboardMarkup(markup_list)
        return "inline_kb", ("Your move:", markup)

@bot.command_handler('yes', pass_context=True)
def agree(upd=None, context=None):
    if context["another_one"]:
        context["another_one"] = ""
        board = context["board"]
        board_obj = TicTacToe(field=board)
        size = board_obj.field_size
        context["board"] = ""
        return start_game((size,) , upd=upd, restart=True, context=context)
    else:
        return "Huh?"


@bot.command_handler('no', pass_context=True)
def disagree(upd=None, context=None):
    if context["another_one"]:
        context["another_one"] = ""
        context["board"] = ""
        context["x"] = ""
        context["y"] = ""
        return "You must be busy. Maybe other time."
    else:
        return "Huh?"


@bot.command_handler(
    command='bot',
    pass_args=True,
    doc="/bot <on/off> - turn bot on and off.",
    pass_context=True
)
@arguments((str,), ())
def toggle_bot(*args, upd=None, context=None):
    if not args:
        return "Bot is {0} now.".format(context["bot"])
    mode = args[0]
    if mode not in ["on", "off"]:
        raise ParseError("Bot can be either on or off.")
    if mode == context["bot"]:
        return "Bot is already {0}.".format(mode)
    else:
        if context["board"] != "":
            return "You can't toggle the bot during the game!"
        context["bot"] = mode
        return "Bot is {0} now.".format(mode)


@bot.command_handler(
    command='field',
    doc="/field - show current state of the board.",
    pass_context=True
)
def print_field(upd=None, context=None):
    if context["board"]:
        board = TicTacToe(field=context["board"])
        return print_game_board(board)
    else:
        return "There is no game in process."

@bot.cbquery_handler(pass_context=True)
def handle_cbquery(bot, upd=None, context=None):
    query = upd.callback_query
    split = query.data.split(" ")
    if not context["board"] or TicTacToe(context["board"]).end:
        bot.editMessageText(text="No game is being played.",
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        return
    board = TicTacToe(context["board"])
    if len(split) == 2:
        result = []
        x = int(split[0])
        y = int(split[1])
        bot.editMessageText(text="Turn accepted",
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)
        try:
            result.append(process_move((x, y), upd=upd, context=context, cbq=True))
        except GameError as e:
            bot.editMessageText(text=str(e),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
            board = TicTacToe(context["board"])
            result = [
                print_controls(board)
            ]
        return result


@bot.message_handler(Filters.command)
def process_unknown(upd=None):
    return "Unknown command. Type /help for available commands."
