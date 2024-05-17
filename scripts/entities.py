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

    def rect(self):
        # Four corners to create the rect
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

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

        # Terminal velocity for y-axis
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

        # Reset for falling or wall-jumping
        if self.collisions["down"] or self.collisions["up"]:
            self.velocity[1] = 0

    def render(self, surf, offset=(0, 0)):
        surf.blit(self.game.assets['player'],
                  (self.pos[0] - offset[0], self.pos[1] - offset[1]))
