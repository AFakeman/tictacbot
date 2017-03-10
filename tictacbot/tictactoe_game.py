from .exception import GameError
from PIL import Image, ImageDraw
from io import BytesIO


def xy(size, x, y):
    return size * y + x

def inspect(field, speed, start, field_size):
    count = {"_": 0, "x": 0, "o": 0}
    speed_x = speed[0]
    speed_y = speed[1]
    x = start[0]
    y = start[1]
    while(x < field_size and y < field_size):
        count[field[xy(field_size, x, y)]] += 1
        x += speed_x
        y += speed_y
    return count



class TicTacToe:
    def __init__(self, field=None, field_size=3):
        if field_size not in range(3, 51):
            raise GameError("Invalid field size. Field size should be between 3 and 50.")
        if field:
            self.field = [i for i in field]
            self.field_size = int(len(self.field) ** 0.5)
        else:
            self.field_size = field_size
            self.field = ["_" for _ in range(self.field_size ** 2)]
        x_count = self.field.count('x')
        o_count = self.field.count('o')
        if x_count == o_count:
            self.turn = 'x'
        elif x_count == o_count + 1:
            self.turn = 'o'
        else:
            raise GameError("Invalid game state")
        self.end = self.check_win(self.field)

    def xy(self, x, y):
        return xy(self.field_size, x, y)


    @staticmethod
    def opposite(player):
        return 'x' if player == 'o' else 'o'

    def moves(self):
        for i in range(self.field_size ** 2):
            if self.field[i] == '_':
                new_field = self.field.copy()
                new_field[i] = self.turn
                yield new_field

    def move(self, x, y):
        if x not in range(self.field_size):
            raise GameError("Invalid x coordinate")
        if y not in range(self.field_size):
            raise GameError("Invalid y coordinate")
        if self.field[x + y * self.field_size] != '_':
            raise GameError("Cell is taken")
        self.field[self.xy(x, y)] = self.turn
        self.turn = self.opposite(self.turn)
        self.end = self.check_win(self.field)

    @staticmethod
    def check_win(field):
        field_size = int(len(field) ** 0.5)
        vert_counts = [inspect(field, (0, 1), (i, 0), field_size) for i in range(field_size)]
        hor_counts = [inspect(field, (1, 0), (0, i), field_size) for i in range(field_size)]
        diag1_count = inspect(field, (1, 1), (0, 0), field_size)
        diag2_count = inspect(field, (1, -1), (0, field_size - 1), field_size)

        empty_count = 0
        free_lanes = 0

        for x in range(field_size):
            empty_count += vert_counts[x]['_']
            if vert_counts[x]['x'] == 0 or vert_counts[x]['o'] == 0:
                free_lanes += 1
            if vert_counts[x]['x'] == field_size or vert_counts[x]['o'] == field_size:
                return "vert", x

        for y in range(field_size):
            if hor_counts[y]['x'] == 0 or hor_counts[y]['o'] == 0:
                free_lanes += 1
            if hor_counts[y]['x'] == field_size or hor_counts[y]['o'] == field_size:
                return "hor", y

        if diag1_count['x'] == 0 or diag1_count['o'] == 0:
            free_lanes += 1

        if diag1_count['x'] == field_size or diag1_count['o'] == field_size:
            return "diag", 1

        if diag2_count['x'] == 0 or diag2_count['o'] == 0:
            free_lanes += 1

        if diag2_count['x'] == field_size or diag2_count['o'] == field_size:
            return "diag", 2

        if free_lanes == 0:
            return "tie", 0

        return False

    def __str__(self):
        build = []
        for y in range(self.field_size):
            for x in range(self.field_size):
                build.append(self.field[x + self.field_size * y])
            build.append('\n')
        return "".join(build)

    def __repr__(self):
        return "".join(self.field)

    def __getitem__(self, *coord):
        if len(coord) == 1:
            return self.field[coord[0]]
        elif len(coord) == 2:
            return self.field[self.xy(*coord)]
        else:
            return

    def img(self, cell_size=50, border_width=1, x_width=1, o_width=1, won_width=5):
        width = cell_size * self.field_size + border_width * (self.field_size - 1)
        size = (width, width)
        image = Image.new("1", size, 1)
        draw = ImageDraw.Draw(image)
        for x in range(self.field_size - 1):
            x_pos = cell_size * (x + 1) + border_width * x
            draw.line([x_pos, 0, x_pos, width - 1], width=border_width)
        for y in range(self.field_size - 1):
            y_pos = cell_size * (y + 1) + border_width * y
            draw.line([0, y_pos, width - 1, y_pos], width=border_width)
        for x in range(self.field_size):
            for y in range(self.field_size):
                x_low = (cell_size + border_width) * x
                x_high = x_low + cell_size - 1
                y_low = (cell_size + border_width) * y
                y_high = y_low + cell_size - 1
                if self[self.xy(x,y)] == 'x':
                    draw.line([x_low, y_low, x_high, y_high], width=x_width)
                    draw.line([x_low, y_high, x_high, y_low], width=x_width)
                elif self[self.xy(x,y)] == 'o':
                    draw.ellipse([x_low, y_low, x_high, y_high])
        if self.end:
            direction, coord = self.end
            if direction == "diag":
                x_low = 0
                x_high = width - 1
                y_low = 0
                y_high = width - 1
                if coord == 1:
                    draw.line([x_low, y_low, x_high, y_high], width=won_width)
                elif coord == 2:
                    draw.line([x_low, y_high, x_high, y_low], width=won_width)
            elif direction == "hor":
                x_low = 0
                x_high = width - 1
                y_low = y_high = coord * (cell_size + border_width) + int(cell_size / 2)
                draw.line([x_low, y_low, x_high, y_high], width=won_width)
            elif direction == "vert":
                y_low = 0
                y_high = width - 1
                x_low = x_high = coord * (cell_size + border_width) + int(cell_size / 2)
                draw.line([x_low, y_low, x_high, y_high], width=won_width)

        buffer = BytesIO()
        image.save(buffer, format="png")
        buffer.seek(0)
        return buffer