import pygame

import math


class Spark:
    def __init__(self, pos, angle, speed):
        self.pos = list(pos)
        self.angle = angle
        self.speed = speed

    def update(self):
        # Polar to Cartesian
        self.pos[0] += math.cos(self.angle) * self.speed
        self.pos[1] += math.sin(self.angle) * self.speed

        # Use speed itself as a timer
        self.speed = max(0, self.speed - 0.1)
        return not self.speed

    def render(self, surf, offset=(0, 0)):
        # Diamond-shaped sparks via trigonometry
        render_points = [
            (self.pos[0] + math.cos(self.angle) * self.speed * 3 - offset[0],
             self.pos[1] + math.sin(self.angle) * self.speed * 3 - offset[1])
        ]

        pygame.draw.polygon(surf, (255, 255, 255), render_points)
