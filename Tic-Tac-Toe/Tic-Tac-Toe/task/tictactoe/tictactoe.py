temp_moves = list(input("Enter cells:"))
rows = [[temp_moves[j] for j in range(i, i + 3)] for i in range(0, len(temp_moves), 3)]

class Game:
    def __init__(self, cells):
        self.cells = cells
        self.is_finished_state = True
        self.x_win = False
        self.y_win = False
        self.x_count = 0
        self.y_count = 0
        self.is_possible_state = True
        self.is_draw_state = False

    def draw(self):
        print("---------" + '\n' +
              f"| {self.cells[0][0]} {self.cells[0][1]} {self.cells[0][2]} |" + '\n' +
              f"| {self.cells[1][0]} {self.cells[1][1]} {self.cells[1][2]} |" + '\n' +
              f"| {self.cells[2][0]} {self.cells[2][1]} {self.cells[2][2]} |" + '\n' +
              "---------")
        self.game_state()

    def game_state(self):
        self.winner_state()
        self.is_possible()
        self.is_finished()
        if not self.is_finished_state:
            print("Game not finished")
        elif not self.is_possible_state:
            print("Impossible")
        elif self.is_draw_state:
            print("Draw")
        elif self.x_win:
            print("X wins")
        elif self.x_win:
            print("O wins")

    def winner_state(self):
        for i in range(len(rows)):
            if rows[i][0] == 'X' and rows[i][1] == 'X' and rows[i][2] == 'X':
                self.x_win = True
                break
            if rows[i][0] == 'O' and rows[i][1] == 'O' and rows[i][2] == 'O':
                self.y_win = True
                break
            if rows[i].count('X') == 3:
                self.x_win = True
                break
            if rows[i].count('O') == 3:
                self.y_win = True
                break

    def is_draw(self):
        if not self.is_finished_state and not self.x_win or not self.y_win:
            self.is_draw_state = True

    def is_finished(self):
        if not self.x_win or not self.y_win:
            for row in self.cells:
                if '_' in row:
                    self.is_finished_state = False

    def count_items(self):
        for i in range(len(rows)):
            self.x_count += rows[i].count('X')
            self.y_count += rows[i].count('O')

    def is_possible(self):
        if self.x_win and self.y_win:
            self.is_possible_state = False
        if self.x_count > self.y_count + 1 or self.y_count > self.x_count + 1:
            self.is_possible_state = False


game = Game(rows)
game.draw()
