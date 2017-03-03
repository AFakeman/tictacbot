from .exception import GameError
from PIL import Image, ImageDraw
from io import BytesIO

class TicTacToe:
    def __init__(self, field=None, field_size=3):
        if field_size <= 0:
            raise GameError("Invalid field size")
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
        self.end = self.check_win()

    def xy(self, x, y):
        return self.field_size * y + x

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
        self.end = self.check_win()

    def check_win(self):
        for x in range(self.field_size):
            flag = self.field[x]
            for y in range(self.field_size):
                coord = self.xy(x, y)
                if self.field[coord] != flag or self.field[coord] == '_':
                    flag = None
                    break
            if flag:
                return "vert", x

        for y in range(self.field_size):
            flag = self.field[self.xy(0, y)]
            for x in range(self.field_size):
                coord = self.xy(x, y)
                if self.field[coord] != flag or self.field[coord] == '_':
                    flag = None
                    break
            if flag:
                return "hor", y

        flag = self.field[self.xy(0, 0)]
        for i in range(self.field_size):
            coord = self.xy(i, i)
            if self.field[coord] != flag or self.field[coord] == '_':
                flag = None
                break
        if flag:
            return "diag", 1

        flag = self.field[self.xy(self.field_size - 1, 0)]
        for i in range(self.field_size):
            coord = self.xy(self.field_size - 1 - i, i)
            if self.field[coord] != flag or self.field[coord] == '_':
                flag = None
                break
        if flag:
            return "diag", 2

        for i in range(self.field_size ** 2):
            flag = True
            if self.field[i] == '_':
                flag = None
                break
        if flag:
            return "tie", 0

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