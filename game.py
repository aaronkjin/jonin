# Run via 'python3 game.py' to view window
import pygame
import sys
import os
import random
import math

from scripts.entities import PhysicsEntity, Player, Enemy
from scripts.utils import load_image, load_images, Animation
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark


class Game:
    def __init__(self):
        pygame.init()

        # Initialize the window (resolution via pixel tuple)
        pygame.display.set_caption('Jonin')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        # Force game to run 60 FPS
        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "clouds": load_images("clouds"),
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), img_dur=6),
            "enemy/run": Animation(load_images("entities/enemy/run"), img_dur=4),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=6),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
            "particle/leaf": Animation(load_images("particles/leaf"), img_dur=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), img_dur=6, loop=False),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }

        self.clouds = Clouds(self.assets["clouds"], count=16)

        self.player = Player(self, (50, 50), (8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        # Load in the map e.g. 0, 1, 2
        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0

    def load_level(self, map_id):
        self.tilemap.load("data/maps/" + str(map_id) + ".json")

        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            # Hitbox for tree
            self.leaf_spawners.append(pygame.Rect(
                4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))

        self.projectiles = []
        self.particles = []
        self.sparks = []

        # Camera position
        self.scroll = [0, 0]

        # Track player's death
        self.dead = 0

        # Transition between levels upon success
        self.transition = -30

    def run(self):
        # Important to remember: each frame is an iteration in a loop, so dynamic sleep
        while True:
            self.display.fill((0, 0, 0, 0))
            # Reset screen color
            self.display_2.blit(self.assets["background"], (0, 0))

            # Screenshake timer goes down to 0
            self.screenshake = max(0, self.screenshake - 1)

            # Killed all the enemies in the level
            if not len(self.enemies):
                self.transition += 1

                # Absolute is 30 = black screen; Absolute is 0 = can see everything
                if self.transition > 30:
                    self.level = min(
                        len(os.listdir("data/maps")) - 1, self.level + 1)
                    self.load_level(self.level)

            if self.transition < 0:
                self.transition += 1

            # Death has been tracked!
            if self.dead:
                self.dead += 1

                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)

                # 40 frames a.k.a. 2/3 of a second
                if self.dead > 40:
                    self.load_level(self.level)

            # Camera movement in relation to player
            self.scroll[0] += (self.player.rect().centerx -
                               self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery -
                               self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Spawn leaf particles at controlled rate
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width,
                           rect.y + random.random() * rect.height)
                    self.particles.append(
                        Particle(self, "leaf", pos, velocity=[-0.1, 0.3], frame=random.randint(0, 20)))

            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            self.tilemap.render(self.display, offset=render_scroll)

            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)

                # Enemies die upon dash
                if kill:
                    self.enemies.remove(enemy)

            if not self.dead:
                # Player moves left and right; no need to change y-axis
                self.player.update(
                    self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets["projectile"]
                self.display.blit(img, (projectile[0][0] - img.get_width(
                ) / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))

                # Check if location of projectile is solid, i.e. it hit something
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)

                    for _ in range(4):
                        # Shoot sparks to the left iff sparks are facing right
                        self.sparks.append(
                            Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                # Remove projectiles that have been flying for more than 6 secs
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                # Dashing makes player invincible against projectiles
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        # Hit the player!
                        self.projectiles.remove(projectile)

                        self.dead += 1
                        self.screenshake = max(16, self.screenshake)

                        # Lots of animations upon player death
                        for _ in range(30):
                            # Random angle in circle
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(
                                Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, "particle", self.player.rect().center, velocity=[
                                                  math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))

            # Self-managing for updating and removing sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            # Mask for image with two colors
            display_mask = pygame.mask.from_surface(self.display)

            for particle in self.particles.copy():
                # Update and render leaf particles
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == "leaf":
                    # Smoothly go between -1 and 1 (sway left and right)
                    particle.pos[0] += math.sin(
                        particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)

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
                        self.player.jump()
                    if event.key == pygame.K_x:  # "X" to dash
                        self.player.dash()

                # User lifts up from a key
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            # Draw level transition circle animation
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width(
                ) // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            # Random modification from pixels 0 to screenshake value
            screenshake_offset = (
                random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(
                self.display, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)  # 60 FPS


Game().run()
