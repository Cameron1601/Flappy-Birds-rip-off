import sys
import pygame
import random
from pygame.locals import *

FPS = 32
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8  # Base image
GAME_SPRITES = {}
GAME_SOUNDS = {}
PLAYER = 'resources\SPRITES\\bird.png'
BACKGROUND = 'resources\SPRITES\\bg.jpeg'
PIPE = 'resources\SPRITES\pipe.png'

def welcomeScreen():

    # Display interactive welcome screen

    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2
    messagex = int(SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0

    # Making a play button from a rectangle (x,y,length,breadth)
    playbutton = pygame.Rect(108, 222, 68, 65)

    # allow to quit game
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

            # make cursor show again if moved outside play button
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            if pygame.mouse.get_pos()[0] and pygame.mouse.get_pos()[0] < playbutton[0] + playbutton[2]:
                if pygame.mouse.get_pos()[1] > playbutton[1] and pygame.mouse.get_pos()[1]+ playbutton[3]:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            if playbutton.collidepoint(pygame.mouse.get_pos()): # checking if mouse collided with play button

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Checking if it was clicked
                    mainGame()

            else:
                SCREEN.blit(GAME_SPRITES['background'],(0,0))
                SCREEN.blit(GAME_SPRITES['player'],(playerx,playery))
                SCREEN.blit(GAME_SPRITES['message'],(messagex,messagey))
                SCREEN.blit(GAME_SPRITES['base'], (basex,GROUNDY))
                pygame.display.update()
                FPSCLOCK.tick(FPS)

def mainGame():
    # Variables
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0

    # Creating the pipes
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # Upper pipe
    upperPipes = [
        {'x':SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x':SCREENWIDTH + 200 + (SCREENWIDTH/2), 'y': newPipe2[0]['y']}
    ]

    # Lower Pipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']}
    ]

    pipeVelX = -4 # Pipe velocity x axis
    playerVelY = -9 # pipe velocity y axis
    playerMaxVelY = 10 # Player max velocity
    playerMinVelY = -8 # Player min Velocity
    playerAccY = 1

    playerFlapAccv = -8 # Velocity while flapping
    playerFlapped = False # only true when  bird is flapping

    while True:

        for event in pygame.event.get():

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP): # Check if player pressed
                if playery > 0:  # If Y is greater than 0, update players velocity
                    playerVelY = playerFlapAccv
                    playerFlapped = True  # change False to true and play noise
                    GAME_SOUNDS['wing'].play()

            crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)  # True if player crashes
            if crashTest:
                return

        # Score check
        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2  # Mid-position of player and pipe
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1  # increase score by 1 and play sound
                print(f"Your score is {score}")
                GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:  # Checks if bird touches the ground layer
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)  # value will be 0 if touches

        # move pipes to the left
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when other is leaving screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # When pipe leaves screen delete it
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # blit sprites
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide (playerx,playery,upperPipes,lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        pygame.mixer.music.stop()
        gameOver()

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width() - 20):
            GAME_SOUNDS['hit'].play()
            print(playerx, pipe['x'],)
            pygame.mixer.music.stop()
            gameOver()

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x'])<GAME_SPRITES['pipe'][0].get_width()-20:
            GAME_SOUNDS['hit'].play()
            pygame.mixer.music.stop()
            gameOver()

    return False


def getRandomPipe():

    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 4.5
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # Upper Pipes
        {'x': pipeX, 'y': y2}  # Lower Pipes
    ]
    return pipe


def gameOver():

    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
    pygame.display.set_caption('Flappy Bird With Sameer')
    GAME_SPRITES['OVER'] = pygame.image.load('resources/SPRITES/gameover.png').convert_alpha()
    GAME_SPRITES['RETRY'] = pygame.image.load('resources/SPRITES/retry.png').convert_alpha()
    GAME_SPRITES['HOME'] = pygame.image.load('resources/SPRITES/Home.png').convert_alpha()
    SCREEN.blit(GAME_SPRITES['background'], (0, 0))
    SCREEN.blit(GAME_SPRITES['base'],(0, GROUNDY))
    SCREEN.blit(GAME_SPRITES['OVER'],(0, 0))
    SCREEN.blit(GAME_SPRITES['RETRY'],(30, 220))
    SCREEN.blit(GAME_SPRITES['HOME'],(30, 280))

    pygame.display.update()

    while True:
        for event in pygame.event.get():

            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and event.key == K_SPACE:
                mainGame()

            # RETRY BUTTON
            if pygame.mouse.get_pos()[0] > 30 and pygame.mouse.get_pos()[0] < 30 + GAME_SPRITES['RETRY'].get_width():
                if pygame.mouse.get_pos()[1] > 220 and pygame.mouse.get_pos()[1] < 220 + GAME_SPRITES['RETRY'].get_height():
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                        mainGame()

            # HOME BUTTON
            if pygame.mouse.get_pos()[0] > 30 and pygame.mouse.get_pos()[0] < 30 + GAME_SPRITES['HOME'].get_width():
                if pygame.mouse.get_pos()[1] > 280 and pygame.mouse.get_pos()[1] < 280 + GAME_SPRITES['HOME'].get_height():
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        welcomeScreen()
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


if __name__ == "__main__":

    pygame.init() ##modules of pygame
    FPSCLOCK = pygame.time.Clock() # allows control over game fps
    pygame.display.set_caption('Flappy Bird With Sameer') # caption of the game

#Srite Time

    GAME_SPRITES['numbers']= (
     pygame.image.load('resources\SPRITES\\0.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\1.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\2.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\3.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\4.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\5.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\6.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\7.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\8.png'). convert_alpha(),
     pygame.image.load('resources\SPRITES\\9.png'). convert_alpha(),

    )

    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert_alpha()
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    GAME_SPRITES['message'] = pygame.image.load('resources\SPRITES\message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('resources\SPRITES\\base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (

    pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(),180),  # Rotate the pipe 180 deg
    pygame.image.load(PIPE).convert_alpha()  # used to lower pipes
    )
    # All audio
    GAME_SOUNDS['die'] = pygame.mixer.Sound('resources\AUDIO\die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('resources\AUDIO\hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('resources\AUDIO\point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('resources\AUDIO\swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('resources\AUDIO\wing.wav')
    while True:
        welcomeScreen()  # Shows a welcome screen to the user until they start the game
        mainGame()  # This is our main game function
