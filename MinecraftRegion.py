import os
import pickle

import litemapy
import nbtlib
import nbtschematic
import torch


class MinecraftRegion:

    def __init__(self, filename):
        self.filename = filename

    def get(self, x: int, y: int, z: int):
        pass

    def iterator(self):
        pass

    def to_tensor(self):
        pass

    @staticmethod
    def convert_to_tensor(root_dir: str = "schematics"):
        subdirectories = [name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]
        files = os.listdir(root_dir)

        for file in files:
            region = MinecraftRegion.from_file(os.path.join(root_dir, file))
            tensor = region.to_tensor()
            torch.save(tensor, os.path.join(root_dir, "../data", file))

        for subdirectory in subdirectories:
            MinecraftRegion.convert_to_tensor(os.path.join(root_dir, subdirectory))

    @staticmethod
    def from_file(filename: str):
        if filename.endswith('.schematic'):
            return SchematicRegion(filename)
        elif filename.endswith('.litematic'):
            return LitematicRegion(filename)
        else:
            return None


class SchematicRegion(MinecraftRegion):
    id_dict = pickle.loads(open("id_dict.pickle", "rb").read())

    def __init__(self, filename):
        super().__init__(filename)
        if filename.endswith('.schematic'):
            self.schematic = nbtschematic.SchematicFile.load(filename)

    def get(self, x: int, y: int, z: int):
        return MinecraftRegion.id_dict[self.schematic.blocks[x, y, z]]

    def iterator(self):
        (width, height, length) = self.schematic.blocks.shape
        for x in range(width):
            for y in range(height):
                for z in range(length):
                    yield MinecraftRegion.id_dict[self.schematic.blocks[x, y, z]]

    def to_tensor(self):
        return torch.tensor()


class LitematicRegion(MinecraftRegion):

    def __init__(self, filename):
        super().__init__(filename)
        nbt = nbtlib.File.load(filename, True)
        self.regions = list(litemapy.Schematic.from_nbt(nbt['']).regions.values())

    def get(self, x: int, y: int, z: int):
        for region in self.regions:
            if region.minschemx() <= x < region.maxschemx() and region.minschemy() <= y < region.maxschemy() and region.minschemz() <= z < region.maxschemz():
                return region[x - region.minschemx(), y - region.minschemy(), z - region.minschemz()]
        return None

    def iterator(self):
        for region in self.regions:
            for (x, y, z) in region.allblockpos():
                yield region[x, y, z]

    def to_tensor(self):
        return torch.tensor()


if __name__ == "__main__":
    # region = MinecraftRegion.from_file(r"schematics\minecraft-schematic\Houses And Shops\Watermill.schematic")
    region = MinecraftRegion.from_file(r"schematics/minecraft-schematic/Houses And Shops/Large Survival Mansion.litematic")
    print(region.get(0, 0, 0))
