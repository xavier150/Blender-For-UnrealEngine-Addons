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

from .export import bfu_export_asset
from . import bfu_write_text
from . import bfu_basics
from . import bfu_utils
from . import bfu_check_potential_error
from . import bfu_ui_utils
from . import languages


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


class BFU_AP_AddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__

    bakeArmatureAction: bpy.props.BoolProperty(
        name=(languages.ti('bake_armature_action_name')),
        description=(languages.tt('bake_armature_action_desc')),
        default=False,
        )

    add_skeleton_root_bone: bpy.props.BoolProperty(
        name=(languages.ti('add_skeleton_root_bone_name')),
        description=(languages.tt('add_skeleton_root_bone_desc')),
        default=False,
        )

    skeleton_root_bone_name: bpy.props.StringProperty(
        name=(languages.ti('skeleton_root_bone_name_name')),
        description=(languages.tt('skeleton_root_bone_name_desc')),
        default="ArmatureRoot",
        )

    rescaleFullRigAtExport: bpy.props.EnumProperty(
        name=(languages.ti('rescale_full_rig_at_export_name')),
        description=(languages.tt('rescale_full_rig_at_export_desc')),
        items=[
            ("auto",
                languages.ti('rescale_full_rig_at_export_auto_name'),
                languages.tt('rescale_full_rig_at_export_auto_desc'),
                "SHADERFX",
                1),
            ("custom_rescale",
                languages.ti('rescale_full_rig_at_export_custom_rescale_name'),
                languages.tt('rescale_full_rig_at_export_custom_rescale_desc'),
                "MODIFIER",
                2),
            ("dont_rescale",
                languages.ti('rescale_full_rig_at_export_dont_rescale_name'),
                languages.tt('rescale_full_rig_at_export_dont_rescale_desc'),
                "CANCEL",
                3)
            ]
        )

    newRigScale: bpy.props.FloatProperty(
        name=(languages.ti('new_rig_scale_name')),
        description=(languages.tt('new_rig_scale_desc')),
        default=100,
        )

    staticSocketsAdd90X: bpy.props.BoolProperty(
        name=(languages.ti('static_sockets_add_90_x_name')),
        description=(languages.tt('static_sockets_add_90_x_desc')),
        default=True,
        )

    rescaleSocketsAtExport: bpy.props.EnumProperty(
        name=(languages.ti('rescale_sockets_at_export_name')),
        description=(languages.tt('rescale_sockets_at_export_desc')),
        items=[
            ("auto",
                languages.ti('rescale_sockets_at_export_auto_name'),
                languages.tt('rescale_sockets_at_export_auto_desc'),
                "SHADERFX",
                1),
            ("custom_rescale",
                languages.ti('rescale_sockets_at_export_custom_rescale_name'),
                languages.tt('rescale_sockets_at_export_custom_rescale_desc'),
                "MODIFIER",
                2),
            ("dont_rescale",
                languages.ti('rescale_sockets_at_export_dont_rescale_name'),
                languages.tt('rescale_sockets_at_export_dont_rescale_desc'),
                "CANCEL",
                3)
            ]
        )

    staticSocketsImportedSize: bpy.props.FloatProperty(
        name=(languages.ti('static_sockets_imported_size_name')),
        description=(languages.tt('static_sockets_imported_size_desc')),
        default=1,
        )

    skeletalSocketsImportedSize: bpy.props.FloatProperty(
        name=(languages.ti('skeletal_sockets_imported_size_name')),
        description=(languages.tt('skeletal_sockets_imported_size_desc')),
        default=1,
        )

    exportCameraAsFBX: bpy.props.BoolProperty(
        name=(languages.ti('export_camera_as_fbx_name')),
        description=(languages.tt('export_camera_as_fbx_desc')),
        default=False,
        )

    bakeOnlyKeyVisibleInCut: bpy.props.BoolProperty(
        name=(languages.ti('bake_only_key_visible_in_cut_name')),
        description=(languages.tt('bake_only_key_visible_in_cut_desc')),
        default=True,
        )

    ignoreNLAForAction: bpy.props.BoolProperty(
        name=(languages.ti('ignore_nla_for_action_name')),
        description=(languages.tt('ignore_nla_for_action_desc')),
        default=False,
        )

    exportWithCustomProps: bpy.props.BoolProperty(
        name=(languages.ti('export_with_custom_props_name')),
        description=(languages.tt('export_with_custom_props_desc')),
        default=False,
        )

    exportWithCustomCurves: bpy.props.BoolProperty(
        name=(languages.ti('export_with_custom_curves_name')),
        description=(languages.tt('export_with_custom_curves_desc')),
        default=False,
        )

    exportWithMetaData: bpy.props.BoolProperty(
        name=(languages.ti('export_with_meta_data_name')),
        description=(languages.tt('export_with_meta_data_desc')),
        default=False,
        )

    revertExportPath: bpy.props.BoolProperty(
        name=(languages.ti('revert_export_path_name')),
        description=(languages.tt('revert_export_path_desc')),
        default=False,
        )

    useGeneratedScripts: bpy.props.BoolProperty(
        name=(languages.ti('use_generated_scripts_name')),
        description=(languages.tt('use_generated_scripts_desc')),
        default=True,
        )

    collisionColor:  bpy.props.FloatVectorProperty(
        name=languages.ti('collision_color_name'),
        description='Color of the collision in Blender',
        subtype='COLOR',
        size=4,
        default=(0, 0.6, 0, 0.11),
        min=0.0, max=1.0,
        )

    notifyUnitScalePotentialError: bpy.props.BoolProperty(
        name=languages.ti('notify_unit_scale_potential_error_name'),
        description=(
            'Notify as potential error' +
            ' if the unit scale is not equal to 0.01.'
            ),
        default=True,
        )

    class BFU_OT_NewReleaseInfo(bpy.types.Operator):
        """Open last release page"""
        bl_label = "Open last release page"
        bl_idname = "object.new_release_info"
        bl_description = "Click to open the latest release page."

        def execute(self, context):
            os.system(
                "start \"\" https://github.com/xavier150/" +
                "Blender-For-UnrealEngine-Addons/releases/latest"
                )
            return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        boxColumn = layout.column().split(
            factor=0.5
            )
        ColumnLeft = boxColumn.column()
        ColumnRight = boxColumn.column()

        rootBone = ColumnLeft.box()

        bfu_ui_utils.LabelWithDocButton(
            rootBone,
            "SKELETON & ROOT BONE",
            "skeleton--root-bone"
            )
        rootBone.prop(self, "add_skeleton_root_bone")
        rootBoneName = rootBone.column()
        rootBoneName.enabled = self.add_skeleton_root_bone
        rootBoneName.prop(self, "skeleton_root_bone_name")

        rootBone.prop(self, "rescaleFullRigAtExport")
        newRigScale = rootBone.column()
        newRigScale.enabled = self.rescaleFullRigAtExport == "custom_rescale"
        newRigScale.prop(self, "newRigScale")

        socket = ColumnLeft.box()
        socket.label(text='SOCKET')
        socket.prop(self, "staticSocketsAdd90X")
        socket.prop(self, "rescaleSocketsAtExport")
        socketRescale = socket.column()
        socketRescale.enabled = self.rescaleSocketsAtExport == "custom_rescale"
        socketRescale.prop(self, "staticSocketsImportedSize")
        socketRescale.prop(self, "skeletalSocketsImportedSize")

        camera = ColumnLeft.box()
        camera.label(text='CAMERA')
        camera.prop(self, "exportCameraAsFBX")
        camera.prop(self, "bakeOnlyKeyVisibleInCut")

        data = ColumnRight.box()
        data.label(text='DATA')
        data.prop(self, "ignoreNLAForAction")
        data.prop(self, "bakeArmatureAction")
        data.prop(self, "exportWithCustomProps")
        data.prop(self, "exportWithMetaData")
        data.prop(self, "revertExportPath")

        other = ColumnRight.box()
        other.label(text='OTHER')
        other.prop(self, "collisionColor")
        other.prop(self, "notifyUnitScalePotentialError")

        script = ColumnRight.box()
        script.label(text='IMPORT SCRIPT')
        script.prop(self, "useGeneratedScripts")

        updateButton = layout.row()
        updateButton.scale_y = 2.0
        updateButton.operator("object.new_release_info", icon="TIME")


classes = (
    BFU_AP_AddonPreferences,
    BFU_AP_AddonPreferences.BFU_OT_NewReleaseInfo,
)


def register():
    """
    Register.
    """
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)


def unregister():
    """
    unregister.
    """
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
