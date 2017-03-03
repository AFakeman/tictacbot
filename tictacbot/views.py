from telegram.ext import Filters
from . import bot, boards, another_one
from .tictactoe import TicTacToe
from .tictactoebot import TicTacPlayer
from .exception import ParseError, GameError
from io import BytesIO, BufferedReader
from random import choice

def arguments(*types):
    def decorator(func):
        def wrapper(update, args):
            if len(args) != len(types):
                raise ParseError("Insufficient arguments")
            parsed = []
            for i in range(len(args)):
                try:
                    if types[i]:
                        parsed.append(types[i](args[i]))
                    else:
                        parsed.append(args[i])
                except:
                    raise ParseError(str(args[i]))
            return func(update, *tuple(parsed))
        return wrapper
    return decorator


@bot.command_handler(
    command='start',
    doc="start <size> <start>",
    pass_args=True
)
@arguments(int, str)
def start_game(update, size, start):
    if update.message.chat_id in another_one:
        del(another_one[update.message.chat_id])
    if start not in ['o', 'x']:
        raise ValueError("Invalid starting piece")
    board = TicTacToe(field_size=size)
    if start == 'o':
        TicTacPlayer.move(board)
    boards[update.message.chat_id] = repr(board)
    return [("img", board.img())]


@bot.command_handler(
    command='move',
    doc="move <x> <y>",
    pass_args=True
)
@arguments(int, int)
def process_move(update, x, y):
    if update.message.chat_id not in boards:
        raise GameError("You are not playing")
    board = TicTacToe(boards[update.message.chat_id].decode("ascii"))
    if board.end:
        raise GameError("Game is over, let it go.")
    board.move(x - 1, y - 1)
    if not board.end:
        TicTacPlayer.move(board)
    boards[update.message.chat_id] = repr(board)
    img = board.img()
    reply = [("img", img)]
    if board.end:
        reply.append("Game is over! {0}'s won! Another one (/yes or /no)?".format(board.opposite(board.turn)))
        another_one[update.message.chat_id] = True
    return reply


@bot.command_handler(
    command='end_game',
    doc="end_game",
    pass_args=True
)
def end_game(update, args):
    if update.message.chat_id in boards:
        del(boards[update.message.chat_id])
        return "You must be busy. Maybe other time."
    else:
        return "You were not playing in the first place..."


@bot.command_handler('yes')
def agree(update):
    if update.message.chat_id in another_one:
        del(another_one[update.message.chat_id])
        board = boards[update.message.chat_id]
        size = int(len(board) ** 0.5)
        return start_game(update, (size, choice(['x','o'])))
    else:
        return "Huh?"


@bot.command_handler('no')
def disagree(update):
    if update.message.chat_id in another_one:
        del(another_one[update.message.chat_id])
        return "You must be busy. Maybe other time."
    else:
        return "Huh?"


@bot.message_handler(Filters.command)
def process_unknown(update):
    return "Unknown command. Type /help for available commands."
