import pygame
import os

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
    if stop == False:
        sound.play(10)
    elif stop == True:
        sound.stop()
    else: sound.play()

def drawText(screen, text, size, x, y, color=(255,255,255), fontstr='freesansbold.ttf', center=True):
    font = pygame.font.Font(fontstr, size)
    text = font.render(text, True, color)
    if center:
        screen.blit(text, (x - (text.get_width() // 2), y - (text.get_height() // 2)))
    else:
        screen.blit(text, (x,y))