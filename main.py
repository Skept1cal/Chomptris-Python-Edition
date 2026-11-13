import pygame
pygame.init()
from constants import *
import defs
from defs import player, arena



def main():
    clock = pygame.time.Clock()
    pygame.key.start_text_input()

    while True:
        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                player.quit()

            if (player.disableInput): break
            if (event.type == pygame.TEXTINPUT):
                player.inputText(event.text)
            elif (event.type == pygame.KEYDOWN):
                if (event.key in player.keys.keys()):
                    player.resetKeys()
                    player.currPressed = player.keys[event.key]
                    player.currPressed.pressed = True
                    player.currPressed.func()
            elif (event.type == pygame.KEYUP):
                if (event.key in player.keys.keys()):
                    player.keys[event.key].reset()
                    player.currPressed = None

        player.disableInput = False

        if (player.currPressed != None):
            player.currPressed.frames += 1
            if (player.currPressed.firstPress):
                if (player.currPressed.frames >= KEY_DELAY):
                    player.currPressed.firstPress = False
                    player.currPressed.frames = 0
            else:
                if (player.currPressed.frames >= (FPS // KEY_FREQ)):
                    player.currPressed.func()
                    player.currPressed.frames = 0

        if (player.canMovePieces()):
            player.movementFrame += 1
            if (player.currToBeFrozen):
                player.lockDelayFrames += 1
                if (player.currPiece.canMoveDown()):
                    player.currToBeFrozen  = False
                    player.lockDelayFrames = 0
                elif (player.lockDelayFrames >= player.lockDelay):
                    arena.engrainPiece(player.currPiece)
                    defs.Piece.copy(defs.PIECES[PIECE_NULL], player.currPiece)

                    player.currToBeFrozen  = False
                    player.lockDelayFrames = 0
                    player.movementFrame   = 0

                    linesCleared = arena.clearLines()

                    player.score     += player.lineClearFormula(linesCleared)
                    player.lines     += linesCleared
                    player.currLines += linesCleared
                    if (linesCleared == 4): player.tetrisCount += 1

                    levelThreshold: int = LEVEL_THRESHOLD * (int(player.firstLevel) * player.startLevel + 1)
                    if (player.currLines >= levelThreshold):
                        player.level     += 1
                        player.score     += player.levelUpFormula()
                        player.updateNonScore()
                        player.currLines -= levelThreshold
                        player.firstLevel = False

                        player.levelUpAnimation()
                        if (player.level >= REBIRTH_THRESHOLD):
                            player.level = 0

                    player.getNextPiece()
                    player.score            += player.pieceFreezeFormula()
                    player.swappedThisRound  = False
                    if (player.currPiece.collides()):
                        arena.renderGame()
                        player.gameOver()

            if (not player.currPiece.canMoveDown()): player.currToBeFrozen = True
            if (player.movementFrame >= player.speed):
                player.currPiece.moveDown()
                player.movementFrame = 0

        if (player.mainMenu):
            player.renderMenu()
        else:
            arena.renderGame(gameOver = not player.gameOn)

        clock.tick(FPS)

main()