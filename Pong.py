#!/usr/bin/env python

#Pong-Classic by Isa Bolling
import os
os.environ['PYSDL2_DLL_PATH'] = os.path.dirname(os.path.abspath(__file__))
from sdl2 import *
from sdl2.sdlttf import *
import ctypes
from math import *

# GLOBALS______________________________________________________________________________________________________
DEBUG = False
WIDTH = 1280
HEIGHT = 720

# CLASSES______________________________________________________________________________________________________
class Pointer:
    cursors = dict()

    def __init__(self):
        self.pointer = SDL_Rect(0, 0, 10, 10)
        self.clicking = False

    def Compute(self, event):
        self.Set_Cursor(SDL_SYSTEM_CURSOR_ARROW)
        self.clicking = False

        if(event.type == SDL_MOUSEBUTTONDOWN):
            if(event.button.button == SDL_BUTTON_LEFT):
                self.clicking = True

        if(event.type == SDL_MOUSEMOTION):
            self.pointer.x = event.motion.x
            self.pointer.y = event.motion.y

    def Is_Touching(self, item):
        return SDL_HasIntersection(self.pointer, item.rect)

    def Is_Clicking(self, item):
        return self.Is_Touching(item) and self.clicking

    def Set_Cursor(self, id):
        if id not in Pointer.cursors:
            Pointer.cursors[id] = SDL_CreateSystemCursor(id)
        SDL_SetCursor(Pointer.cursors[id])

    def __del__(self):
        for cursor in Pointer.cursors:
            SDL_FreeCursor(Pointer.cursors[cursor])


class TextObject:
    fonts = dict()

    def __init__(self, renderer, text, width, height,
                font_name, color = (0, 0, 0), location = (0, 0), font_size = 34):
        self.r = renderer
        if len(font_name) > 1:
            TextObject.fonts[font_name[0]] = TTF_OpenFont(font_name[1], font_size)
        self.color = SDL_Color(color[0], color[1], color[2])
        self.surface = TTF_RenderText_Solid(TextObject.fonts[font_name[0]], text.encode('utf-8'), self.color)
        self.message = SDL_CreateTextureFromSurface(self.r, self.surface)
        SDL_FreeSurface(self.surface)
        self.rect = SDL_Rect(location[0], location[1], width, height)
        self.highlight = False

    def Render(self, x = None, y = None):
        if self.highlight:
            SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
            SDL_RenderDrawRect(self.r, self.rect)
        if x is None and y:
            self.rect.y = y
        elif x and y is None:
            self.rect.x = x
        elif x and y:
            self.rect.x = x
            self.rect.y = y
        SDL_RenderCopy(self.r, self.message, None, self.rect)

    def __del__(self):
        for keys in list(TextObject.fonts):
            font = TextObject.fonts.pop(keys, None)
            if font: TTF_CloseFont(font)
        SDL_DestroyTexture(self.message)


class Paddle:
    def __init__(self, renderer, position = (0,0), color = (0,0,0), size = 17):
        self.r = renderer
        self.head = SDL_Rect(position[0], position[1], size, size)
        self.body = [None for i in range(7)]
        self.body[3] = self.head
        self.direction = None
        self.size = size

        """ This code is for creating the body of the paddle """
        for i in range(3, 0, -1):
            self.body[i-1] = SDL_Rect(self.body[i].x, self.body[i].y - size, size, size)
        for i in range(3, 6):
            self.body[i+1] = SDL_Rect(self.body[i].x, self.body[i].y + size, size, size)

        self.color = SDL_Color(color[0], color[1], color[2], 255)

        if DEBUG:
            for i in self.body:
                print(i)

    def Set_Position(self, position):
        self.body[3].x = position[0]
        self.body[3].y = position[1]
        for i in range(3, 0, -1):
            self.body[i-1].x = self.body[i].x
            self.body[i-1].y = self.body[i].y - self.size
        for i in range(3, 6):
            self.body[i+1].x = self.body[i].x
            self.body[i+1].y = self.body[i].y + self.size

    def Move(self, direction, speed, movement = True):
        self.direction = direction
        if movement:
            if direction == 'UP':
                for body in self.body:
                    body.y -= speed
            elif direction == 'DOWN':
                for body in self.body:
                    body.y += speed

    def Is_Touching(self, item):
        """ This function returns true or false if the paddle is touching the item. it also
            returns the index of the part of the paddle that touched the item. """
        for i in range(len(self.body)):
            if SDL_HasIntersection(self.body[i], item.rect):
                return (True, i)
        return (False, -1)

    def Render(self):
        SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
        for item in self.body:
            SDL_RenderFillRect(self.r, item)


class Walls:
    def __init__(self, renderer, color = (0,0,0), size = (WIDTH, 20), pos = (0, HEIGHT - 20)):
        self.r = renderer
        self.color = SDL_Color(color[0], color[1], color[2], 255)
        self.bounds = [SDL_Rect(0, pos[0], size[0], size[1]),
                       SDL_Rect(0, pos[1], size[0],  size[1])]

    def Touching_Paddle(self, paddle):
        for part in paddle.body:
            if SDL_HasIntersection(self.bounds[0], part):
                return (True, 0)
            elif SDL_HasIntersection(self.bounds[1], part):
                return (True, 1)
        return (False, -1)

    def Render(self):
        SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
        for wall in self.bounds:
            SDL_RenderFillRect(self.r, wall)


class Ball:
    def __init__(self, renderer, position = (0,0), size = 20, color = (0, 0, 0)):
        self.r = renderer
        self.rect = SDL_Rect(position[0], position[1], size, size)
        self.color = SDL_Color(color[0], color[1], color[2], 255)
        self.x = position[0]
        self.y = position[1]

    def Set_Position(self, position):
        self.x = self.rect.x = position[0]
        self.y = self.rect.y = position[1]

    def Is_Touching_Wall(self, wall):
        for w in wall.bounds:
            if SDL_HasIntersection(w, self.rect):
                return True
        return False

    def Move(self, degree, speed = 5):
        self.x += speed * cos(radians(degree))
        self.y += speed * sin(radians(degree))
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def Render(self):
        SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
        SDL_RenderFillRect(self.r, self.rect)


class Clock:
    def __init__(self):
        self.last_time = 0
        self.current_time = SDL_GetPerformanceCounter()
        self.dt = 0
        self.dt_s = 0
        self.s = 0
        self.count = 0.0

    def Tick(self):
        self.last_time = self.current_time
        self.current_time = SDL_GetPerformanceCounter()
        self.dt = (self.current_time - self.last_time) * 1000 / SDL_GetPerformanceFrequency()
        self.dt_s = self.dt * .001
        if DEBUG:
            print('DT SECONDS:', self.dt_s)
            print('DT:', self.dt)

    def Get_Distance(self, speed):
        """ This function returns the amount of pixels to move by under a constant timestep,
            no matter how fast the processor actually is on the host computer """
        return (speed * 100) * self.dt_s

    def Counter(self):
        self.s += self.dt_s


class Scoreboard:
    def __init__(self, renderer, position = (WIDTH // 2 - 2, 0), size = 20, color = (169, 169, 169, 240)):
        self.color = SDL_Color(color[0], color[1], color[2], color[3])
        self.board = []
        self.r = renderer
        y = 0
        """ For creating the actual divider in the middle of the screen """
        while y < HEIGHT - 40:
            y += size * 2
            self.board.append(SDL_Rect(position[0], y - 20, size, size))
        self.P1 = []
        self.P2 = []
        for i in range(11):
            if i != 10:
                self.P1.append(TextObject(renderer, str(i), 50, 70, ['joystix'], location = (position [0] - size * 3 -5, size),
                                          color = (self.color.r, self.color.g, self.color.b)))
                self.P2.append(TextObject(renderer, str(i), 50, 70, ['joystix'], location = (position [0] + size * 2, size),
                                          color = (self.color.r, self.color.g, self.color.b)))
            else:
                self.P1.append(TextObject(renderer, str(i), 70, 70, ['joystix'], location = (position [0] - size * 3 -25, size),
                                          color = (self.color.r, self.color.g, self.color.b)))
                self.P2.append(TextObject(renderer, str(i), 70, 70, ['joystix'], location=(position[0] + size * 2, size),
                               color=(self.color.r, self.color.g, self.color.b)))

    def Render(self, position = None, b = True):
        if position is not None:
            self.P1[position[0]].Render()
            self.P2[position[1]].Render()
        if b:
            SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
            for piece in self.board:
                SDL_RenderFillRect(self.r, piece)


# FUNCTIONS_____________________________________________________________________________________________________
def WindowState(window, renderer, fs):
    if not fs:
        SDL_SetWindowFullscreen(window, 0)

    elif fs:
        SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN_DESKTOP)
        SDL_RenderSetLogicalSize(renderer, WIDTH, HEIGHT)


def Deleter(dictionary_list):
    for dictionary in dictionary_list:
        for item in list(dictionary):
            del dictionary[item]


def Change_Degree(paddles, degree, ball):
    """ The result of the ball touching the paddle is saved under the result variable.
        from the result variable, the second value of the result variable is used to
        check which angle to move the ball in. """
    paddle_1_result = paddles[0].Is_Touching(ball)
    paddle_2_result = paddles[1].Is_Touching(ball)
    if paddle_1_result[0]:
        ball.Set_Position(((int(ball.x) + 10), int(ball.y)))
        if paddle_1_result[1] == 6:
            return 60
        elif paddle_1_result[1] == 5:
            return 45
        elif paddle_1_result[1] == 4:
            return 30
        elif paddle_1_result[1] == 3:
            return 0
        elif paddle_1_result[1] == 2:
            return 330
        elif paddle_1_result[1] == 1:
            return 315
        elif paddle_1_result[1] == 0:
            return 300

    if paddle_2_result[0]:
        ball.Set_Position(((int(ball.x) - 10), int(ball.y)))
        if paddle_2_result[1] == 6:
            return 120
        elif paddle_2_result[1] == 5:
            return 135
        elif paddle_2_result[1] == 4:
            return 150
        elif paddle_2_result[1] == 3:
            return 180
        elif paddle_2_result[1] == 2:
            return 210
        elif paddle_2_result[1] == 1:
            return 225
        elif paddle_2_result[1] == 0:
            return 240
    return degree


# MAIN__________________________________________________________________________________________________________
def main():
    if (TTF_Init() < 0):
        print(TTF_GetError())
        return -1

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER | SDL_INIT_EVENTS) < 0):
        print(SDL_GetError())
        return -1

    window = SDL_CreateWindow(b"Pong Classic - By Isa Bolling", SDL_WINDOWPOS_UNDEFINED,
                            SDL_WINDOWPOS_UNDEFINED, WIDTH, HEIGHT, SDL_WINDOW_SHOWN)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_PRESENTVSYNC)
    event = SDL_Event()

    # Variables_________________________________________________________________________________________________
    running = True
    menu = True
    game = False
    fullscreen = False
    paused = False
    speed = 6
    ball_speed = 10
    degree = 180
    player_1_score = 0
    player_2_score = 0
    scoring = False
    game_over = False
    winner = 0
    board = True

    # Objects___________________________________________________________________________________________________
    mouse = Pointer()
    menu_items = {
    'Title':       TextObject(renderer, 'Pong Classic', 600, 240, ['joystix', b'font/joystix.ttf'], location = (345, 0)),
    'Start':       TextObject(renderer, 'Start', 100, 85, ['joystix'], location = (583, 350)),
    'Fullscreen':  TextObject(renderer, 'Fullscreen', 200, 85, ['joystix'], location = (543, 450)),
    'Quit':        TextObject(renderer, 'Quit', 90, 85, ['joystix'], location = (590, 550))
    }
    paddles = [Paddle(renderer, position = (20, 290)), Paddle(renderer, position = (1245, 290))]
    wall = Walls(renderer)
    ball = Ball(renderer, position = (60, 290))
    clock = Clock()
    scoreboard = Scoreboard(renderer)
    winner_text = [
        TextObject(renderer, 'Player 1 Wins', 900, 340, ['joystix'], location = (210, 40), color = (105, 105, 105)),
        TextObject(renderer, 'Player 2 Wins', 900, 340, ['joystix'], location = (210, 40), color = (105, 105, 105))]
    game_items = {
    'Paused':     TextObject(renderer, 'Paused', 400, 240, ['joystix'], location = (450, 200), color = (105, 105, 105)),
    'Restart':    TextObject(renderer, 'Restart', 120, 85, ['joystix'], location = (450, 350), color = (105, 105, 105)),
    'Menu':       TextObject(renderer, 'Menu', 90, 85, ['joystix'], location = (720, 350), color = (105, 105, 105))
    }

    # Game Loop_________________________________________________________________________________________________
    while (running):
        keystate = SDL_GetKeyboardState(None)
        clock.Tick()

        # Event Loop___________________________________________________________
        while(SDL_PollEvent(ctypes.byref(event))):
            mouse.Compute(event)
            if(event.type == SDL_QUIT):
                running = False
                break
            if game and not game_over:
                if(event.type == SDL_KEYDOWN):
                    if (event.key.keysym.scancode == SDL_SCANCODE_P):
                        if not paused:
                            paused = True
                            board = False
                        else:
                            paused = False
                            board = True

        if keystate[SDL_SCANCODE_ESCAPE]:
            running = False
            break

        # Logic________________________________________________________________
        degree = Change_Degree(paddles, degree, ball)
        if not paused:
            if ball.Is_Touching_Wall(wall):
                degree = 360-degree
            ball.Move(degree, int(clock.Get_Distance(ball_speed)))

        if (menu):
            for item in menu_items:
                if item == 'Title':
                    pass
                else:
                    if mouse.Is_Touching(menu_items[item]):
                        menu_items[item].highlight = True
                        mouse.Set_Cursor(SDL_SYSTEM_CURSOR_HAND)
                    else:
                        menu_items[item].highlight = False

            if mouse.Is_Clicking(menu_items['Quit']):
                running = False
                break

            if mouse.Is_Clicking(menu_items['Fullscreen']):
                if fullscreen is False:
                    fullscreen = True
                    WindowState(window, renderer, fullscreen)
                else:
                    fullscreen = False
                    WindowState(window, renderer, fullscreen)

            if mouse.Is_Clicking(menu_items['Start']):
                ball.Set_Position((WIDTH // 2, HEIGHT // 2 - 30))
                degree = 1
                menu = False
                game = True

        if (game):
            for paddle in paddles:
                result = wall.Touching_Paddle(paddle)
                if result[0]:
                    if result[1] == 0:
                        paddle.Move('DOWN', int(clock.Get_Distance(speed)))
                    else:
                        paddle.Move('UP', int(clock.Get_Distance(speed)))

            if not paused and not game_over:
                """ This code is for controlling the first paddle """
                if keystate[SDL_SCANCODE_W]:
                    paddles[0].Move('UP', int(clock.Get_Distance(speed)))
                if keystate[SDL_SCANCODE_S]:
                    paddles[0].Move('DOWN', int(clock.Get_Distance(speed)))
                """ This code is for controlling the second paddle """
                if keystate[SDL_SCANCODE_UP]:
                    paddles[1].Move('UP', int(clock.Get_Distance(speed)))
                if keystate[SDL_SCANCODE_DOWN]:
                    paddles[1].Move('DOWN', int(clock.Get_Distance(speed)))

            """ This code is for making sure the ball goes back to the middle
                after going outta bounds, and for implementing the scoring """
            if ball.x < - 20 or ball.x > WIDTH + 20:
                ball_speed = 0
                clock.Counter()
                if not scoring:
                    if ball.x < - 20:
                        player_2_score += 1
                        if player_2_score > 10:
                            player_2_score = 10
                        scoring = True
                    else:
                        player_1_score += 1
                        if player_1_score > 10:
                            player_1_score = 10
                        scoring = True
                if clock.s > 2:
                    clock.s = 0
                    ball.Set_Position((WIDTH // 2, HEIGHT // 2 - 20))
                    ball_speed = 10
                    scoring = False

            if player_1_score == 10:
                winner = 0
                game_over = True
            elif player_2_score == 10:
                winner = 1
                game_over = True

            if (game_over):
                paused = False
                board = False
                ball_speed = 0
                ball.Set_Position((40, -40))
                for item in game_items:
                    if item == 'Paused':
                        pass
                    else:
                        if mouse.Is_Touching(game_items[item]):
                            game_items[item].highlight = True
                            mouse.Set_Cursor(SDL_SYSTEM_CURSOR_HAND)
                        else:
                            game_items[item].highlight = False

                if mouse.Is_Clicking(game_items['Restart']):
                    player_1_score = 0
                    player_2_score = 0
                    ball.Set_Position((WIDTH // 2, HEIGHT // 2 - 30))
                    paddles[0].Set_Position((20, 290))
                    paddles[1].Set_Position((1245, 290))
                    degree = 1
                    ball_speed = 10
                    game_over = False
                    scoring = False
                    board = True

                if mouse.Is_Clicking(game_items['Menu']):
                    player_1_score = 0
                    player_2_score = 0
                    ball.Set_Position((60, 290))
                    degree = 180
                    paddles[0].Set_Position((20, 290))
                    paddles[1].Set_Position((1245, 290))
                    ball_speed = 10
                    game_over = False
                    scoring = False
                    board = True
                    game = False
                    menu = True

        # Rendering____________________________________________________________
        SDL_SetRenderDrawColor(renderer, 252, 252, 252, 255)
        SDL_RenderClear(renderer)

        for paddle in paddles:
            paddle.Render()
        wall.Render()

        if (menu):
            for item in menu_items:
                menu_items[item].Render()

        if (game):
            scoreboard.Render((player_1_score, player_2_score), board)
            
        ball.Render()
        
        if (game_over):
            winner_text[winner].Render()
            for item in game_items:
                if item == 'Paused':
                    pass
                else:
                    game_items[item].Render()
        if (paused):
            game_items['Paused'].Render()

        SDL_RenderPresent(renderer)
        SDL_Delay(10)

    Deleter([menu_items, game_items])
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    SDL_Quit()
    TTF_Quit()
    return 0


main()
