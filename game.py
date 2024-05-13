# Run via 'python3 game.py' to view window
import pygame
import sys


class Game:
    def __init__(self):
        pygame.init()

        # Initialize the window (resolution via pixel tuple)
        pygame.display.set_caption('Jonin')
        self.screen = pygame.display.set_mode((640, 480))

        # Force game to run 60 FPS
        self.clock = pygame.time.Clock()

        self.img = pygame.image.load('data/images/clouds/cloud_1.png')

        self.img_pos = [160, 260]  # x,y
        self.movement = [False, False]

    def run(self):
        # Important to remember: each frame is an iteration in a loop, so dynamic sleep
        while True:
            self.img_pos[1] += self.movement[1] - \
                self.movement[0]  # T/F as boolean 1's/0's
            self.screen.blit(self.img, self.img_pos)

            # User input
            for event in pygame.event.get():
                # User quits the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # User presses down on a key
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True

                # User lifts up from a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False

            pygame.display.update()
            self.clock.tick(60)  # 60 FPS


Game().run()
