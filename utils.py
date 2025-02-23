# utils.py
import pygame
import math

def get_edge_point(rect, center, direction):
    """
    Calculate the intersection point on the edge of an axis-aligned rectangle.
    
    Args:
        rect: pygame.Rect object.
        center: (x, y) tuple for the rectangle's center.
        direction: (dx, dy) vector from the center in which to find the edge.
        
    Returns:
        (x, y) tuple representing the point on the rectangle's edge along the direction.
    """
    dx, dy = direction
    # Avoid divide-by-zero: if the direction is (0,0) return the center.
    if dx == 0 and dy == 0:
        return center

    half_width = rect.width / 2.0
    half_height = rect.height / 2.0

    if dx == 0:
        scale = half_height / abs(dy)
    elif dy == 0:
        scale = half_width / abs(dx)
    else:
        scale = min(half_width / abs(dx), half_height / abs(dy))
    return (center[0] + dx * scale, center[1] + dy * scale)

def draw_arrow(screen, start, end, text, font, color=(0, 0, 0)):
    """Draw an arrow from start to end with a text label at its midpoint."""
    pygame.draw.line(screen, color, start, end, 2)
    rotation = math.atan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 10
    arrow_angle = math.pi / 6  # 30° spread
    left = (end[0] - arrow_length * math.cos(rotation - arrow_angle),
            end[1] - arrow_length * math.sin(rotation - arrow_angle))
    right = (end[0] - arrow_length * math.cos(rotation + arrow_angle),
             end[1] - arrow_length * math.sin(rotation + arrow_angle))
    pygame.draw.polygon(screen, color, [end, left, right])
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2
    label_surface = font.render(text, True, color)
    label_rect = label_surface.get_rect(center=(mid_x, mid_y))
    screen.blit(label_surface, label_rect)
