# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================


import os
import bpy
import addon_utils

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

from .. import bfu_basics
from .. import bfu_utils
from ..export import bfu_export_get_info
from .. import bfu_ui_utils
from .. import languages



class BFU_PT_BlenderForUnrealObject(bpy.types.Panel):
    # Unreal engine export panel

    bl_idname = "BFU_PT_BlenderForUnrealObject"
    bl_label = "Blender for Unreal Engine"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    # Object Properties
    bpy.types.Object.bfu_export_type = EnumProperty(
        name="Export type",
        description="Export procedure",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("auto",
                "Auto",
                "Export with the parent if the parents is \"Export recursive\"",
                "BOIDS",
                1),
            ("export_recursive",
                "Export recursive",
                "Export self object and all children",
                "KEYINGSET",
                2),
            ("dont_export",
                "Not exported",
                "Will never export",
                "CANCEL",
                3)
            ]
        )

    bpy.types.Object.bfu_export_folder_name = StringProperty(
        name="Sub folder name",
        description=(
            'The name of sub folder.' +
            ' You can now use ../ for up one directory.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="",
        subtype='FILE_NAME'
        )

    # Collection Properties
    bpy.types.Collection.bfu_export_folder_name = StringProperty(
        name="Sub folder name",
        description=(
            'The name of sub folder.' +
            ' You can now use ../ for up one directory.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="",
        subtype='FILE_NAME'
        )

    bpy.types.Object.bfu_export_fbx_camera = BoolProperty(
        name="Export camera fbx",
        description=(
            'True: export .Fbx object and AdditionalTrack.ini ' +
            'Else: export only AdditionalTrack.ini'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.bfu_fix_axis_flippings = BoolProperty(
        name="Fix camera axis flippings",
        description=(
            'Disable only if you use extrem camera animation in one frame.'
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    bpy.types.Object.bfu_export_procedure = EnumProperty(
        name="Export procedure",
        description=(
            "This will define how the object should" +
            " be exported in case you are using specific Rig."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("ue-standard",
                "UE Standard",
                "Standard fbx I/O API.",
                "ARMATURE_DATA",
                1),
            ("blender-standard",
                "Blender Standard",
                "modified fbx I/O API.",
                "ARMATURE_DATA",
                2),
            ("auto-rig-pro",
                "AutoRigPro",
                "Export using AutoRigPro.",
                "ARMATURE_DATA",
                3),
            ],
        default="blender-standard"
        )

    bpy.types.Object.bfu_export_as_alembic = BoolProperty(
        name="Export as Alembic animation",
        description=(
            "If true this mesh will be exported as a Alembic animation"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_export_as_lod_mesh = BoolProperty(
        name="Export as lod?",
        description=(
            "If true this mesh will be exported" +
            " as a level of detail for another mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_export_skeletal_mesh_as_static_mesh = BoolProperty(
        name="Force staticMesh",
        description="Force export asset like a StaticMesh if is ARMATURE type",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_export_deform_only = BoolProperty(
        name="Export only deform bones",
        description=(
            "Only write deforming bones" +
            " (and non-deforming ones when they have deforming children)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_use_custom_export_name = BoolProperty(
        name="Export with custom name",
        description=(
            "Specify a custom name for the exported file"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_custom_export_name = StringProperty(
        name="",
        description="The name of exported file",
        override={'LIBRARY_OVERRIDABLE'},
        default="MyObjectExportName.fbx"
        )

    # Object Import Properties

    # Lod list
    bpy.types.Object.bfu_lod_target1 = PointerProperty(
        name="LOD1",
        description="Target objet for level of detail 01",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.bfu_lod_target2 = PointerProperty(
        name="LOD2",
        description="Target objet for level of detail 02",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.bfu_lod_target3 = PointerProperty(
        name="LOD3",
        description="Target objet for level of detail 03",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.bfu_lod_target4 = PointerProperty(
        name="LOD4",
        description="Target objet for level of detail 04",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.bfu_lod_target5 = PointerProperty(
        name="LOD5",
        description="Target objet for level of detail 05",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    # ImportUI
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxImportUI/index.html

    bpy.types.Object.bfu_create_physics_asset = BoolProperty(
        name="Create PhysicsAsset",
        description="If checked, create a PhysicsAsset when is imported",
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_skeleton_search_mode = EnumProperty(
        name="Skeleton search mode",
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

    bpy.types.Object.bfu_target_skeleton_custom_path = StringProperty(
        name="",
        description="The path of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="ImportedFbx"
        )

    bpy.types.Object.bfu_target_skeleton_custom_name = StringProperty(
        name="",
        description="The name of the Skeleton in Unreal. Skeleton not the skeletal mesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default="SKM_MySketonName_Skeleton"
        )

    bpy.types.Object.bfu_target_skeleton_custom_ref = StringProperty(
        name="",
        description=(
            "The full reference of the skeleton in Unreal. " +
            "(Use right clic on asset and copy reference.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="SkeletalMesh'/Game/ImportedFbx/SKM_MySketonName_Skeleton.SKM_MySketonName_Skeleton'"
        )

    # StaticMeshImportData
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxStaticMeshImportData/index.html

    bpy.types.Object.bfu_use_static_mesh_lod_group = BoolProperty(
        name="",
        description='',
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_static_mesh_lod_group = StringProperty(
        name="LOD Group",
        description=(
            "The LODGroup to associate with this mesh when it is imported." +
            " Default: LevelArchitecture, SmallProp, " +
            "LargeProp, Deco, Vista, Foliage, HighDetail"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=32,
        default="SmallProp"
        )

    bpy.types.Object.bfu_static_mesh_light_map_enum = EnumProperty(
        name="Light map",
        description='Specify how the light map resolution will be generated',
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("Default",
                "Default",
                "Has no effect on light maps",
                1),
            ("CustomMap",
                "Custom map",
                "Set the custom light map resolution",
                2),
            ("SurfaceArea",
                "surface Area",
                "Set light map resolution depending on the surface Area",
                3)
            ]
        )

    bpy.types.Object.bfu_static_mesh_custom_light_map_res = IntProperty(
        name="Light Map resolution",
        description="This is the resolution of the light map",
        override={'LIBRARY_OVERRIDABLE'},
        soft_max=2048,
        soft_min=16,
        max=4096,  # Max for unreal
        min=4,  # Min for unreal
        default=64
        )

    bpy.types.Object.computedStaticMeshLightMapRes = FloatProperty(
        name="computed Light Map resolution",
        description="This is the computed resolution of the light map",
        override={'LIBRARY_OVERRIDABLE'},
        default=64.0
        )

    bpy.types.Object.bfu_static_mesh_light_map_surface_scale = FloatProperty(
        name="Surface scale",
        description="This is for resacle the surface Area value",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.00001,  # Min for unreal
        default=64
        )

    bpy.types.Object.bfu_static_mesh_light_map_round_power_of_two = BoolProperty(
        name="Round power of 2",
        description=(
            "round Light Map resolution to nearest power of 2"
            ),
        default=True
        )

    bpy.types.Object.bfu_use_static_mesh_light_map_world_scale = BoolProperty(
        name="Use world scale",
        description=(
            "If not that will use the object scale."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_generate_light_map_uvs = BoolProperty(
        name="Generate LightmapUVs",
        description=(
            "If checked, UVs for Lightmap will automatically be generated."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv = BoolProperty(
        name="Convert Attribute To Uv",
        description=(
            "convert target geometry node attribute to UV when found."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    bpy.types.Object.bfu_convert_geometry_node_attribute_to_uv_name = StringProperty(
        name="Attribute name",
        description=(
            "Name of the Attribute to convert"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="UVMap",
        )

    bpy.types.Object.bfu_correct_extrem_uv_scale = BoolProperty(
        name=(languages.ti('correct_extrem_uv_scale_name')),
        description=(languages.tt('correct_extrem_uv_scale_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.bfu_auto_generate_collision = BoolProperty(
        name="Auto Generate Collision",
        description=(
            "If checked, collision will automatically be generated" +
            " (ignored if custom collision is imported or used)."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    # SkeletalMeshImportData:
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxSkeletalMeshImportData/index.html

    # UFbxTextureImportData:
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxTextureImportData/index.html

    bpy.types.Object.bfu_material_search_location = EnumProperty(
        name="Material search location",
        description=(
            "Specify where we should search" +
            " for matching materials when importing"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # Vania python:
        # https://docs.unrealengine.com/en-US/PythonAPI/class/MaterialSearchLocation.html?highlight=materialsearchlocation
        # C++ API:
        # http://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/EMaterialSearchLocation/index.html
        items=[
            ("Local",
                "Local",
                "Search for matching material in local import folder only.",
                1),
            ("UnderParent",
                "Under parent",
                "Search for matching material recursively from parent folder.",
                2),
            ("UnderRoot",
                "Under root",
                "Search for matching material recursively from root folder.",
                3),
            ("AllAssets",
                "All assets",
                "Search for matching material in all assets folders.",
                4)
            ]
        )

    bpy.types.Object.bfu_collision_trace_flag = EnumProperty(
        name="Collision Complexity",
        description="Collision Trace Flag",
        override={'LIBRARY_OVERRIDABLE'},
        # Vania python
        # https://docs.unrealengine.com/en-US/PythonAPI/class/CollisionTraceFlag.html
        # C++ API
        # https://api.unrealengine.com/INT/API/Runtime/Engine/PhysicsEngine/ECollisionTraceFlag/index.html
        items=[
            ("CTF_UseDefault",
                "Project Default",
                "Create only complex shapes (per poly)." +
                " Use complex shapes for all scene queries" +
                " and collision tests." +
                " Can be used in simulation for" +
                " static shapes only" +
                " (i.e can be collided against but not moved" +
                " through forces or velocity.",
                1),
            ("CTF_UseSimpleAndComplex",
                "Use Simple And Complex",
                "Use project physics settings (DefaultShapeComplexity)",
                2),
            ("CTF_UseSimpleAsComplex",
                "Use Simple as Complex",
                "Create both simple and complex shapes." +
                " Simple shapes are used for regular scene queries" +
                " and collision tests. Complex shape (per poly)" +
                " is used for complex scene queries.",
                3),
            ("CTF_UseComplexAsSimple",
                "Use Complex as Simple",
                "Create only simple shapes." +
                " Use simple shapes for all scene" +
                " queries and collision tests.",
                4)
            ]
        )

    bpy.types.Object.bfu_vertex_color_import_option = EnumProperty(
        name="Vertex Color Import Option",
        description="Specify how vertex colors should be imported",
        override={'LIBRARY_OVERRIDABLE'},
        # Vania python
        # https://docs.unrealengine.com/en-US/PythonAPI/class/VertexColorImportOption.html
        # C++ API
        # https://docs.unrealengine.com/en-US/API/Editor/UnrealEd/Factories/EVertexColorImportOption__Type/index.html
        items=[
            ("IGNORE", "Ignore",
                "Ignore vertex colors, and keep the existing mesh vertex colors.", 1),
            ("OVERRIDE", "Override",
                "Override all vertex colors with the specified color.", 2),
            ("REPLACE", "Replace",
                "Import the static mesh using the target vertex colors.", 0)
            ],
        default="REPLACE"
        )

    bpy.types.Object.bfu_vertex_color_override_color = FloatVectorProperty(
            name="Vertex Override Color",
            subtype='COLOR',
            description="Specify override color in the case that bfu_vertex_color_import_option is set to Override",
            override={'LIBRARY_OVERRIDABLE'},
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0
            # Vania python
            # https://docs.unrealengine.com/en-US/PythonAPI/class/FbxSkeletalMeshImportData.html
        )

    bpy.types.Object.bfu_vertex_color_to_use = EnumProperty(
        name="Vertex Color to use",
        description="Specify which vertex colors should be imported",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("FirstIndex", "First Index",
                "Use the the first index in Object Data -> Vertex Color.", 0),
            ("LastIndex", "Last Index",
                "Use the the last index in Object Data -> Vertex Color.", 1),
            ("ActiveIndex", "Active Render",
                "Use the the active index in Object Data -> Vertex Color.", 2),
            ("CustomIndex", "CustomIndex",
                "Use a specific Vertex Color in Object Data -> Vertex Color.", 3)
            ],
        default="ActiveIndex"
        )

    bpy.types.Object.bfu_vertex_color_index_to_use = IntProperty(
        name="Vertex color index",
        description="Vertex Color index to use.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_action_export_enum = EnumProperty(
        name="Action to export",
        description="Export procedure for actions (Animations and poses)",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("export_auto",
                "Export auto",
                "Export all actions connected to the bones names",
                "FILE_SCRIPT",
                1),
            ("export_specific_list",
                "Export specific list",
                "Export only actions that are checked in the list",
                "LINENUMBERS_ON",
                3),
            ("export_specific_prefix",
                "Export specific prefix",
                "Export only actions with a specific prefix" +
                " or the beginning of the actions names",
                "SYNTAX_ON",
                4),
            ("dont_export",
                "Not exported",
                "No action will be exported",
                "MATPLANE",
                5),
            ("export_current",
                "Export Current",
                "Export only the current actions",
                "FILE_SCRIPT",
                6),
            ]
        )

    bpy.types.Object.active_ObjectAction = IntProperty(
        name="Active Scene Action",
        description="Index of the currently active object action",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_prefix_name_to_export = StringProperty(
        # properties used with ""export_specific_prefix" on bfu_anim_action_export_enum
        name="Prefix name",
        description="Indicate the prefix of the actions that must be exported",
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=32,
        default="Example_",
        )

    bpy.types.Object.bfu_anim_action_start_end_time_enum = EnumProperty(
        name="Action Start/End Time",
        description="Set when animation starts and end",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("with_keyframes",
                "Auto",
                "The time will be defined according" +
                " to the first and the last frame",
                "KEYTYPE_KEYFRAME_VEC",
                1),
            ("with_sceneframes",
                "Scene time",
                "Time will be equal to the scene time",
                "SCENE_DATA",
                2),
            ("with_customframes",
                "Custom time",
                'The time of all the animations of this object' +
                ' is defined by you.' +
                ' Use "bfu_anim_action_custom_start_frame" and "bfu_anim_action_custom_end_frame"',
                "HAND",
                3),
            ]
        )

    bpy.types.Object.bfu_anim_action_start_frame_offset = IntProperty(
        name="Offset at start frame",
        description="Offset for the start frame.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_action_end_frame_offset = IntProperty(
        name="Offset at end frame",
        description=(
            "Offset for the end frame. +1" +
            " is recommended for the sequences | 0 is recommended" +
            " for UnrealEngine cycles | -1 is recommended for Sketchfab cycles"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_action_custom_start_frame = IntProperty(
        name="Custom start time",
        description="Set when animation start",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_anim_action_custom_end_frame = IntProperty(
        name="Custom end time",
        description="Set when animation end",
        override={'LIBRARY_OVERRIDABLE'},
        default=1
        )

    bpy.types.Object.bfu_anim_nla_start_end_time_enum = EnumProperty(
        name="NLA Start/End Time",
        description="Set when animation starts and end",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ("with_sceneframes",
                "Scene time",
                "Time will be equal to the scene time",
                "SCENE_DATA",
                1),
            ("with_customframes",
                "Custom time",
                'The time of all the animations of this object' +
                ' is defined by you.' +
                ' Use "bfu_anim_action_custom_start_frame" and "bfu_anim_action_custom_end_frame"',
                "HAND",
                2),
            ]
        )

    bpy.types.Object.bfu_anim_nla_start_frame_offset = IntProperty(
        name="Offset at start frame",
        description="Offset for the start frame.",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_nla_end_frame_offset = IntProperty(
        name="Offset at end frame",
        description=(
            "Offset for the end frame. +1" +
            " is recommended for the sequences | 0 is recommended" +
            " for UnrealEngine cycles | -1 is recommended for Sketchfab cycles"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=0
    )

    bpy.types.Object.bfu_anim_nla_custom_start_frame = IntProperty(
        name="Custom start time",
        description="Set when animation start",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    bpy.types.Object.bfu_anim_nla_custom_end_frame = IntProperty(
        name="Custom end time",
        description="Set when animation end",
        override={'LIBRARY_OVERRIDABLE'},
        default=1
        )


    bpy.types.Object.bfu_sample_anim_for_export = FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.01, max=100.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        )

    bpy.types.Object.bfu_simplify_anim_for_export = FloatProperty(
        name="Simplify animations",
        description=(
            "How much to simplify baked values" +
            " (0.0 to disable, the higher the more simplified)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        # No simplification to up to 10% of current magnitude tolerance.
        min=0.0, max=100.0,
        soft_min=0.0, soft_max=10.0,
        default=0.0,
        )

    bpy.types.Object.bfu_disable_free_scale_animation = BoolProperty(
        name="Disable non-uniform scale animation.",
        description=(
            "If checked, scale animation track's elements always have same value. " + 
            "This applies basic bones only."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )

    bpy.types.Object.bfu_anim_nla_use = BoolProperty(
        name="Export NLA (Nonlinear Animation)",
        description=(
            "If checked, exports the all animation of the scene with the NLA " +
            "(Don't work with Auto-Rig Pro for the moment.)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_anim_nla_export_name = StringProperty(
        name="NLA export name",
        description="Export NLA name (Don't work with Auto-Rig Pro for the moment.)",
        override={'LIBRARY_OVERRIDABLE'},
        maxlen=64,
        default="NLA_animation",
        subtype='FILE_NAME'
        )

    bpy.types.Object.bfu_anim_naming_type = EnumProperty(
        name="Naming type",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('action_name', "Action name", 'Exemple: "Anim_MyAction"'),
            ('include_armature_name',
                "Include Armature Name",
                'Include armature name in animation export file name.' +
                ' Exemple: "Anim_MyArmature_MyAction"'),
            ('include_custom_name',
                "Include custom name",
                'Include custom name in animation export file name.' +
                ' Exemple: "Anim_MyCustomName_MyAction"'),
            ],
        default='action_name'
        )

    bpy.types.Object.bfu_anim_naming_custom = StringProperty(
        name="Export name",
        override={'LIBRARY_OVERRIDABLE'},
        default='MyCustomName'
        )

    bpy.types.Object.bfu_export_global_scale = FloatProperty(
        name="Global scale",
        description="Scale, change is not recommended with SkeletalMesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default=1.0
        )

    bpy.types.Object.bfu_export_axis_forward = EnumProperty(
        name="Axis Forward",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X Forward", ""),
            ('Y', "Y Forward", ""),
            ('Z', "Z Forward", ""),
            ('-X', "-X Forward", ""),
            ('-Y', "-Y Forward", ""),
            ('-Z', "-Z Forward", ""),
            ],
        default='-Z',
        )

    bpy.types.Object.bfu_export_axis_up = EnumProperty(
        name="Axis Up",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X Up", ""),
            ('Y', "Y Up", ""),
            ('Z', "Z Up", ""),
            ('-X', "-X Up", ""),
            ('-Y', "-Y Up", ""),
            ('-Z', "-Z Up", ""),
            ],
        default='Y',
        )

    bpy.types.Object.bfu_export_primary_bone_axis = EnumProperty(
        name="Primary Axis Bone",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
            ],
        default='X',
        )

    bpy.types.Object.bfu_export_secondary_bone_axis = EnumProperty(
        name="Secondary Axis Bone",
        override={'LIBRARY_OVERRIDABLE'},
        items=[
            ('X', "X", ""),
            ('Y', "Y", ""),
            ('Z', "Z", ""),
            ('-X', "-X", ""),
            ('-Y', "-Y", ""),
            ('-Z', "-Z", ""),
            ],
        default='-Z',
        )

    bpy.types.Object.bfu_mirror_symmetry_right_side_bones = BoolProperty(
        name="Revert direction of symmetry right side bones",
        description=(
            "If checked, The right-side bones will be mirrored for mirroring physic object in UE PhysicAsset Editor."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_use_ue_mannequin_bone_alignment = BoolProperty(
        name="Apply bone alignments similar to UE Mannequin.",
        description=(
            "If checked, similar to the UE Mannequin, the leg bones will be oriented upwards, and the pelvis and feet bone will be aligned facing upwards during export."
        ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
    )

    bpy.types.Object.bfu_move_to_center_for_export = BoolProperty(
        name="Move to center",
        description=(
            "If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_to_zero_for_export = BoolProperty(
        name="Rotate to zero",
        description=(
            "If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_move_action_to_center_for_export = BoolProperty(
        name="Move animation to center",
        description=(
            "(Action animation only) If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)" +
            " Note: Unreal Engine ignore the position of the skeleton at the import."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_action_to_zero_for_export = BoolProperty(
        name="Rotate Action to zero",
        description=(
            "(Action animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_move_nla_to_center_for_export = BoolProperty(
        name="Move NLA to center",
        description=(
            "(Non linear animation only) If true use object origin else use scene origin." +
            " | If true the mesh will be moved to the center" +
            " of the scene for export." +
            " (This is used so that the origin of the fbx file" +
            " is the same as the mesh in blender)" +
            " Note: Unreal Engine ignore the position of the skeleton at the import."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_rotate_nla_to_zero_for_export = BoolProperty(
        name="Rotate NLA to zero",
        description=(
            "(Non linear animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.bfu_additional_location_for_export = FloatVectorProperty(
        name="Additional location",
        description=(
            "This will add a additional absolute location to the mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        subtype="TRANSLATION",
        default=(0, 0, 0)
        )

    bpy.types.Object.bfu_additional_rotation_for_export = FloatVectorProperty(
        name="Additional rotation",
        description=(
            "This will add a additional absolute rotation to the mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        subtype="EULER",
        default=(0, 0, 0)
        )

    # Scene and global

    bpy.types.Scene.active_CollectionExportList = IntProperty(
        name="Active Collection",
        description="Index of the currently active collection",
        override={'LIBRARY_OVERRIDABLE'},
        default=0
        )

    class BFU_OT_OpenDocumentationPage(Operator):
        bl_label = "Documentation"
        bl_idname = "object.bfu_open_documentation_page"
        bl_description = "Clic for open documentation page on GitHub"

        def execute(self, context):
            os.system(
                "start \"\" " +
                "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki"
                )
            return {'FINISHED'}

    class BFU_OT_CopyRegularCameraButton(Operator):
        bl_label = "Copy Regular Camera for Unreal"
        bl_idname = "object.copy_regular_camera_command"
        bl_description = "Copy Regular Camera Script command"

        def execute(self, context):
            obj = context.object
            result = bfu_utils.GetImportCameraScriptCommand([obj], False)
            if result[0]:
                bfu_basics.setWindowsClipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}

    class BFU_OT_CopyCineCameraButton(Operator):
        bl_label = "Copy Cine Camera for Unreal"
        bl_idname = "object.copy_cine_camera_command"
        bl_description = "Copy Cine Camera Script command"

        def execute(self, context):
            obj = context.object
            result = bfu_utils.GetImportCameraScriptCommand([obj], True)
            if result[0]:
                bfu_basics.setWindowsClipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}

    class BFU_OT_ComputLightMap(Operator):
        bl_label = "Calculate surface area"
        bl_idname = "object.computlightmap"
        bl_description = "Click to calculate the surface of the object"

        def execute(self, context):
            obj = context.object
            obj.computedStaticMeshLightMapRes = bfu_utils.GetExportRealSurfaceArea(obj)
            self.report(
                {'INFO'},
                "Light map area updated to " + str(round(obj.computedStaticMeshLightMapRes)) + ". " +
                "Compunted Light map: " + str(bfu_utils.GetCompuntedLightMap(obj)))
            return {'FINISHED'}


    # Animation :

    class BFU_UL_ActionExportTarget(bpy.types.UIList):
        def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
            action_is_valid = False
            if item.name in bpy.data.actions:
                action_is_valid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if action_is_valid:  # If action is valid
                    layout.prop(
                        bpy.data.actions[item.name],
                        "name",
                        text="",
                        emboss=False,
                        icon="ACTION"
                    )
                    layout.prop(item, "use", text="")
                else:
                    dataText = (
                        'Action data named "' + item.name +
                        '" Not Found. Please click on update'
                    )
                    layout.label(text=dataText, icon="ERROR")
            # Not optimized for 'GRID' layout type.
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)

    class BFU_OT_UpdateObjActionListButton(Operator):
        bl_label = "Update action list"
        bl_idname = "object.updateobjactionlist"
        bl_description = "Update action list"

        def execute(self, context):
            def UpdateExportActionList(obj):
                # Update the provisional action list known by the object

                def SetUseFromLast(anim_list, ActionName):
                    for item in anim_list:
                        if item[0] == ActionName:
                            if item[1]:
                                return True
                    return False

                animSave = [["", False]]
                for Anim in obj.exportActionList:  # CollectionProperty
                    name = Anim.name
                    use = Anim.use
                    animSave.append([name, use])
                obj.exportActionList.clear()
                for action in bpy.data.actions:
                    obj.exportActionList.add().name = action.name
                    useFromLast = SetUseFromLast(animSave, action.name)
                    obj.exportActionList[action.name].use = useFromLast
            UpdateExportActionList(bpy.context.object)
            return {'FINISHED'}

    class BFU_OT_ShowActionToExport(Operator):
        bl_label = "Show action(s)"
        bl_idname = "object.showobjaction"
        bl_description = (
            "Click to show actions that are" +
            " to be exported with this armature."
            )

        def execute(self, context):
            obj = context.object
            bfu_utils.UpdateActionCache(obj)
            animation_to_export = bfu_utils.GetActionToExport(obj)

            popup_title = "Action list"
            if len(animation_to_export) > 0:
                animationNumber = len(animation_to_export)
                if obj.bfu_anim_nla_use:
                    animationNumber += 1
                popup_title = (
                    str(animationNumber) +
                    ' action(s) found for obj named "'+obj.name+'".'
                    )
            else:
                popup_title = (
                    'No action found for obj named "' +
                    obj.name+'".')

            def draw(self, context):
                col = self.layout.column()

                def addAnimRow(
                        action_name,
                        action_type,
                        frame_start,
                        frame_end):
                    row = col.row()
                    row.label(
                        text="- ["+action_name +
                        "] Frame "+frame_start+" to "+frame_end +
                        " ("+action_type+")"
                        )

                for action in animation_to_export:
                    Frames = bfu_utils.GetDesiredActionStartEndTime(obj, action)
                    frame_start = str(Frames[0])
                    frame_end = str(Frames[1])
                    addAnimRow(
                        action.name,
                        bfu_utils.GetActionType(action),
                        frame_start,
                        frame_end)
                if obj.bfu_anim_nla_use:
                    scene = context.scene
                    addAnimRow(
                        obj.bfu_anim_nla_export_name,
                        "NlAnim",
                        str(scene.frame_start),
                        str(scene.frame_end)
                        )

            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='ACTION'
                )
            return {'FINISHED'}

    class BFU_MT_ObjectGlobalPropertiesPresets(bpy.types.Menu):
        bl_label = 'Global Properties Presets'
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset

    from bl_operators.presets import AddPresetBase

    class BFU_OT_AddObjectGlobalPropertiesPreset(AddPresetBase, Operator):
        bl_idname = 'object.add_globalproperties_preset'
        bl_label = 'Add or remove a preset for Global properties'
        bl_description = 'Add or remove a preset for Global properties'
        preset_menu = 'BFU_MT_ObjectGlobalPropertiesPresets'

        # Common variable used for all preset values
        preset_defines = [
                            'obj = bpy.context.object',
                            'col = bpy.context.collection',
                            'scene = bpy.context.scene'
                         ]

        # Properties to store in the preset
        preset_values = [
                            'obj.bfu_export_type',
                            'obj.bfu_export_folder_name',
                            'col.bfu_export_folder_name',
                            'obj.bfu_export_fbx_camera',
                            'obj.bfu_fix_axis_flippings',
                            'obj.bfu_export_as_alembic',
                            'obj.bfu_export_as_lod_mesh',
                            'obj.bfu_export_skeletal_mesh_as_static_mesh',
                            'obj.bfu_export_deform_only',
                            'obj.bfu_lod_target1',
                            'obj.bfu_lod_target2',
                            'obj.bfu_lod_target3',
                            'obj.bfu_lod_target4',
                            'obj.bfu_lod_target5',
                            'obj.bfu_create_physics_asset',
                            'obj.bfu_skeleton_search_mode',
                            'obj.bfu_target_skeleton_custom_path',
                            'obj.bfu_target_skeleton_custom_name',
                            'obj.bfu_target_skeleton_custom_ref',
                            'obj.bfu_use_static_mesh_lod_group',
                            'obj.bfu_static_mesh_lod_group',
                            'obj.bfu_static_mesh_light_map_enum',
                            'obj.bfu_static_mesh_custom_light_map_res',
                            'obj.bfu_static_mesh_light_map_surface_scale',
                            'obj.bfu_static_mesh_light_map_round_power_of_two',
                            'obj.bfu_use_static_mesh_light_map_world_scale',
                            'obj.bfu_generate_light_map_uvs',
                            'obj.bfu_convert_geometry_node_attribute_to_uv',
                            'obj.bfu_convert_geometry_node_attribute_to_uv_name',
                            'obj.bfu_correct_extrem_uv_scale',
                            'obj.bfu_auto_generate_collision',
                            'obj.bfu_material_search_location',
                            'obj.bfu_collision_trace_flag',
                            'obj.bfu_vertex_color_import_option',
                            'obj.bfu_vertex_color_override_color',
                            'obj.bfu_vertex_color_to_use',
                            'obj.bfu_vertex_color_index_to_use',
                            'obj.bfu_anim_action_export_enum',
                            'obj.bfu_prefix_name_to_export',
                            'obj.bfu_anim_action_start_end_time_enum',
                            'obj.bfu_anim_nla_start_end_time_enum',
                            'obj.bfu_anim_action_start_frame_offset',
                            'obj.bfu_anim_action_end_frame_offset',
                            'obj.bfu_anim_action_custom_start_frame',
                            'obj.bfu_anim_action_custom_end_frame',
                            'obj.bfu_anim_nla_start_frame_offset',
                            'obj.bfu_anim_nla_end_frame_offset',
                            'obj.bfu_anim_nla_custom_start_frame',
                            'obj.bfu_anim_nla_custom_end_frame',
                            'obj.bfu_sample_anim_for_export',
                            'obj.bfu_simplify_anim_for_export',
                            'obj.bfu_anim_nla_use',
                            'obj.bfu_anim_nla_export_name',
                            'obj.bfu_anim_naming_type',
                            'obj.bfu_anim_naming_custom',
                            'obj.bfu_export_global_scale',
                            'obj.bfu_export_axis_forward',
                            'obj.bfu_export_axis_up',
                            'obj.bfu_export_primary_bone_axis',
                            'obj.bfu_export_secondary_bone_axis',
                            'obj.bfu_mirror_symmetry_right_side_bones',
                            'obj.bfu_use_ue_mannequin_bone_alignment',
                            'obj.bfu_disable_free_scale_animation',
                            'obj.bfu_move_to_center_for_export',
                            'obj.bfu_rotate_to_zero_for_export',
                            'obj.bfu_move_action_to_center_for_export',
                            'obj.bfu_rotate_action_to_zero_for_export',
                            'obj.bfu_move_nla_to_center_for_export',
                            'obj.bfu_rotate_nla_to_zero_for_export',
                            'obj.bfu_additional_location_for_export',
                            'obj.bfu_additional_rotation_for_export',
                        ]

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'

    class BFU_UL_CollectionExportTarget(bpy.types.UIList):

        def draw_item(self, context, layout, data, item, icon, active_data, active_property, index, flt_flag):

            collection_is_valid = False
            if item.name in bpy.data.collections:
                collection_is_valid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if collection_is_valid:  # If action is valid
                    layout.prop(
                        bpy.data.collections[item.name],
                        "name",
                        text="",
                        emboss=False,
                        icon="OUTLINER_COLLECTION")
                    layout.prop(item, "use", text="")
                else:
                    dataText = (
                        'Collection named "' +
                        item.name +
                        '" Not Found. Please clic on update')
                    layout.label(text=dataText, icon="ERROR")
            # Not optimised for 'GRID' layout type.
            elif self.layout_type in {'GRID'}:
                layout.alignment = 'CENTER'
                layout.label(text="", icon_value=icon)

    class BFU_OT_UpdateCollectionButton(Operator):
        bl_label = "Update collection list"
        bl_idname = "object.updatecollectionlist"
        bl_description = "Update collection list"

        def execute(self, context):
            def UpdateExportCollectionList(scene):
                # Update the provisional collection list known by the object

                def SetUseFromLast(col_list, CollectionName):
                    for item in col_list:
                        if item[0] == CollectionName:
                            if item[1]:
                                return True
                    return False

                colSave = [["", False]]
                for col in scene.CollectionExportList:  # CollectionProperty
                    name = col.name
                    use = col.use
                    colSave.append([name, use])
                scene.CollectionExportList.clear()
                for col in bpy.data.collections:
                    scene.CollectionExportList.add().name = col.name
                    useFromLast = SetUseFromLast(colSave, col.name)
                    scene.CollectionExportList[col.name].use = useFromLast
            UpdateExportCollectionList(context.scene)
            return {'FINISHED'}

    class BFU_OT_ShowCollectionToExport(Operator):
        bl_label = "Show collection(s)"
        bl_idname = "object.showscenecollection"
        bl_description = "Click to show collections to export"

        def execute(self, context):
            scene = context.scene
            collections = bfu_utils.GetCollectionToExport(scene)
            popup_title = "Collection list"
            if len(collections) > 0:
                popup_title = (
                    str(len(collections))+' collection(s) to export found.')
            else:
                popup_title = 'No collection to export found.'

            def draw(self):
                col = self.layout.column()
                for collection in collections:
                    row = col.row()
                    row.label(text="- "+collection.name)
            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='GROUP')
            return {'FINISHED'}

    def draw(self, context):
        scene = bpy.context.scene
        obj = bpy.context.object
        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout

        version = (0, 0, 0)
        # pylint: disable=no-value-for-parameter
        for addon in addon_utils.modules():
            if addon.bl_info['name'] == "Blender for UnrealEngine":
                version = addon.bl_info.get('version', (0, 0, 0))

        credit_box = layout.box()
        credit_box.label(text=languages.ti('intro'))
        credit_box.label(text='Version '+'.'.join([str(x) for x in version]))
        credit_box.operator("object.bfu_open_documentation_page", icon="HELP")

        row = layout.row(align=True)
        row.menu(
            'BFU_MT_ObjectGlobalPropertiesPresets',
            text='Global Properties Presets'
            )
        row.operator(
            'object.add_globalproperties_preset',
            text='',
            icon='ADD'
            )
        row.operator(
            'object.add_globalproperties_preset',
            text='',
            icon='REMOVE'
            ).remove_active = True

        layout.row().prop(scene, "bfu_active_tab", expand=True)
        if scene.bfu_active_tab == "OBJECT":
            layout.row().prop(scene, "bfu_active_object_tab", expand=True)
        if scene.bfu_active_tab == "SCENE":
            layout.row().prop(scene, "bfu_active_scene_tab", expand=True)

        if bfu_ui_utils.DisplayPropertyFilter("OBJECT", "GENERAL"):
            bfu_ui_utils.LayoutSection(layout, "bfu_object_properties_expanded", "Object Properties")
            if scene.bfu_object_properties_expanded:

                if obj is None:
                    layout.row().label(text='No selected object.')
                else:

                    AssetType = layout.row()
                    AssetType.prop(obj, 'name', text="", icon='OBJECT_DATA')
                    # Show asset type
                    AssetType.label(text='('+bfu_utils.GetAssetType(obj)+')')

                    ExportType = layout.column()
                    ExportType.prop(obj, 'bfu_export_type')

                    if obj.type == "CAMERA":
                        CameraProp = layout.column()
                        CameraProp.operator("object.copy_regular_camera_command", icon="COPYDOWN")
                        CameraProp.operator("object.copy_cine_camera_command", icon="COPYDOWN")

                    if obj.bfu_export_type == "export_recursive":

                        folderNameProperty = layout.column()
                        folderNameProperty.prop(
                            obj,
                            'bfu_export_folder_name',
                            icon='FILE_FOLDER'
                            )

                        if obj.type == "CAMERA":
                            CameraProp.prop(obj, 'bfu_export_fbx_camera')
                            CameraProp.prop(obj, 'bfu_fix_axis_flippings')

                        else:
                            ProxyProp = layout.column()
                            if bfu_utils.GetExportAsProxy(obj):
                                ProxyProp.label(
                                        text="The Armature was detected as a proxy."
                                        )
                                proxy_child = bfu_utils.GetExportProxyChild(obj)
                                if proxy_child:
                                    ProxyProp.label(
                                            text="Proxy child: " + proxy_child.name
                                            )
                                else:
                                    ProxyProp.label(text="Proxy child not found")

                            if obj.type == "ARMATURE":
                                export_procedure_prop = layout.column()
                                export_procedure_prop.prop(obj, 'bfu_export_procedure')

                            if not bfu_utils.GetExportAsProxy(obj):
                                AlembicProp = layout.column()
                                AlembicProp.prop(obj, 'bfu_export_as_alembic')
                                if obj.bfu_export_as_alembic:
                                    AlembicProp.label(
                                        text="(Alembic animation are exported" +
                                        " with scene position.)"
                                        )
                                    AlembicProp.label(
                                        text="(Use import script for" +
                                        " use the origin position.)"
                                        )
                                else:
                                    if addon_prefs.useGeneratedScripts:
                                        # Unreal python no longer support Skeletal mesh LODS import.
                                        if bfu_utils.GetAssetType(obj) != "SkeletalMesh":
                                            LodProp = layout.column()
                                            LodProp.prop(obj, 'bfu_export_as_lod_mesh')
                            if not obj.bfu_export_as_alembic:
                                if obj.type == "ARMATURE":
                                    AssetType2 = layout.column()
                                    # Show asset type
                                    AssetType2.prop(obj, "bfu_export_skeletal_mesh_as_static_mesh")
                                    if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                                        AssetType2.prop(obj, 'bfu_export_deform_only')

                            if not bfu_utils.GetExportAsProxy(obj):
                                # exportCustomName
                                exportCustomName = layout.row()
                                exportCustomName.prop(obj, "bfu_use_custom_export_name")
                                useCustomName = obj.bfu_use_custom_export_name
                                exportCustomNameText = exportCustomName.column()
                                exportCustomNameText.prop(obj, "bfu_custom_export_name")
                                exportCustomNameText.enabled = useCustomName

            bfu_ui_utils.LayoutSection(layout, "bfu_object_advanced_properties_expanded", "Object advanced Properties")
            if scene.bfu_object_advanced_properties_expanded:
                if obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        transformProp = layout.column()
                        if bfu_utils.GetAssetType(obj) != "Alembic" and bfu_utils.GetAssetType(obj) != "Camera":
                            transformProp.prop(obj, "bfu_move_to_center_for_export")
                            transformProp.prop(obj, "bfu_rotate_to_zero_for_export")
                            transformProp.prop(obj, "bfu_additional_location_for_export")
                            transformProp.prop(obj, "bfu_additional_rotation_for_export")
                            
                        transformProp.prop(obj, 'bfu_export_global_scale')
                        if bfu_utils.GetAssetType(obj) == "Camera":
                            transformProp.prop(obj, "bfu_additional_location_for_export")

                        AxisProperty = layout.column()
                        AxisProperty.prop(obj, 'bfu_export_axis_forward')
                        AxisProperty.prop(obj, 'bfu_export_axis_up')
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            BoneAxisProperty = layout.column()
                            BoneAxisProperty.prop(obj, 'bfu_export_primary_bone_axis')
                            BoneAxisProperty.prop(obj, 'bfu_export_secondary_bone_axis')
                else:
                    layout.label(text='(No properties to show.)')

            bfu_ui_utils.LayoutSection(layout, "bfu_skeleton_properties_expanded", "Skeleton")
            if scene.bfu_skeleton_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # SkeletalMesh prop
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            if not obj.bfu_export_as_lod_mesh:

                                Ue4Skeleton = layout.column()
                                Ue4Skeleton.prop(obj, "bfu_skeleton_search_mode")
                                if obj.bfu_skeleton_search_mode == "auto":
                                    pass
                                if obj.bfu_skeleton_search_mode == "custom_name":
                                    Ue4Skeleton.prop(obj, "bfu_target_skeleton_custom_name")
                                if obj.bfu_skeleton_search_mode == "custom_path_name":
                                    Ue4Skeleton.prop(obj, "bfu_target_skeleton_custom_path")
                                    Ue4Skeleton.prop(obj, "bfu_target_skeleton_custom_name")
                                if obj.bfu_skeleton_search_mode == "custom_reference":
                                    Ue4Skeleton.prop(obj, "bfu_target_skeleton_custom_ref")
                                Ue4Skeleton.prop(obj, "bfu_mirror_symmetry_right_side_bones")
                                MirrorSymmetryRightSideBonesRow = Ue4Skeleton.row()
                                MirrorSymmetryRightSideBonesRow.enabled = obj.bfu_mirror_symmetry_right_side_bones
                                MirrorSymmetryRightSideBonesRow.prop(obj, "bfu_use_ue_mannequin_bone_alignment")

        if bfu_ui_utils.DisplayPropertyFilter("OBJECT", "ANIM"):
            if obj is not None:
                if obj.bfu_export_type == "export_recursive" and not obj.bfu_export_as_lod_mesh:

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_action_properties_expanded", "Actions Properties")
                    if scene.bfu_animation_action_properties_expanded:
                        if (bfu_utils.GetAssetType(obj) == "SkeletalMesh" or
                                bfu_utils.GetAssetType(obj) == "Camera" or
                                bfu_utils.GetAssetType(obj) == "Alembic"):

                            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                                # Action list
                                ActionListProperty = layout.column()
                                ActionListProperty.prop(obj, 'bfu_anim_action_export_enum')
                                if obj.bfu_anim_action_export_enum == "export_specific_list":
                                    ActionListProperty.template_list(
                                        # type and unique id
                                        "BFU_UL_ActionExportTarget", "",
                                        # pointer to the CollectionProperty
                                        obj, "exportActionList",
                                        # pointer to the active identifier
                                        obj, "active_ObjectAction",
                                        maxrows=5,
                                        rows=5
                                    )
                                    ActionListProperty.operator(
                                        "object.updateobjactionlist",
                                        icon='RECOVER_LAST')
                                if obj.bfu_anim_action_export_enum == "export_specific_prefix":
                                    ActionListProperty.prop(obj, 'bfu_prefix_name_to_export')

                            # Action Time
                            if obj.type != "CAMERA" and obj.bfu_export_procedure != "auto-rig-pro":
                                ActionTimeProperty = layout.column()
                                ActionTimeProperty.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                                ActionTimeProperty.prop(obj, 'bfu_anim_action_start_end_time_enum')
                                if obj.bfu_anim_action_start_end_time_enum == "with_customframes":
                                    OfsetTime = ActionTimeProperty.row()
                                    OfsetTime.prop(obj, 'bfu_anim_action_custom_start_frame')
                                    OfsetTime.prop(obj, 'bfu_anim_action_custom_end_frame')
                                if obj.bfu_anim_action_start_end_time_enum != "with_customframes":
                                    OfsetTime = ActionTimeProperty.row()
                                    OfsetTime.prop(obj, 'bfu_anim_action_start_frame_offset')
                                    OfsetTime.prop(obj, 'bfu_anim_action_end_frame_offset')

                            else:
                                layout.label(
                                    text=(
                                        "Note: animation start/end use scene frames" +
                                        " with the camera for the sequencer.")
                                    )

                            # Nomenclature
                            if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                                export_anim_naming = layout.column()
                                export_anim_naming.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                                export_anim_naming.prop(obj, 'bfu_anim_naming_type')
                                if obj.bfu_anim_naming_type == "include_custom_name":
                                    export_anim_naming_text = export_anim_naming.column()
                                    export_anim_naming_text.prop(obj, 'bfu_anim_naming_custom')



                        else:
                            layout.label(
                                text='(This assets is not a SkeletalMesh or Camera)')

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_action_advanced_properties_expanded", "Actions Advanced Properties")
                    if scene.bfu_animation_action_advanced_properties_expanded:

                        if bfu_utils.GetAssetType(obj) != "Alembic":
                            transformProp = layout.column()
                            transformProp.enabled = obj.bfu_anim_action_export_enum != 'dont_export'
                            transformProp.prop(obj, "bfu_move_action_to_center_for_export")
                            transformProp.prop(obj, "bfu_rotate_action_to_zero_for_export")

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_nla_properties_expanded", "NLA Properties")
                    if scene.bfu_animation_nla_properties_expanded:
                        # NLA
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            NLAAnim = layout.row()
                            NLAAnim.prop(obj, 'bfu_anim_nla_use')
                            NLAAnimChild = NLAAnim.column()
                            NLAAnimChild.enabled = obj.bfu_anim_nla_use
                            NLAAnimChild.prop(obj, 'bfu_anim_nla_export_name')
                            if obj.bfu_export_procedure == "auto-rig-pro":
                                NLAAnim.enabled = False
                                NLAAnimChild.enabled = False

                        # NLA Time
                        if obj.type != "CAMERA" and obj.bfu_export_procedure != "auto-rig-pro":
                            NLATimeProperty = layout.column()
                            NLATimeProperty.enabled = obj.bfu_anim_nla_use
                            NLATimeProperty.prop(obj, 'bfu_anim_nla_start_end_time_enum')
                            if obj.bfu_anim_nla_start_end_time_enum == "with_customframes":
                                OfsetTime = NLATimeProperty.row()
                                OfsetTime.prop(obj, 'bfu_anim_nla_custom_start_frame')
                                OfsetTime.prop(obj, 'bfu_anim_nla_custom_end_frame')
                            if obj.bfu_anim_nla_start_end_time_enum != "with_customframes":
                                OfsetTime = NLATimeProperty.row()
                                OfsetTime.prop(obj, 'bfu_anim_nla_start_frame_offset')
                                OfsetTime.prop(obj, 'bfu_anim_nla_end_frame_offset')

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_nla_advanced_properties_expanded", "NLA Advanced Properties")
                    if scene.bfu_animation_nla_advanced_properties_expanded:
                        if bfu_utils.GetAssetType(obj) != "Alembic":
                            transformProp2 = layout.column()
                            transformProp2.enabled = obj.bfu_anim_nla_use
                            transformProp2.prop(obj, "bfu_move_nla_to_center_for_export")
                            transformProp2.prop(obj, "bfu_rotate_nla_to_zero_for_export")

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_advanced_properties_expanded", "Animation Advanced Properties")
                    if scene.bfu_animation_advanced_properties_expanded:
                        # Animation fbx properties
                        if (bfu_utils.GetAssetType(obj) != "Alembic"):
                            propsFbx = layout.row()
                            if obj.bfu_export_procedure != "auto-rig-pro":
                                propsFbx.prop(obj, 'bfu_sample_anim_for_export')
                            propsFbx.prop(obj, 'bfu_simplify_anim_for_export')
                        propsScaleAnimation = layout.row()
                        propsScaleAnimation.prop(obj, "bfu_disable_free_scale_animation")

                    # Armature export action list feedback
                    if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                        layout.label(
                            text='Note: The Action with only one' +
                            ' frame are exported like Pose.')
                        ArmaturePropertyInfo = (
                            layout.row().box().split(factor=0.75)
                            )
                        ActionNum = len(bfu_utils.GetActionToExport(obj))
                        if obj.bfu_anim_nla_use:
                            ActionNum += 1
                        actionFeedback = (
                            str(ActionNum) +
                            " Animation(s) will be exported with this object.")
                        ArmaturePropertyInfo.label(
                            text=actionFeedback,
                            icon='INFO')
                        ArmaturePropertyInfo.operator("object.showobjaction")
                else:
                    layout.label(text='(No properties to show.)')
            else:
                layout.label(text='(No properties to show.)')

        if bfu_ui_utils.DisplayPropertyFilter("OBJECT", "MISC"):
            bfu_ui_utils.LayoutSection(layout, "bfu_object_lod_properties_expanded", "Lod")
            if scene.bfu_object_lod_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # Lod selection
                        if not obj.bfu_export_as_lod_mesh:
                            # Unreal python no longer support Skeletal mesh LODS import.
                            if (bfu_utils.GetAssetType(obj) == "StaticMesh"):
                                LodList = layout.column()
                                LodList.prop(obj, 'bfu_lod_target1')
                                LodList.prop(obj, 'bfu_lod_target2')
                                LodList.prop(obj, 'bfu_lod_target3')
                                LodList.prop(obj, 'bfu_lod_target4')
                                LodList.prop(obj, 'bfu_lod_target5')

                        # StaticMesh prop
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            if not obj.bfu_export_as_lod_mesh:
                                bfu_static_mesh_lod_group = layout.row()
                                bfu_static_mesh_lod_group.prop(
                                    obj,
                                    'bfu_use_static_mesh_lod_group',
                                    text="")
                                SMLODGroupChild = bfu_static_mesh_lod_group.column()
                                SMLODGroupChild.enabled = obj.bfu_use_static_mesh_lod_group
                                SMLODGroupChild.prop(
                                    obj,
                                    'bfu_static_mesh_lod_group'
                                    )

            bfu_ui_utils.LayoutSection(layout, "bfu_object_collision_properties_expanded", "Collision")
            if scene.bfu_object_collision_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # StaticMesh prop
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            StaticMeshCollisionTraceFlag = layout.row()
                            StaticMeshCollisionTraceFlag.prop(
                                obj,
                                'bfu_collision_trace_flag'
                                )
                            if not obj.bfu_export_as_lod_mesh:
                                bfu_auto_generate_collision = layout.row()
                                bfu_auto_generate_collision.prop(
                                    obj,
                                    'bfu_auto_generate_collision'
                                    )
                        # SkeletalMesh prop
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            if not obj.bfu_export_as_lod_mesh:
                                bfu_create_physics_asset = layout.row()
                                bfu_create_physics_asset.prop(obj, "bfu_create_physics_asset")

            bfu_ui_utils.LayoutSection(layout, "bfu_object_material_properties_expanded", "Material")
            if scene.bfu_object_material_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # bfu_material_search_location
                        if not obj.bfu_export_as_lod_mesh:
                            if (bfu_utils.GetAssetType(obj) == "StaticMesh" or
                                    bfu_utils.GetAssetType(obj) == "SkeletalMesh" or
                                    bfu_utils.GetAssetType(obj) == "Alembic"):
                                bfu_material_search_location = layout.row()
                                bfu_material_search_location.prop(
                                    obj, 'bfu_material_search_location')

            bfu_ui_utils.LayoutSection(layout, "bfu_object_vertex_color_properties_expanded", "Vertex color")
            if scene.bfu_object_vertex_color_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # Vertex color
                        StaticMeshVertexColorImportOption = layout.column()
                        StaticMeshVertexColorImportOption.prop(obj, 'bfu_vertex_color_import_option')
                        if obj.bfu_vertex_color_import_option == "OVERRIDE":
                            StaticMeshVertexColorImportOptionColor = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionColor.prop(obj, 'bfu_vertex_color_override_color')
                        if obj.bfu_vertex_color_import_option == "REPLACE":
                            StaticMeshVertexColorImportOptionIndex = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionIndex.prop(obj, 'bfu_vertex_color_to_use')
                            if obj.bfu_vertex_color_to_use == "CustomIndex":
                                StaticMeshVertexColorImportOptionIndexCustom = StaticMeshVertexColorImportOption.row()
                                StaticMeshVertexColorImportOptionIndexCustom.prop(obj, 'bfu_vertex_color_index_to_use')

                            StaticMeshVertexColorFeedback = StaticMeshVertexColorImportOption.row()
                            if obj.type == "MESH":
                                vced = bfu_export_get_info.VertexColorExportData(obj)
                                if vced.export_type == "REPLACE":
                                    my_text = 'Vertex color nammed "' + vced.name + '" will be used.'
                                    StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')
                                else:
                                    my_text = 'No vertex color found at this index.'
                                    StaticMeshVertexColorFeedback.label(text=my_text, icon='ERROR')
                            else:
                                my_text = 'Vertex color property will be apply on the childrens.'
                                StaticMeshVertexColorFeedback.label(text=my_text, icon='INFO')

            bfu_ui_utils.LayoutSection(layout, "bfu_object_light_map_properties_expanded", "Light map")
            if scene.bfu_object_light_map_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.bfu_export_type == "export_recursive":

                        # Light map
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            StaticMeshLightMapRes = layout.box()
                            StaticMeshLightMapRes.prop(obj, 'bfu_static_mesh_light_map_enum')
                            if obj.bfu_static_mesh_light_map_enum == "CustomMap":
                                CustomLightMap = StaticMeshLightMapRes.column()
                                CustomLightMap.prop(obj, 'bfu_static_mesh_custom_light_map_res')
                            if obj.bfu_static_mesh_light_map_enum == "SurfaceArea":
                                SurfaceAreaLightMap = StaticMeshLightMapRes.column()
                                SurfaceAreaLightMapButton = SurfaceAreaLightMap.row()
                                SurfaceAreaLightMapButton.operator("object.computlightmap", icon='TEXTURE')
                                SurfaceAreaLightMapButton.operator("object.computalllightmap", icon='TEXTURE')
                                SurfaceAreaLightMap.prop(obj, 'bfu_use_static_mesh_light_map_world_scale')
                                SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_surface_scale')
                                SurfaceAreaLightMap.prop(obj, 'bfu_static_mesh_light_map_round_power_of_two')
                            if obj.bfu_static_mesh_light_map_enum != "Default":
                                CompuntedLightMap = str(bfu_utils.GetCompuntedLightMap(obj))
                                StaticMeshLightMapRes.label(text='Compunted light map: ' + CompuntedLightMap)
                            bfu_generate_light_map_uvs = layout.row()
                            bfu_generate_light_map_uvs.prop(obj, 'bfu_generate_light_map_uvs')

            bfu_ui_utils.LayoutSection(layout, "bfu_object_uv_map_properties_expanded", "UV map")
            if scene.bfu_object_uv_map_properties_expanded:
                if obj.bfu_export_type == "export_recursive":
                    # Geometry Node Uv
                    bfu_convert_geometry_node_attribute_to_uv = layout.column()
                    convert_geometry_node_attribute_to_uv_use = bfu_convert_geometry_node_attribute_to_uv.row()
                    convert_geometry_node_attribute_to_uv_use.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv')
                    bfu_ui_utils.DocPageButton(convert_geometry_node_attribute_to_uv_use, "wiki/UV-Maps", "Geometry Node UV")
                    bfu_convert_geometry_node_attribute_to_uv_name = bfu_convert_geometry_node_attribute_to_uv.row()
                    bfu_convert_geometry_node_attribute_to_uv_name.prop(obj, 'bfu_convert_geometry_node_attribute_to_uv_name')
                    bfu_convert_geometry_node_attribute_to_uv_name.enabled = obj.bfu_convert_geometry_node_attribute_to_uv

                    # Extreme UV Scale
                    bfu_correct_extrem_uv_scale = layout.row()
                    bfu_correct_extrem_uv_scale.prop(obj, 'bfu_correct_extrem_uv_scale')
                    bfu_ui_utils.DocPageButton(bfu_correct_extrem_uv_scale, "wiki/UV-Maps", "Extreme UV Scale")

        if bfu_ui_utils.DisplayPropertyFilter("SCENE", "GENERAL"):
            bfu_ui_utils.LayoutSection(layout, "bfu_collection_properties_expanded", "Collection Properties")
            if scene.bfu_collection_properties_expanded:
                collectionListProperty = layout.column()
                collectionListProperty.template_list(
                    # type and unique id
                    "BFU_UL_CollectionExportTarget", "",
                    # pointer to the CollectionProperty
                    scene, "CollectionExportList",
                    # pointer to the active identifier
                    scene, "active_CollectionExportList",
                    maxrows=5,
                    rows=5
                )
                collectionListProperty.operator(
                    "object.updatecollectionlist",
                    icon='RECOVER_LAST')

                if scene.active_CollectionExportList < len(scene.CollectionExportList):
                    col_name = scene.CollectionExportList[scene.active_CollectionExportList].name
                    if col_name in bpy.data.collections:
                        col = bpy.data.collections[col_name]
                        col_prop = layout
                        col_prop.prop(col, 'bfu_export_folder_name', icon='FILE_FOLDER')

                collectionPropertyInfo = layout.row().box().split(factor=0.75)
                collectionNum = len(bfu_utils.GetCollectionToExport(scene))
                collectionFeedback = (
                    str(collectionNum) +
                    " Collection(s) will be exported.")
                collectionPropertyInfo.label(text=collectionFeedback, icon='INFO')
                collectionPropertyInfo.operator("object.showscenecollection")
                layout.label(text='Note: The collection are exported like StaticMesh.')

class BFU_OT_ObjExportAction(bpy.types.PropertyGroup):
    name: StringProperty(name="Action data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: BoolProperty(name="use this action", default=False, override={'LIBRARY_OVERRIDABLE'})


class BFU_OT_SceneCollectionExport(bpy.types.PropertyGroup):
    name: StringProperty(name="collection data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: BoolProperty(name="export this collection", default=False, override={'LIBRARY_OVERRIDABLE'})




# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_PT_BlenderForUnrealObject,
    BFU_PT_BlenderForUnrealObject.BFU_MT_ObjectGlobalPropertiesPresets,
    BFU_PT_BlenderForUnrealObject.BFU_OT_AddObjectGlobalPropertiesPreset,
    BFU_PT_BlenderForUnrealObject.BFU_OT_OpenDocumentationPage,
    BFU_PT_BlenderForUnrealObject.BFU_OT_CopyRegularCameraButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_CopyCineCameraButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_ComputLightMap,
    BFU_PT_BlenderForUnrealObject.BFU_UL_ActionExportTarget,
    BFU_PT_BlenderForUnrealObject.BFU_OT_UpdateObjActionListButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_ShowActionToExport,
    BFU_PT_BlenderForUnrealObject.BFU_UL_CollectionExportTarget,
    BFU_PT_BlenderForUnrealObject.BFU_OT_UpdateCollectionButton,
    BFU_PT_BlenderForUnrealObject.BFU_OT_ShowCollectionToExport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.utils.register_class(BFU_OT_ObjExportAction)
    bpy.types.Object.exportActionList = CollectionProperty(
        type=BFU_OT_ObjExportAction,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )
    bpy.utils.register_class(BFU_OT_SceneCollectionExport)
    bpy.types.Scene.CollectionExportList = CollectionProperty(
        type=BFU_OT_SceneCollectionExport,
        options={'LIBRARY_EDITABLE'},
        override={'LIBRARY_OVERRIDABLE', 'USE_INSERTION'},
        )


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.utils.unregister_class(BFU_OT_ObjExportAction)
    bpy.utils.unregister_class(BFU_OT_SceneCollectionExport)
