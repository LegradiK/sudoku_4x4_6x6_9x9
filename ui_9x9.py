import pygame


class GameState_9x9:
    def __init__(self, grid, original_grid, cell_size, font_4x4, font_6x6, font_9x9, font_medium, font_text):
        self.grid = grid
        self.original_grid = original_grid
        self.solution = None
        self.cell_size = cell_size
        self.font_num = font_4x4
        self.font_num = font_6x6
        self.font_num = font_9x9
        self.font_medium = font_medium
        self.font_text = font_text
        self.selected_row = 0
        self.selected_col = 0
        self.wrong_cells = set()


def draw_background(screen):
    screen.fill((255, 255, 255))


def draw_grid_lines(screen, state):
    dif = state.cell_size

    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1

        pygame.draw.line(
            screen,
            (0, 0, 0),
            (0, i * dif),
            (dif * 9, i * dif),
            thickness
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            (i * dif, 0),
            (i * dif, dif * 9),
            thickness
        )


def draw_numbers(screen, state):
    dif = state.cell_size
    grid_size = len(state.grid)
    for row in range(grid_size):
        for col in range(grid_size):
            value = state.grid[row][col]

            if value != 0:
                # background color for original fixed cells
                if state.original_grid[row][col] != 0:
                    pygame.draw.rect(
                        screen,
                        (221, 221, 231),
                        (col * dif, row * dif, dif, dif)
                    )
                # background color if user entry is wrong
                if (row, col) in state.wrong_cells:
                    color = (255, 0, 0)
                else:
                    color = (0, 0, 0)

                text = state.font_num.render(str(value), True, color)
                text_rect = text.get_rect(center=(
                    col * dif + dif / 2,
                    row * dif + dif / 2
                ))

                screen.blit(text, text_rect)


def draw_selection(screen, state):
    dif = state.cell_size
    row = state.selected_row
    col = state.selected_col

    pygame.draw.rect(
        screen,
        (255, 222, 33),
        (col * dif, row * dif, dif, dif),
        4
    )


def draw_instructions(screen, font, height):
    lines = [
        "Arrow Keys: Move",
        "1-9: Input",
        "Backspace, Delete, e, d: Erase input",
        "ENTER: Submit your answer",
        "New Game / Restart: Press buttons",
    ]
    for i, line in enumerate(lines):
        text = font.render(line, True, (0, 0, 0))
        screen.blit(text, (820, height - 780 + i * 20))


def draw_result(screen, font, height):
    text = font.render("PUZZLE SOLVED!", True, (255, 140, 0))
    screen.blit(text, (810, height - 720))

def draw_warning(screen, font, height):
    text = font.render("Wrong answers", True, (200, 0, 0))
    screen.blit(text, (820, height - 720))

def draw_fill_warning(screen, font, height):
    text = font.render("Fill all cells", True, (255, 191, 0))
    screen.blit(text, (820, height - 720))