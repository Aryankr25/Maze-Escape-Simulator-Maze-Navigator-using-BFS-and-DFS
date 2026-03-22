# Maze Escape Simulator is a grid based maze simulation demonstrating the application of the Breadth-First Search (BFS) and Depth-First
# Search(DFS) algorithm in a dynamic, multi-agent environment. Multiple autonomous agents navigate a connected maze to collect keys and
# unlock an exit gate to escape while a player hunts them down.

import tkinter as tk
from collections import deque
import random

# DIMENSION AND MOVEMENT
CELL_SIZE = 30
DELAY = 400

WALL = "#"
EMPTY = "."
KEY = "K"
DOOR = "D"

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# MAZE LAYOUT AND OBJECTS' LOCATION
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

current_mode = ""
result = ""

door_open = False
game_over = False

game_started = False

ghost_paths = {}

# BFS IMPLEMENTATION


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


def start_game():
    global game_started, current_mode
    if not game_started:
        game_started = True
        current_mode = mode.get()

        # HIDE UI ELEMENTS
        start_button.pack_forget()
        mode_label.pack_forget()
        bfs_radio.pack_forget()
        dfs_radio.pack_forget()

        redraw()
        game_step()


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


def dfs(start, goals):
    stack = [(start, [])]
    visited = {start}

    while stack:
        (r, c), path = stack.pop()

        if (r, c) in goals:
            return path + [(r, c)]

        for dr, dc in MOVES:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and passable(nr, nc) and (nr, nc) not in visited:
                visited.add((nr, nc))
                stack.append(((nr, nc), path + [(r, c)]))
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
    global ghost_paths

    keys = get_keys()

    if keys:
        goals = keys
    else:
        goals = {(13, 8)}

    if pos in ghost_paths and ghost_paths[pos]:
        path = ghost_paths[pos]
        next_step = path.pop(0)

        ghost_paths[next_step] = path
        del ghost_paths[pos]

        return next_step

    if current_mode == "BFS":
        path = bfs(pos, goals)
    else:
        path = dfs(pos, goals)

    if path and len(path) > 1:
        new_path = path[1:]

        next_step = new_path.pop(0)

        ghost_paths[next_step] = new_path
        return next_step

    return random_move(pos)


# UI
root = tk.Tk()
root.title("Maze Escape Simulator")

INFO_HEIGHT = 40
canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE + INFO_HEIGHT)
canvas.pack()

mode = tk.StringVar(value="BFS")

mode_label = tk.Label(root, text="Select Traversal Mode:")
mode_label.pack()

bfs_radio = tk.Radiobutton(root, text="BFS", variable=mode, value="BFS")
bfs_radio.pack()

dfs_radio = tk.Radiobutton(root, text="DFS", variable=mode, value="DFS")
dfs_radio.pack()

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack()


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

    if game_started:
        canvas.create_rectangle(
            0,
            ROWS * CELL_SIZE,
            COLS * CELL_SIZE,
            ROWS * CELL_SIZE + INFO_HEIGHT,
            fill="white",
            outline="black",
        )
        if game_over:
            canvas.create_rectangle(
                0, 0, COLS * CELL_SIZE, ROWS * CELL_SIZE, fill="black", stipple="gray50"
            )

    canvas.create_text(
        COLS * CELL_SIZE // 2,
        ROWS * CELL_SIZE // 2,
        text=result,
        fill="white",
        font=("Arial", 24, "bold"),
    )

    canvas.create_text(
        COLS * CELL_SIZE // 2,
        ROWS * CELL_SIZE + INFO_HEIGHT // 2,
        text=f"Current Game Mode → {current_mode}",
        fill="black",
        font=("Arial", 14, "bold"),
    )


# PLAYER CHARACTERISTICS
def on_key(event):
    global player_pos, ghosts
    if not game_started or game_over:
        return

    r, c = player_pos
    moves = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}

    if event.char in moves:
        dr, dc = moves[event.char]
        nr, nc = r + dr, c + dc

        if in_bounds(nr, nc) and passable(nr, nc):
            player_pos = (nr, nc)

        ghosts[:] = [g for g in ghosts if g != player_pos]  # KILLS GHOST ON CONTACT

    redraw()


root.bind("<Key>", on_key)


# WORKING OF A GAME


def game_step():
    global ghosts, door_open, game_over, game_started, result

    if not game_started or game_over:
        return

    updated = []
    for g in ghosts:
        nxt = move_ghost(g)

        # GAME OVER (GHOST VICTORY)
        if door_open and maze[nxt[0]][nxt[1]] == DOOR:
            redraw()
            result = "Ghosts win"
            game_over = True
            redraw()
            return

        if maze[nxt[0]][nxt[1]] == KEY:
            maze[nxt[0]][nxt[1]] = EMPTY

        updated.append(nxt)

    ghosts[:] = updated

    if not get_keys():
        door_open = True

    redraw()

    # GAME OVER (PLAYER'S VICTORY)
    if not ghosts:
        result = "Player wins"
        game_over = True
        redraw()
        return

    root.after(DELAY, game_step)


redraw()
root.mainloop()
