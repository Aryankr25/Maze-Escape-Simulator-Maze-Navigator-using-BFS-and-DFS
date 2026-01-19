import tkinter as tk
from collections import deque
import random

# ---------------- CONFIG ----------------
CELL_SIZE = 30
DELAY = 350

WALL = "#"
EMPTY = "."
KEY = "K"
DOOR = "D"

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# ---------------- MAZE (15x15, CONNECTED, 4 KEYS) ----------------
maze = [
    list("###############"),
    list("#..K.....#....#"),
    list("#.#.###.#K#.###"),
    list("#.#...#.#.#...#"),
    list("#...#.#.#.###.#"),
    list("###.#.#.#.#...#"),
    list("#...#...#.#.###"),
    list("#.#.###.#.#..K#"),
    list("#.#...#.#.#.#.#"),
    list("#.#####.#.###.#"),
    list("#..K..#.#...#.#"),
    list("#.###.#.###.#.#"),
    list("#...#.#.....#.#"),
    list("#.#K....D.#...#"),
    list("###############"),
]

ROWS = len(maze)
COLS = len(maze[0])

player_pos = (1, 1)

ghosts = [(10, 9), (1, 13), (7, 1), (11, 13)]

door_open = False
game_over = False


def in_bounds(r, c):
    return 0 <= r < ROWS and 0 <= c < COLS


def passable(r, c):
    if maze[r][c] == WALL:
        return False
    if maze[r][c] == DOOR and not door_open:
        return False
    return True


def get_keys():
    return {(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == KEY}


def bfs(start, goals):
    queue = deque([(start, [])])
    visited = {start}

    while queue:
        (r, c), path = queue.popleft()

        if (r, c) in goals:
            return path + [(r, c)]

        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and passable(nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append(((nr, nc), path + [(r, c)]))
    return None


def random_move(pos):
    r, c = pos
    options = []
    for dr, dc in MOVES:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and passable(nr, nc):
            options.append((nr, nc))
    return random.choice(options) if options else pos


def move_ghost(pos):
    keys = get_keys()

    if keys:
        goals = keys  # collect keys
    else:
        goals = {(13, 8)}  # door position

    path = bfs(pos, goals)
    if path and len(path) > 1:
        return path[1]

    return random_move(pos)


# ---------------- UI ----------------
root = tk.Tk()
root.title("Maze AI – Final Version")

canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE)
canvas.pack()


def draw_cell(r, c, color):
    x1 = c * CELL_SIZE
    y1 = r * CELL_SIZE
    x2 = x1 + CELL_SIZE
    y2 = y1 + CELL_SIZE
    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")


def draw_circle(r, c, color):
    x1 = c * CELL_SIZE + 5
    y1 = r * CELL_SIZE + 5
    x2 = (c + 1) * CELL_SIZE - 5
    y2 = (r + 1) * CELL_SIZE - 5
    canvas.create_oval(x1, y1, x2, y2, fill=color)


def redraw():
    canvas.delete("all")

    for r in range(ROWS):
        for c in range(COLS):
            cell = maze[r][c]
            if cell == WALL:
                draw_cell(r, c, "black")
            elif cell == KEY:
                draw_cell(r, c, "gold")
            elif cell == DOOR:
                draw_cell(r, c, "blue" if door_open else "red")
            else:
                draw_cell(r, c, "white")

    draw_circle(*player_pos, "blue")
    for g in ghosts:
        draw_circle(*g, "red")


# ---------------- PLAYER ----------------
def on_key(event):
    global player_pos, ghosts
    if game_over:
        return

    r, c = player_pos
    moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

    if event.char in moves:
        dr, dc = moves[event.char]
        nr, nc = r + dr, c + dc

        if in_bounds(nr, nc) and passable(nr, nc):
            player_pos = (nr, nc)

        # kill ghost on contact
        ghosts[:] = [g for g in ghosts if g != player_pos]

    redraw()


root.bind("<Key>", on_key)


# ---------------- GAME LOOP ----------------
def game_step():
    global ghosts, door_open, game_over

    if game_over:
        return

    updated = []
    for g in ghosts:
        nxt = move_ghost(g)

        # Ghost reaches door → GAME OVER
        if door_open and maze[nxt[0]][nxt[1]] == DOOR:
            redraw()
            print("Ghosts win")
            game_over = True
            return

        if maze[nxt[0]][nxt[1]] == KEY:
            maze[nxt[0]][nxt[1]] = EMPTY

        updated.append(nxt)

    ghosts[:] = updated

    if not get_keys():
        door_open = True

    redraw()

    if not ghosts:
        print("Player wins")
        game_over = True
        return

    root.after(DELAY, game_step)


# ---------------- START ----------------
redraw()
root.after(DELAY, game_step)
root.mainloop()
