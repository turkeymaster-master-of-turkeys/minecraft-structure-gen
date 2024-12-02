import os

import litemapy
import nbtlib
import nbtschematic
import torch


class MinecraftRegion:
  def __init__(self, filename):
    self.filename = filename
    if filename.endswith('.schematic'):
      self.schematic = nbtschematic.SchematicFile.load(
        "C:\minecraft-structure-gen\schematics\minecraft-schematic\Houses And Shops\Watermill.schematic")
      self.regions = None
    elif filename.endswith('.litematic'):
      self.schematic = None
      nbt = nbtlib.File.load(filename, True)
      self.regions = litemapy.Schematic.from_nbt(nbt['']).regions

  def get(self, x: int, y: int, z: int):
    if self.regions is not None:
      return self.regions[0].getblock(x, y, z)
    elif self.schematic is not None:
      return self.schematic[x, y, z]

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