import os
import pickle

import litemapy
import nbtlib
import nbtschematic
import torch


class MinecraftRegion:

    id_dict = pickle.loads(open("id_dict.pickle", "rb").read())

    def __init__(self, filename):
        self.filename = filename
        if filename.endswith('.schematic'):
            self.schematic = nbtschematic.SchematicFile.load(filename)
            self.regions = None
        elif filename.endswith('.litematic'):
            self.schematic = None
            nbt = nbtlib.File.load(filename, True)
            self.regions = list(litemapy.Schematic.from_nbt(nbt['']).regions.values())

    def get(self, x: int, y: int, z: int):
        if self.regions is not None:
            for region in self.regions:
                if region.minschemx() <= x < region.maxschemx() and region.minschemy() <= y < region.maxschemy() and region.minschemz() <= z < region.maxschemz():
                    return region[x - region.minschemx(), y - region.minschemy(), z - region.minschemz()]
            return None
        elif self.schematic is not None:
            return MinecraftRegion.id_dict[self.schematic.blocks[x, y, z]]

    def iterator(self):
        if self.regions is not None:
            for region in self.regions:
                for (x, y, z) in region.allblockpos():
                    yield region[x, y, z]
        elif self.schematic is not None:
            (width, height, length) = self.schematic.blocks.shape
            for x in range(width):
                for y in range(height):
                    for z in range(length):
                        yield MinecraftRegion.id_dict[self.schematic.blocks[x, y, z]]

    def to_tensor(self):
        return torch.tensor()

    @staticmethod
    def convert_to_tensor(root_dir: str = "schematics"):
        subdirectories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
        files = os.listdir(root_dir)

        for file in files:
            region = MinecraftRegion(os.path.join(root_dir, file))
            tensor = region.to_tensor()
            torch.save(tensor, os.path.join(root_dir, "../data", file))

        for subdirectory in subdirectories:
            MinecraftRegion.convert_to_tensor(os.path.join(root_dir, subdirectory))


if __name__ == "__main__":
    region = MinecraftRegion(r"schematics\minecraft-schematic\Houses And Shops\Watermill.schematic")
    print(list(region.iterator()))
