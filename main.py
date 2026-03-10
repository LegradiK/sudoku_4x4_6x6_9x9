import pygame
import requests
from button import Button
import ui_4x4
import ui_6x6
import ui_9x9

SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 800

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sudoku")

font_4x4 = pygame.font.SysFont("comicsans", 180)
font_6x6 = pygame.font.SysFont("comicsans", 120)
font_9x9 = pygame.font.SysFont("comicsans", 80)
font_medium = pygame.font.SysFont("Arial", 40, bold=True)
font_text = pygame.font.SysFont("Arial", 18)
font_screen_title = pygame.font.SysFont("comicsans", 80, bold=True)
font_screen_text = pygame.font.SysFont("Arial", 24, bold=True)

# buttons at the right hand side
submit_button = Button("Submit", 870, 200, 180, 60, color=(34, 139, 34))

game_4x4_button = Button("4x4", 820, 460, 90, 60, font_size=29)
game_6x6_button = Button("6x6", 910, 460, 90, 60, font_size=29)
game_9x9_button = Button("9x9", 1000, 460, 90, 60, font_size=29)

easy_button = Button("Easy", 820, 540, 90, 60, font_size=29)
medium_button = Button("Medium", 910, 540, 90, 60, font_size=29)
hard_button = Button("Hard", 1000, 540, 90, 60, font_size=29)


new_game_button = Button("New Game", 870, 630, 180, 60)
restart_button = Button("Restart", 870, 700, 180, 60)


DIFFICULTY_CLUES = {
    "4x4": {
        "easy": 8,
        "medium": 6,
        "hard": 4
    },
    "6x6": {
        "easy": 20,
        "medium": 16,
        "hard": 12
    },
    "9x9": {
        "easy": 40,
        "medium": 30,
        "hard": 20
    }
}

UI = {"4x4": ui_4x4, "6x6": ui_6x6, "9x9": ui_9x9}

screen_state = "how_to_play" 
chosen_game = "4x4"
selected_difficulty = "easy"

def get_grid_size(game):
    """Return the integer grid size for the chosen game string."""
    return {"4x4": 4, "6x6": 6, "9x9": 9}[game]

def load_new_game(game, difficulty):
    # sudoku generating from Docker jotools/sudoku
    url = "http://localhost:8080/api/sudoku/generate"

    size = get_grid_size(game)
    num_clues = DIFFICULTY_CLUES[game][difficulty]

    params = {
        "size": size,
        "numClues": num_clues,
        "format": "json",
        "addSolution": "true"
    }

    response = requests.get(url, params=params)
    data = response.json()

    puzzle_cells = data['sudoku']
    solution_cells = data['solution']

    puzzle_grid = [[0] * size for i in range(size)]
    solution_grid = [[0] * size for i in range(size)]
    locked_grid = [[False] * size for i in range(size)]

    for cell in puzzle_cells:
        row = cell['row'] - 1
        col = cell['col'] - 1
        puzzle_grid[row][col] = cell['value']
        locked_grid[row][col] = cell['locked']

    for cell in solution_cells:
        row = cell['row'] - 1
        col = cell['col'] - 1
        solution_grid[row][col] = cell['value'] 
    
    # print('Puzzle: ')
    # for row in puzzle_grid:
    #     print(row)

    # print('\nSolution: ')
    # for row in solution_grid:
    #     print(row)
    
    return puzzle_grid, solution_grid, locked_grid

def make_state(game, quiz, solution):
    size = get_grid_size(game)
    cell_size = SCREEN_HEIGHT // size
    original_grid = [row[:] for row in quiz]

    cls = {"4x4": ui_4x4.GameState_4x4, "6x6": ui_6x6.GameState_6x6, "9x9": ui_9x9.GameState_9x9}[game]
    state = cls(
        grid=quiz,
        original_grid=original_grid,
        cell_size=cell_size,
        font_4x4 = font_4x4,
        font_6x6=font_6x6,
        font_9x9 = font_9x9,
        font_medium=font_medium,
        font_text=font_text
    )
    state.solution = solution
    return state

def switch_game(game, difficulty):
    quiz, solution, locked = load_new_game(game, difficulty)
    return make_state(game, quiz, solution)

def draw_sudoku_buttons(screen, mouse_pos, selected):
    """Draw 4x4/6x6/9x9 buttons, highlighting the selected one."""
    for btn, key in [(game_4x4_button, "4x4"), (game_6x6_button, "6x6"), (game_9x9_button, "9x9")]:
        is_selected = (selected == key)
        btn.draw(screen, mouse_pos, highlighted=is_selected)

def draw_difficulty_buttons(screen, mouse_pos, selected):
    """Draw Easy/Medium/Hard buttons, highlighting the selected one."""
    for btn, key in [(easy_button, "easy"), (medium_button, "medium"), (hard_button, "hard")]:
        is_selected = (selected == key)
        btn.draw(screen, mouse_pos, highlighted=is_selected)

 

def validate_against_solution(state, grid_size):
    state.wrong_cells.clear()
    if state.solution is None:
        return
    for row in range(grid_size):
        for col in range(grid_size):
            current = state.grid[row][col]
            correct = state.solution[row][col]
            if current == 0:
                continue
            if current != correct:
                state.wrong_cells.add((row, col))

def handle_submit(state, grid_size):
    global is_solved, show_warning, show_fill_warning
    board_full = all(
                    state.grid[row][col] != 0
                     for row in range(grid_size)
                     for col in range(grid_size)
                )
    if not board_full:
        show_fill_warning = True
        is_solved = False
        show_warning = False
    else: 
        validate_against_solution(state, grid_size)
        if not state.wrong_cells:
            is_solved = True
            show_warning = False
            show_fill_warning = False
        else:
            is_solved = False
            show_warning = True
            show_fill_warning = False

def draw_how_to_play(screen, mouse_pos):
    screen.fill((255, 255, 255))

    # Title
    title = font_screen_title.render("How to Play", True, (70, 130, 180))
    screen.blit(title, (80, 60))

    # Instructions
    lines = [
        "Choose a grid size: 4x4, 6x6, or 9x9",
        "Choose a difficulty: Easy, Medium, or Hard",
        "Press New Game to load a puzzle",
        "",
        "Click a cell to select it",
        "Type a number to fill it in",
        "Use Arrow Keys or mouse to move between cells",
        "Backspace / Delete / e / d to erase a cell",
        "",
        "Press ENTER or the Submit button to check your answer",
        "Orange = solved!",
        "Yellow = Missing answers",
        "Red = wrong answers",
    ]
    for i, line in enumerate(lines):
        text = font_screen_text.render(line, True, (0, 0, 0))
        screen.blit(text, (80, 180 + i * 38))


# Initial loading
screen_state = "how_to_play"
state = None
is_solved = False
show_warning = False
show_fill_warning = False
running = True


while running:
    mouse_pos = pygame.mouse.get_pos()
    if screen_state == "how_to_play":
        draw_how_to_play(screen, mouse_pos)
        draw_sudoku_buttons(screen, mouse_pos, chosen_game)
        draw_difficulty_buttons(screen, mouse_pos, selected_difficulty)
        new_game_button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.is_clicked(event):
                    state = switch_game(chosen_game, selected_difficulty)
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False
                    screen_state = "playing"
                elif game_4x4_button.is_clicked(event):
                        chosen_game = "4x4"
                elif game_6x6_button.is_clicked(event):
                    chosen_game = "6x6"
                elif game_9x9_button.is_clicked(event):
                    chosen_game = "9x9"
                elif easy_button.is_clicked(event):
                    selected_difficulty = "easy"
                elif medium_button.is_clicked(event):
                    selected_difficulty = "medium"
                elif hard_button.is_clicked(event):
                    selected_difficulty = "hard"


    elif screen_state == "playing":

        grid_size = get_grid_size(chosen_game)
        max_index = grid_size - 1

        ui = UI[chosen_game]
        ui.draw_background(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.is_clicked(event):
                    state = switch_game(chosen_game, selected_difficulty)
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False

                elif restart_button.is_clicked(event):
                    state.grid = [row[:] for row in state.original_grid]
                    state.wrong_cells.clear()
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False
                
                elif submit_button.is_clicked(event):
                    handle_submit(state, grid_size)

                elif game_4x4_button.is_clicked(event):
                    chosen_game = "4x4"
                    state = switch_game(chosen_game, selected_difficulty)
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False
                elif game_6x6_button.is_clicked(event):
                    chosen_game = "6x6"
                    state = switch_game(chosen_game, selected_difficulty)
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False
                elif game_9x9_button.is_clicked(event):
                    chosen_game = "9x9"
                    state = switch_game(chosen_game, selected_difficulty)
                    is_solved = False
                    show_warning = False
                    show_fill_warning = False

                elif easy_button.is_clicked(event):
                    selected_difficulty = "easy"
                elif medium_button.is_clicked(event):
                    selected_difficulty = "medium"
                elif hard_button.is_clicked(event):
                    selected_difficulty = "hard"

                else:
                    cell_size = SCREEN_HEIGHT // grid_size
                    x, y = event.pos
                    col = x // cell_size
                    row = y // cell_size
                    if 0 <= row < grid_size and 0 <= col < grid_size:
                        state.selected_row = row
                        state.selected_col = col

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_LEFT:
                    state.selected_col = max(0, state.selected_col - 1)

                if event.key == pygame.K_RIGHT:
                    state.selected_col = min(max_index, state.selected_col + 1)

                if event.key == pygame.K_UP:
                    state.selected_row = max(0, state.selected_row - 1)

                if event.key == pygame.K_DOWN:
                    state.selected_row = min(max_index, state.selected_row + 1)

                if event.key in (
                    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,pygame.K_5, 
                    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9,
                    pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, 
                    pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9
                ):
                    value = int(event.unicode)
                    # Ignore numbers out of range for the current grid size
                    if value < 1 or value > grid_size:
                        pass
                    else:
                        row = state.selected_row
                        col = state.selected_col
                        if state.original_grid[row][col] == 0:
                            state.grid[row][col] = value
                            if state.solution and value == state.solution[row][col]:
                                state.wrong_cells.discard((row, col))
                            else:
                                state.wrong_cells.add((row, col))

                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    handle_submit(state, grid_size)

                if event.key in (
                    pygame.K_BACKSPACE,
                    pygame.K_DELETE,
                    pygame.K_e,
                    pygame.K_d
                ):
                    row = state.selected_row
                    col = state.selected_col

                    # Only allow erasing user-entered cells
                    if state.original_grid[row][col] == 0:
                        state.grid[row][col] = 0
                        state.wrong_cells.discard((row, col))

        # Draw everything
        ui.draw_numbers(screen, state)
        ui.draw_grid_lines(screen, state)
        ui.draw_selection(screen, state)

        if is_solved:
            ui.draw_result(screen, font_medium, SCREEN_HEIGHT)
        elif show_warning:
            ui.draw_warning(screen, font_medium, SCREEN_HEIGHT)
        elif show_fill_warning:
            ui.draw_fill_warning(screen, font_medium, SCREEN_HEIGHT)
        else:
            ui.draw_instructions(screen, font_text, SCREEN_HEIGHT)

        draw_sudoku_buttons(screen, mouse_pos, chosen_game)
        draw_difficulty_buttons(screen, mouse_pos, selected_difficulty)
        new_game_button.draw(screen, mouse_pos)
        restart_button.draw(screen, mouse_pos)
        submit_button.draw(screen, mouse_pos)

    pygame.display.update()

pygame.quit()