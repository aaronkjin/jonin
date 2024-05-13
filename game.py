import pygame

pygame.init()

# Initialize the window (resolution via pixel tuple)
pygame.display.set_caption('Jonin')
screen = pygame.display.set_mode((640, 480))

# Force game to run 60 FPS
clock = pygame.time.Clock()

# Important to remember: each frame is an iteration in a loop, so dynamic sleep
while True:
    # User input
    for event in pygame.event.get():
        # User quits the game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    pygame.display.update()
    clock.tick(60)  # 60 FPS
