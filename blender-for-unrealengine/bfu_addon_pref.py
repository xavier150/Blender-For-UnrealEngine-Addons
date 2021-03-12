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

import os
import bpy
import addon_utils

from . import bfu_export_asset
from . import bfu_write_text
from . import bfu_basics
from .bfu_basics import *
from . import bfu_utils
from . import bfu_check_potential_error
from .bfu_utils import *
from . import bfu_ui_utils
from . import languages
from .languages import *


if "bpy" in locals():
    import importlib
    if "bfu_export_asset" in locals():
        importlib.reload(bfu_export_asset)
    if "bfu_write_text" in locals():
        importlib.reload(bfu_write_text)
    if "bfu_basics" in locals():
        importlib.reload(bfu_basics)
    if "bfu_utils" in locals():
        importlib.reload(bfu_utils)
    if "bfu_check_potential_error" in locals():
        importlib.reload(bfu_check_potential_error)
    if "bfu_ui_utils" in locals():
        importlib.reload(bfu_ui_utils)
    if "languages" in locals():
        importlib.reload(languages)


from bpy.props import (
        StringProperty,
        BoolProperty,
        EnumProperty,
        IntProperty,
        FloatProperty,
        FloatVectorProperty,
        PointerProperty,
        CollectionProperty,
        )

from bpy.types import (
        Operator,
        )


class BFU_AP_AddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    bakeArmatureAction: BoolProperty(
        name=(ti('bake_armature_action_name')),
        description=(tt('bake_armature_action_desc')),
        default=False,
        )

    correctExtremUVScale: BoolProperty(
        name=(ti('correct_extrem_uv_scale_name')),
        description=(tt('correct_extrem_uv_scale_desc')),
        default=False,
        )

    removeSkeletonRootBone: BoolProperty(
        name=(ti('remove_skeleton_root_bone_name')),
        description=(tt('remove_skeleton_root_bone_desc')),
        default=True,
        )

    skeletonRootBoneName: StringProperty(
        name=(ti('skeleton_root_bone_name_name')),
        description=(tt('skeleton_root_bone_name_desc')),
        default="ArmatureRoot",
        )

    rescaleFullRigAtExport: EnumProperty(
        name=(ti('rescale_full_rig_at_export_name')),
        description=(tt('rescale_full_rig_at_export_desc')),
        items=[
            ("auto",
                ti('rescale_full_rig_at_export_auto_name'),
                tt('rescale_full_rig_at_export_auto_desc'),
                "SHADERFX",
                1),
            ("custom_rescale",
                ti('rescale_full_rig_at_export_custom_rescale_name'),
                tt('rescale_full_rig_at_export_custom_rescale_desc'),
                "MODIFIER",
                2),
            ("dont_rescale",
                ti('rescale_full_rig_at_export_dont_rescale_name'),
                tt('rescale_full_rig_at_export_dont_rescale_desc'),
                "CANCEL",
                3)
            ]
        )

    newRigScale: FloatProperty(
        name=(ti('new_rig_scale_name')),
        description=(tt('new_rig_scale_desc')),
        default=100,
        )

    staticSocketsAdd90X: BoolProperty(
        name=(ti('static_sockets_add_90_x_name')),
        description=(tt('static_sockets_add_90_x_desc')),
        default=True,
        )

    rescaleSocketsAtExport: EnumProperty(
        name=(ti('rescale_sockets_at_export_name')),
        description=(tt('rescale_sockets_at_export_desc')),
        items=[
            ("auto",
                ti('rescale_sockets_at_export_auto_name'),
                tt('rescale_sockets_at_export_auto_desc'),
                "SHADERFX",
                1),
            ("custom_rescale",
                ti('rescale_sockets_at_export_custom_rescale_name'),
                tt('rescale_sockets_at_export_custom_rescale_desc'),
                "MODIFIER",
                2),
            ("dont_rescale",
                ti('rescale_sockets_at_export_dont_rescale_name'),
                tt('rescale_sockets_at_export_dont_rescale_desc'),
                "CANCEL",
                3)
            ]
        )

    staticSocketsImportedSize: FloatProperty(
        name=(ti('static_sockets_imported_size_name')),
        description=(tt('static_sockets_imported_size_desc')),
        default=1,
        )

    skeletalSocketsImportedSize: FloatProperty(
        name=(ti('skeletal_sockets_imported_size_name')),
        description=(tt('skeletal_sockets_imported_size_desc')),
        default=1,
        )

    ignoreNLAForAction: BoolProperty(
        name=(ti('ignore_nla_for_action_name')),
        description=(tt('ignore_nla_for_action_desc')),
        default=False,
        )

    exportWithCustomProps: BoolProperty(
        name=(ti('export_with_custom_props_name')),
        description=(tt('export_with_custom_props_desc')),
        default=False,
        )

    exportWithMetaData: BoolProperty(
        name=(ti('export_with_meta_data_name')),
        description=(tt('export_with_meta_data_desc')),
        default=False,
        )

    revertExportPath: BoolProperty(
        name=(ti('revert_export_path_name')),
        description=(tt('revert_export_path_desc')),
        default=False,
        )

    useGeneratedScripts: BoolProperty(
        name=(ti('use_generated_scripts_name')),
        description=(tt('use_generated_scripts_desc')),
        default=True,
        )

    collisionColor:  FloatVectorProperty(
        name='Collision color.',
        description='Color of the collision in Blender',
        subtype='COLOR',
        size=4,
        default=(0, 0.6, 0, 0.11),
        min=0.0, max=1.0,
        )

    notifyUnitScalePotentialError: BoolProperty(
        name='Notify UnitScale (PotentialError)',
        description=(
            'Notify as potential error' +
            ' if the unit scale is not equal to 0.01.'
            ),
        default=True,
        )

    class BFU_OT_OpenDocumentationTargetPage(Operator):
        bl_label = "Documentation"
        bl_idname = "object.open_documentation_target_page"
        bl_description = "Clic for open documentation page on GitHub"
        octicon: StringProperty(default="")

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/How-export-assets" +
                "#"+self.octicon
                )
            return {'FINISHED'}

    class BFU_OT_NewReleaseInfo(Operator):
        bl_label = "Open last release page"
        bl_idname = "object.new_release_info"
        bl_description = "Clic for open latest release page."

        def execute(self, context):
            os.system(
                "start \"\" https://github.com/xavier150/" +
                "Blender-For-UnrealEngine-Addons/releases/latest"
                )
            return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        def LabelWithDocButton(tagetlayout, name, docOcticon):
            newRow = tagetlayout.row()
            newRow.label(text=name)
            docOperator = newRow.operator(
                "object.open_documentation_target_page",
                icon="HELP",
                text=""
                )
            docOperator.octicon = docOcticon

        def PropWithDocButton(tagetlayout, name, docOcticon):
            newRow = tagetlayout.row()
            newRow.prop(self, name)
            docOperator = newRow.operator(
                "object.open_documentation_target_page",
                icon="HELP",
                text=""
                )
            docOperator.octicon = docOcticon

        boxColumn = layout.column().split(
            factor=0.5
            )

        rootBone = boxColumn.box()

        LabelWithDocButton(
            rootBone,
            "SKELETON & ROOT BONE",
            "skeleton--root-bone"
            )
        rootBone.prop(self, "removeSkeletonRootBone")
        rootBoneName = rootBone.column()
        rootBoneName.enabled = not self.removeSkeletonRootBone
        rootBoneName.prop(self, "skeletonRootBoneName")

        rootBone.prop(self, "rescaleFullRigAtExport")
        newRigScale = rootBone.column()
        newRigScale.enabled = self.rescaleFullRigAtExport == "custom_rescale"
        newRigScale.prop(self, "newRigScale")

        socket = boxColumn.box()
        socket.label(text='SOCKET')
        socket.prop(self, "staticSocketsAdd90X")
        socket.prop(self, "rescaleSocketsAtExport")
        socketRescale = socket.column()
        socketRescale.enabled = self.rescaleSocketsAtExport == "custom_rescale"
        socketRescale.prop(self, "staticSocketsImportedSize")
        socketRescale.prop(self, "skeletalSocketsImportedSize")

        boxColumn = layout.column().split(factor=0.5)

        data = boxColumn.box()
        data.label(text='DATA')
        data.prop(self, "ignoreNLAForAction")
        PropWithDocButton(data, "correctExtremUVScale", "uv")
        data.prop(self, "bakeArmatureAction")
        data.prop(self, "exportWithCustomProps")
        data.prop(self, "exportWithMetaData")
        data.prop(self, "revertExportPath")

        script = boxColumn.box()
        script.label(text='IMPORT SCRIPT')
        script.prop(self, "useGeneratedScripts")

        boxColumn = layout.column().split(factor=0.5)

        other = boxColumn.box()
        other.label(text='OTHER')
        other.prop(self, "collisionColor")
        other.prop(self, "notifyUnitScalePotentialError")

        updateButton = layout.row()
        updateButton.scale_y = 2.0
        updateButton.operator("object.new_release_info", icon="TIME")


classes = (
    BFU_AP_AddonPreferences,
    BFU_AP_AddonPreferences.BFU_OT_NewReleaseInfo,
    BFU_AP_AddonPreferences.BFU_OT_OpenDocumentationTargetPage,
)


def menu_func(self, context):
    layout = self.layout
    col = layout.column()
    col.separator(factor=1.0)
    col.operator(BFU_PT_CorrectAndImprov.BFU_OT_CorrectExtremUV.bl_idname)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.VIEW3D_MT_uv_map.remove(menu_func)
