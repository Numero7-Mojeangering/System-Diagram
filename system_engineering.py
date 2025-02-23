# main.py
import pygame
import sys
import json
from system import load_system_from_dict

def main():
    pygame.init()
    font = pygame.font.SysFont(None, 20)

    # Load architecture from a JSON file.
    with open("game_system.json", "r") as f:
        data = json.load(f)
    game_system = load_system_from_dict(data)
    
    # Prepare the top-level system for layout.
    game_system.rect = pygame.Rect(0, 0, game_system.size[0], game_system.size[1])
    game_system.rect.center = game_system.position
    # Use the circle layout to position direct subsystems.
    game_system.layout_subsystems_circle(150)
    
    # Compute the bounding box of the entire systems hierarchy and shift to add margin.
    dummy_surface = pygame.Surface((800, 600))
    game_system.draw(dummy_surface, font)
    bbox = game_system.get_bounding_box()
    margin = 50
    canvas_width = int(bbox[2] - bbox[0] + 2 * margin)
    canvas_height = int(bbox[3] - bbox[1] + 2 * margin)
    offset_x = -bbox[0] + margin
    offset_y = -bbox[1] + margin
    game_system.shift(offset_x, offset_y)
    
    screen = pygame.display.set_mode((canvas_width, canvas_height))
    pygame.display.set_caption("Game Systems Interaction Loaded from JSON")
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game_system.update_physics(dt)
        screen.fill((255, 255, 255))
        game_system.draw(screen, font)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
