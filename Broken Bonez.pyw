import pygame
import string
import random
import sys
import os
import time
from datetime import datetime

# make tricks into mash a letter & hold an arrow key
# fork a branch for different points system (chicken)
    # mash a button to build up points in the air
    # risk grows as time passes
# 1branch for diff main menus
# branch for getting a couple thousand points per trick to be more realistic
# display rank at gameover if highscore
# cheats - Enter code to unlock new;Background, soundtrack, effects, secret trick, audio quotes form characters, etc.
# rigby achievement: special secret trick for tapping two buttons back and forth
# use button mashing to accumulate points directly; have tricks assocaited with points ranges
    # or have them mash a button aas much as they can while the animation is playing
    # use left and right arrow keys ?

# Version 1.2.1
    # limited highscore entries to 5 instead of 10
    # entries at the bottom are replaced if the leaderboard is full
    # fixed player entering jump phase outside of main loop
    # fixed no HUD before first jump when replaying
    # New achievement
    # New extras
    # score no wait time afterwards if animation reactivated
# 'partytime'
# 'duckpower'
# 'rig juice'
# make drawtext for unlocks

    
white = (255,255,255)
black = (0)
date = datetime.date(datetime.now())

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 1, 512) # reduces audio latency
        pygame.init()
        pygame.mixer.music.load('Assets/Sounds/bgMusic.mp3')
        pygame.mixer.music.play(-1) # loop music
        # Fetch settings
        with open('Assets/Misc/settings.txt','r') as f:
            savedSettings = f.readlines()
        self.windowMode = savedSettings[0]
        if self.windowMode == 'RESIZABLE\n':
            self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        else: self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.volume = float(savedSettings[1])
        pygame.mixer.music.set_volume(self.volume)
        pygame.display.set_icon(get_image('Assets/Images/bbm.png')) # sets window icon
        pygame.display.set_caption('Broken Bones') # sets window title
        self.bg = get_image('Assets/Images/bbBG.png')
        self.bgnh = get_image('Assets/Images/bbBGnoHUD.png')
        self.blit_bg = self.bg
        # Fetch achievements
        self.achievements = []
        with open('Assets/Misc/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        self.highscore, self.entries = getScores()
        self.clock = pygame.time.Clock()


    def mainMenu(self):
        try: play_sound('Assets/Sounds/score_add.wav', True)
        except: pass
        self.framecount = 0
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # object initialization
        self.scoreDisplay = Score()
        self.player = Player()
        self.windlines = []
        for x in range(10):
            self.windlines.append(Wind())
        self.pebbles = []
        for x in range(10):
            self.pebbles.append(Pebble())
        buttons = [Button((1920//2-(418//2))-300, 1080//2+200, 'SETTINGS'),
                   Button((1920//2-(418//2))+300, 1080//2+200, 'QUIT'),
                   Button((1920//2-(418//2))+300, 1080//2+50, 'LEADERBOARD'),
                   Button((1920//2-(418//2))-300, 1080//2+50, 'ACHIEVEMENTS')]
        
        while True:
            self.framecount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.play(2)
                for button in buttons:
                    button.update(event)
                    
            # call updates on all objects
            for line in self.windlines:
                line.update()
            for pebble in self.pebbles:
                pebble.update()

            # Environment
            self.screen.blit(self.blit_bg, (0,0)) # background
            for pebble in self.pebbles:
                pebble.draw()
            for line in self.windlines:
                line.draw()
            self.player.draw()
            # HUD
            pygame.draw.rect(self.screen, black, (0,0,1920,265))
            drawText('BROKEN BONEZ', 220, 1920//2, 130, (255,255,0), 'Assets/Misc/ipaexg.ttf')
            drawText('PRESS SPACE TO START', 100, 1920//2, 1080//2-120, black)
            for button in buttons:
                button.draw()
        
            pygame.display.flip()
            self.clock.tick(60)


    def play(self, lives, score=0, timeLeft=60):
        self.blit_bg = self.bg
        # frame counting for animation
        self.framecount = 0
        self.animations = []
        # mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        # object initialization
        self.player = Player()
        self.obstacle = Obstacle()
        self.windlines = []
        for x in range(10):
            self.windlines.append(Wind())
        self.pebbles = []
        for x in range(10):
            self.pebbles.append(Pebble())
        # trick flags & vars
        trick_key = random.choice(string.ascii_uppercase)
        req = random.choice([3,5,7])
        multiplierFlag = False
        multiplier = 1
        tricks = 0
        trick = False
        trickScore = None
        crash = False
        self.frameJumped = None
        
        while True:
            self.framecount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.settings(False)
                    elif self.player.isJumping and len(self.animations) == 0:
                        if pygame.key.name(event.key).upper() == trick_key:
                            self.player.trickcount += 1
                            # trick complete
                            if self.player.trickcount >= req:
                                multiplierFlag = True
                                trick_key = ''
                                if req == 7: trick = Trick(self.framecount, 4, trick3animation, 27000)
                                elif req == 5: trick = Trick(self.framecount, 10, trick2animation, 23000)
                                else: trick = Trick(self.framecount, 15, trick1animation, 19000)
                                self.animations.append(trick)
                        # wrong key pressed
                        else:
                            crash = Crash(self.framecount, [30,40,80], crashAnimation)
                            self.animations.append(crash)
            
            # call updates on all objects
            self.player.update()
            for line in self.windlines:
                line.update()
            for pebble in self.pebbles:
                pebble.update()
            self.obstacle.update()

            # in air
            if self.player.isJumping:
                if self.frameJumped == None: self.frameJumped = self.framecount
                # check multiplier
                if (self.framecount-self.frameJumped) % (60*3) == 0 and tricks < 3:
                    # reset trick
                    trick_key = random.choice(string.ascii_uppercase)
                    self.player.trickcount = 0
                    req = random.choice([3,5,7])
                    if multiplierFlag:
                        multiplierFlag = False
                        if multiplier < 5:
                            multiplier += 1
                    else:
                        multiplier = 1
            else:
                tricks = 0
                self.frameJumped = None
                    
            # animations
            if len(self.animations) > 0:
                self.animations[0].animate(self.framecount)
                
                if trick in self.animations:
                    if trick.done:
                        tricks += 1
                        trickScore = trick.base_score*multiplier
                        score += trickScore
                        self.animations.remove(trick)
                        trick = False
                            

                elif crash in self.animations:
                    self.blit_bg = self.bg
                    if crash.done:
                        if lives == 0:
                            self.gameOver(score)
                        else:
                            lives -= 1
                            score -= 10000
                            self.play(lives, score, timeLeft)
                        self.animations.remove(crash)
                    
            # time
            if self.framecount % 60 == 0:
                timeLeft -= 1
                if timeLeft == 0:
                    self.gameOver(score)

            # render things to the screen
            self.screen.blit(self.blit_bg, (0,0))
            # Environment
            for pebble in self.pebbles:
                pebble.draw()
            for line in self.windlines:
                line.draw()
            self.obstacle.draw()
            self.player.draw()
            # HUD
            if not self.player.isJumping or crash != False:
                drawText('PLAYER 1', 50, 350, 50)
                drawText(str(score), 50, 350, 125)
                drawText('HI-SCORE', 50, 950, 50)
                drawText(str(highscores[0]), 50, 950, 125)
                drawText(str(timeLeft), 50, 1870, 220, black)
                for x in range(multiplier):
                    self.screen.blit(get_image('Assets/Images/bones.png'), ((135*x)+1200, 30))
                for x in range(lives):
                    self.screen.blit(get_image('Assets/Images/helmet.png'), ((100*x)+20, 1000))
            else:
                # key to press
                if len(self.animations) == 0 and trick_key != '':
                    self.screen.blit(get_image('Assets/Images/blank_key.png'), (self.player.x-25,220))
                    drawText(trick_key, 25, self.player.x-25+24, 220+20, black)
                # theater mode borders
                pygame.draw.rect(self.screen, black, (0,0,1920,140))
                pygame.draw.rect(self.screen, black, (0,1080-500,1920,500))
            # Trick count and score
            self.scoreDisplay.animate(trickScore)
            trickScore = None
            if 0 < self.player.trickcount < req:
                self.screen.blit(get_image('Assets/Images/countBubble.png'), (self.player.x-195, self.player.y-140))
                drawText(str(self.player.trickcount), 75, self.player.x-100, self.player.y-50, black)

            pygame.display.flip()
            self.clock.tick(60)


    def gameOver(self, score):
        self.score = score
        if self.score < 0: self.achievements[0] = 1
        if self.score >= 1279000: self.achievements[1] = 1
        if self.score >= 1300000: self.achievements[2] = 1
        with open('Assets/Misc/achievements.txt', 'w') as f:
            f.write(str(self.achievements[0]) + '\n' + str(self.achievements[1]) + '\n' + str(self.achievements[2]) + '\n')
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # initials
        self.blanks = ['_', '_', '_']
        # object initialization
        self.player = Player()
        self.windlines = []
        for x in range(10):
            self.windlines.append(Wind())
        self.pebbles = []
        for x in range(10):
            self.pebbles.append(Pebble())
        buttons = [Button((1920//2-(418//2))-300, 1080//2+250, 'MAIN MENU'), Button((1920//2-(418//2))+300, 1080//2+250, 'QUIT')]
        if any(i < self.score for i in highscores) or len(self.entries) < 5: buttons.append(Button(1920//2-(418//2), 1080//2+100, 'SUBMIT'))

        while True:
            self.framecount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    # initials input
                    if any(i < self.score for i in highscores) or len(self.entries) < 5:
                        blanks_num = self.blanks.count('_')
                        if event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                            self.blanks = ['_','_','_']
                        elif blanks_num > 0 and pygame.key.name(event.key).lower() in string.ascii_lowercase:
                            self.blanks[3-blanks_num] = pygame.key.name(event.key).upper()
                        elif event.key == pygame.K_RETURN:
                            with open('Assets/Misc/highscores.txt', 'a') as f:
                                f.write(self.blanks[0]+self.blanks[1]+self.blanks[2]+'     '+str(self.score)+'     '+str(date)+'\n')
                            self.mainMenu()

                for button in buttons:
                    button.update(event)

            # call updates on all objects
            for line in self.windlines:
                line.update()
            for pebble in self.pebbles:
                pebble.update()

            # render things to the screen
            self.screen.blit(self.bg, (0,0))
            # HUD
            drawText('PLAYER 1', 50, 350, 50)
            drawText(str(self.score), 50, 350, 125)
            drawText('HI-SCORE', 50, 950, 50)
            drawText(str(highscores[0]), 50, 950, 125)
            if any(i < self.score for i in highscores) or len(self.entries) < 5:
                if len(self.entries) == 5:
                    with open('Assets/Misc/highscores.txt', 'r') as f:
                        lines = f.readlines()
                        lines = lines[:-1]
                    with open('Assets/Misc/highscores.txt', 'w') as f:
                        for line in lines:
                            f.write(line)
                    self.highscore, self.entries = getScores()
                drawText('NEW HI-SCORE!', 150, 1920//2, 1080//2-260, black)
                i = -125
                for blank in self.blanks:
                    drawText(blank, 120, 1920//2+i, 1080//2+20)
                    i += 125
                drawText(str(self.score), 150, 1920//2, 1080//2-120, (255,0,0))
            else:
                drawText('GAMEOVER', 150, 1920//2, 1080//2-200, (255,0,0))
                drawText(str(self.score), 150, 1920//2, 1080//2-25, 150)
            self.screen.blit(get_image('Assets/Images/bones.png'), (1200, 30))
            if self.score < 0: self.screen.blit(get_image('Assets/Images/ach1.png'), (1920-300,1080-75))
            if self.score >= 1279000: self.screen.blit(get_image('Assets/Images/ach2.png'), (1920-300,1080-75))
            if self.score >= 1300000: self.screen.blit(get_image('Assets/Images/ach3.png'), (1920-300,1080-155))
            try: self.scoreDisplay.animate(None)
            except: pass
            # Environment
            for pebble in self.pebbles:
                pebble.draw()
            for line in self.windlines:
                line.draw()
            self.player.draw()
            for button in buttons:
                button.draw()

            pygame.display.flip()
            self.clock.tick(60)


    def leaderboard(self):
        # refresh scores
        self.highscore, self.entries = getScores()
        button = Button((1920//2-(400//2)), 900, 'BACK')
        self.paused = True
        while self.paused:
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                button.update(event)

            self.screen.fill(black)
            drawText('HI-SCORES', 100, 1920//2, 80)
            for entry in self.entries:
                drawText(entry, 60, 1920//2-360, 220+(80*self.entries.index(entry)), white, 'Assets/Misc/ipaexg.ttf', False)
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)


    def achievementsMenu(self):
        # refresh achievements
        self.achievements = []
        with open('Assets/Misc/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        button = Button((1920//2-(400//2)), 900, 'BACK')
        self.paused = True
        while self.paused:
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                button.update(event)

            self.screen.fill(black)
            count = 0
            for entry in self.achievements:
                count += 1
                pygame.draw.rect(self.screen, (120,120,120), (1920//2-154,-5+(100*count),310,85))
                if entry:
                    self.screen.blit(get_image('Assets/Images/ach'+str(count)+'.png'), (1920//2-150, 100*count))
                else:
                    self.screen.blit(get_image('Assets/Images/ach'+str(count)+'locked.png'), (1920//2-150, 100*count))
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)
        

    def settings(self, mainmenu=True):
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        self.cheatCode = ''
        canClick = True
        if mainmenu: buttons = [Button((1920//2-(400//2)), 900, 'BACK')]
        else: buttons = [Button((1920//2-(400//2)-300), 900, 'BACK'),
                         Button((1920//2-(400//2))+300, 900, 'MAIN MENU')]
        options = [Option('FULLSCREEN', (725, 185)),
                   Option('WINDOWED', (1025, 185)),
                   Option('TOGGLE MUTE', (725, 385)),
                   Option('-', (1050, 385)),
                   Option('+', (1150, 385))]
        input_box1 = InputBox(725, 580, 140, 32)
        input_boxes = [input_box1]
        
        self.paused = True
        while self.paused:
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                for button in buttons:
                    button.update(event)
                for box in input_boxes:
                    box.handle_event(event)
                    
            for box in input_boxes:
                box.update()
            if self.cheatCode != '':
                if self.cheatCode == 'all nighter':
                    self.bg = get_image('Assets/Images/bbBGnight.png')
                    self.bgnh = get_image('Assets/Images/bbBGnoHUDnight.png')
                    self.blit_bg = self.bg
                self.cheatCode = ''
                
            for option in options:
                if option.rect.collidepoint(pygame.mouse.get_pos()):
                    option.hovered = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                   
                        if option.text == 'FULLSCREEN':
                            self.windowMode = 'FULLSCREEN\n'
                            self.screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
                        elif option.text == 'WINDOWED':
                            self.windowMode = 'RESIZABLE\n'
                            self.screen = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
                        with open('Assets/Misc/settings.txt', 'w') as f:
                            f.write(self.windowMode + str(self.volume))

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if canClick:
                            if option.text == '-':
                               self.volume = pygame.mixer.music.get_volume()-0.1
                               pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()-0.1)
                            elif option.text == '+':
                               self.volume = pygame.mixer.music.get_volume()+0.1
                               pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()+0.1)
                            if option.text == 'TOGGLE MUTE':
                                if self.volume > 0:
                                    self.volume = 0
                                    pygame.mixer.music.set_volume(0)
                                else:
                                    self.volume = 0.5
                                    pygame.mixer.music.set_volume(0.5)
                            if self.volume < 0:
                                self.volume = 0
                            elif self.volume > 1:
                                self.volume = 1
                            with open('Assets/Misc/settings.txt', 'w') as f:
                                f.write(self.windowMode + str(self.volume))
                            canClick = False
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        canClick = True
                else:
                    option.hovered = False

            self.screen.fill(black)
            drawText('VIDEO', 50, 300, 200)
            drawText('AUDIO', 50, 300, 400)
            drawText('EXTRA', 50, 300, 600)
            drawText(str(int((self.volume+0.05)*10)*10), 30, 1110, 400)
            for button in buttons:
                button.draw()
            for box in input_boxes:
                box.draw(self.screen)
            for option in options:
                option.draw()
            pygame.display.flip()
            self.clock.tick(60)
            

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
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
            if self.rect.colliderect(game.obstacle.rect):
                if self.onRamp == False:
                    self.onRamp = True
                    self.image = pygame.transform.rotate(self.image, 23)
            elif self.onRamp: # Update this flag to false
                self.onRamp = False
                self.initJump = game.framecount
        except: pass
            
        if self.onRamp or game.framecount - self.initJump <= 30:
            self.y -= 10
        # jumping
        elif game.framecount - self.initJump < 10*60:
            game.blit_bg = game.bgnh
            if self.x < 1920-200-self.rect.w:
                self.x += 2
            self.isJumping = True
        # landing
        elif self.y < 800 and game.framecount - self.initJump >= (5*60)+40:
            game.blit_bg = game.bg
            self.isJumping = False
            self.trickcount = 0
            self.y += 10
            self.x = 200
        if self.y == 800:
            self.image = get_image('Assets/Images/bbm.png')
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        game.screen.blit(self.image, (self.x, self.y))


class Animation:
    def __init__(self, initFrame, interval, animation):
        self.initFrame = initFrame
        self.interval = interval*2
        self.animation = animation
        self.count = -1
        self.done = False


class Trick(Animation):
    def __init__(self, initFrame, interval, animation, base_score):
        super().__init__(initFrame, interval, animation)
        self.base_score=base_score

    def animate(self, framecount):
        if (framecount - self.initFrame) % self.interval == 0:
            if self.count == len(self.animation)-1:
                self.done = True
            else: self.count += 1
        game.player.image = get_image(self.animation[self.count])


class Crash(Animation):
    def __init__(self, initFrame, interval, animation):
        super().__init__(initFrame, interval, animation)
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
        game.player.image = get_image(self.animation[self.count+1])
        game.player.y = 900
        game.player.x -= 2
        game.obstacle.x = 10000
        for pebble in game.pebbles:
            pebble.x += 25


class Score:
    def __init__(self):
        self.max = 0
        self.score = 0
        self.tricks = 0
        self.capped = False

    def animate(self, trickScore=None):
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
                    self.initCap = game.framecount
                    self.capped = True
        # if capped and waited 2 seconds and no new score, reset
        elif self.capped:
            if game.framecount-self.initCap >= 60*2: # breaks on new scene?
                self.max = 0
                self.score = 0
                self.tricks = 0
                self.capped = False
        if self.max != 0:
            self.r = 105+(self.tricks*50)
            if self.r > 255: self.r = 255
            drawText(str(self.score), 75+(self.tricks*2), game.player.x+300, game.player.y-50, (self.r,255-self.r,0))


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
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
        game.screen.blit(self.image, (self.x, self.y))


class Wind:
    def __init__(self):
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
        pygame.draw.rect(game.screen, (155, 155, 155), (self.x,self.y,150,1))


class Pebble:
    def __init__(self):
        self.x = random.randint(0, 4000)
        self.y = random.randint(950, 1080)

    def update(self):
        if self.x < -100:
            self.x = random.randint(1920, 4000)
            self.y = random.randint(950, 1080)
        self.x -= 25

    def draw(self):
        pygame.draw.rect(game.screen, black, (self.x,self.y,5,5))


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.text = text
        self.image = get_image('Assets/Images/button0.png')
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.soundFlag = False
        self.showBorder = False
        self.size = 40

    def update(self, event):
        # update flags for glow and mouseover
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
                elif self.text == 'LEADERBOARD':
                    game.leaderboard()
                elif self.text == 'BACK':
                    game.paused = False
                elif self.text == 'MAIN MENU':
                    game.mainMenu()
                elif self.text == 'ACHIEVEMENTS':
                    game.achievementsMenu()
                elif self.text == 'SETTINGS':
                    game.settings()
                elif self.text == 'SUBMIT' and not bool(game.blanks.count('_')):
                    with open('Assets/Misc/highscores.txt', 'a') as f:
                        f.write(game.blanks[0]+game.blanks[1]+game.blanks[2]+'     '+str(game.score)+'     '+str(date)+'\n')
                    game.mainMenu()
        else:
            self.showBorder = False
            self.soundFlag = True

    def draw(self):
        if self.showBorder:
            game.screen.blit(get_image("Assets/Images/limeborder.png"), (self.x-3, self.y-3))
        game.screen.blit(self.image, self.rect)
        drawText(self.text, self.size, self.x+200, self.y+55, black)


class Option:
    hovered = False
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.set_rect()
        self.draw()
            
    def draw(self):
        self.set_rend()
        game.screen.blit(self.rend, self.rect)
        
    def set_rend(self):
        self.rend = menu_font.render(self.text, True, self.get_color())
        
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
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
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
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    game.cheatCode = self.text
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        game.screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(game.screen, self.color, self.rect, 2)
        

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


def drawText(text, size, x, y, color=white, fontstr='freesansbold.ttf', center=True):
    font = pygame.font.Font(fontstr, size)
    text = font.render(text, True, color)
    if center: game.screen.blit(text, (x - (text.get_width() // 2), y - (text.get_height() // 2)))
    else: game.screen.blit(text, (x,y))


def getScores():
    # read highscore entries, put scores in a list and the whole entry in another, all sorted
    global highscores
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
    if len(highscores) == 0:
        highscores = [0]
        highScore = 0
    else: highScore = highscores[-1]
    return highScore, entries


def checkForQuit(event, pressed_keys):
    quit_attempt = False
    if event.type == pygame.QUIT:
        quit_attempt = True
    # keydown events
    elif event.type == pygame.KEYDOWN:
        alt_pressed = pressed_keys[pygame.K_LALT] or \
                        pressed_keys[pygame.K_RALT]
        # alt + f4
        if event.key == pygame.K_F4 and alt_pressed:
            quit_attempt = True
    if quit_attempt:
        pygame.quit()
        sys.exit()
        

trick1animation = ['Assets/Animations/trick1/1.png',
                   'Assets/Animations/trick1/2.png',
                   'Assets/Images/bbm.png']

trick2animation = ['Assets/Animations/trick2/1.png',
                   'Assets/Animations/trick2/2.png',
                   'Assets/Animations/trick2/3.png',
                   'Assets/Images/bbm.png']

trick3animation = ['Assets/Animations/trick3/1.png',
                   'Assets/Animations/trick3/2.png',
                   'Assets/Animations/trick3/3.png',
                   'Assets/Animations/trick3/4.png',
                   'Assets/Animations/trick3/5.png',
                   'Assets/Animations/trick3/6.png',
                   'Assets/Animations/trick3/7.png',
                   'Assets/Images/bbm.png']

crashAnimation = ['Assets/Animations/crash/1.png',
                  'Assets/Animations/crash/2.png',
                  'Assets/Animations/crash/2.png']
game = Game()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
menu_font = pygame.font.Font(None, 40)
game.mainMenu()
