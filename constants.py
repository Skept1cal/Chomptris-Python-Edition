import pygame

PIECE_NULL: int = 0
PIECE_I:    int = 1
PIECE_O:    int = 2
PIECE_T:    int = 3
PIECE_J:    int = 4
PIECE_L:    int = 5
PIECE_S:    int = 6
PIECE_Z:    int = 7
FIELD_LINE: int = 8 # Marks lines to be cleared for the renderer
FIELD_OVER: int = 9 # Marks lines for the game-over animation for the renderer

FIELD_TF_BLUE:  int = 10
FIELD_TF_PINK:  int = 11
FIELD_TF_WHITE: int = 12

MARKERS: list[int] = [
    PIECE_NULL,
    PIECE_I,
    PIECE_O,
    PIECE_T,
    PIECE_J,
    PIECE_L,
    PIECE_S,
    PIECE_Z,
    FIELD_LINE,
    FIELD_OVER,

    FIELD_TF_BLUE,
    FIELD_TF_PINK,
    FIELD_TF_WHITE
]

ARENA_COLS: int = 10 # Width
ARENA_ROWS: int = 20 # Height
CELL_SIZE:  int = 30
GRID_WIDTH: int = CELL_SIZE // 10 # How many pixels the grid itself should be

NEXT_PIECE_START_X:      int = (ARENA_COLS + 2) * CELL_SIZE
NEXT_PIECE_START_Y:      int = 1 * CELL_SIZE
NEXT_PIECE_START_MARGIN: int = 2 # Number of cells to shift the actual piece display down vertically
HELD_PIECE_START_X:      int = NEXT_PIECE_START_X
HELD_PIECE_START_Y:      int = 10 * CELL_SIZE
HELD_PIECE_START_MARGIN: int = NEXT_PIECE_START_MARGIN
STATS_START_MARGIN:      int = 2

FPS:               int = 60
BASE_ANIM_TIMEOUT: int = FPS // 2          # How many frames a general animation takes
KEY_FREQ:          int = 30                # How many times per second a key can fire
KEY_DELAY:         int = 10                # How many frames of delay a key has before it starts firing repeatedly
START_SPEED:       int = FPS               # Number of frames per forced movement down
START_LOCK_DELAY:  int = FPS // 2          # Number of frames it takes for a piece to be locked in place
START_LN_TIMEOUT:  int = BASE_ANIM_TIMEOUT # Number of frames a line-clear takes in total
MIN_SPEED:         int = FPS // 30
MIN_LOCK_DELAY:    int = 8
MIN_LN_TIMEOUT:    int = FPS // 5
GAME_OVER_TIMEOUT: int = FPS

LEVEL_THRESHOLD:   int = 10
REBIRTH_THRESHOLD: int = 256

BLACK: tuple[int, int, int] = (  0,   0,   0)
WHITE: tuple[int, int, int] = (255, 255, 255)

TEXT_FG_COLOR: tuple[int, int, int] = WHITE
TEXT_BG_COLOR: tuple[int, int, int] = BLACK
TEXT_COLORS: list[tuple[int, int, int]] = [
    TEXT_BG_COLOR,
    TEXT_FG_COLOR
]
TEXT_HEIGHT: int = int(CELL_SIZE * 0.75)
FONT: pygame.font.Font = pygame.font.Font(
    "CascadiaCode.ttf", # name
    TEXT_HEIGHT         # size (height in px)
)

BTN_TYPE_TRIG:  int = 0
BTN_TYPE_STR:   int = 1
BTN_TYPE_NUM:   int = 2
BTN_TYPE_CYC:   int = 3

BTN_NAME:       int = 0
BTN_LEVEL:      int = 1

BTN_SORT_BY:    int = 2
BTN_SORT_ORDER: int = 3
BTN_TOGGLE_LOG: int = 4
BTN_EXPORT_LOG: int = 5
BTN_CLEAR_LOG:  int = 6

BTN_START:      int = 7
BTN_HELP:       int = 8
BTN_QUIT:       int = 9

MAX_NAME_LEN:    int = 8
MAX_START_LEVEL: int = 29

BTN_VAL_START_X:     int = 6         # How many cells to the right the values for buttons should be rendered if they are not trigger buttons
BTN_LABEL_MIN_WIDTH: int = 12        # How many cells the label must at least take up, with or without padding

BTN_TRIG_TIMEOUT: int = FPS // 20 # How many frames of timeout selecting a trigger button invokes, for visual feedback

BTN_CONF_CONTROL_HINT: str = "(ENTER: Confirm, ESC: Abort)" # Inline explanation of confirmation prompt controls

PAUSED_STR: str = "PAUSED"

INTRN_LOG_FNM: str = "hs.txt"
EXTRN_LOG_FNM: str = "highscores.txt"

LOG_LINE_NUM_MIN_WIDTH:     int = 8  # How many characters the effective width of the log numbering should take up at least
LOG_SCORE_MIN_WIDTH:        int = 10 # How many digits the score should be padded to at least
LOG_LINES_MIN_WIDTH:        int = 6  # How many digits the number of lines should be padded to at least
LOG_LEVEL_MIN_WIDTH:        int = 3  # How many digits the level reached should be padded to atleast
LOG_START_LEVEL_MIN_WIDTH:  int = 2  # How many digits the starting level should be padded to at least
LOG_TETRIS_COUNT_MIN_WIDTH: int = 5  # How many digits the number of tetrises should be padded to at least

VERSION_STR: str = "V1.0.1"
MENU_TITLE:  str = f"CHOMPTRIS: PYTHON EDITION {VERSION_STR}"
