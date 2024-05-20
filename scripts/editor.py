# Run via 'python3 scripts/editor.py' to view window
import pygame
import sys

from utils import load_images
from tilemap import Tilemap

RENDER_SCALE = 2.0


class Editor:
    def __init__(self):
        pygame.init()

        # Initialize the window (resolution via pixel tuple)
        pygame.display.set_caption('Jonin Level Editor')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        # Force game to run 60 FPS
        self.clock = pygame.time.Clock()

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
        }

        self.movement = [False, False, False, False]

        self.tilemap = Tilemap(self, tile_size=16)

        # Camera position
        self.scroll = [0, 0]

        # List of keys in self.assets dict
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False

    def run(self):
        # Important to remember: each frame is an iteration in a loop, so dynamic sleep
        while True:
            # Reset screen color
            self.display.fill((0, 0, 0))

            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy(
            )
            current_tile_img.set_alpha(100)  # Somewhat transparent

            self.display.blit(current_tile_img, (5, 5))

            # User input
            for event in pygame.event.get():
                # User quits the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # User activates mouse button/scroll wheel
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True

                    if event.button == 3:
                        self.right_clicking = True

                    # Shift for variants within group
                    if self.shift:
                        if event.button == 4:
                            # Loop trick with modulo
                            self.tile_variant = (
                                self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])

                        if event.button == 5:
                            self.tile_variant = (
                                self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    # Non-shift for groups
                    else:
                        if event.button == 4:
                            # Loop trick with modulo
                            self.tile_group = (
                                self.tile_group - 1) % len(self.tile_list)
                            # Default variant for that group
                            self.tile_variant = 0

                        if event.button == 5:
                            self.tile_group = (
                                self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0

                # Clicking variable based on mouse state
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                # User presses down on a key
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                # User lifts up from a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)  # 60 FPS


Editor().run()
