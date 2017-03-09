from .tictactoe import TicTacToe, inspect, xy

opposite = TicTacToe.opposite


def calculate_attr(lane, turn, field_size, at_price=2, def_price=3, reinforce_price=2):
    if lane["_"] == 0:
        return "atk", 0
    if lane[opposite(turn)] == 0 and lane[turn] == 0:  # We should attack!
        return "atk", at_price
    elif lane[opposite(turn)] != 0 and lane[turn] == 0:  # We should protect!
        return "def",  def_price ** lane[opposite(turn)]
    elif lane[opposite(turn)] == 0 and lane[turn] != 0:  # We should reinforce!
        return "frc", at_price ** lane[turn]
    else:
        return "atk", 0


class TicTacPlayer:
    @staticmethod
    def move(game):
        field_size = game.field_size
        turn = game.turn
        vert_counts = [inspect(game.field, (0, 1), (i, 0), field_size) for i in range(field_size)]
        hor_counts = [inspect(game.field, (1, 0), (0, i), field_size) for i in range(field_size)]
        diag1_count = inspect(game.field, (1, 1), (0, 0), field_size)
        diag2_count = inspect(game.field, (1, -1), (0, field_size - 1), field_size)
        vert_lanes = [calculate_attr(vert_counts[i], turn, field_size) for i in range(field_size)]
        hor_lanes = [calculate_attr(hor_counts[i], turn, field_size) for i in range(field_size)]
        diag1 = calculate_attr(diag1_count, turn, field_size)
        diag2 = calculate_attr(diag2_count, turn, field_size)
        scores = {}
        for x in range(field_size):
            for y in range(field_size):
                score = 0
                if x == y:
                    score += diag1[1]
                if x == field_size - 1 - y:
                    score += diag2[1]
                score += vert_lanes[x][1]
                score += hor_lanes[y][1]
                scores[(x, y)] = score

        max_cell = (-1, -1)
        max_score = -1

        for x in range(field_size):
            for y in range(field_size):
                if (max_score < scores[(x, y)]) and game.field[xy(field_size, x, y)] == '_':
                    max_score = scores[(x, y)]
                    max_cell = (x, y)

        game.move(*max_cell)
