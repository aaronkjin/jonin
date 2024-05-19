# Run via 'python3 game.py' to view window
import pygame
import sys

from scripts.utils import load_images
from scripts.tilemap import Tilemap

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

    def run(self):
        # Important to remember: each frame is an iteration in a loop, so dynamic sleep
        while True:
            # Reset screen color
            self.display.fill((0, 0, 0))

            # User input
            for event in pygame.event.get():
                # User quits the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

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

            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()
            self.clock.tick(60)  # 60 FPS


Editor().run()
