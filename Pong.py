import os
os.environ['PYSDL2_DLL_PATH'] = os.path.dirname(os.path.abspath(__file__))
from sdl2 import *
from sdl2.sdlttf import *
import ctypes
from math import *

# GLOBALS______________________________________________________________________________________________________
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
                font_name, color = (0, 0, 0), location = (0, 0), font_size = 36):
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
    renderer = SDL_CreateRenderer(window, -1, 0)
    event = SDL_Event()

    # Variables_________________________________________________________________________________________________
    running = True
    menu = True
    game = False
    fullscreen = False

    # Objects___________________________________________________________________________________________________
    mouse = Pointer()
    menu_items = {
    'Title':       TextObject(renderer, 'Pong   Classic', 600, 300, ['arcade', b'font/arcade.ttf'], location = (345, 0)),
    'Start':       TextObject(renderer, 'Start', 100, 100, ['arcade'], location = (583, 350)),
    'Fullscreen':  TextObject(renderer, 'Fullscreen', 200, 85, ['arcade'], location = (543, 454)),
    'Quit':        TextObject(renderer, 'Quit', 80, 100, ['arcade'], location = (590, 550))
    }

    # Game Loop_________________________________________________________________________________________________
    while(running):
        keystate = SDL_GetKeyboardState(None)
        # Event Loop___________________________________________________________
        while(SDL_PollEvent(ctypes.byref(event))):
            mouse.Compute(event)
            if(event.type == SDL_QUIT):
                running = False
                break

        # Logic________________________________________________________________
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

        if (game):
            pass

        # Rendering____________________________________________________________
        SDL_SetRenderDrawColor(renderer, 252, 252, 252, 255)
        SDL_RenderClear(renderer)

        if (menu):
            for item in menu_items:
                menu_items[item].Render()

        if (game):
            pass

        SDL_RenderPresent(renderer)

        SDL_Delay(10)

    Deleter([menu_items])
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    TTF_Quit()
    SDL_Quit()
    return 0


main()
