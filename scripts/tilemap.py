import pygame
import json

# All permutations of -1 to 1 for player's position
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1),
                    (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
# A set of tiles that interact with physics
PHYSICS_TILES = {"grass", "stone"}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def tiles_around(self, pos):
        tiles = []
        # Change pixel position to grid position
        tile_loc = (int(pos[0] // self.tile_size),
                    int(pos[1] // self.tile_size))

        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + \
                ";" + str(tile_loc[1] + offset[1])

            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])

        return tiles

    # Save level-edited map as JSON
    def save(self, path):
        f = open(path, "w")
        json.dump({"tilemap": self.tilemap, "tile_size": self.tile_size,
                  "offgrid": self.offgrid_tiles}, f)
        f.close()

    def physics_rects_around(self, pos):
        rects = []

        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(pygame.Rect(
                    tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects

    def render(self, surf, offset=(0, 0)):
        # Render logic for off-grid lists
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile["type"]]
                      [tile["variant"]], (tile["pos"][0] - offset[0], tile["pos"][1] - offset[1]))

        # Iterate from left edge to right edge, top edge to bottom edge of screen
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ";" + str(y)

                # Render logic for dicts in tilemap
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile["type"]][tile["variant"]], (
                        tile["pos"][0] * self.tile_size - offset[0], tile["pos"][1] * self.tile_size - offset[1]))
