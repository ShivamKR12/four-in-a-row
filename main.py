import random, copy, sys, pygame, os
from pygame.locals import *

# Configuration Constants
BOARDWIDTH = 7
BOARDHEIGHT = 6
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'
DIFFICULTY = 2
SPACESIZE = 50
FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2)
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2)

BRIGHTBLUE = (0, 50, 255)
WHITE = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Board:
    def __init__(self):
        self.grid = []
        for x in range(BOARDWIDTH):
            self.grid.append([EMPTY] * BOARDHEIGHT)

    def get_lowest_empty_space(self, column):
        # Return the row number of the lowest empty row in the given column.
        for y in range(BOARDHEIGHT - 1, -1, -1):
            if self.grid[column][y] == EMPTY:
                return y
        return -1

    def is_valid_move(self, column):
        # Returns True if there is an empty space in the given column.
        if column < 0 or column >= BOARDWIDTH or self.grid[column][0] != EMPTY:
            return False
        return True

    def is_full(self):
        # Returns True if there are no empty spaces anywhere on the board.
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.grid[x][y] == EMPTY:
                    return False
        return True

    def make_move(self, player, column):
        lowest = self.get_lowest_empty_space(column)
        if lowest != -1:
            self.grid[column][lowest] = player

    def is_winner(self, tile):
        # check horizontal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT):
                if self.grid[x][y] == tile and self.grid[x+1][y] == tile and self.grid[x+2][y] == tile and self.grid[x+3][y] == tile:
                    return True
        # check vertical spaces
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if self.grid[x][y] == tile and self.grid[x][y+1] == tile and self.grid[x][y+2] == tile and self.grid[x][y+3] == tile:
                    return True
        # check / diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if self.grid[x][y] == tile and self.grid[x+1][y-1] == tile and self.grid[x+2][y-2] == tile and self.grid[x+3][y-3] == tile:
                    return True
        # check \ diagonal spaces
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if self.grid[x][y] == tile and self.grid[x+1][y+1] == tile and self.grid[x+2][y+2] == tile and self.grid[x+3][y+3] == tile:
                    return True
        return False

    def copy(self):
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        return new_board

class ComputerAI:
    def __init__(self, difficulty):
        self.difficulty = difficulty

    def get_move(self, board):
        potential_moves = self.get_potential_moves(board, BLACK, self.difficulty)
        # get the best fitness from the potential moves
        best_move_fitness = -1
        for i in range(BOARDWIDTH):
            if potential_moves[i] > best_move_fitness and board.is_valid_move(i):
                best_move_fitness = potential_moves[i]
        # find all potential moves that have this best fitness
        best_moves = []
        for i in range(len(potential_moves)):
            if potential_moves[i] == best_move_fitness and board.is_valid_move(i):
                best_moves.append(i)
        return random.choice(best_moves)

    def get_potential_moves(self, board, tile, look_ahead):
        if look_ahead == 0 or board.is_full():
            return [0] * BOARDWIDTH

        enemy_tile = BLACK if tile == RED else RED

        # Figure out the best move to make.
        potential_moves = [0] * BOARDWIDTH
        for first_move in range(BOARDWIDTH):
            dupe_board = board.copy()
            if not dupe_board.is_valid_move(first_move):
                continue
            dupe_board.make_move(tile, first_move)
            if dupe_board.is_winner(tile):
                # a winning move automatically gets a perfect fitness
                potential_moves[first_move] = 1
                break # don't bother calculating other moves
            else:
                # do other player's counter moves and determine best one
                if dupe_board.is_full():
                    potential_moves[first_move] = 0
                else:
                    for counter_move in range(BOARDWIDTH):
                        dupe_board2 = dupe_board.copy()
                        if not dupe_board2.is_valid_move(counter_move):
                            continue
                        dupe_board2.make_move(enemy_tile, counter_move)
                        if dupe_board2.is_winner(enemy_tile):
                            # a losing move automatically gets the worst fitness
                            potential_moves[first_move] = -1
                            break
                        else:
                            # do the recursive call to get_potential_moves()
                            results = self.get_potential_moves(dupe_board2, tile, look_ahead - 1)
                            potential_moves[first_move] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
        return potential_moves

class FourInARow:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Four in a Row')

        logo = pygame.image.load(resource_path('icon.png'))
        pygame.display.set_icon(logo)

        self.red_pile_rect = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        self.black_pile_rect = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        
        self.red_img = pygame.transform.smoothscale(pygame.image.load(resource_path('assets/red.png')), (SPACESIZE, SPACESIZE))
        self.black_img = pygame.transform.smoothscale(pygame.image.load(resource_path('assets/black.png')), (SPACESIZE, SPACESIZE))
        self.board_img = pygame.transform.smoothscale(pygame.image.load(resource_path('assets/board.png')), (SPACESIZE, SPACESIZE))

        self.human_winner_img = pygame.image.load(resource_path('assets/humanwinner.png'))
        self.computer_winner_img = pygame.image.load(resource_path('assets/computerwinner.png'))
        self.tie_winner_img = pygame.image.load(resource_path('assets/tie.png'))
        
        self.winner_rect = self.human_winner_img.get_rect()
        self.winner_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

        self.arrow_img = pygame.image.load(resource_path('assets/arrow.png'))
        self.arrow_rect = self.arrow_img.get_rect()
        self.arrow_rect.left = self.red_pile_rect.right + 10
        self.arrow_rect.centery = self.red_pile_rect.centery
        
        self.is_first_game = True
        self.ai = ComputerAI(DIFFICULTY)

    def main_loop(self):
        while True:
            self.run_game()
            self.is_first_game = False

    def run_game(self):
        if self.is_first_game:
            # Let the computer go first on the first game, so the player
            # can see how the tokens are dragged from the token piles.
            turn = COMPUTER
            show_help = True
        else:
            # Randomly choose who goes first.
            turn = COMPUTER if random.randint(0, 1) == 0 else HUMAN
            show_help = False

        board = Board()
        winner_img = None

        while True: # main game loop
            if turn == HUMAN:
                # Human player's turn.
                self.get_human_move(board, show_help)
                if show_help:
                    # turn off help arrow after the first move
                    show_help = False
                if board.is_winner(RED):
                    winner_img = self.human_winner_img
                    break
                turn = COMPUTER # switch to other player's turn
            else:
                # Computer player's turn.
                column = self.ai.get_move(board)
                self.animate_computer_moving(board, column)
                board.make_move(BLACK, column)
                if board.is_winner(BLACK):
                    winner_img = self.computer_winner_img
                    break
                turn = HUMAN # switch to other player's turn

            if board.is_full():
                # A completely filled board means it's a tie.
                winner_img = self.tie_winner_img
                break

        while True:
            # Keep looping until player clicks the mouse or quits.
            self.draw_board(board)
            self.surface.blit(winner_img, self.winner_rect)
            pygame.display.update()
            self.clock.tick(FPS)
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    return

    def get_human_move(self, board, is_first_move):
        dragging_token = False
        tokenx, tokeny = None, None
        
        while True:
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN and not dragging_token and self.red_pile_rect.collidepoint(event.pos):
                    # start of dragging on red token pile.
                    dragging_token = True
                    tokenx, tokeny = event.pos
                elif event.type == MOUSEMOTION and dragging_token:
                    # update the position of the red token being dragged
                    tokenx, tokeny = event.pos
                elif event.type == MOUSEBUTTONUP and dragging_token:
                    # let go of the token being dragged
                    if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
                        # let go at the top of the screen.
                        column = int((tokenx - XMARGIN) / SPACESIZE)
                        if board.is_valid_move(column):
                            self.animate_dropping_token(board, column, RED)
                            board.make_move(RED, column)
                            self.draw_board(board)
                            pygame.display.update()
                            return
                    tokenx, tokeny = None, None
                    dragging_token = False
            
            if tokenx is not None and tokeny is not None:
                self.draw_board(board, {'x': tokenx - int(SPACESIZE / 2), 'y': tokeny - int(SPACESIZE / 2), 'color': RED})
            else:
                self.draw_board(board)

            if is_first_move:
                # Show the help arrow for the player's first move.
                self.surface.blit(self.arrow_img, self.arrow_rect)

            pygame.display.update()
            self.clock.tick(FPS)

    def draw_board(self, board, extra_token=None):
        self.surface.fill(BGCOLOR)

        # draw tokens
        space_rect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                space_rect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                if board.grid[x][y] == RED:
                    self.surface.blit(self.red_img, space_rect)
                elif board.grid[x][y] == BLACK:
                    self.surface.blit(self.black_img, space_rect)

        # draw the extra token
        if extra_token is not None:
            img = self.red_img if extra_token['color'] == RED else self.black_img
            self.surface.blit(img, (extra_token['x'], extra_token['y'], SPACESIZE, SPACESIZE))

        # draw board over the tokens
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                space_rect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                self.surface.blit(self.board_img, space_rect)

        # draw the red and black tokens off to the side
        self.surface.blit(self.red_img, self.red_pile_rect) # red on the left
        self.surface.blit(self.black_img, self.black_pile_rect) # black on the right

    def animate_dropping_token(self, board, column, color):
        x = XMARGIN + column * SPACESIZE
        y = YMARGIN - SPACESIZE
        drop_speed = 1.0

        lowest_empty_space = board.get_lowest_empty_space(column)

        while True:
            y += int(drop_speed)
            drop_speed += 0.5
            if int((y - YMARGIN) / SPACESIZE) >= lowest_empty_space:
                return
            self.draw_board(board, {'x': x, 'y': y, 'color': color})
            pygame.display.update()
            self.clock.tick(FPS)

    def animate_computer_moving(self, board, column):
        x = self.black_pile_rect.left
        y = self.black_pile_rect.top
        speed = 1.0
        
        # moving the black tile up
        while y > (YMARGIN - SPACESIZE):
            y -= int(speed)
            speed += 0.5
            self.draw_board(board, {'x': x, 'y': y, 'color': BLACK})
            pygame.display.update()
            self.clock.tick(FPS)
            
        # moving the black tile over
        y = YMARGIN - SPACESIZE
        speed = 1.0
        while x > (XMARGIN + column * SPACESIZE):
            x -= int(speed)
            speed += 0.5
            self.draw_board(board, {'x': x, 'y': y, 'color': BLACK})
            pygame.display.update()
            self.clock.tick(FPS)
            
        # dropping the black tile
        self.animate_dropping_token(board, column, BLACK)

def main():
    game = FourInARow()
    game.main_loop()


if __name__ == '__main__':
    main()
