# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

import importlib

from . import asset_import
from . import sequencer_import

if "asset_import" in locals():
    importlib.reload(asset_import)
if "sequencer_import" in locals():
    importlib.reload(sequencer_import)



print("Import module loaded.")

def run_asset_import(assets_data):
    pass
    asset_import.ImportAllAssets(assets_data)

def run_sequencer_import(sequence_data):
    pass
    sequencer_import.CreateSequencer(sequence_data)