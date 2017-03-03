from telegram.ext import Filters
from . import bot, boards, another_one
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
                raise ParseError("Invalid arguments")
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


@bot.command_handler(
    command='start',
    doc="/start <size> <side> - start with a <size> cell field, <side> is x or o. X's go first!",
    pass_args=True
)
@arguments((int, str), ())
def start_game(update, args):
    if args:
        size = args[0]
        start = args[1]
        if update.message.chat_id in another_one:
            del(another_one[update.message.chat_id])
        if start not in ['o', 'x']:
            raise ValueError("Invalid starting piece")
        board = TicTacToe(field_size=size)
        if start == 'o':
            TicTacPlayer.move(board)
        boards[update.message.chat_id] = repr(board)
        return [("img", board.img())]
    else:
        return "Hello! Type start <size> <side> to play the game, or use /help!"


@bot.command_handler(
    command='move',
    doc="/move <x> <y> - place a tile at coordinates",
    pass_args=True
)
@arguments((int, int))
def process_move(update, args):
    x = args[0]
    y = args[1]
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
        game_result, param = board.check_win()
        if game_result == "tie":
            reply.append("It's a tie!")
        else:
            reply.append("Game is over! {0}'s won!".format(board.opposite(board.turn)))
        reply.append("Another one (/yes or /no)?")
        another_one[update.message.chat_id] = True
    return reply


@bot.command_handler(
    command='end_game',
    doc="/end_game - stop current game. /start will work anyway, though.",
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
