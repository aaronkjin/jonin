import pygame


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

        # Zero as the equilibrium
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)

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
                self.dashing = -60
            else:
                self.dashing = 60
