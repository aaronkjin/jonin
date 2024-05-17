import random


class Cloud:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        self.pos[0] += self.speed

    def render(self, surf, offset=(0, 0)):
        # Parallax effect with cloud's depth's relationship with its speed
        render_pos = (self.pos[0] - offset[0] * self.depth,
                      self.pos[1] - offset[1] * self.depth)

        # Let's make life easy by looping the clouds
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(
        ), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
