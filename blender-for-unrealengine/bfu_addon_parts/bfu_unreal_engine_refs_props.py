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

classes = (
)

def draw_skeleton_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeleton_search_mode")
    if obj.bfu_engine_ref_skeleton_search_mode == "auto":
        pass
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_name":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_path_name":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_name")
    if obj.bfu_engine_ref_skeleton_search_mode == "custom_reference":
        layout.prop(obj, "bfu_engine_ref_skeleton_custom_ref")


def draw_skeletal_mesh_prop(layout: bpy.types.UILayout, obj: bpy.types.Object):
    layout.prop(obj, "bfu_engine_ref_skeletal_mesh_search_mode")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "auto":
        pass
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_name":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_path_name":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_path")
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_name")
    if obj.bfu_engine_ref_skeletal_mesh_search_mode == "custom_reference":
        layout.prop(obj, "bfu_engine_ref_skeletal_mesh_custom_ref")


def get_preset_values():
    preset_values = [
        'obj.bfu_engine_ref_skeleton_search_mode',
        'obj.bfu_engine_ref_skeleton_custom_path',
        'obj.bfu_engine_ref_skeleton_custom_name',
        'obj.bfu_engine_ref_skeleton_custom_ref',

        'obj.bfu_engine_ref_skeletal_mesh_search_mode',
        'obj.bfu_engine_ref_skeletal_mesh_custom_path',
        'obj.bfu_engine_ref_skeletal_mesh_custom_name',
        'obj.bfu_engine_ref_skeletal_mesh_custom_ref'
        ]
    return preset_values


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.bfu_engine_ref_skeleton_search_mode = bpy.props.EnumProperty(
        name="Skeleton Ref",
        description='Specify the skeleton location in Unreal',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("auto",
                "Auto",
                "...",
                1),
            ("custom_name",
                "Custom name",
                "Default location with custom name",
                2),
            ("custom_path_name",
                "Custom path and name",
                "Set the custom light map resolution",
                3),
            ("custom_reference",
                "custom reference",
                "Reference from Unreal.",
                4)
            ]
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_path = bpy.props.StringProperty(
        name="",
        description="The path of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="ImportedFbx"
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_name = bpy.props.StringProperty(
        name="",
        description="The name of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="SK_MySketon_Skeleton"
        )

    bpy.types.Object.bfu_engine_ref_skeleton_custom_ref = bpy.props.StringProperty(
        name="",
        description=(
            "The full reference of the Skeleton in Unreal. " +
            "(Use right clic on asset and copy reference.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="SkeletalMesh'/Game/ImportedFbx/SK_MySketon_Skeleton.SK_MySketon_Skeleton'"
        )


    bpy.types.Object.bfu_engine_ref_skeletal_mesh_search_mode = bpy.props.EnumProperty(
        name="Skeletal Mesh Ref",
        description='Specify the Skeletal Mesh location in Unreal',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("auto",
                "Auto",
                "...",
                1),
            ("custom_name",
                "Custom name",
                "Default location with custom name",
                2),
            ("custom_path_name",
                "Custom path and name",
                "Set the custom light map resolution",
                3),
            ("custom_reference",
                "custom reference",
                "Reference from Unreal.",
                4)
            ]
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_path = bpy.props.StringProperty(
        name="",
        description="The path of the Skeletal Mesh in Unreal. Skeletal Mesh not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="ImportedFbx"
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_name = bpy.props.StringProperty(
        name="",
        description="The name of the Skeletal Mesh in Unreal. Skeletal Mesh not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="SKM_MySkeletalMesh"
        )

    bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_ref = bpy.props.StringProperty(
        name="",
        description=(
            "The full reference of the Skeletal Mesh in Unreal. " +
            "(Use right clic on asset and copy reference.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="SkeletalMesh'/Game/ImportedFbx/SKM_MySkeletalMesh.SKM_MySkeletalMesh'"
        )



def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.bfu_engine_ref_skeleton_custom_ref
    del bpy.types.Object.bfu_engine_ref_skeleton_custom_name
    del bpy.types.Object.bfu_engine_ref_skeleton_custom_path
    del bpy.types.Object.bfu_engine_ref_skeleton_search_mode

    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_ref
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_name
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_custom_path
    del bpy.types.Object.bfu_engine_ref_skeletal_mesh_search_mode