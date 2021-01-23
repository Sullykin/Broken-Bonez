import pygame, sys, os, random, time
from datetime import datetime

# doing tricks in a row builds multiplier
# not doing a trick removes all multipliers
# no trick twice in a row = crash & lost life

# cheats - Enter code to unlock new;Background, soundtrack, effects, secret trick, audio quotes form characters, etc.
# rigby achievement: special secret trick for tapping two buttons back and forth

# fps bug

# Version 1.0.1
    # reduced difficulty
    # moved main menu buttons

white = (255,255,255)
black = (0,0,0)

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
        global obstacle
        global frameCount
        # gravity
        if self.y < 800:
            if self.rect.colliderect(obstacle.rect):
                self.gravityFlag = True
                self.initialGravityFrame = frameCount
            if self.gravityFlag:
                if (frameCount - self.initialGravityFrame) >= 15:
                    self.deltaY += 10
                    self.gravityFlag = False
        elif self.y >= 800:
            self.deltaY = 0
                
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self):
        self.y += self.deltaY
        screen.blit(self.image, (self.x, self.y))


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
                    leaderboard()
                elif self.text == 'BACK':
                    mainMenu()
                elif self.text == 'MAIN MENU':
                    mainMenu()
                elif self.text == 'ACHIEVEMENTS':
                    achievementsMenu()
                elif self.text == 'SETTINGS':
                    settings()
        else:
            self.showBorder = False
            self.soundFlag = True

    def draw(self):
        if self.showBorder:
            screen.blit(get_image("Assets\\limeborder.png"), (self.x-3, self.y-3))
        screen.blit(self.image, self.rect)
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
        screen.blit(self.image, (self.x, self.y))


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
        pygame.draw.rect(screen, (155, 155, 155), (self.x,self.y,150,1))


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
        pygame.draw.rect(screen, black, (self.x,self.y,5,5))

class Option:
    hovered = False
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.set_rect()
        self.draw()
            
    def draw(self):
        self.set_rend()
        screen.blit(self.rend, self.rect)
        
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
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)
        

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
    screen.blit(TextSurf, TextRect)

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
    
pygame.mixer.pre_init(44100, -16, 1, 512) # reduces audio latency
pygame.init()
pygame.mixer.music.load('Assets\\bgMusic.mp3')
pygame.mixer.music.play(-1) # loop music

COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)
screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
fav = get_image('Assets\\bbm.png')
pygame.display.set_icon(fav) # sets window icon
pygame.display.set_caption('Broken Bones') # sets window title
menu_font = pygame.font.Font(None, 40)
bg = get_image('Assets\\bbBG.png')
bgnh = get_image('Assets\\bbBG.png')

# achievement flags
ach1 = 0
ach2 = 0
ach3 = 0

achievements = []
with open('Assets\\achievements.txt','r') as f:
    entries = f.readlines()
for entry in entries:
        achievements.append(int(entry))

with open('Assets\\settings.txt','r') as f:
    savedSettings = f.readlines()
windowMode = savedSettings[0]
currentVolume = float(savedSettings[1])
if windowMode == 'RESIZABLE\n':
    screen = pygame.display.set_mode((1920, 1080), pygame.RESIZABLE)
pygame.mixer.music.set_volume(currentVolume)

# main menu
#-------------------------------------------------------------------------------
def mainMenu():
    global bg, bgnh
    highScore, entries = getScores()
    global currentVolume
    pygame.mixer.music.set_volume(currentVolume)
    # frame counting for animation
    global frameCount
    frameCount = 0
    captureAnimationFrame = True

    # flags for going up the ramp
    rotateFlag = True
    movementFlag = True
    rotated = False

    # object initialization
    player = Player()
    global obstacle
    obstacle = Obstacle()
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

    global saveAchievements
    saveAchievements = True
    
    clock = pygame.time.Clock()
    while True:
        frameCount += 1
        
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            # keydown events
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                                pressed_keys[pygame.K_RALT]
                space_pressed = pressed_keys[pygame.K_SPACE]
                # esc
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                # alt + f4
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
                else:
                    play(3)
                    
            if quit_attempt:
                pygame.quit()
                sys.exit()
            for button in buttons:
                button.update(event)

        # call updates on all objects
        player.update()
        for line in windlines:
            line.update()
        for pebble in pebbles:
            pebble.update()
        obstacle.update()

        # player & obstacle collision
        if player.rect.colliderect(obstacle.rect):
            # image rotation
            if rotateFlag:
                initialFrame = frameCount
                player.image = pygame.transform.rotate(player.image, 23)
                rotateFlag = False
                rotated = True
            # image movement
            if movementFlag:
                player.deltaY -= 10
                movementFlag = False
        elif rotated:    
            if (frameCount - initialFrame) == 70: # 70 frames after no collision with the ramp
                player.image = get_image('Assets\\bbm.png')
                player.deltaY += 10
                rotated = False
                rotateFlag = True
                movementFlag = True

        # render things to the screen
        screen.fill(black) # clear screen
        screen.blit(bgnh, (0,0)) # background

        # Environment
        for pebble in pebbles:
            pebble.draw()
        for line in windlines:
            line.draw()
        obstacle.draw()
        player.draw()
        pygame.draw.rect(screen, black, (0,0,1920,265))
        message_display('BROKEN BONEZ', 1920//2, 130, 230, (255,255,0), 'Assets\\ipaexg.ttf')
        message_display('PRESS ANY KEY TO START', 1920//2, 1080//2, 100, white)
        for button in buttons:
            button.draw()
    
        pygame.display.flip()
        clock.tick(60)

#-------------------------------------------------------------------------------




# Main game loop
#-------------------------------------------------------------------------------
def play(lives, score=0, timeLeft=60):
    global bg, bgnh
    highScore, entries = getScores()
    # frame counting for animation
    global frameCount
    frameCount = 0
    captureAnimationFrame = True

    # flags for going up the ramp
    rotateFlag = True
    movementFlag = True
    rotated = False

    multiplier = 1

    # object initialization
    player = Player()
    global obstacle
    obstacle = Obstacle()
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
    
    clock = pygame.time.Clock()
    while True:
        frameCount += 1
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
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
                # trick 1
                if event.key == pygame.K_c:
                    trick1buttons = True
                # trick 2
                if event.key == pygame.K_v:
                    trick2buttons = True
                # trick 3
                if event.key == pygame.K_b:
                    trick3buttons = True
                    
            if quit_attempt:
                pygame.quit()
                sys.exit()

        # tricks
        if player.rect.colliderect(obstacle.rect): # if colliding
            if trick1buttons: # and trick buttons have been pressed
                trick1Count += 1 # count towards trickcount; need 3
                trick1buttons = False # reset buttons flag for next ramp
                if trick1Count >= 6: # if req has been met
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
        obstacle.update()

        # player & obstacle collision
        if player.rect.colliderect(obstacle.rect):
            # image rotation
            if rotateFlag:
                initialFrame = frameCount
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
                    initialTrickFrame = frameCount
                    captureAnimationFrame = False
                if frameCount - initialTrickFrame >= 10:
                    player.image = get_image('Assets\\Animations\\trick1.1.png')
                if frameCount - initialTrickFrame >= 25:
                    player.image = get_image('Assets\\Animations\\trick1.2.png')
                if frameCount - initialTrickFrame >= 40: # the sum of all these frames should be less than the buffer for resetting the rotated image (70)
                    done = True
                # when animation is finished, reset flags and initialize score processing
                if done:
                    trickScore = 5000*multiplier
                    showTrickScore = True
                    initialScoreFrame = frameCount
                    addScore = True
                    trick1 = False
                    captureAnimationFrame = True
                    scoreSound = True
                    done = False
                    
            elif trick2:
                if captureAnimationFrame:
                    initialTrickFrame = frameCount
                    captureAnimationFrame = False
                if frameCount - initialTrickFrame >= 10:
                    player.image = get_image('Assets\\Animations\\trick2.1.png')
                if frameCount - initialTrickFrame >= 20:
                    player.image = get_image('Assets\\Animations\\trick2.2.png')
                if frameCount - initialTrickFrame >= 30:
                   player.image = get_image('Assets\\Animations\\trick2.3.png')
                if frameCount - initialTrickFrame >= 40:
                    done = True
                if done:
                    trickScore = 10000*multiplier
                    showTrickScore = True
                    initialScoreFrame = frameCount
                    addScore = True
                    trick2 = False
                    captureAnimationFrame = True
                    scoreSound = True
                    done = False
                    
            elif trick3:
                if captureAnimationFrame:
                    initialTrickFrame = frameCount
                    captureAnimationFrame = False
                if frameCount - initialTrickFrame >= 10:
                    player.image = get_image('Assets\\Animations\\trick3.1.png')
                if frameCount - initialTrickFrame >= 14:
                    player.image = get_image('Assets\\Animations\\trick3.2.png')
                if frameCount - initialTrickFrame >= 18:
                    player.image = get_image('Assets\\Animations\\trick3.3.png')
                if frameCount - initialTrickFrame >= 22:
                    player.image = get_image('Assets\\Animations\\trick3.4.png')
                if frameCount - initialTrickFrame >= 26:
                    player.image = get_image('Assets\\Animations\\trick3.5.png')
                if frameCount - initialTrickFrame >= 30:
                    player.image = get_image('Assets\\Animations\\trick3.6.png')
                if frameCount - initialTrickFrame >= 34:
                    player.image = get_image('Assets\\Animations\\trick3.7.png')
                if frameCount - initialTrickFrame >= 38:
                    player.image = get_image('Assets\\bbm.png')
                if frameCount - initialTrickFrame >= 42: 
                    done = True
                if done:
                    trickScore = 30000*multiplier
                    showTrickScore = True
                    initialScoreFrame = frameCount
                    addScore = True
                    trick3 = False
                    scoreSound = True
                    captureAnimationFrame = True
                    done = False
                    
            if (frameCount - initialFrame) == 70: # 70 frames after no collision with the ramp
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
            obstacle.x = 10000
            for pebble in pebbles:
                pebble.x += 25
            if captureLifeFrame:
                initialCrashFrame = frameCount
                captureLifeFrame = False
            if frameCount - initialCrashFrame >= 30:
                player.image = get_image('Assets\\Animations\\crash1.1.png')
                player.y = 900
                if crashSound:
                    play_sound('Assets\\crash.wav')
                    crashSound = False
            if frameCount - initialCrashFrame >= 40:
                player.image = get_image('Assets\\Animations\\crash1.2.png')
                player.y = 900
            if frameCount - initialCrashFrame >= 80:
                crashDone = True
            if crashDone:
                if lives == 0:
                    gameOver(score)
                play(lives, score, timeLeft)
                
        # time
        previousGameTime = currentGameTime
        currentGameTime = int((time.time()-initialTime))
        if currentGameTime != previousGameTime:
            timeLeft -= 1
            if timeLeft == 0:
                gameOver(score)


        # render things to the screen
        screen.fill(black) # clear screen
        screen.blit(bg, (0,0)) # background

        # HUD
        message_display('PLAYER 1', 350, 50, 50, white)
        message_display(str(score), 350, 125, 50, white)
        message_display('HI-SCORE', 950, 50, 50, white)
        message_display(str(highScore), 950, 125, 50, white)
        message_display('c x 6 : 5000  |  v x 8 : 10000  |  b x 10 : 30000', 280, 200, 25, black)
        message_display(str(timeLeft), 1870, 220, 50, black)
        for x in range(multiplier):
            screen.blit(get_image('Assets\\bones.png'), ((135*x)+1200, 30))
        for x in range(lives):
            screen.blit(get_image('Assets\\helmet.png'), ((100*x)+20, 1000))

        # Environment
        for pebble in pebbles:
            pebble.draw()
        for line in windlines:
            line.draw()
        obstacle.draw()
        player.draw()

        # Trick Score
        if showTrickScore:
            if frameCount - initialScoreFrame >= 43:
                if scoreSound:
                    play_sound('Assets\\score.wav')
                    scoreSound = False
                if addScore:
                    score += trickScore
                    addScore = False
                message_display(str(trickScore), player.x+100, player.y-100, 75, (255,255,0))
                if frameCount - initialScoreFrame >= 55:
                    showTrickScore = False
        if trick1Count > 0:
            message_display(str(trick1Count), player.x-100, player.y-100, 75, white)
            if trick1Count >= 7:
                screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))
        elif trick2Count > 0:
            message_display(str(trick2Count), player.x-100, player.y-100, 75, white)
            if trick2Count >= 9:
                screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))
        elif trick3Count > 0:
            message_display(str(trick3Count), player.x-100, player.y-100, 75, white)
            if trick3Count >= 11:
                screen.blit(get_image('Assets\\countBubble.png'), (player.x-195, player.y-190))      
        pygame.display.flip()
        clock.tick(60)


#-------------------------------------------------------------------------------





# Game over
#-------------------------------------------------------------------------------
def gameOver(score):
    global bg, bgnh
    highScore, entries = getScores()
    GObuttons = [Button((1920//2-(418//2))-300, 1080//2+250, 'MAIN MENU'), Button((1920//2-(418//2))+300, 1080//2+250, 'QUIT')]
    # frame counting for animation
    global frameCount
    frameCount = 0
    captureAnimationFrame = True

    # flags for going up the ramp
    rotateFlag = True
    movementFlag = True
    rotated = False

    # blank flags
    nextBlank = False
    lastBlank = False
    blanks = ['_', '_', '_']
    finished = False

    # achievement flags
    global achievements
    global ach1
    global ach2
    global ach3
    global saveAchievements
    saveAchievements = True

    # object initialization
    player = Player()
    global obstacle
    obstacle = Obstacle()
    windlines = []
    for x in range(10):
        windlines.append(Wind())
    pebbles = []
    for x in range(10):
        pebbles.append(Pebble())
    buttons = [Button((1920//2-(418//2))-300, 1080//2+100, 'Leaderboard')]
 
    clock = pygame.time.Clock()
    while True:
        frameCount += 1
        
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            quit_attempt = False
            if event.type == pygame.QUIT:
                quit_attempt = True
            # keydown events
            elif event.type == pygame.KEYDOWN:
                alt_pressed = pressed_keys[pygame.K_LALT] or \
                                pressed_keys[pygame.K_RALT]
                space_pressed = pressed_keys[pygame.K_SPACE]
                # esc
                if event.key == pygame.K_ESCAPE:
                    quit_attempt = True
                # alt + f4
                elif event.key == pygame.K_F4 and alt_pressed:
                    quit_attempt = True
                # initials input
                else:
                    if score > highScore:
                        if event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                            nextBlank = False
                            lastBlank = False
                            finished = False
                            blanks = ['_','_','_']
                        if lastBlank:
                            blanks[2] = pygame.key.name(event.key)
                            try: blanks[2] = blanks[2].upper()
                            except: pass
                            lastBlank = False
                            finished = True
                        elif nextBlank:
                            blanks[1] = pygame.key.name(event.key)
                            try: blanks[1] = blanks[1].upper()
                            except: pass
                            lastBlank = True
                            nextBlank = False
                        elif not nextBlank and not lastBlank:
                            if not finished and event.key != pygame.K_LEFT and event.key != pygame.K_BACKSPACE:
                                blanks[0] = pygame.key.name(event.key)
                                try: blanks[0] = blanks[0].upper()
                                except: pass
                                nextBlank = True
                        if event.key == pygame.K_RETURN:
                            with open('Assets\\highscores.txt', 'a') as f:
                                f.write(blanks[0] + blanks[1] + blanks[2] + '     ' + str(score) + '     ' + str(date) + '\n')
                            mainMenu()
                    
            if quit_attempt:
                pygame.quit()
                sys.exit()

            for button in GObuttons:
                button.update(event)

        # call updates on all objects
        player.update()
        for line in windlines:
            line.update()
        for pebble in pebbles:
            pebble.update()
        obstacle.update()

        # player & obstacle collision
        if player.rect.colliderect(obstacle.rect):
            # image rotation
            if rotateFlag:
                initialFrame = frameCount
                player.image = pygame.transform.rotate(player.image, 23)
                rotateFlag = False
                rotated = True
            # image movement
            if movementFlag:
                player.deltaY -= 10
                movementFlag = False
        elif rotated:    
            if (frameCount - initialFrame) == 70: # 70 frames after no collision with the ramp
                player.image = get_image('Assets\\bbm.png')
                player.deltaY += 10
                rotated = False
                rotateFlag = True
                movementFlag = True

        # render things to the screen
        screen.fill(black) # clear screen
        screen.blit(bg, (0,0)) # background

        # HUD
        message_display('PLAYER 1', 350, 50, 50, white)
        message_display(str(score), 350, 125, 50, white)
        message_display('HI-SCORE', 950, 50, 50, white)
        message_display(str(highScore), 950, 125, 50, white)
        if score > highScore:
            message_display('NEW HI-SCORE!', 1920//2, 1080//2-200, 150, white)
            message_display(blanks[0], 1920//2-125, 1080//2+150, 150, white)
            message_display(blanks[1], 1920//2, 1080//2+150, 150, white)
            message_display(blanks[2], 1920//2+125, 1080//2+150, 150, white)
        else:
            message_display('GAMEOVER', 1920//2, 1080//2-200, 150, (255,0,0))
        message_display(str(score), 1920//2, 1080//2-25, 150, white)
        screen.blit(get_image('Assets\\bones.png'), (1200, 30))

        # Environment
        for pebble in pebbles:
            pebble.draw()
        for line in windlines:
            line.draw()
        obstacle.draw()
        player.draw()
        for button in GObuttons:
            button.draw()
        if score < 0:
            screen.blit(get_image('Assets\\ach1.png'), (1920-300,1080-75))
            achievements[0] = 1
        if score >= 1300000:
            screen.blit(get_image('Assets\\ach3.png'), (1920-300,1080-155))
            achievements[2] = 1
        if score >= 1279000:
            screen.blit(get_image('Assets\\ach2.png'), (1920-300,1080-75))
            achievements[1] = 1
        if saveAchievements:
            with open('Assets\\achievements.txt', 'w') as f:
                f.write(str(achievements[0]) + '\n' + str(achievements[1]) + '\n' + str(achievements[2]) + '\n')
            saveAchievements = False

        pygame.display.flip()
        clock.tick(60)

#-------------------------------------------------------------------------------



# Leaderboard
#-------------------------------------------------------------------------------
def leaderboard():
    highScore, entries = getScores()
    global currentVolume
    pygame.mixer.music.set_volume(currentVolume)
    button = Button((1920//2-(400//2)), 900, 'BACK')
    clock = pygame.time.Clock()
    while True:
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
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
            button.update(event)

        screen.fill(black)
        message_display('HI-SCORES', 1920//2, 80, 100, white)
        for x in range(len(entries)):
            message_display(str(entries[x]), 1920//2, 220+(80*x), 60, white, 'Assets\\ipaexg.ttf')
        button.draw()
        pygame.display.flip()
        clock.tick(60)
#-------------------------------------------------------------------------------



#-------------------------------------------------------------------------------
def achievementsMenu():
    global ach1
    global ach2
    global ach3
    global achievements
    pygame.mixer.music.set_volume(currentVolume)
    button = Button((1920//2-(400//2)), 900, 'BACK')
    clock = pygame.time.Clock()
    while True:
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
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
            button.update(event)

        screen.fill(black)
        if achievements[0] == 1:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,95,310,85))
            screen.blit(get_image('Assets\\ach1.png'), (1920//2-150, 100))
        else:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,95,310,85))
            screen.blit(get_image('Assets\\ach1locked.png'), (1920//2-150, 100))
            
        if achievements[1] == 1:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,195,310,85))
            screen.blit(get_image('Assets\\ach2.png'), (1920//2-150, 200))
        else:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,195,310,85))
            screen.blit(get_image('Assets\\ach2locked.png'), (1920//2-150, 200))
            
        if achievements[2] == 1:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,295,310,85))
            screen.blit(get_image('Assets\\ach3.png'), (1920//2-150, 300))
        else:
            pygame.draw.rect(screen, (120,120,120), (1920//2-154,295,310,85))
            screen.blit(get_image('Assets\\ach3locked.png'), (1920//2-150, 300))
        button.draw()
        pygame.display.flip()
        clock.tick(60)
#-------------------------------------------------------------------------------


# Settings
#-------------------------------------------------------------------------------
def settings():
    global menu_font
    global cheatCode
    cheatCode = ''
    global bg
    global bgnh
    canClick = True
    global windowMode
    global currentVolume
    pygame.mixer.music.set_volume(currentVolume)
    button = Button((1920//2-(400//2)), 900, 'BACK')
    options = [Option('FULLSCREEN', (725, 185)),
               Option('WINDOWED', (1025, 185)),
               Option('TOGGLE MUTE', (725, 385)),
               Option('-', (1050, 385)),
               Option('+', (1150, 385))]
    input_box1 = InputBox(725, 580, 140, 32)
    input_boxes = [input_box1]
    clock = pygame.time.Clock()
    while True:
        # process user input
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
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
            button.update(event)

            for box in input_boxes:
                box.handle_event(event)
        for box in input_boxes:
            box.update()
        if cheatCode != '':
            if cheatCode == 'all nighter':
                bg = get_image('Assets\\bbBGnight.png')
                bgnh = get_image('Assets\\bbBGnoHUDnight.png')
            cheatCode = ''
            
        for option in options:
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    global screen                    
                    if option.text == 'FULLSCREEN':
                        windowMode = 'FULLSCREEN\n'
                        screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
                    elif option.text == 'WINDOWED':
                        windowMode = 'RESIZABLE\n'
                        screen = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
                    with open('Assets\\settings.txt', 'w') as f:
                        f.write(windowMode + str(currentVolume))

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if canClick:
                        if option.text == '-':
                           currentVolume = pygame.mixer.music.get_volume()-0.1
                           pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()-0.1)
                        elif option.text == '+':
                           currentVolume = pygame.mixer.music.get_volume()+0.1
                           pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()+0.1)
                        if option.text == 'TOGGLE MUTE':
                            if currentVolume > 0:
                                currentVolume = 0
                                pygame.mixer.music.set_volume(0)
                            else:
                                currentVolume = 0.5
                                pygame.mixer.music.set_volume(0.5)
                                pygame.mixer.music.play(-1)
                        if currentVolume < 0:
                            currentVolume = 0
                        elif currentVolume > 1:
                            currentVolume = 1
                        with open('Assets\\settings.txt', 'w') as f:
                            f.write(windowMode + str(currentVolume))


                        canClick = False
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    canClick = True
            else:
                option.hovered = False

        screen.fill(black)
        message_display('VIDEO', 300, 200, 50, white)
        message_display('AUDIO', 300, 400, 50, white)
        message_display('EXTRA', 300, 600, 50, white)
        message_display(str(int((currentVolume+0.05)*10)*10), 1110, 400, 30, white)
        button.draw()
        for box in input_boxes:
            box.draw(screen)
        for option in options:
            option.draw()
        pygame.display.flip()
        clock.tick(60)
#-------------------------------------------------------------------------------

mainMenu()
