import pygame
from utils import *
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.x = 200
        self.y = 800
        self.image = get_image('Assets/Images/bbm.png')
        self.rect = self.image.get_rect()
        self.onRamp = False
        self.initJump = -9000 # avoid floating on first 30 frames
        self.isJumping = False
        self.trickcount = 0

    def update(self):
        # on ramp
        try:
            if self.rect.colliderect(self.game.gsm.game_state_stack[0].ramp.rect):
                if not self.onRamp:
                    self.onRamp = True
                    self.image = pygame.transform.rotate(self.image, 23)
            elif self.onRamp: # Update this flag to false
                self.onRamp = False
                self.initJump = self.game.framecount
        except: pass
            
        if self.onRamp or self.game.framecount - self.initJump <= 30:
            self.y -= 10

        # jumping
        elif self.game.framecount - self.initJump < 10*60:
            self.game.hud = False
            if self.x < 1920-200-self.rect.w:
                self.x += 2
            self.isJumping = True

        # landing
        elif self.y < 800 and self.game.framecount - self.initJump >= (5*60)+40:
            self.game.hud = True
            self.isJumping = False
            self.trickcount = 0
            self.y += 10
            self.x = 200
        if self.y == 800:
            self.image = get_image('Assets/Images/bbm.png')
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))


class Ramp(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.x = 2500
        self.y = 735
        self.image = get_image('Assets/Images/ramp.png')
        self.rect = self.image.get_rect()
        self.rect.y = self.y

    def update(self):
        self.x -= 25
        self.rect.x = self.x
        if self.x < -800:
            self.x = 10000

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))


class Animation:
    def __init__(self, game, interval, animation):
        self.game = game
        self.active_state = self.game.gsm.game_state_stack[0]
        self.initFrame = self.game.framecount
        self.interval = interval*2
        self.animation = animation
        self.count = -1
        self.done = False


class Trick(Animation):
    def __init__(self, game, interval, animation, base_score):
        super().__init__(game, interval, animation)
        self.base_score=base_score

    def animate(self, framecount):
        if (framecount - self.initFrame) % self.interval == 0:
            if self.count == len(self.animation)-1:
                self.done = True
            else: self.count += 1
        self.active_state.player.image = get_image(self.animation[self.count])


class Crash(Animation):
    def __init__(self, game, interval, animation):
        super().__init__(game, interval, animation)
        self.crashSound = True

    def animate(self, framecount):
        if (framecount - self.initFrame) >= self.interval[self.count+1]:
            if self.count+1 == 0 and self.crashSound:
                play_sound('Assets/Sounds/crash.wav')
                self.crashSound = False
            if self.count != len(self.animation)-2:
                self.count += 1
            else:
                self.done = True
        self.active_state.player.image = get_image(self.animation[self.count+1])
        self.active_state.player.y = 900
        self.active_state.player.x -= 2
        self.active_state.ramp.x = 10000
        for pebble in self.active_state.pebbles:
            pebble.x += 25

class Score:
    def __init__(self, game):
        self.game = game
        #self.active_state = self.game.gsm.game_state_stack[0]
        self.max = 0
        self.score = 0
        self.tricks = 0
        self.capped = False

    def animate(self, player_x, player_y, trickScore=None):
        # Add new score to max if any; if caught up, start sound again
        if trickScore != None:
            if self.score == self.max:
                play_sound('Assets/Sounds/score_add.wav', False)
            self.max += trickScore
            self.capped = False
            self.tricks += 1
        # Add to score until score reaches the current points
        if self.score < self.max:
            if self.max < 100000:
                self.score += 123
            else: self.score += 589 # speeds up when over 100k
            # check if cap is reached
            if self.score >= self.max:
                play_sound('Assets/Sounds/score_add.wav', True)
                # frame flag for reaching cap
                if not self.capped:
                    self.score = self.max
                    self.initCap = self.game.framecount
                    self.capped = True
        # if capped and waited 2 seconds and no new score, reset
        elif self.capped:
            if self.game.framecount-self.initCap >= 60*2: # breaks on new scene?
                self.max = 0
                self.score = 0
                self.tricks = 0
                self.capped = False
        if self.max != 0:
            self.r = 105 + (self.tricks*50)
            if self.r > 255: self.r = 255
            draw_text(self.game.screen, str(self.score), (player_x+300, player_y-50), (self.r,255-self.r,0), 75+(self.tricks*2))


class Wind:
    def __init__(self, game):
        self.game = game
        self.x = random.randint(1920, 4000)
        self.y = random.randint(300, 1070)

    def update(self):
        if self.x < -100:
            self.x = random.randint(1920, 4000)
            self.y = random.randint(300, 1070)
        self.x -= 50
        # add slight y variation
        self.y += random.randint(-1,1)

    def draw(self):
        pygame.draw.rect(self.game.screen, (155, 155, 155), (self.x,self.y,150,1))


class Pebble:
    def __init__(self, game):
        self.game = game
        self.x = random.randint(0, 4000)
        self.y = random.randint(950, 1080)

    def update(self):
        if self.x < -100:
            self.x = random.randint(1920, 4000)
            self.y = random.randint(950, 1080)
        self.x -= 25

    def draw(self):
        pygame.draw.rect(self.game.screen, (0,0,0), (self.x,self.y,5,5))