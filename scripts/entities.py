import pygame


class PhysicsEntity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)  # S.t. each entity has its own list for positions
        self.size = size
        self.velocity = [0, 0]  # Derivative of position

    def update(self, movement=(0, 0)):
        frame_movement = (movement[0] + self.velocity[0],
                          movement[1] + self.velocity[1])

        # Change x, y position based on movement changes
        self.pos[0] += frame_movement[0]
        self.pos[1] += frame_movement[1]

        # Terminal velocity for y-axis
        self.velocity[1] = min(5, self.velocity[1] + 0.1)

    def render(self, surf):
        surf.blit(self.game.assets['player'], self.pos)
