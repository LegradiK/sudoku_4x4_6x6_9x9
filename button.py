import pygame
import sys

WHITE = (255, 255, 255)
BLUE = (70, 130, 180)
HIGHLIGHT = (30, 60, 110)  # darker shade for selected difficulty

class Button:
    def __init__(self, text, x, y, width, height, font_size=36, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.color = color if color is not None else BLUE
        self.hover_color = tuple(max(0, c - 30) for c in self.color)
    
    def draw(self, surface, mouse_position, highlighted=False):
        if highlighted:
            color = HIGHLIGHT
        elif self.rect.collidepoint(mouse_position):
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=0)
    
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)