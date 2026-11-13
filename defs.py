from __future__ import annotations
from collections.abc import Callable
from typing import Hashable
import pygame
import random
import math
import time
import numpy as np
import json
import base64
import binascii
import os
from typing import Any

from constants import *
import utils



class Key:
    def __init__(self, func: Callable[[], None]):
        self.pressed:    bool = False
        self.func             = func
        self.firstPress: bool = True
        self.frames:     int  = 0

    def reset(self):
        self.pressed    = False
        self.firstPress = True
        self.frames     = 0

    @staticmethod
    def bindKey(obj: dict[Hashable, Key], keys: list[Hashable], func: Callable[[], None]) -> None:
        for key in keys:
            obj[key] = Key(func)



class Pos:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y



class Button:
    def __init__(
            self,
            label:        str,
            *,
            type:         int                       = BTN_TYPE_TRIG,
            func:         Callable[[], None] | None = None,
            confPrompt:   str | None                = None,
            buffer:       list[str] | None          = None,
            bufferSize:   int                       = 0,
            cycle:        dict[str, Any] | None     = None,
            cyclePos:     int | None                = None,
            marginTop:    int                       = 0,
            marginBottom: int                       = 0
    ):
        self.label        = label
        self.type         = type
        self.func         = func
        self.confPrompt   = confPrompt
        self.buffer       = buffer
        self.bufferSize   = bufferSize
        self.cycle        = cycle
        self.cyclePos     = cyclePos
        self.marginTop    = marginTop
        self.marginBottom = marginBottom

    @staticmethod
    def addConfPrompt(func: Callable[[], None]) -> Callable[[], None]:
        def extended() -> None:
            if (not player.confirmation):
                player.confirmation = True
            else:
                player.confirmation = False
                func()
        
        return extended

    @staticmethod
    def startGame() -> None:
        player.mainMenu = False
        player.gameOn   = True
        player.updateFromInput()
        player.updateNonScore()

    @staticmethod
    def printHelpText() -> None:
        utils.clearterm()
        print(
            ""
            "---------- HOW TO PLAY ----------\r\n"

            "\r\n----- TERMINOLOGY -----\r\n"

            "\r\n- Btn cursor     (Shortening of \"Button cursor\") Cursor in main menu,"
            "\r\n                 used to navigate between individual buttons."
            "\r\n- Input cursor   Cursor in main menu,"
            "\r\n                 used to navigate between individual characters/digits within an input field."

            "\r\n- Tick           One forced movement downward."
            "\r\n                     By default, this is 1 per second, becoming faster as the game goes on.\r\n"

            "\r\n- Lock-delay     Amount of time it takes for a falling piece to be frozen.\r\n"

            "\r\n----- MENU CONTROLS -----\r\n"

            "\r\n-    UP          If outside an input field, move button cursor up"
            "\r\n-  DOWN          If outside an input field, move button cursor down"
            "\r\n- RIGHT          If inside an input field, move input cursor right"
            "\r\n-  LEFT          If inside an input field, move input cursor left\r\n"

            "\r\n- ENTER          Select/deselect a button\r\n"

            "\r\n----- GAMEPLAY CONTROLS -----\r\n"

            "\r\n-  DOWN/S        Move current piece down."
            "\r\n- RIGHT/D        Move current piece right."
            "\r\n-  LEFT/A        Move current piece left.\r\n"

            "\r\n- X/N/UP/W       Rotate 90 degrees clockwise (right)."
            "\r\n-    Y/Z/B       Rotate 90 degrees counter-clockwise (left).\r\n"

            "\r\n- C/M            Hold or swap to a held piece.\r\n"

            "\r\n                     If there is no held piece, the current piece is stored and the next one grabbed."
            "\r\n                     If there is a held piece, the current piece is swapped with the held piece."
            "\r\n                     In both cases, the position of the current piece is reset to the top of the arena.\r\n"

            "\r\n                     There can only be one swap/hold per round (until the current piece is frozen).\r\n"

            "\r\n----- OTHER CONTROLS -----\r\n"

            "\r\n- SPACE          Pause/Resume the game if not in main menu."
            "\r\n-    F1          Restart the game if not in main menu."
            "\r\n                     This does not reset anything input within the main menu."
            "\r\n- ESC            Go to main menu.\r\n"

            "\r\n- F10            Shortcut to exit the game.\r\n"

            "\r\n----- MECHANICS -----\r\n"

            "\r\n- Every tick, the current piece falls by 1 tile."
            "\r\n  When it reaches the ground,"
            "\r\n  it remains movable for the duration of the lock-delay before being frozen. When a piece is frozen,"
            "\r\n  a new one spawns in its place, which can be seen from the next-piece display.\r\n"

            "\r\n  If the piece is rotated into a position which is higher than the ground,"
            "\r\n  the piece won't be frozen until reaching the ground again and the lock-delay passing.\r\n"

            "\r\n- If a piece is frozen and it fills one or multiple lines, those lines are cleared,"
            "\r\n  and everything above them falls down by the number of lines that were cleared."
            "\r\n  Every 10 cleared lines, there is a level-up, which increases the speed at which a piece falls.\r\n"

            "\r\n- Every piece frozen is worth 50 score.\r\n"

            "\r\n  The amount of score gained from line clears is based on the formula:"
            "\r\n  (CLEARED ^ 2) * 100 * (1 + 0.075 * LEVEL),"
            "\r\n  where CLEARED is the number of lines that were just cleared, and LEVEL is the current level."
            "\r\n  The score is always rounded down to the nearest integer.\r\n"

            "\r\n  This means possible line-clears are worth the following:"
            "\r\n  1 Line:   100-> 107-> 115...;"
            "\r\n  2 Lines:  400-> 430-> 460...;"
            "\r\n  3 Lines:  900-> 967->1035...;"
            "\r\n  4 Lines: 1600->1720->1840....\r\n"

            "\r\n  The amount of score gained from level-ups is based on the formula:"
            "\r\n  200 * LEVEL, where LEVEL is the current level AFTER advancing.\r\n"

            "\r\n  This means the first few level-ups are worth the following:"
            "\r\n  0->1: 200;"
            "\r\n  1->2: 400;"
            "\r\n  2->3: 600.\r\n"

            "\r\n  All three of these sources of score can happen within a single tick.\r\n"

            "\r\n- If a piece spawns in and immediately overlaps any frozen piece, the game ends.\r\n"

            "\r\n----- LOGGING -----\r\n"

            "\r\n- If enabled, a statistics log is saved at the end of every run."
            "\r\n  The \"%s\" button sorts these logs based on the selected criteria,"
            "\r\n  saving it to a file named \"%s\"."
            "\r\n  Restarting does not create logs.\r\n"

            "\r\n  Internally, these logs are stored in \"%s\"."
            "\r\n  Attempting to edit this file will result in near-guaranteed data-loss,"
            "\r\n  as well as potential crashes.\r\n"

            "\r\n- The \"%s\" button will clear the entire history of logs.\r\n"

            "\r\n- There is no limit to how many logs there can be."
            %
            (
                buttons[BTN_EXPORT_LOG].label,
                EXTRN_LOG_FNM,
                INTRN_LOG_FNM,
                buttons[BTN_CLEAR_LOG].label
            )
        )
        exit(0)

    @staticmethod
    def quitGame() -> None:
        player.quit()

    @staticmethod
    def exportLog() -> None:
        if (player.log.unsorted):
            btnSortBy: Button = buttons[BTN_SORT_BY]
            btnSortOrder: Button = buttons[BTN_SORT_ORDER]
            if (
                btnSortBy    == None or btnSortBy.cycle    == None or btnSortBy.cyclePos    == None or
                btnSortOrder == None or btnSortOrder.cycle == None or btnSortOrder.cyclePos == None
            ): return
            player.log.sort(
                sortBy   = list(btnSortBy.cycle.values())[btnSortBy.cyclePos],
                reversed = list(btnSortOrder.cycle.values())[btnSortOrder.cyclePos]
            )
        player.log.export()

    @staticmethod
    @addConfPrompt
    def clearLog() -> None:
        player.log.clear()



class Arena:
    def __init__(self):
        self.arena: list[list[int]] = [[0] * ARENA_COLS for _ in range(ARENA_ROWS)]
    
    def engrainPiece(self, piece: Piece) -> None:
        for i, iv in enumerate(piece.shape):
            for j, jv in enumerate(iv):
                if (not jv): continue

                apos: Pos = piece.FPOStoAPOS(i, j)
                self.arena[apos.y][apos.x] = jv 

    def renderGame(self, levelUp: bool | None = None, inGameOverSequence: bool | None = None, gameOver: bool | None = None) -> None:
        from font import renderFont

        screen.fill(BLACK)

        if (player.paused):
            renderFont(
                screen,
                PAUSED_STR,
                Pos(0, 0),
                False
            )
            pygame.display.flip()
            return

        #region Render main arena
        for i, iv in enumerate(self.arena):
            for j, jv in enumerate(iv):
                if (not inGameOverSequence and not gameOver and player.currPiece.APOSInPiece(i, j)):
                    fpos = player.currPiece.APOStoFPOS(i, j)
                    if (not player.currPiece.shape[fpos.y][fpos.x]): continue

                    pygame.draw.rect(
                        screen,
                        player.currPiece.color,
                        pygame.Rect(
                            j * CELL_SIZE,          # x
                            i * CELL_SIZE,          # y
                            CELL_SIZE - GRID_WIDTH, # width
                            CELL_SIZE - GRID_WIDTH  # height
                        )
                    )

                elif (jv):
                    pygame.draw.rect(
                        screen,
                        PIECES[jv].color,
                        pygame.Rect(
                            j * CELL_SIZE,          # x
                            i * CELL_SIZE,          # y
                            CELL_SIZE - GRID_WIDTH, # width
                            CELL_SIZE - GRID_WIDTH  # height
                        )
                    )
        #endregion
        
        #region Render arena frame
        pygame.draw.rect(
            screen,
            WHITE,
            pygame.Rect(
                ARENA_COLS  * CELL_SIZE, # x
                0,                        # y
                GRID_WIDTH,               # width
                ARENA_ROWS * CELL_SIZE  # height
            )
        )
        pygame.draw.rect(
            screen,
            WHITE,
            pygame.Rect(
                0,                                     # x
                ARENA_ROWS * CELL_SIZE,              # y
                ARENA_COLS  * CELL_SIZE + GRID_WIDTH, # width
                GRID_WIDTH                             # height
            )
        )
        #endregion

        #region Render next and held piece
        if (not inGameOverSequence and not gameOver):
            renderFont(
                screen,
                "NEXT:",
                Pos(
                    x = NEXT_PIECE_START_X,
                    y = NEXT_PIECE_START_Y
                ),
                False
            )
            noLeftPadding: bool = player.nextPiece.noLeftPadding()
            for i, iv in enumerate(player.nextPiece.shape):
                for j, jv in enumerate(iv):
                    if (not jv): continue

                    pygame.draw.rect(
                        screen,
                        player.nextPiece.color,
                        pygame.Rect(
                            NEXT_PIECE_START_X + (j + int(noLeftPadding))      * CELL_SIZE,
                            NEXT_PIECE_START_Y + (i + NEXT_PIECE_START_MARGIN) * CELL_SIZE,
                            CELL_SIZE - GRID_WIDTH,
                            CELL_SIZE - GRID_WIDTH
                        )
                    )
            
            renderFont(
                screen,
                "HELD:",
                Pos(
                    x = HELD_PIECE_START_X,
                    y = HELD_PIECE_START_Y
                ),
                False
            )
            noLeftPadding: bool = player.heldPiece.noLeftPadding()
            for i, iv in enumerate(player.heldPiece.shape):
                for j, jv in enumerate(iv):
                    if (not jv): continue

                    pygame.draw.rect(
                        screen,
                        player.heldPiece.color,
                        pygame.Rect(
                            HELD_PIECE_START_X + (j + int(noLeftPadding))      * CELL_SIZE,
                            HELD_PIECE_START_Y + (i + HELD_PIECE_START_MARGIN) * CELL_SIZE,
                            CELL_SIZE - GRID_WIDTH,
                            CELL_SIZE - GRID_WIDTH
                        )
                    )
        #endregion

        #region Render Stats
        row = 0
        if (not inGameOverSequence):
            if (gameOver):
                renderFont(
                    screen,
                    "GAME OVER!",
                    Pos(
                        x = 0,
                        y = (ARENA_ROWS + STATS_START_MARGIN + row) * CELL_SIZE
                    ),
                    False
                )
                row += 2
            statTexts: list[str] = [
                f"NAME:     \"{player.name}\"",
                f"SCORE:    {player.score}",
                f"LINES:    {player.lines}",
                f"LEVEL:    {player.level}",
                f"TETRISES: {player.tetrisCount}"
            ]
            for i, s in enumerate(statTexts):
                if (i == 0):
                    if (player.name != ""):
                        renderFont(
                            screen,
                            s,
                            Pos(
                                x = 0,
                                y = (ARENA_ROWS + STATS_START_MARGIN + row) * CELL_SIZE
                            ),
                            False
                        )
                        row += 1
                        renderFont(
                            screen,
                            " ",
                            Pos(
                                x = 0,
                                y = (ARENA_ROWS + STATS_START_MARGIN + row) * CELL_SIZE
                            ),
                            False
                        )
                        row += 1
                else:
                    renderFont(
                        screen,
                        s,
                        Pos(
                            x = 0,
                            y = (ARENA_ROWS + STATS_START_MARGIN + row) * CELL_SIZE
                        ),
                        False
                    )
                    row += 1
            row += 1
            if (levelUp):
                renderFont(
                    screen,
                    "LEVEL UP!",
                    Pos(
                        x = 0,
                        y = (ARENA_ROWS + STATS_START_MARGIN + row) * CELL_SIZE
                    ),
                    False
                )
                row += 1
        #endregion

        pygame.display.flip()
    
    def clearLines(self) -> int:
        fullLineInds: list[int] = []

        for i, row in enumerate(self.arena):
            if (all(x != 0 for x in row)):
                fullLineInds.append(i)
                row[:] = [FIELD_LINE] * ARENA_COLS

        fullLines: int = len(fullLineInds)
        if (fullLines == 0): return 0

        player.disableInput = True
        self.renderGame()

        # We must round up for decimals (gotten if the result is odd), as the decimal represents a valid step.
            # The first step will be covered twice by the animation's loop if the width is odd.
        steps: int = math.ceil(ARENA_COLS / 2)

        start: int = ARENA_COLS // 2 - 1 # Must subtract 1 as indexing is 0-based
        sleep: float = player.lnTimeout / (steps + 1) / FPS # Must add 1 to include the initial phase where no fields are cleared

        time.sleep(sleep)

        while (start >= 0):
            for rowInd in fullLineInds:
                self.arena[rowInd][start], self.arena[rowInd][-(start + 1)] = PIECE_NULL, PIECE_NULL
            start -= 1
            self.renderGame()
            time.sleep(sleep)

        for rowInd in fullLineInds:
            self.arena.pop(rowInd)
            self.arena.insert(0, [PIECE_NULL] * ARENA_COLS)

        return fullLines

    def gameOverAnimation(self) -> None:
        fullSleep: float = BASE_ANIM_TIMEOUT / FPS
        sleep:     float = (GAME_OVER_TIMEOUT / FPS) / ARENA_ROWS
        time.sleep(fullSleep)
        if (player.trans):
            for i, row in enumerate(self.arena):
                row[:] = [FIELD_TF_BLUE if (i < 4 or i >= 16) else FIELD_TF_PINK if (i < 8 or i >= 12) else FIELD_TF_WHITE] * ARENA_COLS
                self.renderGame(inGameOverSequence = True)
                time.sleep(sleep)
        else:
            for row in self.arena:
                row[:] = [FIELD_OVER] * ARENA_COLS
                self.renderGame(inGameOverSequence = True)
                time.sleep(sleep)
        time.sleep(fullSleep)
        self.renderGame(gameOver = True)


class Piece:
    def __init__(self, shape: list[list[int]], type: int, color: tuple[int, int, int], pos: Pos = Pos(0, 0)):
        self.pos   = pos
        self.shape = shape
        self.type  = type
        self.color = color



    @staticmethod
    def createPiece(ind: int | None = None) -> Piece:
        index: int = 0
        if (ind == None): index = random.randint(PIECE_I, PIECE_Z)
        elif (0 <= ind <= PIECE_Z): index = ind

        return Piece(
            [[0 if (col == 0) else PIECES[index].type for col in row] for row in PIECES[index].shape],
            index,
            PIECES[index].color,
            Piece.getStartPos(index)
        )

    def noLeftPadding(self) -> bool:
        return (self.type in [PIECE_O, PIECE_J])

    @staticmethod
    def getStartPos(pieceInd: int) -> Pos:
        return Pos(
            x = ARENA_COLS // 2 - 1 - int(not PIECES[pieceInd].noLeftPadding()),
            y = 0
        )


    
    def clone(self) -> Piece:
        return Piece(
            [[0 if (col == 0) else self.type for col in row] for row in self.shape],
            self.type,
            PIECES[self.type].color,
            Piece.getStartPos(self.type)
        )
    
    @staticmethod
    def copy(src: Piece, dest: Piece) -> None:
        dest.shape = [[0 if (col == 0) else src.type for col in row] for row in src.shape]
        dest.type  = src.type
        dest.color = (x for x in src.color)

        dest.pos.x = src.pos.x
        dest.pos.y = src.pos.y



    def FPOStoAPOS(self, i: int, j: int) -> Pos:
        return Pos(
            x = j + self.pos.x,
            y = i + self.pos.y
        )

    def APOStoFPOS(self, i: int, j: int) -> Pos:
        return Pos(
            x = j - self.pos.x,
            y = i - self.pos.y
        )

    def APOSInPiece(self, i: int, j: int) -> bool:
        fpos: Pos = self.APOStoFPOS(i, j)
        if (0 <= fpos.y < len(self.shape) and 0 <= fpos.x < len(self.shape[fpos.y])):
            return bool(self.shape[fpos.y][fpos.x])
        return False



    def wallKick(self) -> bool:
        if (not self.collides()): return True

        orgPos: Pos = Pos(self.pos.x, self.pos.y)
        for kick in WALL_KICKS:
            self.pos.x += kick.x
            self.pos.y += kick.y
            if (not self.collides()): return True
            self.pos.x  = orgPos.x
            self.pos.y  = orgPos.y

        return False

    def canRotCW(self) -> bool:
        if (not player.canMovePieces()): return False
        copy = self.clone()
        copy.rotCW()
        return copy.wallKick()
    
    def canRotCCW(self) -> bool:
        if (not player.canMovePieces()): return False
        copy = self.clone()
        copy.rotCCW()
        return copy.wallKick()

    def rotCW(self) -> None:
        self.shape = [list(col)[::-1] for col in zip(*self.shape)]

    def rotCCW(self) -> None:
        self.shape = [list(col) for col in zip(*[row[::-1] for row in self.shape])]

    @staticmethod
    def rotatePieceO(func: Callable[[Piece], None]) -> Callable[[Piece], None]:
        def temp(self) -> None:
            if (self.type == PIECE_O): return
            func(self)
        return temp

    @rotatePieceO
    def rotateCW(self) -> None:
        if (self.canRotCW()):
            self.rotCW()
            self.wallKick()
    
    @rotatePieceO
    def rotateCCW(self) -> None:
        if (self.canRotCCW()):
            self.rotCCW()
            self.wallKick()
    


    def collides(self) -> bool:
        return any(
            (col and not (0 <= (apos := self.FPOStoAPOS(i, j)).x < ARENA_COLS and 0 <= apos.y < ARENA_ROWS and arena.arena[apos.y][apos.x] == 0))
            for i, row in enumerate(self.shape) for j, col in enumerate(row)
        )
    
    def canMoveRight(self) -> bool:
        if (not player.canMovePieces()): return False
        self.pos.x += 1
        collision   = self.collides()
        self.pos.x -= 1
        return not collision
    
    def canMoveLeft(self) -> bool:
        if (not player.canMovePieces()): return False
        self.pos.x -= 1
        collision   = self.collides()
        self.pos.x += 1
        return not collision

    def canMoveDown(self) -> bool:
        if (not player.canMovePieces()): return False
        self.pos.y += 1
        collision   = self.collides()
        self.pos.y -= 1
        return not collision

    def moveRight(self) -> None:
        if (self.canMoveRight()): self.pos.x += 1
    
    def moveLeft(self) -> None:
        if (self.canMoveLeft()): self.pos.x -= 1

    def moveDown(self) -> None:
        if (self.canMoveDown()): self.pos.y += 1

    def print(self):
        print(f"{self}:\n" + "{")
        for key, val in self.__dict__.items():
            print(f"    {key}: {val}")
        print("}")



class Log:
    class LogRow:
        def __init__(self, name: str = "", score: int = 0, lines: int = 0, level: int = 0, startLevel: int = 0, tetrisCount: int = 0):
            self.name        = name
            self.score       = score
            self.lines       = lines
            self.level       = level
            self.startLevel  = startLevel
            self.tetrisCount = tetrisCount

    def __init__(self):
        self.log:      list[Log.LogRow] = []
        self.toggle:   bool             = True
        self.unsorted: bool             = True

    def sort(self, sortBy: str, reversed: bool):
        def getAttr(logRow: Log.LogRow) -> str | int:
            return logRow.__dict__[sortBy]

        self.log.sort(key = getAttr, reverse = reversed)
        self.unsorted = False
        self.write()

    def read(self) -> None:
        try:
            with open(INTRN_LOG_FNM, "rb") as f:
                content = f.read()
                temp: list[dict[str, str | int]] = json.loads(base64.b85decode(content).decode())
                for logRow in temp:
                    new: Log.LogRow = Log.LogRow()
                    for key in logRow.keys():
                        new.__dict__.update({key: logRow.get(key)})
                    self.log.append(new)
        except FileNotFoundError:
            print(f"\nWARNING: Couldn't find internal log file (\"{INTRN_LOG_FNM}\"), attempting to create a new one\n")
            try:
                with open(INTRN_LOG_FNM, "w", encoding = "utf-8") as f:
                    f.write(base64.b85encode(b"{}").decode())
            except Exception as e:
                print(f"\nERROR: Couldn't create internal log file (\"{INTRN_LOG_FNM}\"). Exception: {e}\n")
                exit(1)
        except (binascii.Error, UnicodeDecodeError, ValueError) as e:
            print(f"\nERROR: Encountered incorrectly encoded internal log file: \"{e}\", exiting\n")
            exit(1)
        except Exception as e:
            print(f"\nERROR: Encountered unknown error: \"{e}\", exiting\n")
            exit(1)

    def write(self) -> None:
        with open(INTRN_LOG_FNM, "wb") as f:
            temp: list[dict[str, str | int]] = [logRow.__dict__ for logRow in self.log]
            f.write(base64.b85encode(json.dumps(temp).encode()))

    @staticmethod
    def formatLogRow(ln: int, logRow: Log.LogRow, logLen: int) -> str:
        return (
            f"{(str(ln) + '.'):<{LOG_LINE_NUM_MIN_WIDTH}}"
            f"Name: {logRow.name:>{MAX_NAME_LEN}}; "
            f"Score: {logRow.score:0{LOG_SCORE_MIN_WIDTH}}; "
            f"Lines: {logRow.lines:0{LOG_LINES_MIN_WIDTH}}; "
            f"Level: {logRow.level:0{LOG_LEVEL_MIN_WIDTH}}; "
            f"Starting level: {logRow.startLevel:0{LOG_START_LEVEL_MIN_WIDTH}}; "
            f"Tetrises: {logRow.tetrisCount:0{LOG_TETRIS_COUNT_MIN_WIDTH}}{'\n' if (ln < logLen) else ""}"
        )

    def export(self) -> None:
        with open(EXTRN_LOG_FNM, "w", encoding = "utf-8") as f:
            for i, log in enumerate(self.log):
                f.write(Log.formatLogRow(i + 1, log, len(self.log))) # Must add 1 so line numbering starts from 1 and not 0

    def clear(self) -> None:
        self.log = []
        if (os.path.exists(INTRN_LOG_FNM)):
            os.remove(INTRN_LOG_FNM)



class Player:
    def __init__(self):
        self.name:             str           = ""
        self.score:            int           = 0
        self.lines:            int           = 0
        self.currLines:        int           = 0                             # Number of lines cleared in current level
        self.level:            int           = 0
        self.tetrisCount:      int           = 0
        self.startLevel:       int           = 0
        self.firstLevel:       bool          = True                          # If true, the level threshold is increased based on the starting level

        self.cursorPos:        Pos           = Pos(0, 0)
        self.selected:         Button | None = None

        self.paused:           bool          = False
        self.mainMenu:         bool          = True
        self.confirmation:     bool          = False                         # Whether the player is currently looking at the confirmation for a button, if there is one
        self.gameOn:           bool          = False
        self.disableInput:     bool          = False                         # Prevents any form of input other than closing the window until the next iteration

        self.swappedThisRound: bool          = False                         # Prevents using the hold mechanic more than once per "round"

        self.currPiece:        Piece         = Piece.createPiece()
        self.nextPiece:        Piece         = Piece.createPiece()
        self.heldPiece:        Piece         = Piece.createPiece(PIECE_NULL)
        self.bag:              list[Piece]   = []

        self.speed:            int           = START_SPEED
        self.movementFrame:    int           = 0                             # Forces a movement down when exceeding speed

        self.currToBeFrozen:   bool          = False                         # Starts a timer to lock the current piece if true
        self.lockDelayFrames:  int           = 0                             # Frames passed since the current piece was marked to be frozen
        self.lockDelay:        int           = START_LOCK_DELAY              # How many frames a piece takes to be locked in place and engrained into the arena

        self.lnTimeout:        int           = START_LN_TIMEOUT

        self.log:              Log           = Log()
        self.log.read()

        self.keys: dict[Hashable, Key] = {}
        Key.bindKey(self.keys, [pygame.K_LEFT],                       self.leftPressed)
        Key.bindKey(self.keys, [pygame.K_RIGHT],                      self.rightPressed)
        Key.bindKey(self.keys, [pygame.K_DOWN],                       self.downPressed)
        Key.bindKey(self.keys, [pygame.K_UP],                         self.upPressed)

        # We must use lambdas as otherwise the functions would be bound to the single piece created at initialization,
        # instantly breaking upon the piece getting locked and engrained.
        Key.bindKey(self.keys, [pygame.K_a],                          lambda: self.currPiece.moveLeft())
        Key.bindKey(self.keys, [pygame.K_d],                          lambda: self.currPiece.moveRight())
        Key.bindKey(self.keys, [pygame.K_s],                          lambda: self.currPiece.moveDown())

        Key.bindKey(self.keys, [pygame.K_w, pygame.K_x, pygame.K_n],  lambda: self.currPiece.rotateCW())
        Key.bindKey(self.keys, [pygame.K_y, pygame.K_z, pygame.K_b],  lambda: self.currPiece.rotateCCW())
        Key.bindKey(self.keys, [pygame.K_c, pygame.K_m],              self.swapHeldPiece)

        Key.bindKey(self.keys, [pygame.K_SPACE],                      self.togglePause)
        Key.bindKey(self.keys, [pygame.K_KP_ENTER, pygame.K_RETURN],  self.selectButton)
        Key.bindKey(self.keys, [pygame.K_ESCAPE],                     self.goToMenu)

        Key.bindKey(self.keys, [pygame.K_BACKSPACE, pygame.K_DELETE], self.deleteText)

        Key.bindKey(self.keys, [pygame.K_F1],                         self.restart)
        Key.bindKey(self.keys, [pygame.K_F10],                        self.quit)
        self.currPressed: Key | None = None

        self.trans: bool = False

        self.regenBag()
        


    def resetKeys(self) -> None:
        for key in self.keys.values():
            key.reset()



    def markLogUnsorted(self) -> None:
        # Called if the player changes the setting for either the sort-by or sort-order button
        if (self.selected in [buttons[BTN_SORT_BY], buttons[BTN_SORT_ORDER]]):
            self.log.unsorted = True


    def upPressed(self) -> None:
        if (self.canMovePieces()):
            self.currPiece.rotateCW()
        elif (self.canNavigateMenu() and not self.selected and self.cursorPos.y > 0):
            self.cursorPos.y -= 1

    def downPressed(self) -> None:
        if (self.canMovePieces()):
            self.currPiece.moveDown()
        elif (self.canNavigateMenu() and not self.selected and self.cursorPos.y < len(buttons) - 1):
            self.cursorPos.y += 1

    def leftPressed(self) -> None:
        if (self.canMovePieces()):
            self.currPiece.moveLeft()
        elif (self.canNavigateMenu() and self.selected != None):
            if (
                self.selected.type in [BTN_TYPE_STR, BTN_TYPE_NUM] and
                self.selected.buffer != None                       and
                self.cursorPos.x > 0
            ):
                self.cursorPos.x -= 1
            elif (
                self.selected.type == BTN_TYPE_CYC and
                self.selected.cycle != None        and
                self.selected.cyclePos != None
            ):
                self.selected.cyclePos -= 1
                if (self.selected.cyclePos < 0):
                    self.selected.cyclePos = len(self.selected.cycle.keys()) - 1

                self.markLogUnsorted()

    def rightPressed(self) -> None:
        if (self.canMovePieces()):
            self.currPiece.moveRight()
        elif (self.canNavigateMenu() and self.selected != None):
            if (
                self.selected.type in [BTN_TYPE_STR, BTN_TYPE_NUM] and
                self.selected.buffer != None                       and
                self.cursorPos.x < len(self.selected.buffer) - int(self.selected.type == BTN_TYPE_NUM)
            ):
                self.cursorPos.x += 1
            elif (
                self.selected.type == BTN_TYPE_CYC and
                self.selected.cycle != None        and
                self.selected.cyclePos != None
            ):
                self.selected.cyclePos += 1
                if (self.selected.cyclePos >= len(self.selected.cycle.keys())):
                    self.selected.cyclePos = 0

                self.markLogUnsorted()



    def reset(self) -> None:
        name:        str        = self.name
        startLevel:  int        = self.startLevel
        currPressed: Key | None = self.currPressed
        self.__init__()
        arena.__init__()
        self.name        = name
        self.startLevel  = startLevel
        self.currPressed = currPressed

    def restart(self) -> None:
        if (player.mainMenu): return
        self.reset()
        Button.startGame()



    def regenBag(self) -> None:
        remaining: list[int] = [x for x in range(PIECE_I, PIECE_Z + PIECE_I)]
        while (len(remaining) > 0):
            picked:   int   = random.choice(remaining)
            newPiece: Piece = Piece.createPiece(picked)
            self.bag.append(newPiece)
            remaining.remove(picked)
    
    def getNextPiece(self) -> None:
        self.currPiece = self.nextPiece
        self.nextPiece = self.bag[-1]
        self.bag.pop()
        if (len(self.bag) == 0): self.regenBag()

    def swapHeldPiece(self) -> None:
        if (not player.canMovePieces() or self.swappedThisRound): return

        if (not self.heldPiece.type): # No active held piece yet
            self.heldPiece = self.currPiece
            self.getNextPiece()
        else:
            temp: Piece    = self.currPiece
            self.currPiece = self.heldPiece
            self.heldPiece = temp

            self.currPiece.pos = Piece.getStartPos(self.currPiece.type)

        self.swappedThisRound = True



    def canMovePieces(self) -> bool:
        return not self.paused and not self.mainMenu and self.gameOn

    def canNavigateMenu(self) -> bool:
        return self.mainMenu and not self.confirmation

    def togglePause(self) -> None:
        if (player.mainMenu): return
        self.paused = not self.paused

    def goToMenu(self) -> None:
        self.reset()

    def gameOver(self) -> None:
        player.disableInput = True
        arena.gameOverAnimation()
        self.gameOn = False
        if (self.log.toggle):
            logRow: Log.LogRow = Log.LogRow(
                self.name,
                self.score,
                self.lines,
                self.level,
                self.startLevel,
                self.tetrisCount
            )
            self.log.log.append(logRow)
            self.log.unsorted = True
            self.log.write()



    def selectButton(self) -> None:
        if (player.disableInput): return

        btn: Button = buttons[self.cursorPos.y]
        if (btn.func):
            # We must make an exception for trigger-buttons, as they can have confirmation prompts,
            # and toggling the selection simply doesn't work due to the button having to stay selected for two presses.

            self.selected = btn
            btn.func()
            if (self.canNavigateMenu()): # For buttons without a confirmation prompt, this will run no matter what
                self.renderMenu()
                time.sleep(BTN_TRIG_TIMEOUT / FPS)
                self.selected = None

            return

        self.selected = buttons[self.cursorPos.y] if (self.selected == None) else None
        if (self.selected != None):
            if (self.selected.buffer != None):
                pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()
            self.cursorPos.x = 0

    def inputText(self, text: str) -> None:
        if (
            player.disableInput          or
            not self.selected            or
            self.selected.buffer == None or
            (self.selected.type == BTN_TYPE_STR and len(self.selected.buffer) >= self.selected.bufferSize)
        ): return

        if (self.selected.type == BTN_TYPE_NUM):
            if (not text.isdigit()): return
            self.selected.buffer[self.cursorPos.x] = text
        else:
            if (self.cursorPos.x == len(self.selected.buffer)): self.selected.buffer.append(text)
            else:                                               self.selected.buffer.insert(self.cursorPos.x, text)
            self.rightPressed()

        self.updateFromInput()

    def deleteText(self) -> None:
        if (
            self.disableInput                        or
            not self.selected                        or
            not self.selected.buffer                 or
            self.selected.type not in [BTN_TYPE_STR] or
            self.cursorPos.x <= 0
        ): return
        self.cursorPos.x -= 1
        self.selected.buffer.pop(self.cursorPos.x)

    def updateFromInput(self) -> None:
        self.name = "".join(buttons[BTN_NAME].buffer or [])

        startLevel: int = int("".join(buttons[BTN_LEVEL].buffer or []))
        if (startLevel > MAX_START_LEVEL):
            buttons[BTN_LEVEL].buffer = [c for c in str(MAX_START_LEVEL)]
            startLevel = MAX_START_LEVEL
        self.startLevel = startLevel
        self.level      = startLevel

        btnToggleLog = buttons[BTN_TOGGLE_LOG]
        if (btnToggleLog != None and btnToggleLog.cycle != None and btnToggleLog.cyclePos != None):
            self.log.toggle = list(btnToggleLog.cycle.values())[btnToggleLog.cyclePos]



    def lockDelayFormula(self) -> int:
        return max(self.speed // 2, MIN_LOCK_DELAY)

    def lnTimeoutFormula(self) -> int:
        # Must multiply by FPS as the original timeout was second-based,
        # while the timeout here is frame-based.
        return int(max( float(START_LN_TIMEOUT) - (float(self.level) / 10.0 * FPS), MIN_LN_TIMEOUT ))
    
    def speedFormula(self) -> int:
        return max(START_SPEED - self.level * (1 + int(self.level >= 10)), MIN_SPEED)

    def pieceFreezeFormula(self) -> int:
        return 50

    def lineClearFormula(self, lines) -> int:
        return int(lines * lines * 100 * (1.0 + 0.075 * self.level))

    def levelUpFormula(self) -> int:
        return 200 * self.level

    def updateNonScore(self) -> None:
        self.speed     = self.speedFormula()
        self.lockDelay = self.lockDelayFormula() # Must be set after speed as the formula relies on speed
        self.lnTimeout = self.lnTimeoutFormula()

    def levelUpAnimation(self) -> None:
        self.disableInput = True
        arena.renderGame(True)
        time.sleep(BASE_ANIM_TIMEOUT / FPS)
        self.resetKeys()



    def renderMenu(self) -> None:
        from font import renderFont

        screen.fill(BLACK)

        if (self.selected != None and player.confirmation):
            renderFont(
                screen,
                self.selected.confPrompt if (self.selected.confPrompt) else "",
                Pos(x = 0, y = 0),
                False
            )
        else:
            row = 0

            renderFont(
                screen,
                MENU_TITLE,
                Pos(x = 0, y = row * CELL_SIZE),
                False
            )
            row += 2
            for i, btn in zip(range(len(buttons.keys())), buttons.values()):
                for _ in range(btn.marginTop):
                    renderFont(
                        screen,
                        "",
                        Pos(x = 0, y = row * CELL_SIZE),
                        False
                    )
                    row += 1
                renderFont(
                    screen,
                    btn.label,
                    Pos(x = 0, y = row * CELL_SIZE),
                    not self.selected and self.cursorPos.y == i
                )
                if (btn.buffer != None):
                    s:    list[str] = btn.buffer
                    slen: int       = len(s)
                    for j in range(slen + 1):
                        renderFont(
                            screen,
                            s[j] if (j < slen) else " ",
                            Pos(x = int((BTN_VAL_START_X + j / 2) * CELL_SIZE), y = row * CELL_SIZE),
                            self.selected == btn and self.cursorPos.x == j
                        )
                elif (btn.cycle != None and btn.cyclePos != None):
                    renderFont(
                        screen,
                        list(btn.cycle.keys())[btn.cyclePos],
                        Pos(x = BTN_VAL_START_X * CELL_SIZE, y = row * CELL_SIZE),
                        self.selected == btn
                    )
                row += 1
                for _ in range(btn.marginBottom):
                    renderFont(
                        screen,
                        "",
                        Pos(x = 0, y = row * CELL_SIZE),
                        False
                    )
                    row += 1

        pygame.display.flip()



    def quit(self) -> None:
        pygame.quit()
        print("\nExited.\n")
        exit(0)



WALL_KICKS: list[Pos] = [
    Pos(x =  1, y =  0),
    Pos(x = -1, y =  0),
    Pos(x =  2, y =  0),
    Pos(x = -2, y =  0),
    Pos(x =  0, y = -1),
    Pos(x =  0, y = -2),
]

PIECES: dict[int, Piece] = {
    PIECE_NULL: Piece([
        [0],
    ], PIECE_NULL, (0, 0, 0)),
    PIECE_I:    Piece([
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 0],
    ], PIECE_I, (0, 255, 255)),
    PIECE_O:    Piece([
        [1, 1],
        [1, 1],
    ], PIECE_O, (255, 255, 0)),
    PIECE_T:    Piece([
        [0, 1, 0],
        [0, 1, 1],
        [0, 1, 0],
    ], PIECE_T, (255, 0, 255)),
    PIECE_J:    Piece([
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 0],
    ], PIECE_J, (0, 255, 0)),
    PIECE_L:    Piece([
        [0, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
    ], PIECE_L, (255, 0, 0)),
    PIECE_S:    Piece([
        [0, 1, 0],
        [0, 1, 1],
        [0, 0, 1]
    ], PIECE_S, (0, 0, 255)),
    PIECE_Z:    Piece([
        [0, 0, 1],
        [0, 1, 1],
        [0, 1, 0]
    ], PIECE_Z, (255, 135, 0)),

    FIELD_LINE: Piece([
        [1]
    ], FIELD_LINE, (255, 255, 255)),
    FIELD_OVER: Piece([
        [1]
    ], FIELD_OVER, (128, 128, 128)),

    FIELD_TF_BLUE: Piece([
        [1]
    ], FIELD_TF_BLUE, (91, 206, 250)),
    FIELD_TF_PINK: Piece([
        [1]
    ], FIELD_TF_PINK, (245, 169, 184)),
    FIELD_TF_WHITE: Piece([
        [1]
    ], FIELD_TF_WHITE, (255, 255, 255)),
}



buttons: dict[int, Button] = {
    BTN_NAME: Button(
        label      = "NAME",
        type       = BTN_TYPE_STR,
        buffer     = [],
        bufferSize = MAX_NAME_LEN,
    ),
    BTN_LEVEL: Button(
        label        = "LEVEL",
        type         = BTN_TYPE_NUM,
        buffer       = ['0', '0'],
        bufferSize   = len(str(MAX_START_LEVEL)),
        marginBottom = 1
    ),



    BTN_SORT_BY: Button(
        label    = "SORT BY",
        type     = BTN_TYPE_CYC,
        cycle    = {
            "SCORE":    "score",
            "LINES":    "lines",
            "LEVEL":    "level",
            "START":    "startLevel",
            "TETRISES": "tetrisCount"
        },
        cyclePos = 0
    ),
    BTN_SORT_ORDER: Button(
        label    = "SORT ORDER",
        type     = BTN_TYPE_CYC,
        cycle    = { # Used by list.sort() for reversing. The method sorts in ascending order by default, so descending order reverses it.
            "DESCENDING": True,
            "ASCENDING":  False
        },
        cyclePos = 0    
    ),
    BTN_TOGGLE_LOG: Button(
        label    = "TOGGLE LOG",
        type     = BTN_TYPE_CYC,
        cycle    = {
            "ON":  True,
            "OFF": False
        },
        cyclePos = 0
    ),
    BTN_EXPORT_LOG: Button(
        label = "EXPORT LOG",
        func  = Button.exportLog
    ),
    BTN_CLEAR_LOG: Button(
        label        = "CLEAR LOG",
        func         = Button.clearLog,
        confPrompt   = f"Clear log? {BTN_CONF_CONTROL_HINT}",
        marginBottom = 1
    ),



    BTN_START: Button(
        label = "START",
        func  = Button.startGame
    ),
    BTN_HELP: Button(
        label = "HELP",
        func  = Button.printHelpText
    ),
    BTN_QUIT: Button(
        label = "QUIT",
        func  = Button.quitGame
    )
}



#initPieces()
player: Player         = Player()
arena:  Arena          = Arena()
screen: pygame.Surface = pygame.display.set_mode(((ARENA_COLS + 8) * CELL_SIZE, (ARENA_ROWS + 10) * CELL_SIZE))

STAT_TEXTS: list[str] = [
    f"NAME: {player.name}",
    f"SCORE: {player.score}",
    f"LINES: {player.lines}",
    f"LEVEL: {player.level}",
    f"TETRISES: {player.tetrisCount}"
]
