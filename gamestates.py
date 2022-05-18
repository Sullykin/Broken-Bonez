import pygame
from sprites import *
from utils import *
import string
import random
import sys
from datetime import datetime

class GameState:
    def __init__(self, game):
        self.game = game
        self.active = True
        self.is_obscured = False

    def resume(self):
        pass

    def pause(self):
        pass

    def obscure(self):
        self.is_obscured = True

    def reveal(self):
        self.is_obscured = False

    def update(self):
        pass

    def draw(self):
        pass

    def send_frame(self):
        pygame.display.update()
        self.game.clock.tick(self.game.fps)
        self.game.framecount += 1

    def check_universal_events(self, pressed_keys, event):
        quit_attempt = False
        if event.type == pygame.QUIT:
            quit_attempt = True
        elif event.type == pygame.KEYDOWN:
            alt_pressed = pressed_keys[pygame.K_LALT] or \
                            pressed_keys[pygame.K_RALT]
            if event.key == pygame.K_F4 and alt_pressed:
                quit_attempt = True
        if quit_attempt:
            pygame.quit()
            sys.exit()


class SceneBase(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.windlines = []
        for x in range(10):
            self.windlines.append(Wind(game))
        self.pebbles = []
        for x in range(10):
            self.pebbles.append(Pebble(game))

    def update_bg(self):
        # call updates on all objects
        for line in self.windlines:
            line.update()
        for pebble in self.pebbles:
            pebble.update()

    def draw_bg(self):
        self.game.screen.blit(self.game.blit_bg, (0,0))
        if self.game.hud:
            self.game.screen.blit(get_image("Assets/images/hud.png"), (0,0))
        for pebble in self.pebbles:
            pebble.draw()
        for line in self.windlines:
            line.draw()


class MainMenu(SceneBase):
    def __init__(self, game):
        super().__init__(game)

        # mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        # object initialization
        self.player = Player(game)
        self.buttons = [Button(game, (1920//2-(418//2))-300, 1080//2+200, 'SETTINGS', Settings),
                   Button(game, (1920//2-(418//2))+300, 1080//2+200, 'QUIT'),
                   Button(game, (1920//2-(418//2))+300, 1080//2+50, 'LEADERBOARD', Leaderboard),
                   Button(game, (1920//2-(418//2))-300, 1080//2+50, 'ACHIEVEMENTS', Achievements)]

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            self.check_universal_events(pressed_keys, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game.gsm.switch(MainScene(self.game))

            for button in self.buttons:
                if button.update(event):
                    if button.gamestate == Settings:
                        self.game.gsm.game_state_stack.append(Settings(self.game))
                    else:
                        self.game.gsm.switch(button.gamestate(self.game))
            
        self.update_bg()

    def draw(self):
        # Environment
        self.draw_bg()
        self.player.draw()

        # HUD
        pygame.draw.rect(self.game.screen, (0,0,0), (0,0,1920,265))
        draw_text(self.game.screen, 'BROKEN BONEZ', (1920//2, 130), (255,255,0), 220)
        draw_text(self.game.screen, 'PRESS SPACE TO START', (1920//2, 1080//2-120), (0,0,0), 100)
        for button in self.buttons:
            button.draw()

        # Display the frame
        self.send_frame()


class MainScene(SceneBase):
    def __init__(self, game, lives=0, score=0, timeLeft=60):
        super().__init__(game)
        self.score = score
        highscores, self.entries = getScores()
        self.highscore = highscores[-1]
        self.timeLeft = timeLeft
        self.lives = lives
        self.animations = []

        # mouse
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        # object initialization
        self.player = Player(game)
        self.ramp = Ramp(game)
        self.scoreDisplay = Score(game)

        # trick flags & vars
        self.trick_key = random.choice(string.ascii_uppercase)
        self.req = random.choice([3,5,7])
        self.multiplierFlag = False
        self.multiplier = 1
        self.tricks = 0
        self.trick = False
        self.trickScore = None
        self.crash = False
        self.frameJumped = None
        self.game.hud = True

        # Animations
        self.trick1animation = [
                        'Assets/Animations/trick1/1.png',
                        'Assets/Animations/trick1/2.png',
                        'Assets/Images/bbm.png'
                        ]

        self.trick2animation = [
                        'Assets/Animations/trick2/1.png',
                        'Assets/Animations/trick2/2.png',
                        'Assets/Animations/trick2/3.png',
                        'Assets/Images/bbm.png'
                        ]

        self.trick3animation = [
                        'Assets/Animations/trick3/1.png',
                        'Assets/Animations/trick3/2.png',
                        'Assets/Animations/trick3/3.png',
                        'Assets/Animations/trick3/4.png',
                        'Assets/Animations/trick3/5.png',
                        'Assets/Animations/trick3/6.png',
                        'Assets/Animations/trick3/7.png',
                        'Assets/Images/bbm.png'
                        ]

        self.crashAnimation = [
                        'Assets/Animations/crash/1.png',
                        'Assets/Animations/crash/2.png',
                        'Assets/Animations/crash/2.png'
                        ]

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            self.check_universal_events(pressed_keys, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.gsm.game_state_stack.append(Settings(self.game))

                elif self.player.isJumping and not self.animations:
                    if pygame.key.name(event.key).upper() == self.trick_key:
                        self.player.trickcount += 1

                        # trick complete
                        if self.player.trickcount >= self.req:
                            self.multiplierFlag = True
                            self.trick_key = ''
                            if self.req == 7: self.trick = Trick(self.game, 4, self.trick3animation, 27000)
                            elif self.req == 5: self.trick = Trick(self.game, 10, self.trick2animation, 23000)
                            else: self.trick = Trick(self.game, 15, self.trick1animation, 19000)
                            self.animations.append(self.trick)

                    # wrong key pressed
                    else:
                        self.crash = Crash(self.game, [30,40,80], self.crashAnimation)
                        self.animations.append(self.crash)

        # call updates on all objects
        self.update_bg()
        self.player.update()
        self.ramp.update()

        # in air
        if self.player.isJumping:
            if self.frameJumped is None: 
                self.frameJumped = self.game.framecount

            # check multiplier
            if (self.game.framecount-self.frameJumped) % (60*3) == 0 and self.tricks < 3:
                # reset trick
                self.trick_key = random.choice(string.ascii_uppercase)
                self.player.trickcount = 0
                self.req = random.choice([3,5,7])
                if self.multiplierFlag:
                    self.multiplierFlag = False
                    if self.multiplier < 5:
                        self.multiplier += 1
                else:
                    self.multiplier = 1
        else:
            self.tricks = 0
            self.frameJumped = None

        # animations
        if self.animations:
            self.animations[0].animate(self.game.framecount)

            if self.trick in self.animations:
                if self.trick.done:
                    self.tricks += 1
                    self.trickScore = self.trick.base_score*self.multiplier
                    self.score += self.trickScore
                    self.animations.remove(self.trick)
                    self.trick = False


            elif self.crash in self.animations:
                self.game.hud = False
                if self.crash.done:
                    if self.lives == 0:
                        self.game.gsm.switch(GameOver(self.game, self.score))
                    else:
                        self.lives -= 1
                        self.score -= 10000
                        self.game.gsm.switch(MainScene(self.game, lives=self.lives, score=self.score, timeLeft=self.timeLeft))
                    self.animations.remove(self.crash)

        # time
        if not self.game.framecount % 60:
            self.timeLeft -= 1
            if self.timeLeft == 0:
                self.game.gsm.switch(GameOver(self.game, self.score))

    def draw(self):
        # Environment
        self.draw_bg()
        self.ramp.draw()
        self.player.draw()

        # HUD
        if not self.player.isJumping and not self.crash:
            draw_text(self.game.screen, 'PLAYER 1', (350, 50), size=50)
            draw_text(self.game.screen, str(self.score), (350, 125), size=50)
            draw_text(self.game.screen, 'HI-SCORE', (950, 50), size=50)
            draw_text(self.game.screen, str(self.highscore), (950, 125), size=50)
            draw_text(self.game.screen, str(self.timeLeft), (1870, 220), size=50)
            for x in range(self.multiplier):
                self.game.screen.blit(get_image('Assets/Images/bones.png'), ((135*x)+1200, 30))
            for x in range(self.lives):
                self.game.screen.blit(get_image('Assets/Images/helmet.png'), ((100*x)+20, 1000))
        else:
            # key to press
            if not self.animations and self.trick_key:
                self.game.screen.blit(get_image('Assets/Images/blank_key.png'), (self.player.x-25,220))
                draw_text(self.game.screen, self.trick_key, (self.player.x-25+24, 220+20), size=25)
            # theater mode borders
            if not self.crash:
                pygame.draw.rect(self.game.screen, (0,0,0), (0,0,1920,140))
                pygame.draw.rect(self.game.screen, (0,0,0), (0,1080-500,1920,500))

        # Trick count and score
        self.scoreDisplay.animate(self.player.x, self.player.y, self.trickScore)
        self.trickScore = None
        if 0 < self.player.trickcount < self.req:
            self.game.screen.blit(get_image('Assets/Images/countBubble.png'), (self.player.x-195, self.player.y-140))
            draw_text(self.game.screen, str(self.player.trickcount), (self.player.x-100, self.player.y-50), size=75)

        self.send_frame()


class GameOver(SceneBase):
    def __init__(self, game, score):
        super().__init__(game)
        self.game.hud = True  # Re-enable for edge case

        self.score = score
        self.highscores, self.entries = getScores()
        self.date = datetime.date(datetime.now())

        if self.score < 0: game.achievements[0] = 1
        if self.score >= 1279000: game.achievements[1] = 1
        if self.score >= 1300000: game.achievements[2] = 1
        with open('Assets/Misc/achievements.txt', 'w') as f:
            f.write(str(game.achievements[0]) + '\n' + str(game.achievements[1]) + '\n' + str(game.achievements[2]) + '\n')

        # re-enable mouse
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        # new record initials
        self.blanks = ['_', '_', '_']

        # object initialization
        self.player = Player(game)

        # Buttons
        self.buttons = [Button(game, (1920//2-(418//2))-300, 1080//2+250, 'MAIN MENU'),
                        Button(game, (1920//2-(418//2))+300, 1080//2+250, 'QUIT')]
        if any(i < self.score for i in self.highscores) or len(self.entries) < 5:
            self.buttons.append(Button(game, 1920//2-(418//2), 1080//2+100, 'SUBMIT'))

    def update(self):
            pressed_keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                self.check_universal_events(pressed_keys, event)
                if event.type == pygame.KEYDOWN:

                    # check if score earns a spot in leaderboard
                    if any(i < self.score for i in self.highscores) or len(self.entries) < 5:
                        blanks_num = self.blanks.count('_')
                        if event.key == pygame.K_LEFT or event.key == pygame.K_BACKSPACE:
                            self.blanks = ['_','_','_']
                        elif blanks_num > 0 and pygame.key.name(event.key).lower() in string.ascii_lowercase:
                            self.blanks[3-blanks_num] = pygame.key.name(event.key).upper()
                        elif event.key == pygame.K_RETURN:
                            with open('Assets/Misc/highscores.txt', 'a') as f:
                                f.write(''.join(self.blanks)+'     '+str(self.score)+'     '+str(self.date)+'\n')
                            self.game.gsm.switch(MainMenu(self.game))

                for button in self.buttons:
                    if button.update(event):
                        if button.text == 'SUBMIT':
                            with open('Assets/Misc/highscores.txt', 'a') as f:
                                f.write(''.join(self.blanks)+'     '+str(self.score)+'     '+str(self.date)+'\n')
                        self.game.gsm.switch(MainMenu(self.game))

            self.update_bg()

    def draw(self):
        self.draw_bg()
        # HUD
        draw_text(self.game.screen, 'PLAYER 1', (350, 50), size=50)
        draw_text(self.game.screen, str(self.score), (350, 125), size=50)
        draw_text(self.game.screen, 'HI-SCORE', (950, 50), size=50)
        draw_text(self.game.screen, str(self.highscores[0]), (950, 125), size=50)
        if any(i < self.score for i in self.highscores) or len(self.entries) < 5:
            if len(self.entries) == 5:
                with open('Assets/Misc/highscores.txt', 'r') as f:
                    lines = f.readlines()
                    lines = lines[:-1]
                with open('Assets/Misc/highscores.txt', 'w') as f:
                    for line in lines:
                        f.write(line)
                self.highscore, self.entries = getScores()
            draw_text(self.game.screen, 'NEW HI-SCORE!', (1920//2, 1080//2-260), size=150, color=(0,0,0))
            i = -125
            for blank in self.blanks:
                draw_text(self.game.screen, blank, (1920//2+i, 1080//2+20), size=120)
                i += 125
            draw_text(self.game.screen, str(self.score), (1920//2, 1080//2-120), size=150, color=(255,0,0))
        else:
            draw_text(self.game.screen, 'GAMEOVER', (1920//2, 1080//2-200), size=150, color=(255,0,0))
            draw_text(self.game.screen, str(self.score), (1920//2, 1080//2-25), size=150)
        self.game.screen.blit(get_image('Assets/Images/bones.png'), (1200, 30))
        if self.score < 0: self.game.screen.blit(get_image('Assets/Images/ach1.png'), (1920-300,1080-75))
        if self.score >= 1279000: self.game.screen.blit(get_image('Assets/Images/ach2.png'), (1920-300,1080-75))
        if self.score >= 1300000: self.game.screen.blit(get_image('Assets/Images/ach3.png'), (1920-300,1080-155))

        self.player.draw()
        for button in self.buttons:
            button.draw()
        self.send_frame()


class Leaderboard(GameState):
    def __init__(self, game):
        super().__init__(game)
        highscores, self.entries = getScores()
        self.button = Button(self.game, (1920//2-(400//2)), 900, 'BACK', MainMenu)

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            self.check_universal_events(pressed_keys, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if self.button.update(event):
                self.game.gsm.switch(self.button.gamestate(self.game))

    def draw(self):
        self.game.screen.fill((0,0,0))
        draw_text(self.game.screen, 'HI-SCORES', (1920//2, 80), size=100)
        for entry in self.entries:
            draw_text(self.game.screen, entry, (1920//2, 220+(80*self.entries.index(entry))), size=60, color=(255,255,255))#, 'Assets/Misc/ipaexg.ttf', False)
        self.button.draw()
        self.send_frame()


class Achievements(GameState):
    def __init__(self, game):
        super().__init__(game)
        # refresh achievements
        self.achievements = []
        with open('Assets/Misc/achievements.txt','r') as f:
            for entry in f.readlines():
                self.achievements.append(int(entry))

        self.button = Button(game, (1920//2-(400//2)), 900, 'BACK', MainMenu)

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            self.check_universal_events(pressed_keys, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if self.button.update(event):
                self.game.gsm.switch(self.button.gamestate(self.game))

    def draw(self):
        self.game.screen.fill((0,0,0))
        count = 0
        for entry in self.achievements:
            count += 1
            pygame.draw.rect(self.game.screen, (120,120,120), (1920//2-154,-5+(100*count),310,85))
            self.game.screen.blit(get_image(f'Assets/Images/ach{str(count)}.png'), (1920//2-150, 100*count))
            if entry:
                self.game.screen.blit(get_image(f'Assets/Images/ach_star.png'), (1920//2-150, 100*count))
        self.button.draw()
        self.send_frame()
        

class Settings(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.cheat_code_activated = 120
        self.canClick = True

        # Buttons
        self.prev_gamestate = self.game.gsm.game_state_stack[-1]
        self.prev_gamestate.is_obscured = True
        self.prev_gamestate.active = False
        if isinstance(self.prev_gamestate, MainMenu):
            self.buttons = [Button(game, (1920//2-(400//2)), 900, 'BACK')]
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
            self.buttons = [Button(game, (1920//2-(400//2)-300), 900, 'BACK'),
                            Button(game, (1920//2-(400//2))+300, 900, 'MAIN MENU', MainMenu)]
        
        # Settings inputs
        self.options = [Option(game, 'FULLSCREEN', (725, 185)),
                        Option(game, 'WINDOWED', (1025, 185)),
                        Option(game, 'TOGGLE MUTE', (725, 385)),
                        Option(game, '-', (1050, 385)),
                        Option(game, '+', (1150, 385))]
        self.input_boxes = [InputBox(game, 725, 580, 140, 32)]

    def update(self):
        pressed_keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            self.check_universal_events(pressed_keys, event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.gsm.game_state_stack.pop()
                    self.prev_gamestate.is_obscured = False
                    self.prev_gamestate.active = True

            for button in self.buttons:
                if button.update(event):
                    if not button.gamestate == MainMenu:
                        self.game.gsm.game_state_stack.pop()
                        self.prev_gamestate.is_obscured = False
                        self.prev_gamestate.active = True
                    else:
                        self.game.gsm.game_state_stack = [MainMenu(self.game)]

            for box in self.input_boxes:
                box.handle_event(event)

            # Extras       
            for box in self.input_boxes:
                box.update()
            if self.game.cheatCode:
                if self.game.cheatCode == 'all nighter':
                    self.game.bg = get_image('Assets/Images/bg_night.png')
                    self.blit_bg = self.game.bg
                    self.cheat_code_activated = 0
                self.game.cheatCode = ''

            # All other settings
            for option in self.options:
                if option.rect.collidepoint(pygame.mouse.get_pos()):
                    option.hovered = True
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:                   
                        if option.text == 'FULLSCREEN':
                            self.game.windowMode = 'FULLSCREEN\n'
                            self.game.screen = pygame.display.set_mode((1920,1080), pygame.FULLSCREEN)
                        elif option.text == 'WINDOWED':
                            self.game.windowMode = 'RESIZABLE\n'
                            self.game.screen = pygame.display.set_mode((1920,1080), pygame.RESIZABLE)
                        with open('Assets/Misc/settings.txt', 'w') as f:
                            f.write(self.game.windowMode + str(self.game.volume))

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.canClick:
                            if option.text == '-':
                                self.game.volume = pygame.mixer.music.get_volume()-0.1
                                pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()-0.1)
                            elif option.text == '+':
                                self.game.volume = pygame.mixer.music.get_volume()+0.1
                                pygame.mixer.music.set_volume(pygame.mixer.music.get_volume()+0.1)
                            if option.text == 'TOGGLE MUTE':
                                if self.game.volume > 0:
                                    self.game.volume = 0
                                    pygame.mixer.music.set_volume(0)
                                else:
                                    self.game.volume = 0.5
                                    pygame.mixer.music.set_volume(0.5)
                            if self.game.volume < 0:
                                self.game.volume = 0
                            elif self.game.volume > 1:
                                self.game.volume = 1
                            with open('Assets/Misc/settings.txt', 'w') as f:
                                f.write(self.game.windowMode + str(self.game.volume))
                            self.canClick = False
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.canClick = True
                else:
                    option.hovered = False

    def draw(self):
        self.game.screen.fill((0,0,0))
        draw_text(self.game.screen, 'VIDEO', (300, 200), size=50, color=(255,255,255))
        draw_text(self.game.screen, 'AUDIO', (300, 400), size=50, color=(255,255,255))
        draw_text(self.game.screen, 'EXTRA', (300, 600), size=50, color=(255,255,255))
        draw_text(self.game.screen, str(int((self.game.volume+0.05)*10)*10), (1110, 400), size=30, color=(255,255,255))
        if self.cheat_code_activated < 120:
            draw_text(self.game.screen, "New extra unlocked!", (1070, 598), size=20, color=(255,255,0))
            self.cheat_code_activated += 1
        for button in self.buttons:
            button.draw()
        for box in self.input_boxes:
            box.draw()
        for option in self.options:
            option.draw()
        self.send_frame()