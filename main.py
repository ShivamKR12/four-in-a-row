# /// script
# dependencies = [
#     "pygame-ce",
# ]
# /// 

import random, copy, sys, pygame, asyncio
from pygame.locals import *

BOARDWIDTH = 7  # how many spaces wide the board is
BOARDHEIGHT = 6 # how many spaces tall the board is
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'

DIFFICULTY = 2 # how many moves to look ahead. (>2 is usually too much)

SPACESIZE = 50 # size of the tokens and individual board spaces in pixels

FPS = 30 # frames per second to update the screen
WINDOWWIDTH = 640 # width of the program's window, in pixels
WINDOWHEIGHT = 480 # height in pixels

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

class FourInARowGame:
    def __init__(self):
        pygame.init()
        self.fps_clock = pygame.time.Clock()

        self.is_android = hasattr(sys, "getandroidapilevel")
        self.is_emscripten = hasattr(sys, "_emscripten_info")

        if self.is_android:
            self.display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),
                                            pygame.SCALED | pygame.FULLSCREEN)
        elif self.is_emscripten:
            self.display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0)
        else:
            self.display_surf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT),
                                            pygame.SCALED | pygame.RESIZABLE)
                                            
        pygame.display.set_caption('Four in a Row')
        try:
            logo = pygame.image.load('icon.png')
            pygame.display.set_icon(logo)
        except Exception:
            pass

        self.red_pile_rect = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        self.black_pile_rect = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
        
        red_token = pygame.image.load('4row_red.png')
        self.red_token_img = pygame.transform.smoothscale(red_token, (SPACESIZE, SPACESIZE))
        
        black_token = pygame.image.load('4row_black.png')
        self.black_token_img = pygame.transform.smoothscale(black_token, (SPACESIZE, SPACESIZE))
        
        board_img = pygame.image.load('4row_board.png')
        self.board_img = pygame.transform.smoothscale(board_img, (SPACESIZE, SPACESIZE))

        self.human_winner_img = pygame.image.load('4row_humanwinner.png')
        self.computer_winner_img = pygame.image.load('4row_computerwinner.png')
        self.tie_winner_img = pygame.image.load('4row_tie.png')
        
        self.winner_rect = self.human_winner_img.get_rect()
        self.winner_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))

        self.arrow_img = pygame.image.load('4row_arrow.png')
        self.arrow_rect = self.arrow_img.get_rect()
        self.arrow_rect.left = self.red_pile_rect.right + 10
        self.arrow_rect.centery = self.red_pile_rect.centery

        self.is_first_game = True

    async def run(self):
        while True:
            await self.run_game()
            self.is_first_game = False
            await asyncio.sleep(0) # allow other tasks to run while waiting for the next game to start

    async def run_game(self):
        if self.is_first_game:
            turn = COMPUTER
            show_help = True
        else:
            turn = COMPUTER if random.randint(0, 1) == 0 else HUMAN
            show_help = False

        board = self.get_new_board()
        winner_img = None

        while True:
            if turn == HUMAN:
                await self.get_human_move(board, show_help)
                if show_help:
                    show_help = False
                if self.is_winner(board, RED):
                    winner_img = self.human_winner_img
                    break
                turn = COMPUTER
            else:
                column = self.get_computer_move(board)
                await self.animate_computer_moving(board, column)
                self.make_move(board, BLACK, column)
                if self.is_winner(board, BLACK):
                    winner_img = self.computer_winner_img
                    break
                turn = HUMAN

            if self.is_board_full(board):
                winner_img = self.tie_winner_img
                break

            await asyncio.sleep(0)

        while True:
            self.draw_board(board)
            self.display_surf.blit(winner_img, self.winner_rect)
            pygame.display.update()
            self.fps_clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type in (MOUSEBUTTONUP, FINGERUP):
                    return
            
            await asyncio.sleep(0)

    def make_move(self, board, player, column):
        lowest = self.get_lowest_empty_space(board, column)
        if lowest != -1:
            board[column][lowest] = player

    def draw_board(self, board, extra_token=None):
        self.display_surf.fill(BGCOLOR)

        space_rect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                space_rect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                if board[x][y] == RED:
                    self.display_surf.blit(self.red_token_img, space_rect)
                elif board[x][y] == BLACK:
                    self.display_surf.blit(self.black_token_img, space_rect)

        if extra_token != None:
            img = self.red_token_img if extra_token['color'] == RED else self.black_token_img
            self.display_surf.blit(img, (extra_token['x'], extra_token['y'], SPACESIZE, SPACESIZE))

        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                space_rect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
                self.display_surf.blit(self.board_img, space_rect)

        self.display_surf.blit(self.red_token_img, self.red_pile_rect)
        self.display_surf.blit(self.black_token_img, self.black_pile_rect)

    def get_new_board(self):
        board = []
        for x in range(BOARDWIDTH):
            board.append([EMPTY] * BOARDHEIGHT)
        return board

    async def get_human_move(self, board, show_help):
        dragging_token = False
        tokenx, tokeny = None, None
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                
                pos = None
                is_down = False
                is_motion = False
                is_up = False

                if event.type == MOUSEBUTTONDOWN:
                    pos = event.pos
                    is_down = True
                elif event.type == FINGERDOWN:
                    pos = (event.x * WINDOWWIDTH, event.y * WINDOWHEIGHT)
                    is_down = True
                elif event.type == MOUSEMOTION:
                    pos = event.pos
                    is_motion = True
                elif event.type == FINGERMOTION:
                    pos = (event.x * WINDOWWIDTH, event.y * WINDOWHEIGHT)
                    is_motion = True
                elif event.type == MOUSEBUTTONUP:
                    pos = event.pos
                    is_up = True
                elif event.type == FINGERUP:
                    pos = (event.x * WINDOWWIDTH, event.y * WINDOWHEIGHT)
                    is_up = True

                if is_down and not dragging_token and self.red_pile_rect.collidepoint(pos):
                    dragging_token = True
                    tokenx, tokeny = pos
                elif is_motion and dragging_token:
                    tokenx, tokeny = pos
                elif is_up and dragging_token:
                    if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
                        column = int((tokenx - XMARGIN) / SPACESIZE)
                        if self.is_valid_move(board, column):
                            await self.animate_dropping_token(board, column, RED)
                            board[column][self.get_lowest_empty_space(board, column)] = RED
                            self.draw_board(board)
                            pygame.display.update()
                            return
                    tokenx, tokeny = None, None
                    dragging_token = False
                    
            if tokenx != None and tokeny != None:
                self.draw_board(board, {'x': tokenx - int(SPACESIZE / 2), 'y': tokeny - int(SPACESIZE / 2), 'color': RED})
            else:
                self.draw_board(board)

            if show_help:
                self.display_surf.blit(self.arrow_img, self.arrow_rect)

            pygame.display.update()
            self.fps_clock.tick(FPS)

            await asyncio.sleep(0)

    async def animate_dropping_token(self, board, column, color):
        x = XMARGIN + column * SPACESIZE
        y = YMARGIN - SPACESIZE
        drop_speed = 1.0

        lowest_empty_space = self.get_lowest_empty_space(board, column)

        while True:
            y += int(drop_speed)
            drop_speed += 0.5
            if int((y - YMARGIN) / SPACESIZE) >= lowest_empty_space:
                return
            self.draw_board(board, {'x': x, 'y': y, 'color': color})
            pygame.display.update()
            self.fps_clock.tick(FPS)

            await asyncio.sleep(0)

    async def animate_computer_moving(self, board, column):
        x = self.black_pile_rect.left
        y = self.black_pile_rect.top
        speed = 1.0
        
        while y > (YMARGIN - SPACESIZE):
            y -= int(speed)
            speed += 0.5
            self.draw_board(board, {'x': x, 'y': y, 'color': BLACK})
            pygame.display.update()
            self.fps_clock.tick(FPS)
            await asyncio.sleep(0)

        y = YMARGIN - SPACESIZE
        speed = 1.0
        while x > (XMARGIN + column * SPACESIZE):
            x -= int(speed)
            speed += 0.5
            self.draw_board(board, {'x': x, 'y': y, 'color': BLACK})
            pygame.display.update()
            self.fps_clock.tick(FPS)
            await asyncio.sleep(0)

        await self.animate_dropping_token(board, column, BLACK)

    def get_computer_move(self, board):
        potential_moves = self.get_potential_moves(board, BLACK, DIFFICULTY)
        best_move_fitness = -1
        for i in range(BOARDWIDTH):
            if potential_moves[i] > best_move_fitness and self.is_valid_move(board, i):
                best_move_fitness = potential_moves[i]
        
        best_moves = []
        for i in range(len(potential_moves)):
            if potential_moves[i] == best_move_fitness and self.is_valid_move(board, i):
                best_moves.append(i)
        return random.choice(best_moves)

    def get_potential_moves(self, board, tile, look_ahead):
        if look_ahead == 0 or self.is_board_full(board):
            return [0] * BOARDWIDTH

        enemy_tile = BLACK if tile == RED else RED

        potential_moves = [0] * BOARDWIDTH
        for first_move in range(BOARDWIDTH):
            dupe_board = copy.deepcopy(board)
            if not self.is_valid_move(dupe_board, first_move):
                continue
            self.make_move(dupe_board, tile, first_move)
            if self.is_winner(dupe_board, tile):
                potential_moves[first_move] = 1
                break
            else:
                if self.is_board_full(dupe_board):
                    potential_moves[first_move] = 0
                else:
                    for counter_move in range(BOARDWIDTH):
                        dupe_board2 = copy.deepcopy(dupe_board)
                        if not self.is_valid_move(dupe_board2, counter_move):
                            continue
                        self.make_move(dupe_board2, enemy_tile, counter_move)
                        if self.is_winner(dupe_board2, enemy_tile):
                            potential_moves[first_move] = -1
                            break
                        else:
                            results = self.get_potential_moves(dupe_board2, tile, look_ahead - 1)
                            potential_moves[first_move] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
        return potential_moves

    def get_lowest_empty_space(self, board, column):
        for y in range(BOARDHEIGHT-1, -1, -1):
            if board[column][y] == EMPTY:
                return y
        return -1

    def is_valid_move(self, board, column):
        if column < 0 or column >= BOARDWIDTH or board[column][0] != EMPTY:
            return False
        return True

    def is_board_full(self, board):
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if board[x][y] == EMPTY:
                    return False
        return True

    def is_winner(self, board, tile):
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
                    return True
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
                    return True
        for x in range(BOARDWIDTH - 3):
            for y in range(3, BOARDHEIGHT):
                if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
                    return True
        for x in range(BOARDWIDTH - 3):
            for y in range(BOARDHEIGHT - 3):
                if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
                    return True
        return False

if __name__ == '__main__':
    game = FourInARowGame()
    asyncio.run(game.run())
