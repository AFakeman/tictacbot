class TicTacPlayer:
    @staticmethod
    def move(game):
        for i in range(game.field_size ** 2):
            if game.field[i] == '_':
                game.move(i % game.field_size, i // game.field_size)
                return
