# All permutations of -1 to 1 for player's position
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1),
                    (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]


class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []

        for i in range(10):
            # Tile as a dictionary of metadata
            self.tilemap[str(
                3 + i) + ";10"] = {"type": "grass", "variant": 1, "pos": (3 + i, 10)}
            self.tilemap["10;" + str(
                5 + i)] = {"type": "stone", "variant": 1, "pos": (10, i + 5)}

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

    def render(self, surf):
        # Render logic for off-grid lists
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile["type"]]
                      [tile["variant"]], tile["pos"])

        # Render logic for dicts
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile["type"]][tile["variant"]], (
                tile["pos"][0] * self.tile_size, tile["pos"][1] * self.tile_size))
