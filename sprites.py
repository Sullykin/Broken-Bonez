import pygame
from utils import get_image

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
            if self.rect.colliderect(self.game.obstacle.rect):
                if self.onRamp == False:
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
            self.game.blit_bg = self.game.bgnh
            if self.x < 1920-200-self.rect.w:
                self.x += 2
            self.isJumping = True
        # landing
        elif self.y < 800 and self.game.framecount - self.initJump >= (5*60)+40:
            self.game.blit_bg = self.game.bg
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


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, game):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.x = 2500
        self.y = 735
        self.image = get_image('Assets/Images/obstacle.png')
        self.rect = self.image.get_rect()
        self.rect.y = self.y

    def update(self):
        self.x -= 25
        self.rect.x = self.x
        if self.x < -800:
            self.x = 10000

    def draw(self):
        self.game.screen.blit(self.image, (self.x, self.y))