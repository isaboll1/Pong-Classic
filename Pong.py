import os
os.environ['PYSDL2_DLL_PATH'] = os.path.dirname(os.path.abspath(__file__))
from sdl2 import *
from sdl2.sdlttf import *
import ctypes
from math import *

# GLOBALS_____________________________________________________________
WIDTH = 800
HEIGHT = 600

# CLASSES_____________________________________________________________
class Pointer:
    def __init__(self):
        self.pointer = SDL_Rect(0, 0, 10, 10)
        self.clicking = False

    def Compute(self, event):
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
        return

    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER | SDL_INIT_EVENTS) < 0):
        print(SDL_GetError())
        return

    window = SDL_CreateWindow(b"Pong Classic - By Isa Bolling", SDL_WINDOWPOS_UNDEFINED,
                            SDL_WINDOWPOS_UNDEFINED, WIDTH, HEIGHT, SDL_WINDOW_SHOWN)
    renderer = SDL_CreateRenderer(window, -1, 0)
    event = SDL_Event()

    # Variables_________________________________________________________________________________________________
    running = True

    # Objects___________________________________________________________________________________________________

    # Game Loop_________________________________________________________________________________________________
    while(running):
        keystate = SDL_GetKeyboardState(None)
        # Event Loop
        while(SDL_PollEvent(ctypes.byref(event))):
            if(event.type == SDL_QUIT):
                running = False
                break

    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    TTF_Quit()
    SDL_Quit()
    return 0


main()
