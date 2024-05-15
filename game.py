# Run via 'python3 game.py' to view window
import pygame
import sys

from scripts.entities import PhysicsEntity


class Game:
    def __init__(self):
        pygame.init()

        # Initialize the window (resolution via pixel tuple)
        pygame.display.set_caption('Jonin')
        self.screen = pygame.display.set_mode((640, 480))

        # Force game to run 60 FPS
        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.player = PhysicsEntity(self, 'player', (50, 50), (8, 15))

    def run(self):
        # Important to remember: each frame is an iteration in a loop, so dynamic sleep
        while True:
            # Reset screen color
            self.screen.fill((14, 219, 248))

            # Player moves left and right; no need to change y-axis
            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.screen)

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

                # User lifts up from a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            pygame.display.update()
            self.clock.tick(60)  # 60 FPS


Game().run()
