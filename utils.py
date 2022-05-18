import pygame
import sys, os
from datetime import datetime

date = datetime.date(datetime.now())  # change to check date when needed // delete this wtf

class Option:
    hovered = False
    def __init__(self, game, text, pos):
        self.game = game
        self.text = text
        self.pos = pos
        self.menu_font = pygame.font.Font(None, 40)
        self.set_rect()
        self.draw()
            
    def draw(self):
        self.set_rend()
        self.game.screen.blit(self.rend, self.rect)
        
    def set_rend(self):
        self.rend = self.menu_font.render(self.text, True, self.get_color())
        
    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)
        
    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos


class InputBox:
    def __init__(self, game, x, y, w, h, text=''):
        self.game = game
        self.COLOR_ACTIVE = pygame.Color('dodgerblue2')
        self.COLOR_INACTIVE = pygame.Color('lightskyblue3')
        self.FONT = pygame.font.Font(None, 32)
        self.rect = pygame.Rect(x, y, w, h)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.game.cheatCode = self.text.lower()
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self):
        # Blit the text.
        self.game.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(self.game.screen, self.color, self.rect, 2)

class Button(pygame.sprite.Sprite):
    def __init__(self, game, x, y, text, gamestate=None):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.x = x
        self.y = y
        self.text = text
        self.gamestate = gamestate
        self.image = get_image('Assets/Images/button0.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.soundFlag = False
        self.showBorder = False
        self.size = 40

    def update(self, event):
        # update flags for mouseover
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos[0], pos[1]):
            if self.soundFlag:
                play_sound('Assets/Sounds/mouseover.wav')
            self.soundFlag = False
            self.showBorder = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_sound('Assets/Sounds/select.wav')
                if self.text == 'QUIT':
                    pygame.quit()
                    sys.exit()
                return True
        else:
            self.showBorder = False
            self.soundFlag = True

    def draw(self):
        if self.showBorder:
            self.game.screen.blit(get_image("Assets/Images/border.png"), (self.x-3, self.y-3))
        self.game.screen.blit(self.image, self.rect)
        draw_text(self.game.screen, self.text, (self.x+200, self.y+55), (0,0,0), self.size)

def getScores():
    # read highscore entries
    # put scores in a list and the whole entry in another
    # sort both lists
    highscores = []
    with open('Assets/Misc/highscores.txt','r') as f:
        entries = f.readlines()
    for entry in entries:
        entry = entry.split()
        highscores.append(int(entry[1]))
    entries = [item.strip() for item in entries]
    temp = zip(highscores,entries)
    temp = sorted(temp)
    entries = [x for y, x in temp]
    entries.reverse()
    highscores.sort()
    return highscores, entries

_text_library = {}
def draw_text(surf, text, pos, color=(0,0,0), size=20):
    global _text_library
    text_surf = _text_library.get(f"{text}{color}{size}")
    if text_surf is None:
        font = pygame.font.Font('Assets/Misc/ipaexg.ttf', size)
        text_surf = font.render(text, True, color)
        _text_library[f"{text}{color}{size}"] = text_surf
    x, y = pos
    surf.blit(text_surf, (x - (text_surf.get_width() // 2), y - (text_surf.get_height() // 2)))

_image_library = {}
def get_image(path):
    global _image_library
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        _image_library[path] = image
    return image

_sound_library = {}
def play_sound(path, stop=None):
    global _sound_library
    sound = _sound_library.get(path)
    if sound == None:
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        sound = pygame.mixer.Sound(canonicalized_path)
        _sound_library[path] = sound
    if stop is None:
        sound.play()
    elif stop:
        sound.stop()
    else:
        sound.play(10)