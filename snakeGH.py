"""
SnakeGH - A Classic Arcade Game
Lab 2 - Python (Level 200)
Name: Judah Ekow Affadu-Mensah | Index No: 2526402221
"""
import os
import random
import tkinter as tk

CELL = 24             # size of one square in pixels (keep it a multiple of 24: the head picture is 24x24)
COLS = 25             # squares across
ROWS = 20             # squares down
WIDTH = CELL * COLS   # 600 pixels
HEIGHT = CELL * ROWS  # 480 pixels
START_SPEED = 150     # milliseconds between moves (smaller = faster)

# Everything the game saves or loads lives next to this file
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(APP_DIR, "snake_highscore.txt")

# Golden fruit
BONUS_EVERY_MS = 10000     # a golden fruit appears every 10 seconds
BONUS_LIFETIME_MS = 5000   # ...and disappears after 5 seconds
BONUS_POINTS = 3           # worth 3 points
BLINK_MS = 1500            # it blinks during its last 1.5 seconds

DIRECTIONS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
OPPOSITE = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
KEYS = {"up": "Up", "w": "Up", "down": "Down", "s": "Down",
        "left": "Left", "a": "Left", "right": "Right", "d": "Right"}

# Pixel-art snake head, 24 x 24. The tongue points DOWN, so this is the "Down" head.
# The other three directions are made by rotating it
SNAKE_HEAD_24X24 = [
    "                        ",
    "      xxxxxxxxxxxx      ",
    "    xxXXXXXXXXXXXXxx    ",
    "   xXXXXXXXXXXXXXXXXx   ",
    "  xXXXXXXXXXXXXXXXXXXx  ",
    "  xXXXXXXXXXXXXXXXXXXx  ",
    "  xXX...XXXXXXXX...XXx  ",  # '.' = white eyes (3x3)
    "  xXX...XXXXXXXX...XXx  ",
    "  xXX...XXXXXXXX...XXx  ",
    "  xXXXXXXXXXXXXXXXXXXx  ",
    "   xXXXXXXXXXXXXXXXXx   ",
    "   xXXXXXXXXXXXXXXXXx   ",
    "    xXXXXXXXXXXXXXXx    ",
    "    xXXXXXXXXXXXXXXx    ",
    "     xXXXXXXXXXXXXx     ",
    "     xXXXXXXXXXXXXx     ",
    "      xXXXXXXXXXXx      ",
    "       xxxxxxxxxx       ",
    "           rr           ",  # 'r' = short forked tongue
    "           rr           ",
    "          rrrr          ",
    "         rr  rr         ",
    "                        ",
    "                        ",
]
COLOR_MAP = {
    'x': "#1e4d2b",  # Dark green/black outline
    'X': "#2E7D32",  # Solid snake green body
    '.': "#FFFFFF",  # White eyes and nostrils
    'r': "#E53935",  # Bright red forked tongue
}


# ---------------- Logic functions (no GUI code here) ----------------

def next_head(head, direction):
    """Return the square the head moves into."""
    dx, dy = DIRECTIONS[direction]
    x, y = head
    return (x + dx, y + dy)

def hits_wall(cell):
    """True if the square is outside the board."""
    x, y = cell
    return x < 0 or x >= COLS or y < 0 or y >= ROWS

def hits_self(head, snake):
    """True if the head runs into the body (the tail moves away, so skip it)."""
    return head in snake[:-1]

def random_food(snake, avoid=()):
    """Pick a random empty square, or None if the board is completely full."""
    free = [(x, y) for x in range(COLS) for y in range(ROWS)
            if (x, y) not in snake and (x, y) not in avoid]
    if not free:
        return None
    return random.choice(free)

def level_for(score):
    """Level goes up every 5 points."""
    return score // 5 + 1

def speed_for(level):
    """Each level is 15 ms faster, but never faster than 60 ms."""
    return max(60, START_SPEED - (level - 1) * 15)

def bonus_visible(time_left, tick_ms):
    """Golden fruit is always shown, except it blinks off every other tick
    during its last BLINK_MS milliseconds."""
    return time_left >= BLINK_MS or (time_left // tick_ms) % 2 == 1

def rotate_cw(matrix):
    """Turn a picture (list of strings) 90 degrees clockwise."""
    return ["".join(row) for row in zip(*matrix[::-1])]

def rotate_ccw(matrix):
    """Turn a picture (list of strings) 90 degrees anticlockwise."""
    return ["".join(row) for row in list(zip(*matrix))[::-1]]

def rotate_180(matrix):
    """Turn a picture (list of strings) upside down."""
    return [row[::-1] for row in matrix[::-1]]

def load_high_score():
    """Read the saved high score, or 0 if there is none yet."""
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            return int(file.read().strip())
    except (OSError, ValueError):   # no file / cannot read it / not a number
        return 0

def save_high_score(score):
    """Write the new high score to the file."""
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(score))
    except OSError:
        pass   # if the folder is read-only the game must still carry on


# ---------------- Game state ----------------
snake = []
direction = "Right"
next_direction = "Right"
food = (0, 0)
score = 0
level = 1
high_score = load_high_score()
running = False
paused = False
loop_id = None
bonus_food = None            # position of the golden fruit, or None
bonus_left = 0               # ms the golden fruit has left
bonus_wait = BONUS_EVERY_MS  # ms until the next golden fruit


# ---------------- GUI event handlers ----------------

def create_snake_head_image(matrix, cell_size=CELL):
    """Paint a pixel-art matrix onto a transparent in-memory image."""
    img = tk.PhotoImage(width=cell_size, height=cell_size)
    scale = cell_size // 24
    for y, row in enumerate(matrix):
        for x, char in enumerate(row):
            if char in COLOR_MAP:
                for sx in range(scale):
                    for sy in range(scale):
                        img.put(COLOR_MAP[char], (x * scale + sx, y * scale + sy))
    return img

def draw_grid():
    """Draw faint grid lines once, at the start."""
    for x in range(0, WIDTH, CELL):
        canvas.create_line(x, 0, x, HEIGHT, fill="#706C6C")
    for y in range(0, HEIGHT, CELL):
        canvas.create_line(0, y, WIDTH, y, fill="#706C6C")

def update_labels():
    score_level_label.config(text=f"Score: {score}\nLevel: {level}")
    best_label.config(text=f"Best Score\n{high_score}")

def draw():
    """Clear the old snake and food, then draw them in their new places."""
    canvas.delete("piece", "message")

    if food is not None:
        fx, fy = food
        canvas.create_oval(fx * CELL + 4, fy * CELL + 4,
                           fx * CELL + CELL - 4, fy * CELL + CELL - 4,
                           fill="#e53935", outline="", tags="piece")

    if bonus_food is not None and bonus_visible(bonus_left, speed_for(level)):
        bx, by = bonus_food
        canvas.create_oval(bx * CELL + 2, by * CELL + 2,
                           bx * CELL + CELL - 2, by * CELL + CELL - 2,
                           fill="#ffd600", outline="#ff8f00", width=2,
                           tags="piece")

    for index, (x, y) in enumerate(snake):
        if index == 0:   # the head is the pixel-art picture, facing the way we move
            canvas.create_image(x * CELL, y * CELL, image=head_images[direction],
                                anchor="nw", tags="piece")
        else:
            canvas.create_rectangle(x * CELL + 1, y * CELL + 1,
                                    x * CELL + CELL - 1, y * CELL + CELL - 1,
                                    fill="#43a047", outline="", tags="piece")
    update_labels()

def show_message(title, subtitle):
    """Write a big message in the middle of the board."""
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 25, text=title, fill="#D4AF37", font=("Aref Ruqaa", 35, "bold"), tags="message")
    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 30, text=subtitle, fill="white", font=("Segoe UI", 15), tags="message")

def start_game(event=None):
    global snake, direction, next_direction, food, score, level, running
    global paused, loop_id, bonus_food, bonus_left, bonus_wait
    if loop_id is not None:
        root.after_cancel(loop_id)
    snake = [(5, 10), (4, 10), (3, 10)]
    direction = "Right"
    next_direction = "Right"
    food = random_food(snake)
    score = 0
    level = 1
    running = True
    paused = False
    bonus_food = None
    bonus_left = 0
    bonus_wait = BONUS_EVERY_MS
    draw()
    loop_id = root.after(speed_for(level), game_loop)

def update_bonus(elapsed):
    """Advance the golden fruit clocks by one tick.
    Time is counted in game ticks, so pausing the game also pauses these clocks."""
    global bonus_food, bonus_left, bonus_wait
    bonus_wait -= elapsed
    if bonus_food is not None:
        bonus_left -= elapsed
        if bonus_left <= 0:
            bonus_food = None            # it expired
    if bonus_wait <= 0:
        bonus_wait = BONUS_EVERY_MS
        if bonus_food is None:
            bonus_food = random_food(snake, [food])
            bonus_left = BONUS_LIFETIME_MS

def game_loop():
    """One tick: move, eat, draw, then schedule the next tick."""
    global direction, food, score, level, loop_id, bonus_food
    direction = next_direction
    head = next_head(snake[0], direction)
    if hits_wall(head) or hits_self(head, snake):
        game_over()
        return
    snake.insert(0, head)
    if head == food:
        score += 1
        level = level_for(score)
        food = random_food(snake, [bonus_food] if bonus_food is not None else [])
        if food is None:                 # no free square left: the player wins
            draw()
            game_over(won=True)
            return
    elif head == bonus_food:
        score += BONUS_POINTS
        level = level_for(score)
        bonus_food = None
    else:
        snake.pop()
    update_bonus(speed_for(level))
    draw()
    loop_id = root.after(speed_for(level), game_loop)

def on_key(event):
    """Change direction, but never straight back into the body."""
    global next_direction
    new_direction = KEYS.get(event.keysym.lower())
    if new_direction is None or not running or paused:
        return
    if new_direction != OPPOSITE[direction]:
        next_direction = new_direction

def on_space(event=None):
    if not running:
        start_game()

def toggle_pause(event=None):
    global paused, loop_id
    if not running:
        return
    paused = not paused
    if paused:
        root.after_cancel(loop_id)
        show_message("PAUSED", "Press P to continue")
    else:
        canvas.delete("message")
        loop_id = root.after(speed_for(level), game_loop)

def game_over(won=False):
    global running, high_score
    running = False
    if score > high_score:
        high_score = score
        save_high_score(high_score)
        title = "NEW HIGH SCORE!"
    else:
        title = "YOU WIN!" if won else "GAME OVER"
    show_message(title, f"          You scored {score}.\nPress Space to play again" )
    update_labels()


# ---------------- Build the window ----------------
root = tk.Tk()
root.title("SnakeGH - Classic Arcade Game")
root.resizable(1, 1)
root.configure(bg="#222222")
root.minsize(WIDTH + 60, HEIGHT + 140)      # never smaller than the game itself

# The four head pictures (images can only be made after the window exists)
head_images = {
    "Down":  create_snake_head_image(SNAKE_HEAD_24X24),
    "Up":    create_snake_head_image(rotate_180(SNAKE_HEAD_24X24)),
    "Right": create_snake_head_image(rotate_ccw(SNAKE_HEAD_24X24)),
    "Left":  create_snake_head_image(rotate_cw(SNAKE_HEAD_24X24)),
}

# --- Top Header Container Frame ---
header_frame = tk.Frame(root, bg="#222222")
header_frame.pack(fill=tk.X, padx=20, pady=(10, 5))

# Left: Score & Level
score_level_label = tk.Label(header_frame, text="Score: 0\nLevel: 1",
                             font=("Consolas", 11, "bold"), fg="white", bg="#0d1b2a", padx=10, relief="flat")
score_level_label.pack(side=tk.LEFT)

# Center: Game Title
title_label = tk.Label(header_frame, text="SnakeGH",
                       font=("ArcadeClassic", 35, "bold"), fg="#D4AF37", bg="#222222")
title_label.pack(side=tk.LEFT, expand=True)

# Right: Best Score
best_label = tk.Label(header_frame, text="Best: 0",
                      font=("Consolas", 11, "bold"), fg="#FFF1A8", bg="#0d1b2a", padx=10, relief="flat")
best_label.pack(side=tk.RIGHT)


canvas = tk.Canvas(width=WIDTH, height=HEIGHT, bg="#121212", highlightthickness=2, highlightbackground="#800020")#1A1E24
canvas.pack(padx=15)

tk.Label(text="Arrows / W A S D = move | P = pause | Space = start | Gold Fruit = 3 points",
         fg="#FFF1A8", bg="#0d1b2a").pack(pady=8)

root.bind("<Key>", on_key)
root.bind("<space>", on_space)
root.bind("p", toggle_pause)
root.bind("P", toggle_pause)

draw_grid()
update_labels()
show_message("SnakeGH", "Press Space to start")
root.focus_force()   # so the keys work without clicking the window first
root.mainloop()