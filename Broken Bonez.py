import pygame
from gamestates import *
from utils import get_image

# fork a branch for different points system (chicken)
    # mash a button to build up points in the air
    # risk grows as time passes
# cheats - Enter code to unlock new;Background, soundtrack, effects, secret trick, audio quotes form characters, etc.
# rigby achievement: special secret trick for tapping two buttons back and forth

# Version 1.6.0 changelog:
    # refactor into a gamestate manager format 

# add extras
    # 'party time'
    # 'duck power'
    # 'rig juice'
# change mechanics
    # use button mashing to accumulate points directly; have tricks assocaited with points ranges
        # or have them mash a button aas much as they can while the animation is playing
        # use left and right arrow keys ?
# display rank in lb on gameover if highscore

class Game:
    def __init__(self):
        # Fetch settings
        with open('Assets/Misc/settings.txt','r') as f:
            savedSettings = f.readlines()
        self.windowMode = savedSettings[0]
        self.volume = float(savedSettings[1])
        self.cheatCode = ''

        # Fetch achievements
        self.achievements = []
        with open('Assets/Misc/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        self.highscore, self.entries = getScores()

        # Initialize pygame with current settings
        pygame.mixer.pre_init(44100, -16, 1, 512) # reduces audio latency
        pygame.init()
        pygame.mixer.music.load('Assets/Sounds/hangin_tough.mp3')
        pygame.mixer.music.play(-1) # loop music
        pygame.mixer.music.set_volume(self.volume)
        self.framecount = 0
        self.fps = 60
        self.width = 1920
        self.height = 1080
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.bg = get_image("Assets/images/bg_day.png")
        self.blit_bg = self.bg
        self.hud = True
        self.font = pygame.freetype.Font('Assets/Misc/ipaexg.ttf', 20)
        self.clock = pygame.time.Clock()

    def main(self):
        while True:
            gsm.update()  # Updates AND draws each gamestate


class GameStateManager:
    def __init__(self):
        self.game = game
        self.game.gsm = self
        self.current_state = MainMenu(game)
        self.game_state_stack = [self.current_state]

    def switch(self, state):
        self.current_state = state
        self.game_state_stack.pop()
        self.game_state_stack.append(self.current_state)

    def update(self):
        for gamestate in self.game_state_stack:
            if gamestate.active:
                gamestate.update()
            if not gamestate.is_obscured:
                gamestate.draw()


if __name__ == "__main__":
    game = Game()
    gsm = GameStateManager()
    game.main()
