import pygame
import pygame.freetype
from random import randint

pygame.init()

window_width = 550
window_height = 700
grid_width = 300
grid_height = 600
col_num = 10
row_num = 20
top_left_x = 50
top_left_y = 50
grid_color = (50, 50, 50)

fps = 30
cooldown = round(fps / 10)

window = (window_width, window_height)
win = pygame.display.set_mode(window)

pygame.display.set_caption("Tetriada")
bg = pygame.Surface(window)

clock = pygame.time.Clock()

figures = [(1, 1, 2,
            3, 1),
           (1, 3, 1, 2,
            1, 0, 0),
           (1, 3, 1, 1),
           (1, 0, 0, 2,
            1, 3, 1),
           (0, 1, 0, 2,
            1, 3, 1),
           (1, 1, 0, 2,
            0, 3, 1),
           (0, 1, 1, 2,
            1, 3, 0)]


figures_color = [(232, 229, 77),
                (212, 34, 164),
                (33, 88, 191),
                (212, 34, 96),
                (35, 168, 38),
                (162, 219, 64),
                (199, 36, 28)]

block_size = int(grid_width / col_num)
start_x = int(top_left_x + grid_width/2 - block_size*2)
# start_y = int(top_left_y)

start_y = int(top_left_y - block_size*3)
border_r = top_left_x + grid_width - block_size
border_l = top_left_x
border_b = top_left_y + grid_height


class Grid:
    def __init__(self, x, y):
        self.start_x = x
        self.start_y = y
        self.grid_positions_x = []
        self.grid_positions_y = []

    def draw(self, surface):
        self.grid_positions_x = []
        self.grid_positions_y = []

        for c in range(col_num + 1):
            pygame.draw.line(surface, grid_color, (self.start_x + c * block_size, self.start_y),
                             (self.start_x + c * block_size, self.start_y + row_num * block_size))
            self.grid_positions_x.append(self.start_x + c*block_size)
        for r in range(row_num + 1):
            pygame.draw.line(surface, grid_color, (self.start_x, self.start_y + r * block_size),
                             (self.start_x + grid_width, self.start_y + r * block_size))
            self.grid_positions_y.append(self.start_y + r * block_size)





class Fig:
    def __init__(self, shape, start_x, start_y):
        self.shape = shape
        self.x = start_x
        self.y = start_y
        self.timecount = 0
        self.color = (0, 0, 0)
        self.coord = []

        self.abs_coord = []
        self.rel_coord = []
        self.rot_point = []

        self.collision_left = False
        self.collision_right = False
        self.rotCw = False
        self.isFallen = False
        self.draw_shape(self.shape, self.x, self.y)
        self.stored_coord = []

    def fig_appear(self):
        if self.shape == figures[2]:
            pass


    def draw_shape(self, shape, sx, sy):
        row = 0
        column = 0
        self.abs_coord = []
        self.rel_coord = []
        
        for i in shape:
            if i == 1:
                column += 1
                self.abs_coord.append((sx + block_size * (column - 1), sy + block_size * row))
            if i == 2:
                row += 1
                column = 0
            if i == 3:
                column += 1
                self.abs_coord.append((sx + block_size * (column - 1), sy + block_size * row))
                self.rot_point = [sx + block_size * (column - 1), sy + block_size * row]
            if i == 0:
                column += 1

        # \|/ Gets relative coordinates once instance of Fig is created
        for x, y in self.abs_coord:
            rx = x - self.rot_point[0]
            ry = y - self.rot_point[1]

            self.rel_coord.append((rx, ry))

        return self.rel_coord

    def converter(self, rel):
        converted_coord = []
        for x, y in rel:
            abs_x = x + self.rot_point[0] #
            abs_y = y + self.rot_point[1] # get absolute coordinates

            converted_coord.append([abs_x, abs_y])

        self.coord = converted_coord
        return self.coord

    def draw_figure(self):
        # Modifies:
        if self.rotCw:
            self.rotate_cw()
            self.rotCw = False
        else:
            pass
        self.fall()
        self.collision_right = False
        self.collision_left = False
        # Checks if space is valid, takes self.coord from converter as arg
        self.valid_space(self.converter(self.rel_coord))

        # Stores final coordinates in memory
        self.stored_coord = self.coord
        self.color = figures_color[figures.index(self.shape)]
        for x, y in self.coord:
            if y < top_left_y:
                pygame.draw.rect(win, (0, 0, 0), (x, y, block_size, block_size))
            else:
                pygame.draw.rect(win, self.color, (x, y, block_size, block_size))

    def valid_space(self, coord):
        global taken_pos
        fixed_coord = []
        at_right_b = False
        at_left_b = False
        for x, y in coord:
            # Border check
            if x > border_r:
                at_right_b = True
            if x < border_l:
                at_left_b = True
            if y + block_size >= border_b:
                self.isFallen = True
            # Collision check
            if (x, y + block_size) in taken_pos:
                self.isFallen = True
                # Game over check
                if y + block_size <= top_left_y:
                    gameOver()
            if (x + block_size, y) in taken_pos:
                self.collision_right = True
            if (x - block_size, y) in taken_pos:
                self.collision_left = True


        if at_right_b:
            for x, y in coord:
                fixed_coord.append((x - block_size, y))
            self.rot_point[0] -= block_size
            self.coord = fixed_coord
        if at_left_b:
            for x, y in coord:
                fixed_coord.append((x + block_size, y))
            self.rot_point[0] += block_size
            self.coord = fixed_coord

        return self.coord

    def rotate_cw(self):
        new_rel_coord = []
        for x, y in self.rel_coord:
            rel_x = -y
            rel_y = x
            new_rel_coord.append((rel_x, rel_y))
        self.rel_coord = new_rel_coord
        return self.rel_coord

    def fall(self):
        if self.timecount >= fps:
            self.timecount = 0
        elif self.timecount % (fps/1) == 0:
            self.rot_point[1] += block_size
            self.timecount += 1
        else:
            self.timecount += 1


def grid_painter(xy_color):
    for xy, color in xy_color:
        if xy[1] >= top_left_y:
            pygame.draw.rect(win, color, (xy[0], xy[1], block_size, block_size))


def clear_row(y):
    global taken_grid
    global score
    clear_y = []
    taken_sub = []
    for i in y:
        if y.count(i) >= col_num:
            clear_y.append(i)
    lines_score = len(clear_y)
    if lines_score == 10:
        score += lines_score
    elif lines_score >= 20:
        score += int(lines_score * (lines_score / 10))
    if len(clear_y) > 0:
        for xycolor in taken_grid:
            if xycolor[0][1] in clear_y:
                pass
            else:
                if xycolor[0][1] > max(clear_y):
                    taken_sub.append(xycolor)
                else:
                    xycolor = ((xycolor[0][0], xycolor[0][1] + block_size * int((len(clear_y)/col_num))), xycolor[1])
                    taken_sub.append(xycolor)
        taken_grid = taken_sub


score = 0


def scoreboard():
    score_text = pygame.freetype.SysFont('Verdana', 30)
    score_pos = (top_left_x + grid_width + 30, int(top_left_y + grid_height / 2))
    score_text.render_to(win, score_pos, f'Score: {score}', (255, 255, 255))


tetris_grid = Grid(top_left_x, top_left_y)
taken_grid = []
taken_pos = []
taken_y = []


def taken():
    global taken_pos
    global taken_y
    taken_pos = []
    taken_y = []
    for xy, color in taken_grid:
        taken_pos.append(xy)
        taken_y.append(xy[1])


def text_object(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()


def quit_click():
    pygame.quit()
    quit()


def button(text, y, action=None):
    # ic = inactive color; ac = active color
    ic = (12, 150, 0)
    ac = (42, 212, 42)
    largeText = pygame.font.SysFont('Verdana', 40)
    click = pygame.mouse.get_pressed()

    TextSurf, TextRect = text_object(text, largeText, ic)
    TextRect.center = (int(window_width / 2), y)

    bx = TextRect[0]
    by = TextRect[1]
    width = TextRect[2]
    height = TextRect[3]
    mouse = pygame.mouse.get_pos()
    if bx < mouse[0] < bx + width and by < mouse[1] < by + height:
        TextSurf, TextRect = text_object(text, largeText, ac)
        TextRect.center = (int(window_width / 2), y)
        if click[0] == 1 and action != None:
            action()

    win.blit(TextSurf, TextRect)


def gameOver():
    show = True
    gameoverbg = pygame.Surface(window)
    gameoverbg.convert_alpha(bg)
    gameoverbg.set_alpha(150)
    gameoverbg.fill((0, 0, 0))
    go_font = pygame.freetype.SysFont("Verdana", 50)
    pe_font = pygame.freetype.SysFont("Verdana", 30)

    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                loop_menu()
        grid_painter(taken_grid)
        scoreboard()
        tetris_grid.draw(win)

        win.blit(gameoverbg, (0, 0))
        go_font.render_to(win, (145, 150), "Game over", (255, 0, 0))
        pe_font.render_to(win, (205, 200), "Press ESC", (255, 0, 0))

        pygame.display.update()


def redraw_game_window():
    win.blit(bg, (0, 0))

    current_figure.draw_figure()
    taken()
    grid_painter(taken_grid)
    scoreboard()
    tetris_grid.draw(win)
    pygame.display.update()


def loop_menu():
    # ic = inactive_color
    menu = True
    while menu:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        win.fill((0, 0, 0))

        button("Start game", 100, loop_game)
        button("Leaderboards", 200)
        button("Quit", 300, quit_click)

        pygame.display.update()


random_shape = figures[randint(0, len(figures) - 1)]
current_figure = Fig(random_shape, start_x, start_y)


def loop_game():
    global random_shape
    global current_figure

    ticker = 0
    run = True
    while run:

        clock.tick(fps)
        if ticker > 0:
            ticker -= 1

        if current_figure.isFallen:
            for xy in current_figure.coord:
                taken_grid.append(((xy[0], xy[1]), current_figure.color))
            taken()
            clear_row(taken_y)
            random_shape = figures[randint(0, len(figures) - 1)]
            new_figure = Fig(random_shape, start_x, start_y)
            current_figure = new_figure

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            loop_menu()

        if keys[pygame.K_UP]:
            if ticker == 0:
                current_figure.rotCw = True
                ticker = cooldown

        if keys[pygame.K_DOWN]:
            if ticker == 0:
                current_figure.rot_point[1] += block_size
                ticker = cooldown

        if keys[pygame.K_RIGHT]:
            if ticker == 0 and not current_figure.collision_right:
                current_figure.rot_point[0] += block_size
                ticker = cooldown

        if keys[pygame.K_LEFT]:
            if ticker == 0 and not current_figure.collision_left:
                current_figure.rot_point[0] -= block_size
                ticker = cooldown

        redraw_game_window()


loop_menu()
loop_game()
pygame.quit()
