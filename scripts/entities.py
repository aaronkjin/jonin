import pygame
import math
import random

from scripts.particle import Particle
from scripts.spark import Spark


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)  # S.t. each entity has its own list for positions
        self.size = size
        self.velocity = [0, 0]  # Derivative of position
        self.collisions = {"up": False, "down": False,
                           "right": False, "left": False}

        self.action = ""
        # Padding to edges of images, so there's space for animations
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action("idle")

        self.last_movement = [0, 0]

    def rect(self):
        # Four corners to create the rect
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def set_action(self, action):
        # Action has changed, so change animation
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type +
                                              "/" + self.action].copy()

    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {"up": False, "down": False,
                           "right": False, "left": False}
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        # X-axis
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()

        # Collision detection
        for rect in tilemap.physics_rects_around(self.pos):
            # There is a collision
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:  # Right
                    entity_rect.right = rect.left
                    self.collisions["right"] = True
                if frame_movement[0] < 0:  # Left
                    entity_rect.left = rect.right
                    self.collisions["left"] = True

                self.pos[0] = entity_rect.x

        # Y-axis
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()

        # Collision detection
        for rect in tilemap.physics_rects_around(self.pos):
            # There is a collision
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:  # Bottom
                    entity_rect.bottom = rect.top
                    self.collisions["down"] = True
                if frame_movement[1] < 0:  # Top
                    entity_rect.top = rect.bottom
                    self.collisions["up"] = True

                self.pos[1] = entity_rect.y

        if movement[0] > 0:  # Player moving right
            self.flip = False
        if movement[0] < 0:  # Player moving left
            self.flip = True

        self.last_movement = movement

        # Terminal velocity for y-axis
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Reset for falling or wall-jumping
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

        self.animation.update()

    def render(self, surf, offset=(0, 0)):
        # If player faces left, animate towards left, and vice versa (only for x-axis)
        surf.blit(pygame.transform.flip(
            self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Enemy(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, "enemy", pos, size)

        # Walking movement like a Koopa from Mario
        self.walking = 0

    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            # Scan forward-facing direction and into the ground
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions["right"] or self.collisions["left"]):
                    # Flip around like a Koopa when running into walls
                    self.flip = not self.flip
                else:
                    # Walk in one direction
                    movement = (
                        movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip

            # 1 frame between walking and not walking
            self.walking = max(0, self.walking - 1)

            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0],
                       self.game.player.pos[1] - self.pos[1])

                # Enemy is able to shoot player
                if (abs(dis[1]) < 16):
                    # Facing left
                    if (self.flip and dis[0] < 0):
                        self.game.projectiles.append(
                            [[self.rect().centerx - 7, self.rect().centery], -1.5, 0])

                        for _ in range(4):
                            # Unit circle logic with variance added to speed
                            self.game.sparks.append(Spark(
                                self.game.projectiles[-1][0], random.random() - 0.5 + math.pi, 2 + random.random()))
                    # Facing right
                    if (not self.flip and dis[0] > 0):
                        self.game.projectiles.append(
                            [[self.rect().centerx + 7, self.rect().centery], 1.5, 0])

                        for _ in range(4):
                            self.game.sparks.append(Spark(
                                self.game.projectiles[-1][0], random.random() - 0.5, 2 + random.random()))

        # 1 in every 1.67 seconds because 60 FPS
        elif random.random() < 0.01:
            # 0.5 seconds to 2 seconds
            self.walking = random.randint(30, 120)

        super().update(tilemap, movement=movement)

        # Animation: either moving or staying still
        if movement[0] != 0:
            self.set_action("run")
        else:
            self.set_action("idle")

        # Player's hitbox collides into enemy's hitbox while they are dashing
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                return True

    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)

        if self.flip:
            # Load gun to make it flippable and placed correctly on enemy
            surf.blit(pygame.transform.flip(self.game.assets["gun"], True, False), (self.rect(
            ).centerx - 4 - self.game.assets["gun"].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets["gun"], (self.rect(
            ).centerx + 4 - offset[0], self.rect().centery - offset[1]))


class Player(PhysicsEntity):
    # Player class inherits all of physics entity's class plus more
    def __init__(self, game, pos, size):
        super().__init__(game, "player", pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0

    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)

        self.air_time += 1
        if self.collisions["down"]:
            self.air_time = 0
            self.jumps = 1

        # A single frame switch when on a wall + in the air
        self.wall_slide = False
        if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 4:
            self.wall_slide = True
            # Cap velocity to 0.5
            self.velocity[1] = min(self.velocity[1], 0.5)

            # Right wall slide animation
            if self.collisions["right"]:
                self.flip = False
            # Left wall slide animation
            else:
                self.flip = True
            self.set_action("wall_slide")

        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action("jump")
            elif movement[0] != 0:
                self.set_action("run")
            else:
                self.set_action("idle")

        # Burst of particles
        if abs(self.dashing) in {60, 50}:  # Start or end of dash
            for _ in range(20):
                # Add particles while dashing using trigonometry
                angle = random.random() * math.pi * 2  # Angle from circle
                speed = random.random() * 0.5 + 0.5    # 0.5 to 1
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(
                    Particle(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            # 1 x 8 or -1 x 8 for first ten frames
            self.velocity[0] = abs(self.dashing) / self.dashing * 8

            if abs(self.dashing) == 51:
                # Sudden stop to the dash; acts as a cooldown
                self.velocity[0] *= 0.1

            # Stream of particles
            angle = random.random() * math.pi * 2
            speed = random.random() * 0.5 + 0.5
            pvelocity = [abs(self.dashing) / self.dashing *
                         random.random() * 3, 0]      # 0 to 3
            self.game.particles.append(
                Particle(self.game, "particle", self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))

        # Zero as the equilibrium
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

    def render(self, surf, offset=(0, 0)):
        # Dash is on cooldown, or not dashing at all
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)

    def jump(self):
        if self.wall_slide:
            # Facing left and moving towards the left
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5  # Force to animate jump
                self.jumps = max(0, self.jumps - 1)
                return True
            # Facing right and moving towards the right
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True

        elif self.jumps:
            self.velocity[1] = -3
            self.jumps -= 1
            self.air_time = 5
            return True

    def dash(self):
        if not self.dashing:
            # How much to dash + direction
            if self.flip:
                self.dashing = -60  # Velocity = speed + direction
            else:
                self.dashing = 60
