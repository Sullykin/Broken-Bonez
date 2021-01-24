import pygame, sys, os, random, time
from datetime import datetime

# doing tricks in a row builds multiplier
# not doing a trick removes all multipliers
# no trick twice in a row = crash & lost life

# cheats - Enter code to unlock new;Background, soundtrack, effects, secret trick, audio quotes form characters, etc.
# rigby achievement: special secret trick for tapping two buttons back and forth

# fps bug // fixed? no

# Version 1.0.2
    # Fixed bubbles not showing up at the reduced difficulty trick counts
    # Mouse is no longer visible in-game

# combnie wind/pebbles into environment class ?

white = (255,255,255)
black = (0)

date = datetime.date(datetime.now())

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 200
        self.y = 800
        self.deltaY = 0
        self.image = get_image('Assets\\bbm.png')
        self.rect = self.image.get_rect()
        self.gravityFlag = False

    def update(self):
        # gravity
        if self.y < 800:
            if self.rect.colliderect(game.obstacle.rect):
                self.gravityFlag = True
                self.initialGravityFrame = game.frameCount
            if self.gravityFlag:
                if (game.frameCount - self.initialGravityFrame) >= 15:
                    self.deltaY += 10
                    self.gravityFlag = False
        elif self.y >= 800:
            self.deltaY = 0
                
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        self.y += self.deltaY
        game.screen.blit(self.image, (self.x, self.y))


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, text):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.text = text
        self.image = get_image('Assets\\button0.png')
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
                play_sound('Assets\\mouseover.wav')
            self.soundFlag = False
            self.showBorder = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                play_sound('Assets\\select.wav')
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
            game.screen.blit(get_image("Assets\\limeborder.png"), (self.x-3, self.y-3))
        game.screen.blit(self.image, self.rect)
        message_display(self.text, self.x+200, self.y+55, self.size, black)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.x = 2500
        self.y = 735
        self.image = get_image('Assets\\obstacle.png')
        self.rect = self.image.get_rect()
        self.rect.y = self.y

    def update(self):
        self.x -= 25
        self.rect.x = self.x
        if self.x < -800:
            self.x = random.randint(2500, 3750)

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
        global cheatCode
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
                    cheatCode = self.text
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


class Trick:
    def __init__(self, req, interval, animation):
        self.req = req
        self.interval = interval
        self.animation = animation
        self.count = 0

    def animate(self, framecount):
        if (framecount - self.initFrame) % interval == 0:
            self.count += 1
            player.image = get_image(animation[count])
            if self.count == len(animation):
                pass

        
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
def play_sound(path):
  global _sound_library
  sound = _sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    _sound_library[path] = sound
  sound.play()

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def message_display(text, x, y, size, color, fontstr='freesansbold.ttf'):
    largeText = pygame.font.Font(fontstr, size)
    TextSurf, TextRect = text_objects(text, largeText, color)
    TextRect.center = (x, y)
    game.screen.blit(TextSurf, TextRect)

def getScores():
    # read highscore entries, put scores in a list and the whole entry in another, all sorted
    highscores = []
    with open('Assets\\highscores.txt','r') as f:
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
        

class Game:
    def __init__(self):
        # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 1, 512) # reduces audio latency
        pygame.init()
        pygame.mixer.music.load('Assets\\bgMusic.mp3')
        pygame.mixer.music.play(-1) # loop music
        # Fetch settings
        with open('Assets\\settings.txt','r') as f:
            savedSettings = f.readlines()
        self.windowMode = savedSettings[0]
        if self.windowMode == 'RESIZABLE\n':
            self.screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
        else: self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        self.volume = float(savedSettings[1])
        pygame.mixer.music.set_volume(self.volume)
        pygame.display.set_icon(get_image('Assets\\bbm.png')) # sets window icon
        pygame.display.set_caption('Broken Bones') # sets window title
        self.bg = get_image('Assets\\bbBG.png')
        self.bgnh = get_image('Assets\\bbBG.png')
        # Fetch achievements
        self.achievements = []
        with open('Assets\\achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))
        self.highscore, self.entries = getScores()
        self.clock = pygame.time.Clock()


    def mainMenu(self):
        # frame counting for animation
        self.frameCount = 0
        captureAnimationFrame = True
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # flags for going up the ramp
        rotateFlag = True
        movementFlag = True
        rotated = False
        # object initialization
        player = Player()
        self.obstacle = Obstacle()
        windlines = []
        for x in range(10):
            windlines.append(Wind())
        pebbles = []
        for x in range(10):
            pebbles.append(Pebble())
        buttons = [Button((1920//2-(418//2))-300, 1080//2+300, 'SETTINGS'),
                   Button((1920//2-(418//2))+300, 1080//2+300, 'QUIT'),
                   Button((1920//2-(418//2))+300, 1080//2+150, 'LEADERBOARD'),
                   Button((1920//2-(418//2))-300, 1080//2+150, 'ACHIEVEMENTS')]
        
        while True:
            self.frameCount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.play(3)
                for button in buttons:
                    button.update(event)
                    
            # call updates on all objects
            player.update()
            for line in windlines:
                line.update()
            for pebble in pebbles:
                pebble.update()
            self.obstacle.update()

            # player & obstacle collision
            if player.rect.colliderect(self.obstacle.rect):
                # image rotation
                if rotateFlag:
                    initialFrame = self.frameCount
                    player.image = pygame.transform.rotate(player.image, 23)
                    rotateFlag = False
                    rotated = True
                # image movement
                if movementFlag:
                    player.deltaY -= 10
                    movementFlag = False
            elif rotated:    
                if (self.frameCount - initialFrame) == 70: # 70 frames after no collision with the ramp
                    player.image = get_image('Assets\\bbm.png')
                    player.deltaY += 10
                    rotated = False
                    rotateFlag = True
                    movementFlag = True

            # render things to the screen
            # Environment
            self.screen.blit(self.bgnh, (0,0)) # background
            for pebble in pebbles:
                pebble.draw()
            for line in windlines:
                line.draw()
            self.obstacle.draw()
            player.draw()
            # HUD
            pygame.draw.rect(self.screen, black, (0,0,1920,265))
            message_display('BROKEN BONEZ', 1920//2, 130, 230, (255,255,0), 'Assets\\ipaexg.ttf')
            message_display('PRESS ANY KEY TO START', 1920//2, 1080//2, 100, white)
            for button in buttons:
                button.draw()
        
            pygame.display.flip()
            self.clock.tick(60)


    def play(self, lives, score=0, timeLeft=60):
        # frame counting for animation
        self.frameCount = 0
        captureAnimationFrame = True

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # flags for going up the ramp
        rotateFlag = True
        movementFlag = True
        rotated = False

        multiplier = 1

        # object initialization
        player = Player()
        self.obstacle = Obstacle()
        windlines = []
        for x in range(10):
            windlines.append(Wind())
        pebbles = []
        for x in range(10):
            pebbles.append(Pebble())
            
        # time vars
        currentGameTime = 0
        initialTime = time.time()

        # trick flags & vars
        trick1 = False
        trick2 = False
        trick3 = False
        trick1buttons = False
        trick2buttons = False
        trick3buttons = False
        trick1Count = 0
        trick2Count = 0
        trick3Count = 0
        done = False
        showTrickScore = False
        addScore = False

        # multiplier flags
        noLife = False
        multiplierFlag = False

        # crash flags
        captureLifeFrame = True
        crashAnimation = False
        crashDone = False

        # sound flags
        scoreSound = False
        crashSound = False
        while True:
            self.frameCount += 1
            # process user input
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                # keydown events
                if event.type == pygame.KEYDOWN:
                    # trick 1
                    if event.key == pygame.K_c:
                        trick1buttons = True
                    # trick 2
                    if event.key == pygame.K_v:
                        trick2buttons = True
                    # trick 3
                    if event.key == pygame.K_b:
                        trick3buttons = True
# update objects
# if collide
#   use rotated image
# if buttons pressed on ramp >= req:
#   start animation
            # tricks
            if player.rect.colliderect(self.obstacle.rect): # if colliding
                if trick1buttons: # and trick buttons have been pressed
                    trick1Count += 1 # count towards trickcount; need 3
                    trick1buttons = False # reset buttons flag for next ramp
                    if trick1Count >= 3: # if req has been met
                        trick1 = True # enable trick flag
                elif trick2buttons:
                    trick2Count += 1
                    trick2buttons = False
                    if trick2Count >= 8:
                        trick2 = True
                elif trick3buttons:
                    trick3Count += 1
                    trick3buttons = False
                    if trick3Count >= 10:
                        trick3 = True
            else: # if NOT colliding
                trick1Count = 0 # reset trickcounts
                trick2Count = 0
                trick3Count = 0
                trick1buttons = False
                trick2buttons = False
                trick3buttons = False

            # call updates on all objects
            player.update()
            for line in windlines:
                line.update()
            for pebble in pebbles:
                pebble.update()
            self.obstacle.update()

            # player & obstacle collision
            if player.rect.colliderect(self.obstacle.rect):
                # image rotation
                if rotateFlag:
                    initialFrame = self.frameCount
                    player.image = pygame.transform.rotate(player.image, 23)
                    rotateFlag = False
                    rotated = True
                # image movement
                if movementFlag:
                    player.deltaY -= 10
                    movementFlag = False
            elif rotated:
                # multiplier
                if trick1 or trick2 or trick3: # if player did a trick
                    multiplierFlag = True # enable multiplier flag
                    
                if trick1:
                    # animation
                    if captureAnimationFrame: # flag for getting the initial frame
                        initialTrickFrame = self.frameCount
                        captureAnimationFrame = False
                    if self.frameCount - initialTrickFrame >= 10:
                        player.image = get_image('Assets\\Animations\\trick1.1.png')
                    if self.frameCount - initialTrickFrame >= 25:
                        player.image = get_image('Assets\\Animations\\trick1.2.png')
                    if self.frameCount - initialTrickFrame >= 40: # the sum of all these frames should be less than the buffer for resetting the rotated image (70)
                        done = True
                    # when animation is finished, reset flags and initialize score processing
                    if done:
                        trickScore = 5000*multiplier
                        showTrickScore = True
                        initialScoreFrame = self.frameCount
                        addScore = True
                        trick1 = False
                        captureAnimationFrame = True
                        scoreSound = True
                        done = False
                        
                elif trick2:
                    if captureAnimationFrame:
                        initialTrickFrame = self.frameCount
                        captureAnimationFrame = False
                    if self.frameCount - initialTrickFrame >= 10:
                        player.image = get_image('Assets\\Animations\\trick2.1.png')
                    if self.frameCount - initialTrickFrame >= 20:
                        player.image = get_image('Assets\\Animations\\trick2.2.png')
                    if self.frameCount - initialTrickFrame >= 30:
                       player.image = get_image('Assets\\Animations\\trick2.3.png')
                    if self.frameCount - initialTrickFrame >= 40:
                        done = True
                    if done:
                        trickScore = 10000*multiplier
                        showTrickScore = True
                        initialScoreFrame = self.frameCount
                        addScore = True
                        trick2 = False
                        captureAnimationFrame = True
                        scoreSound = True
                        done = False
                        
                elif trick3:
                    if captureAnimationFrame:
                        initialTrickFrame = self.frameCount
                        captureAnimationFrame = False
                    if self.frameCount - initialTrickFrame >= 10:
                        player.image = get_image('Assets\\Animations\\trick3.1.png')
                    if self.frameCount - initialTrickFrame >= 14:
                        player.image = get_image('Assets\\Animations\\trick3.2.png')
                    if self.frameCount - initialTrickFrame >= 18:
                        player.image = get_image('Assets\\Animations\\trick3.3.png')
                    if self.frameCount - initialTrickFrame >= 22:
                        player.image = get_image('Assets\\Animations\\trick3.4.png')
                    if self.frameCount - initialTrickFrame >= 26:
                        player.image = get_image('Assets\\Animations\\trick3.5.png')
                    if self.frameCount - initialTrickFrame >= 30:
                        player.image = get_image('Assets\\Animations\\trick3.6.png')
                    if self.frameCount - initialTrickFrame >= 34:
                        player.image = get_image('Assets\\Animations\\trick3.7.png')
                    if self.frameCount - initialTrickFrame >= 38:
                        player.image = get_image('Assets\\bbm.png')
                    if self.frameCount - initialTrickFrame >= 42: 
                        done = True
                    if done:
                        trickScore = 30000*multiplier
                        showTrickScore = True
                        initialScoreFrame = self.frameCount
                        addScore = True
                        trick3 = False
                        scoreSound = True
                        captureAnimationFrame = True
                        done = False
                        
                if (self.frameCount - initialFrame) == 70: # 70 frames after no collision with the ramp
                    # multiplier
                    if multiplierFlag:
                        noLife = False
                        if multiplier < 5:
                            multiplier += 1
                    else:
                        multiplier = 1
                        if noLife:
                            lives -= 1
                            score -= 10000
                            crashAnimation = True
                            crashSound = True
                        noLife = True
                        
                    player.image = get_image('Assets\\bbm.png')
                    player.deltaY += 10
                    rotated = False
                    rotateFlag = True
                    movementFlag = True
                    multiplierFlag = False

            if crashAnimation:
                self.obstacle.x = 10000
                for pebble in pebbles:
                    pebble.x += 25
                if captureLifeFrame:
                    initialCrashFrame = self.frameCount
                    captureLifeFrame = False
                if self.frameCount - initialCrashFrame >= 30:
                    player.image = get_image('Assets\\Animations\\crash1.1.png')
                    player.y = 900
                    if crashSound:
                        play_sound('Assets\\crash.wav')
                        crashSound = False
                if self.frameCount - initialCrashFrame >= 40:
                    player.image = get_image('Assets\\Animations\\crash1.2.png')
                    player.y = 900
                if self.frameCount - initialCrashFrame >= 80:
                    crashDone = True
                if crashDone:
                    if lives == 0:
                        self.gameOver(score)
                    self.play(lives, score, timeLeft)
                    
            # time
            previousGameTime = currentGameTime
            currentGameTime = int((time.time()-initialTime))
            if currentGameTime != previousGameTime:
                timeLeft -= 1
                if timeLeft == 0:
                    self.gameOver(score)


            # render things to the screen
            self.screen.blit(self.bg, (0,0))
            # HUD
            message_display('PLAYER 1', 350, 50, 50, white)
            message_display(str(score), 350, 125, 50, white)
            message_display('HI-SCORE', 950, 50, 50, white)
            message_display(str(self.highscore), 950, 125, 50, white)
            message_display('c x 6 : 5000  |  v x 8 : 10000  |  b x 10 : 30000', 280, 200, 25, black)
            message_display(str(timeLeft), 1870, 220, 50, black)
            for x in range(multiplier):
                self.screen.blit(get_image('Assets\\bones.png'), ((135*x)+1200, 30))
            for x in range(lives):
                self.screen.blit(get_image('Assets\\helmet.png'), ((100*x)+20, 1000))
            # Environment
            for pebble in pebbles:
                pebble.draw()
            for line in windlines:
                line.draw()
            self.obstacle.draw()
            player.draw()
            # Trick Score
            if showTrickScore:
                if self.frameCount - initialScoreFrame >= 43:
                    if scoreSound:
                        play_sound('Assets\\score.wav')
                        scoreSound = False
                    if addScore:
                        score += trickScore
                        addScore = False
                    message_display(str(trickScore), player.x+100, player.y-100, 75, (255,255,0))
                    if self.frameCount - initialScoreFrame >= 55:
                        showTrickScore = False
            if trick1Count > 0:
                message_display(str(trick1Count), player.x-100, player.y-100, 75, white)
                if trick1Count >= 6:
                    self.screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))
            elif trick2Count > 0:
                message_display(str(trick2Count), player.x-100, player.y-100, 75, white)
                if trick2Count >= 8:
                    self.screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))
            elif trick3Count > 0:
                message_display(str(trick3Count), player.x-100, player.y-100, 75, white)
                if trick3Count >= 10:
                    self.screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))      
            pygame.display.flip()
            self.clock.tick(60)


    def gameOver(self, score):
        if score < 0: self.achievements[0] = 1
        if score >= 1279000: self.achievements[1] = 1
        if score >= 1300000: self.achievements[2] = 1
        with open('Assets\\achievements.txt', 'w') as f:
            f.write(str(self.achievements[0]) + '\n' + str(self.achievements[1]) + '\n' + str(self.achievements[2]) + '\n')

        buttons = [Button((1920//2-(418//2))-300, 1080//2+250, 'MAIN MENU'), Button((1920//2-(418//2))+300, 1080//2+250, 'QUIT')]
        # frame counting for animation
        self.frameCount = 0
        captureAnimationFrame = True
        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        # flags for going up the ramp
        rotateFlag = True
        movementFlag = True
        rotated = False
        # blank flags
        nextBlank = False
        lastBlank = False
        blanks = ['_', '_', '_']
        finished = False
        # object initialization
        player = Player()
        self.obstacle = Obstacle()
        windlines = []
        for x in range(10):
            windlines.append(Wind())
        pebbles = []
        for x in range(10):
            pebbles.append(Pebble())
        #buttons = [Button((1920//2-(418//2))-300, 1080//2+100, 'Leaderboard')]
        initials = []
        while True:
            self.frameCount += 1
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                if event.type == pygame.KEYDOWN:
                    # initials input
                    if score > self.highscore:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                            nextBlank = False
                            lastBlank = False
                            finished = False
                            blanks = ['_','_','_']
                        elif len(initials) < 3:
                            initials.append(pygame.key.name(event.key).upper())
                            blanks[len(initials)-1] = initials[-1]
                        if event.key == pygame.K_RETURN and len(initials) == 3:
                            with open('Assets\\highscores.txt', 'a') as f:
                                f.write(blanks[0] + blanks[1] + blanks[2] + '     ' + str(score) + '     ' + str(date) + '\n')
                            game.mainMenu()

                for button in buttons:
                    button.update(event)

            # call updates on all objects
            player.update()
            for line in windlines:
                line.update()
            for pebble in pebbles:
                pebble.update()
            self.obstacle.update()

            # player & obstacle collision
            if player.rect.colliderect(self.obstacle.rect):
                # image rotation
                player.image = pygame.transform.rotate(player.image, 23)
                    player.deltaY -= 10
                player.image = get_image('Assets\\bbm.png')

            # render things to the screen
            self.screen.blit(self.bg, (0,0)) # background
            # HUD
            message_display('PLAYER 1', 350, 50, 50, white)
            message_display(str(score), 350, 125, 50, white)
            message_display('HI-SCORE', 950, 50, 50, white)
            message_display(str(self.highscore), 950, 125, 50, white)
            if score >= self.highscore:
                message_display('NEW HI-SCORE!', 1920//2, 1080//2-200, 150, white)
                message_display(blanks[0], 1920//2-125, 1080//2+150, 150, white)
                message_display(blanks[1], 1920//2, 1080//2+150, 150, white)
                message_display(blanks[2], 1920//2+125, 1080//2+150, 150, white)
            else:
                message_display('GAMEOVER', 1920//2, 1080//2-200, 150, (255,0,0))
            message_display(str(score), 1920//2, 1080//2-25, 150, white)
            self.screen.blit(get_image('Assets\\bones.png'), (1200, 30))
            if score < 0: self.screen.blit(get_image('Assets\\ach1.png'), (1920-300,1080-75))
            if score >= 1279000: self.screen.blit(get_image('Assets\\ach2.png'), (1920-300,1080-75))
            if score >= 1300000: self.screen.blit(get_image('Assets\\ach3.png'), (1920-300,1080-155))
            # Environment
            for pebble in pebbles:
                pebble.draw()
            for line in windlines:
                line.draw()
            self.obstacle.draw()
            player.draw()
            for button in buttons:
                button.draw()

            pygame.display.flip()
            self.clock.tick(60)


    def leaderboard(self):
        button = Button((1920//2-(400//2)), 900, 'BACK')
        while True:
            # process user input
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                checkForQuit(event, pressed_keys)
                button.update(event)

            self.screen.fill(black)
            message_display('HI-SCORES', 1920//2, 80, 100, white)
            for x in range(len(self.entries)):
                message_display(str(self.entries[x]), 1920//2, 220+(80*x), 60, white, 'Assets\\ipaexg.ttf')
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)


    def achievementsMenu(self):
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
                    self.screen.blit(get_image('Assets\\ach'+str(count)+'.png'), (1920//2-150, 100*count))
                else:
                    self.screen.blit(get_image('Assets\\ach'+str(count)+'locked.png'), (1920//2-150, 100*count))
            button.draw()
            pygame.display.flip()
            self.clock.tick(60)
        

    def settings(self):
        cheatCode = ''
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
            if cheatCode != '':
                if cheatCode == 'all nighter':
                    self.bg = get_image('Assets\\bbBGnight.png')
                    self.bgnh = get_image('Assets\\bbBGnoHUDnight.png')
                cheatCode = ''
                
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
                        with open('Assets\\settings.txt', 'w') as f:
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
                            with open('Assets\\settings.txt', 'w') as f:
                                f.write(self.windowMode + str(self.volume))
                            canClick = False
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        canClick = True
                else:
                    option.hovered = False

            self.screen.fill(black)
            message_display('VIDEO', 300, 200, 50, white)
            message_display('AUDIO', 300, 400, 50, white)
            message_display('EXTRA', 300, 600, 50, white)
            message_display(str(int((self.volume+0.05)*10)*10), 1110, 400, 30, white)
            button.draw()
            for box in input_boxes:
                box.draw(self.screen)
            for option in options:
                option.draw()
            pygame.display.flip()
            self.clock.tick(60)

trick1animation = []

game = Game()
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
menu_font = pygame.font.Font(None, 40)
game.mainMenu()
