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

import bpy

from . import bfu_basics
from . import bfu_utils


def WriteImportPythonHeadComment(useSequencer=False):

    scene = bpy.context.scene

    # Comment
    ImportScript = (
        "#This script was generated with the addons Blender for UnrealEngine" +
        " : https://github.com/xavier150/Blender-For-UnrealEngine-Addons" +
        "\n"
        )
    if useSequencer:
        ImportScript += (
            "#It will import into Unreal Engine all the assets of type" +
            " StaticMesh, SkeletalMesh, Animation and Pose" +
            "\n")
    else:
        ImportScript += (
            "#This script will import in unreal" +
            " all camera in target sequencer" +
            "\n")

    ImportScript += (
        "#The script must be used in Unreal Engine Editor" +
        " with Python plugins : " +
        "https://docs.unrealengine.com/en-US/Engine/" +
        "Editor/ScriptingAndAutomation/Python" +
        "\n"
        )

    if useSequencer:
        ImportScript += "#Use this command : " + bfu_utils.GetImportSequencerScriptCommand() + "\n"
    else:
        ImportScript += "#Use this command : " + bfu_utils.GetImportAssetScriptCommand() + "\n"
    ImportScript += "\n"
    ImportScript += "\n"
    return ImportScript
