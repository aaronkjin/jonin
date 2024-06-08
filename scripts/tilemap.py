import pygame
import json
import os

# All permutations of -1 to 1 for player's position
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1),
                    (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]

# A set of tiles that interact with physics
PHYSICS_TILES = {"grass", "stone"}

# Constants for autotiling
AUTOTILE_TYPES = {"grass", "stone"}
AUTOTILE_MAP = {
    # To ensure same order every time
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, -1)])): 8,
}


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

    def extract(self, id_pairs, keep=False):
        matches = []

        for tile in self.offgrid_tiles.copy():
            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())

                # Remove from list if we don't want to keep
                if not keep:
                    self.offgrid_tiles.remove(tile)

        for loc in list(self.tilemap.keys()):
            tile = self.tilemap[loc]

            if (tile["type"], tile["variant"]) in id_pairs:
                matches.append(tile.copy())
                # Change position to pixels
                matches[-1]["pos"] = matches[-1]["pos"].copy()
                matches[-1]["pos"][0] *= self.tile_size
                matches[-1]["pos"][1] *= self.tile_size

                if not keep:
                    del self.tilemap[loc]

        return matches

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
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

        f = open(path, "w")
        json.dump({"tilemap": self.tilemap, "tile_size": self.tile_size,
                  "offgrid": self.offgrid_tiles}, f)
        f.close()

    def load(self, path):
        f = open(path, "r")
        map_data = json.load(f)
        f.close()

        # Load up existing level-edited map
        self.tilemap = map_data["tilemap"]
        self.tile_size = map_data["tile_size"]
        self.offgrid_tiles = map_data["offgrid"]

    def physics_rects_around(self, pos):
        rects = []

        for tile in self.tiles_around(pos):
            if tile["type"] in PHYSICS_TILES:
                rects.append(pygame.Rect(
                    tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size, self.tile_size, self.tile_size))

        return rects

    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()

            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile["pos"][0] + shift[0]) + \
                    ";" + str(tile["pos"][1] + shift[1])
                if check_loc in self.tilemap:
                    # Neighbor tile is in same group as the tile itself
                    if self.tilemap[check_loc]["type"] == tile["type"]:
                        neighbors.add(shift)

            neighbors = tuple(sorted(neighbors))
            if (tile["type"] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile["variant"] = AUTOTILE_MAP[neighbors]

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
