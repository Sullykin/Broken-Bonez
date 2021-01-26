import pygame, sys, os, random, time, string
from datetime import datetime

# cheats - Enter code to unlock new;Background, soundtrack, effects, secret trick, audio quotes form characters, etc.
# rigby achievement: special secret trick for tapping two buttons back and forth

# Version 1.1.0
    # make the points accumulate with time
    # subclass tricks/crashes as animations
    # refresh achs/leaderboard
# combnie wind/pebbles into environment class ?
# play a game of chicken with the player for points
# sidetrack: search more andora music
# drop player smoothly on landing
# submit initials button
# make tricks into mash a letter & hold an arrow key

white = (255,255,255)
black = (0)

date = datetime.date(datetime.now())

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 1, 512) # reduces audio latency
        pygame.init()
        pygame.mixer.music.load('Assets/bgMusic.mp3')
        pygame.mixer.music.play(-1) # loop music
        # Fetch settings
        with open('Assets/settings.txt','r') as f:
            savedSettings = f.readlines()
        self.windowMode = savedSettings[0]
        if self.windowMode == 'RESIZABLE\n':
            self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        else: self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.volume = float(savedSettings[1])
        pygame.mixer.music.set_volume(self.volume)
        pygame.display.set_icon(get_image('Assets/bbm.png')) # sets window icon
        pygame.display.set_caption('Broken Bones') # sets window title
        self.bg = get_image('Assets/bbBG.png')
        self.bgnh = get_image('Assets/bbBGnoHUD.png')
        self.blit_bg = self.bg
        # Fetch achievements
        self.achievements = []
        with open('Assets/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        self.highscore, self.entries = getScores()
        self.clock = pygame.time.Clock()


    def mainMenu(self):
        self.framecount = 0
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # object initialization
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
                        self.play(3)
                for button in buttons:
                    button.update(event)
                    
            # call updates on all objects
            self.player.update()
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
            drawText('BROKEN BONEZ', 220, 1920//2, 130, (255,255,0), 'Assets/ipaexg.ttf')
            drawText('PRESS SPACE TO START', 100, 1920//2, 1080//2-120, black)
            for button in buttons:
                button.draw()
        
            pygame.display.flip()
            self.clock.tick(60)


    def play(self, lives, score=0, timeLeft=60):
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
        self.scoreDisplay = Score()
        # trick flags & vars
        trick_key = random.choice(string.ascii_uppercase)
        req = random.choice([3,5,7])
        multiplierFlag = False
        multiplier = 1
        trick = False
        trickScore = None
        crash = False
        
        while True:
            self.framecount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if self.player.isJumping and len(self.animations) == 0:
                        if pygame.key.name(event.key).upper() == trick_key:
                            self.player.trickcount += 1
                            # trick complete
                            if self.player.trickcount >= req:
                                multiplierFlag = True
                                trick_key = ''
                                if req == 7: trick = Trick(self.framecount, 4, trick3animation, 15000)
                                elif req == 5: trick = Trick(self.framecount, 10, trick2animation, 10000)
                                else: trick = Trick(self.framecount, 15, trick1animation, 5000)
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
                # check multiplier
                if (self.framecount-(self.player.initJump+200)) % (60*3) == 0:
                    # reset trick
                    trick_key = random.choice(string.ascii_uppercase)
                    self.player.trickcount = 0
                    req = random.choice([3,5,7])
                    if multiplierFlag:
                        multiplierFlag = False
                        if multiplier < 5:
                            multiplier += 1
                    else: multiplier = 1

            # animations
            if len(self.animations) > 0:
                self.animations[0].animate(self.framecount)
                
                if trick in self.animations:
                    if trick.done:
                        trickScore = trick.base_score*multiplier
                        score += trickScore
                        self.animations.remove(trick)
                        trick = False

                elif crash in self.animations:
                    self.bg = get_image('Assets/bbBG.png')
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
                drawText(str(self.highscore), 50, 950, 125)
                drawText(str(timeLeft), 50, 1870, 220, black)
                for x in range(multiplier):
                    self.screen.blit(get_image('Assets/bones.png'), ((135*x)+1200, 30))
                for x in range(lives):
                    self.screen.blit(get_image('Assets/helmet.png'), ((100*x)+20, 1000))
            else:
                # key to press
                if len(self.animations) == 0 and trick_key != '':
                    self.screen.blit(get_image('Assets/blank_key.png'), (self.player.x-25,220))
                    drawText(trick_key, 25, self.player.x-25+24, 220+20, black)
                # theater mode borders
                pygame.draw.rect(self.screen, black, (0,0,1920,140))
                pygame.draw.rect(self.screen, black, (0,1080-500,1920,500))
            # Trick count and score
            self.scoreDisplay.animate(trickScore)
            trickScore = None
            if 0 < self.player.trickcount < req:
                self.screen.blit(get_image('Assets/countBubble.png'), (self.player.x-195, self.player.y-140))
                drawText(str(self.player.trickcount), 75, self.player.x-100, self.player.y-50)

            pygame.display.flip()
            self.clock.tick(60)


    def gameOver(self, score):
        if score < 0: self.achievements[0] = 1
        if score >= 1279000: self.achievements[1] = 1
        if score >= 1300000: self.achievements[2] = 1
        with open('Assets/achievements.txt', 'w') as f:
            f.write(str(self.achievements[0]) + '\n' + str(self.achievements[1]) + '\n' + str(self.achievements[2]) + '\n')

        buttons = [Button((1920//2-(418//2))-300, 1080//2+250, 'MAIN MENU'), Button((1920//2-(418//2))+300, 1080//2+250, 'QUIT')]
        # frame counting for animation
        self.framecount = 0
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # initials
        blanks = ['_', '_', '_']
        # object initialization
        self.player = Player()
        self.windlines = []
        for x in range(10):
            self.windlines.append(Wind())
        self.pebbles = []
        for x in range(10):
            self.pebbles.append(Pebble())
        
        while True:
            self.framecount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    # initials input
                    if score >= self.highscore:
                        blanks_num = blanks.count('_')
                        if event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                            blanks = ['_','_','_']
                        elif blanks_num > 0 and pygame.key.name(event.key).lower() in string.ascii_lowercase:
                            blanks[3-blanks_num] = pygame.key.name(event.key).upper()
                        elif event.key == pygame.K_RETURN:
                            with open('Assets/highscores.txt', 'a') as f:
                                f.write(blanks[0]+blanks[1]+blanks[2]+'     '+str(score)+'     '+str(date)+'\n')
                            game.mainMenu()

                for button in buttons:
                    button.update(event)

            # call updates on all objects
            self.player.update()
            for line in self.windlines:
                line.update()
            for pebble in self.pebbles:
                pebble.update()

            # render things to the screen
            self.screen.blit(self.bg, (0,0))
            # HUD
            drawText('PLAYER 1', 50, 350, 50)
            drawText(str(score), 50, 350, 125)
            drawText('HI-SCORE', 50, 950, 50)
            drawText(str(self.highscore), 50, 950, 125)
            if score >= self.highscore:
                drawText('NEW HI-SCORE!', 150, 1920//2, 1080//2-200)
                i = -125
                for blank in blanks:
                    drawText(blank, 150, 1920//2+i, 1080//2+150)
                    i += 125
            else:
                drawText('GAMEOVER', 150, 1920//2, 1080//2-200, (255,0,0))
            drawText(str(score), 150, 1920//2, 1080//2-25, 150)
            self.screen.blit(get_image('Assets/bones.png'), (1200, 30))
            if score < 0: self.screen.blit(get_image('Assets/ach1.png'), (1920-300,1080-75))
            if score >= 1279000: self.screen.blit(get_image('Assets/ach2.png'), (1920-300,1080-75))
            if score >= 1300000: self.screen.blit(get_image('Assets/ach3.png'), (1920-300,1080-155))
            self.scoreDisplay.animate(None)
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
        while True:
            # process user input
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                button.update(event)

            self.screen.fill(black)
            drawText('HI-SCORES', 100, 1920//2, 80)
            for x in range(len(self.entries)):
                drawText(str(self.entries[x]), 60, 1920//2, 220+(80*x), white, 'Assets/ipaexg.ttf')
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)


    def achievementsMenu(self):
        # refresh achievements
        self.achievements = []
        with open('Assets/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        button = Button((1920//2-(400//2)), 900, 'BACK')
        while True:
            # process user input
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                button.update(event)

            self.screen.fill(black)
            count = 0
            for entry in self.achievements:
                count += 1
                pygame.draw.rect(self.screen, (120,120,120), (1920//2-154,-5+(100*count),310,85))
                if entry:
                    self.screen.blit(get_image('Assets/ach'+str(count)+'.png'), (1920//2-150, 100*count))
                else:
                    self.screen.blit(get_image('Assets/ach'+str(count)+'locked.png'), (1920//2-150, 100*count))
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)
        

    def settings(self):
        self.cheatCode = ''
        canClick = True
        button = Button((1920//2-(400//2)), 900, 'BACK')
        options = [Option('FULLSCREEN', (725, 185)),
                   Option('WINDOWED', (1025, 185)),
                   Option('TOGGLE MUTE', (725, 385)),
                   Option('-', (1050, 385)),
                   Option('+', (1150, 385))]
        input_box1 = InputBox(725, 580, 140, 32)
        input_boxes = [input_box1]
        while True:
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                button.update(event)
                for box in input_boxes:
                    box.handle_event(event)
                    
            for box in input_boxes:
                box.update()
            if self.cheatCode != '':
                if self.cheatCode == 'all nighter':
                    self.bg = get_image('Assets/bbBGnight.png')
                    self.bgnh = get_image('Assets/bbBGnoHUDnight.png')
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
                        with open('Assets/settings.txt', 'w') as f:
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
                                    pygame.mixer.music.play(-1)
                            if self.volume < 0:
                                self.volume = 0
                            elif self.volume > 1:
                                self.volume = 1
                            with open('Assets/settings.txt', 'w') as f:
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
        self.image = get_image('Assets/bbm.png')
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
            self.image = get_image('Assets/bbm.png')
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
                play_sound('Assets/crash.wav')
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

    def animate(self, trickScore=None):
        if trickScore != None:
            if self.score == self.max:
                play_sound('Assets/score_add.wav', False)
            self.max += trickScore
            self.tricks += 1
        if self.score < self.max:
            if self.max < 100000:
                self.score += 123
            else: self.score += 789
            if self.score >= self.max:
                play_sound('Assets/score_add.wav', True)
                self.max = 0
                self.score = 0
                self.tricks = 0
        if self.max != 0:
            self.r = 100+(self.tricks*2)
            if self.r > 255: self.r = 255
            drawText(str(self.score), 75+(self.tricks*2), game.player.x+300, game.player.y-50, (100+(self.tricks*30),200-(self.tricks*30),0))


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.text = text
        self.image = get_image('Assets/button0.png')
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
                play_sound('Assets/mouseover.wav')
            self.soundFlag = False
            self.showBorder = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_sound('Assets/select.wav')
                if self.text == 'QUIT':
                    pygame.quit()
                    sys.exit()
                elif self.text == 'LEADERBOARD':
                    game.leaderboard()
                elif self.text == 'BACK':
                    game.mainMenu()
                elif self.text == 'MAIN MENU':
                    game.mainMenu()
                elif self.text == 'ACHIEVEMENTS':
                    game.achievementsMenu()
                elif self.text == 'SETTINGS':
                    game.settings()
        else:
            self.showBorder = False
            self.soundFlag = True

    def draw(self):
        if self.showBorder:
            game.screen.blit(get_image("Assets/limeborder.png"), (self.x-3, self.y-3))
        game.screen.blit(self.image, self.rect)
        drawText(self.text, self.size, self.x+200, self.y+55, black)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 2500
        self.y = 735
        self.image = get_image('Assets/obstacle.png')
        self.rect = self.image.get_rect()
        self.rect.y = self.y

    def update(self):
        self.x -= 25
        self.rect.x = self.x
        if self.x < -800:
            self.x = random.randint(9500, 11750)

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


def drawText(text, size, x, y, color=white, fontstr='freesansbold.ttf'):
    font = pygame.font.Font(fontstr, size)
    text = font.render(text, True, color)
    game.screen.blit(text, (x - (text.get_width() // 2), y - (text.get_height() // 2)))


def getScores():
    # read highscore entries, put scores in a list and the whole entry in another, all sorted
    highscores = []
    with open('Assets/highscores.txt','r') as f:
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
    try:
        highScore = highscores[-1]
    except:
        highScore = 0
    return highScore, entries


def checkForQuit(event, pressed_keys):
    quit_attempt = False
    if event.type == pygame.QUIT:
        quit_attempt = True
    # keydown events
    elif event.type == pygame.KEYDOWN:
        alt_pressed = pressed_keys[pygame.K_LALT] or \
                        pressed_keys[pygame.K_RALT]
        # esc
        if event.key == pygame.K_ESCAPE:
            quit_attempt = True
        # alt + f4
        elif event.key == pygame.K_F4 and alt_pressed:
            quit_attempt = True
    if quit_attempt:
        pygame.quit()
        sys.exit()
        

trick1animation = ['Assets/Animations/trick1.1.png',
                   'Assets/Animations/trick1.2.png',
                   'Assets/bbm.png']

trick2animation = ['Assets/Animations/trick2.1.png',
                   'Assets/Animations/trick2.2.png',
                   'Assets/Animations/trick2.3.png',
                   'Assets/bbm.png']

trick3animation = ['Assets/Animations/trick3.1.png',
                   'Assets/Animations/trick3.2.png',
                   'Assets/Animations/trick3.3.png',
                   'Assets/Animations/trick3.4.png',
                   'Assets/Animations/trick3.5.png',
                   'Assets/Animations/trick3.6.png',
                   'Assets/Animations/trick3.7.png',
                   'Assets/bbm.png']

crashAnimation = ['Assets/Animations/crash1.1.png',
                  'Assets/Animations/crash1.2.png',
                  'Assets/Animations/crash1.2.png']
game = Game()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
menu_font = pygame.font.Font(None, 40)
game.mainMenu()
