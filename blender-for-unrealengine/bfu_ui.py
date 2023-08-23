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
import time

from .export import bfu_export_asset
from . import bfu_write_text
from . import bfu_basics
from . import bfu_utils
from .export import bfu_export_get_info
from . import bfu_check_potential_error
from . import bfu_ui_utils
from . import languages

from . import bbpl
from . import bps

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
    if "bfu_export_get_info" in locals():
        importlib.reload(bfu_export_get_info)
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


class BFU_OT_ObjExportAction(bpy.types.PropertyGroup):
    name: StringProperty(name="Action data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: BoolProperty(name="use this action", default=False, override={'LIBRARY_OVERRIDABLE'})


class BFU_OT_SceneCollectionExport(bpy.types.PropertyGroup):
    name: StringProperty(name="collection data name", default="Unknown", override={'LIBRARY_OVERRIDABLE'})
    use: BoolProperty(name="export this collection", default=False, override={'LIBRARY_OVERRIDABLE'})


class BFU_PT_BlenderForUnrealObject(bpy.types.Panel):
    # Unreal engine export panel

    bl_idname = "BFU_PT_BlenderForUnrealObject"
    bl_label = "Blender for Unreal Engine"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    # Object Properties
    bpy.types.Object.ExportEnum = EnumProperty(
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

    bpy.types.Object.exportFolderName = StringProperty(
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

    bpy.types.Collection.exportFolderName = StringProperty(
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
            ("normal",
                "Normal",
                "No specific Rig.",
                "ARMATURE_DATA",
                1),
            ("auto-rig-pro",
                "AutoRigPro",
                "Export using AutoRigPro.",
                "ARMATURE_DATA",
                2),
            ]
        )

    bpy.types.Object.ExportAsAlembic = BoolProperty(
        name="Export as Alembic animation",
        description=(
            "If true this mesh will be exported as a Alembic animation"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.ExportAsLod = BoolProperty(
        name="Export as lod?",
        description=(
            "If true this mesh will be exported" +
            " as a level of detail for another mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.ForceStaticMesh = BoolProperty(
        name="Force staticMesh",
        description="Force export asset like a StaticMesh if is ARMATURE type",
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.exportDeformOnly = BoolProperty(
        name="Export only deform Bones",
        description=(
            "Only write deforming bones" +
            " (and non-deforming ones when they have deforming children)"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True
        )

    bpy.types.Object.bfu_use_custom_export_name = BoolProperty(
        name="Export with custom name.",
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
    bpy.types.Object.Ue4Lod1 = PointerProperty(
        name="LOD1",
        description="Target objet for level of detail 01",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.Ue4Lod2 = PointerProperty(
        name="LOD2",
        description="Target objet for level of detail 02",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.Ue4Lod3 = PointerProperty(
        name="LOD3",
        description="Target objet for level of detail 03",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.Ue4Lod4 = PointerProperty(
        name="LOD4",
        description="Target objet for level of detail 04",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    bpy.types.Object.Ue4Lod5 = PointerProperty(
        name="LOD5",
        description="Target objet for level of detail 05",
        override={'LIBRARY_OVERRIDABLE'},
        type=bpy.types.Object
        )

    # ImportUI
    # https://api.unrealengine.com/INT/API/Editor/UnrealEd/Factories/UFbxImportUI/index.html

    bpy.types.Object.CreatePhysicsAsset = BoolProperty(
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

    bpy.types.Object.UseStaticMeshLODGroup = BoolProperty(
        name="",
        description='',
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.StaticMeshLODGroup = StringProperty(
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

    bpy.types.Object.StaticMeshLightMapEnum = EnumProperty(
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

    bpy.types.Object.customStaticMeshLightMapRes = IntProperty(
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

    bpy.types.Object.staticMeshLightMapSurfaceScale = FloatProperty(
        name="Surface scale",
        description="This is for resacle the surface Area value",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.00001,  # Min for unreal
        default=64
        )

    bpy.types.Object.staticMeshLightMapRoundPowerOfTwo = BoolProperty(
        name="Round power of 2",
        description=(
            "round Light Map resolution to nearest power of 2"
            ),
        default=True
        )

    bpy.types.Object.useStaticMeshLightMapWorldScale = BoolProperty(
        name="Use world scale",
        description=(
            "If not that will use the object scale."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.GenerateLightmapUVs = BoolProperty(
        name="Generate LightmapUVs",
        description=(
            "If checked, UVs for Lightmap will automatically be generated."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    bpy.types.Object.convert_geometry_node_attribute_to_uv = BoolProperty(
        name="Convert Attribute To Uv",
        description=(
            "convert target geometry node attribute to UV when found."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=True,
        )

    bpy.types.Object.convert_geometry_node_attribute_to_uv_name = StringProperty(
        name="Attribute name",
        description=(
            "Name of the Attribute to convert"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default="UVMap",
        )

    bpy.types.Object.correct_extrem_uv_scale = BoolProperty(
        name=(languages.ti('correct_extrem_uv_scale_name')),
        description=(languages.tt('correct_extrem_uv_scale_desc')),
        override={'LIBRARY_OVERRIDABLE'},
        default=False,
        )

    bpy.types.Object.AutoGenerateCollision = BoolProperty(
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

    bpy.types.Object.MaterialSearchLocation = EnumProperty(
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

    bpy.types.Object.CollisionTraceFlag = EnumProperty(
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

    bpy.types.Object.VertexColorImportOption = EnumProperty(
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

    bpy.types.Object.VertexOverrideColor = FloatVectorProperty(
            name="Vertex Override Color",
            subtype='COLOR',
            description="Specify override color in the case that VertexColorImportOption is set to Override",
            override={'LIBRARY_OVERRIDABLE'},
            default=(1.0, 1.0, 1.0),
            min=0.0,
            max=1.0
            # Vania python
            # https://docs.unrealengine.com/en-US/PythonAPI/class/FbxSkeletalMeshImportData.html
        )

    bpy.types.Object.VertexColorToUse = EnumProperty(
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

    bpy.types.Object.VertexColorIndexToUse = IntProperty(
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

    bpy.types.Object.PrefixNameToExport = StringProperty(
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


    bpy.types.Object.SampleAnimForExport = FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        override={'LIBRARY_OVERRIDABLE'},
        min=0.01, max=100.0,
        soft_min=0.01, soft_max=100.0,
        default=1.0,
        )

    bpy.types.Object.SimplifyAnimForExport = FloatProperty(
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

    bpy.types.Object.exportGlobalScale = FloatProperty(
        name="Global scale",
        description="Scale, change is not recommended with SkeletalMesh.",
        override={'LIBRARY_OVERRIDABLE'},
        default=1.0
        )

    bpy.types.Object.exportAxisForward = EnumProperty(
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

    bpy.types.Object.exportAxisUp = EnumProperty(
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

    bpy.types.Object.exportPrimaryBoneAxis = EnumProperty(
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

    bpy.types.Object.exportSecondaryBoneAxis = EnumProperty(
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

    bpy.types.Object.MoveToCenterForExport = BoolProperty(
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

    bpy.types.Object.RotateToZeroForExport = BoolProperty(
        name="Rotate to zero",
        description=(
            "If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.MoveActionToCenterForExport = BoolProperty(
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

    bpy.types.Object.RotateActionToZeroForExport = BoolProperty(
        name="Rotate Action to zero",
        description=(
            "(Action animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.MoveNLAToCenterForExport = BoolProperty(
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

    bpy.types.Object.RotateNLAToZeroForExport = BoolProperty(
        name="Rotate NLA to zero",
        description=(
            "(Non linear animation only) If true use object rotation else use scene rotation." +
            " | If true the mesh will use zero rotation for export."
            ),
        override={'LIBRARY_OVERRIDABLE'},
        default=False
        )

    bpy.types.Object.AdditionalLocationForExport = FloatVectorProperty(
        name="Additional location",
        description=(
            "This will add a additional absolute location to the mesh"
            ),
        override={'LIBRARY_OVERRIDABLE'},
        subtype="TRANSLATION",
        default=(0, 0, 0)
        )

    bpy.types.Object.AdditionalRotationForExport = FloatVectorProperty(
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
        def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
            ActionIsValid = False
            if item.name in bpy.data.actions:
                bpy.data.actions[item.name]
                ActionIsValid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if ActionIsValid:  # If action is valid
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
                        '" Not Found. Please clic on update'
                        )
                    layout.label(text=dataText, icon="ERROR")
            # Not optimised for 'GRID' layout type.
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

                def SetUseFromLast(list, ActionName):
                    for item in list:
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
                            'obj.exportFolderName',
                            'col.exportFolderName',
                            'obj.bfu_export_fbx_camera',
                            'obj.bfu_fix_axis_flippings',
                            'obj.ExportAsAlembic',
                            'obj.ExportAsLod',
                            'obj.ForceStaticMesh',
                            'obj.exportDeformOnly',
                            'obj.Ue4Lod1',
                            'obj.Ue4Lod2',
                            'obj.Ue4Lod3',
                            'obj.Ue4Lod4',
                            'obj.Ue4Lod5',
                            'obj.CreatePhysicsAsset',
                            'obj.bfu_skeleton_search_mode',
                            'obj.bfu_target_skeleton_custom_path',
                            'obj.bfu_target_skeleton_custom_name',
                            'obj.bfu_target_skeleton_custom_ref',
                            'obj.UseStaticMeshLODGroup',
                            'obj.StaticMeshLODGroup',
                            'obj.StaticMeshLightMapEnum',
                            'obj.customStaticMeshLightMapRes',
                            'obj.staticMeshLightMapSurfaceScale',
                            'obj.staticMeshLightMapRoundPowerOfTwo',
                            'obj.useStaticMeshLightMapWorldScale',
                            'obj.GenerateLightmapUVs',
                            'obj.convert_geometry_node_attribute_to_uv',
                            'obj.convert_geometry_node_attribute_to_uv_name',
                            'obj.correct_extrem_uv_scale',
                            'obj.AutoGenerateCollision',
                            'obj.MaterialSearchLocation',
                            'obj.CollisionTraceFlag',
                            'obj.VertexColorImportOption',
                            'obj.VertexOverrideColor',
                            'obj.VertexColorToUse',
                            'obj.VertexColorIndexToUse',
                            'obj.bfu_anim_action_export_enum',
                            'obj.PrefixNameToExport',
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
                            'obj.SampleAnimForExport',
                            'obj.SimplifyAnimForExport',
                            'obj.bfu_anim_nla_use',
                            'obj.bfu_anim_nla_export_name',
                            'obj.bfu_anim_naming_type',
                            'obj.bfu_anim_naming_custom',
                            'obj.exportGlobalScale',
                            'obj.exportAxisForward',
                            'obj.exportAxisUp',
                            'obj.exportPrimaryBoneAxis',
                            'obj.exportSecondaryBoneAxis',
                            'obj.bfu_mirror_symmetry_right_side_bones',
                            'obj.bfu_use_ue_mannequin_bone_alignment',
                            'obj.bfu_disable_free_scale_animation',
                            'obj.MoveToCenterForExport',
                            'obj.RotateToZeroForExport',
                            'obj.MoveActionToCenterForExport',
                            'obj.RotateActionToZeroForExport',
                            'obj.MoveNLAToCenterForExport',
                            'obj.RotateNLAToZeroForExport',
                            'obj.AdditionalLocationForExport',
                            'obj.AdditionalRotationForExport',
                        ]

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/global-properties-presets'

    class BFU_UL_CollectionExportTarget(bpy.types.UIList):

        def draw_item(self, context, layout, data, item, icon, active_data, active_propname):

            CollectionIsValid = False
            if item.name in bpy.data.collections:
                bpy.data.collections[item.name]
                CollectionIsValid = True

            if self.layout_type in {'DEFAULT', 'COMPACT'}:
                if CollectionIsValid:  # If action is valid
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

                def SetUseFromLast(list, CollectionName):
                    for item in list:
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

            def draw(self, context):
                col = self.layout.column()
                for collection in collections:
                    row = col.row()
                    row.label(text="- "+collection.name)
            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='GROUP')
            return {'FINISHED'}

    def draw(self, contex):
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
                    ExportType.prop(obj, 'ExportEnum')

                    if obj.type == "CAMERA":
                        CameraProp = layout.column()
                        CameraProp.operator("object.copy_regular_camera_command", icon="COPYDOWN")
                        CameraProp.operator("object.copy_cine_camera_command", icon="COPYDOWN")

                    if obj.ExportEnum == "export_recursive":

                        folderNameProperty = layout.column()
                        folderNameProperty.prop(
                            obj,
                            'exportFolderName',
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
                                AlembicProp.prop(obj, 'ExportAsAlembic')
                                if obj.ExportAsAlembic:
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
                                            LodProp.prop(obj, 'ExportAsLod')
                            if not obj.ExportAsAlembic:
                                if obj.type == "ARMATURE":
                                    AssetType2 = layout.column()
                                    # Show asset type
                                    AssetType2.prop(obj, "ForceStaticMesh")
                                    if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                                        AssetType2.prop(obj, 'exportDeformOnly')

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
                    if obj.ExportEnum == "export_recursive":

                        transformProp = layout.column()
                        if bfu_utils.GetAssetType(obj) != "Alembic" and bfu_utils.GetAssetType(obj) != "Camera":
                            transformProp.prop(obj, "MoveToCenterForExport")
                            transformProp.prop(obj, "RotateToZeroForExport")
                            transformProp.prop(obj, "AdditionalLocationForExport")
                            transformProp.prop(obj, "AdditionalRotationForExport")
                            transformProp.prop(obj, 'exportGlobalScale')
                        elif bfu_utils.GetAssetType(obj) == "Camera":
                            transformProp.prop(obj, "AdditionalLocationForExport")

                        AxisProperty = layout.column()
                        AxisProperty.prop(obj, 'exportAxisForward')
                        AxisProperty.prop(obj, 'exportAxisUp')
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            BoneAxisProperty = layout.column()
                            BoneAxisProperty.prop(obj, 'exportPrimaryBoneAxis')
                            BoneAxisProperty.prop(obj, 'exportSecondaryBoneAxis')
                else:
                    layout.label(text='(No properties to show.)')

            bfu_ui_utils.LayoutSection(layout, "bfu_skeleton_properties_expanded", "Skeleton")
            if scene.bfu_skeleton_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.ExportEnum == "export_recursive":

                        # SkeletalMesh prop
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            if not obj.ExportAsLod:

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
                if obj.ExportEnum == "export_recursive" and not obj.ExportAsLod:

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
                                    ActionListProperty.prop(obj, 'PrefixNameToExport')

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
                            transformProp.prop(obj, "MoveActionToCenterForExport")
                            transformProp.prop(obj, "RotateActionToZeroForExport")

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
                            transformProp2.prop(obj, "MoveNLAToCenterForExport")
                            transformProp2.prop(obj, "RotateNLAToZeroForExport")

                    bfu_ui_utils.LayoutSection(layout, "bfu_animation_advanced_properties_expanded", "Animation Advanced Properties")
                    if scene.bfu_animation_advanced_properties_expanded:
                        # Animation fbx properties
                        if (bfu_utils.GetAssetType(obj) != "Alembic"):
                            propsFbx = layout.row()
                            if obj.bfu_export_procedure != "auto-rig-pro":
                                propsFbx.prop(obj, 'SampleAnimForExport')
                            propsFbx.prop(obj, 'SimplifyAnimForExport')
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
                    if obj.ExportEnum == "export_recursive":

                        # Lod selection
                        if not obj.ExportAsLod:
                            # Unreal python no longer support Skeletal mesh LODS import.
                            if (bfu_utils.GetAssetType(obj) == "StaticMesh"):
                                LodList = layout.column()
                                LodList.prop(obj, 'Ue4Lod1')
                                LodList.prop(obj, 'Ue4Lod2')
                                LodList.prop(obj, 'Ue4Lod3')
                                LodList.prop(obj, 'Ue4Lod4')
                                LodList.prop(obj, 'Ue4Lod5')

                        # StaticMesh prop
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            if not obj.ExportAsLod:
                                StaticMeshLODGroup = layout.row()
                                StaticMeshLODGroup.prop(
                                    obj,
                                    'UseStaticMeshLODGroup',
                                    text="")
                                SMLODGroupChild = StaticMeshLODGroup.column()
                                SMLODGroupChild.enabled = obj.UseStaticMeshLODGroup
                                SMLODGroupChild.prop(
                                    obj,
                                    'StaticMeshLODGroup'
                                    )

            bfu_ui_utils.LayoutSection(layout, "bfu_object_collision_properties_expanded", "Collision")
            if scene.bfu_object_collision_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.ExportEnum == "export_recursive":

                        # StaticMesh prop
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            StaticMeshCollisionTraceFlag = layout.row()
                            StaticMeshCollisionTraceFlag.prop(
                                obj,
                                'CollisionTraceFlag'
                                )
                            if not obj.ExportAsLod:
                                AutoGenerateCollision = layout.row()
                                AutoGenerateCollision.prop(
                                    obj,
                                    'AutoGenerateCollision'
                                    )
                        # SkeletalMesh prop
                        if bfu_utils.GetAssetType(obj) == "SkeletalMesh":
                            if not obj.ExportAsLod:
                                CreatePhysicsAsset = layout.row()
                                CreatePhysicsAsset.prop(obj, "CreatePhysicsAsset")

            bfu_ui_utils.LayoutSection(layout, "bfu_object_material_properties_expanded", "Material")
            if scene.bfu_object_material_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.ExportEnum == "export_recursive":

                        # MaterialSearchLocation
                        if not obj.ExportAsLod:
                            if (bfu_utils.GetAssetType(obj) == "StaticMesh" or
                                    bfu_utils.GetAssetType(obj) == "SkeletalMesh" or
                                    bfu_utils.GetAssetType(obj) == "Alembic"):
                                MaterialSearchLocation = layout.row()
                                MaterialSearchLocation.prop(
                                    obj, 'MaterialSearchLocation')

            bfu_ui_utils.LayoutSection(layout, "bfu_object_vertex_color_properties_expanded", "Vertex color")
            if scene.bfu_object_vertex_color_properties_expanded:
                if addon_prefs.useGeneratedScripts and obj is not None:
                    if obj.ExportEnum == "export_recursive":

                        # Vertex color
                        StaticMeshVertexColorImportOption = layout.column()
                        StaticMeshVertexColorImportOption.prop(obj, 'VertexColorImportOption')
                        if obj.VertexColorImportOption == "OVERRIDE":
                            StaticMeshVertexColorImportOptionColor = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionColor.prop(obj, 'VertexOverrideColor')
                        if obj.VertexColorImportOption == "REPLACE":
                            StaticMeshVertexColorImportOptionIndex = StaticMeshVertexColorImportOption.row()
                            StaticMeshVertexColorImportOptionIndex.prop(obj, 'VertexColorToUse')
                            if obj.VertexColorToUse == "CustomIndex":
                                StaticMeshVertexColorImportOptionIndexCustom = StaticMeshVertexColorImportOption.row()
                                StaticMeshVertexColorImportOptionIndexCustom.prop(obj, 'VertexColorIndexToUse')

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
                    if obj.ExportEnum == "export_recursive":

                        # Light map
                        if bfu_utils.GetAssetType(obj) == "StaticMesh":
                            StaticMeshLightMapRes = layout.box()
                            StaticMeshLightMapRes.prop(obj, 'StaticMeshLightMapEnum')
                            if obj.StaticMeshLightMapEnum == "CustomMap":
                                CustomLightMap = StaticMeshLightMapRes.column()
                                CustomLightMap.prop(obj, 'customStaticMeshLightMapRes')
                            if obj.StaticMeshLightMapEnum == "SurfaceArea":
                                SurfaceAreaLightMap = StaticMeshLightMapRes.column()
                                SurfaceAreaLightMapButton = SurfaceAreaLightMap.row()
                                SurfaceAreaLightMapButton.operator("object.computlightmap", icon='TEXTURE')
                                SurfaceAreaLightMapButton.operator("object.computalllightmap", icon='TEXTURE')
                                SurfaceAreaLightMap.prop(obj, 'useStaticMeshLightMapWorldScale')
                                SurfaceAreaLightMap.prop(obj, 'staticMeshLightMapSurfaceScale')
                                SurfaceAreaLightMap.prop(obj, 'staticMeshLightMapRoundPowerOfTwo')
                            if obj.StaticMeshLightMapEnum != "Default":
                                CompuntedLightMap = str(bfu_utils.GetCompuntedLightMap(obj))
                                StaticMeshLightMapRes.label(text='Compunted light map: ' + CompuntedLightMap)
                            GenerateLightmapUVs = layout.row()
                            GenerateLightmapUVs.prop(obj, 'GenerateLightmapUVs')

            bfu_ui_utils.LayoutSection(layout, "bfu_object_uv_map_properties_expanded", "UV map")
            if scene.bfu_object_uv_map_properties_expanded:
                if obj.ExportEnum == "export_recursive":
                    # Geometry Node Uv
                    convert_geometry_node_attribute_to_uv = layout.column()
                    convert_geometry_node_attribute_to_uv_use = convert_geometry_node_attribute_to_uv.row()
                    convert_geometry_node_attribute_to_uv_use.prop(obj, 'convert_geometry_node_attribute_to_uv')
                    bfu_ui_utils.DocPageButton(convert_geometry_node_attribute_to_uv_use, "wiki/UV-Maps", "Geometry Node UV")
                    convert_geometry_node_attribute_to_uv_name = convert_geometry_node_attribute_to_uv.row()
                    convert_geometry_node_attribute_to_uv_name.prop(obj, 'convert_geometry_node_attribute_to_uv_name')
                    convert_geometry_node_attribute_to_uv_name.enabled = obj.convert_geometry_node_attribute_to_uv

                    # Extreme UV Scale
                    correct_extrem_uv_scale = layout.row()
                    correct_extrem_uv_scale.prop(obj, 'correct_extrem_uv_scale')
                    bfu_ui_utils.DocPageButton(correct_extrem_uv_scale, "wiki/UV-Maps", "Extreme UV Scale")

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
                        col_prop.prop(col, 'exportFolderName', icon='FILE_FOLDER')

                collectionPropertyInfo = layout.row().box().split(factor=0.75)
                collectionNum = len(bfu_utils.GetCollectionToExport(scene))
                collectionFeedback = (
                    str(collectionNum) +
                    " Collection(s) will be exported.")
                collectionPropertyInfo.label(text=collectionFeedback, icon='INFO')
                collectionPropertyInfo.operator("object.showscenecollection")
                layout.label(text='Note: The collection are exported like StaticMesh.')


class BFU_PT_BlenderForUnrealTool(bpy.types.Panel):
    # Tool panel with Collisions And Sockets

    bl_idname = "BFU_PT_BlenderForUnrealTool"
    bl_label = "Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    bpy.types.Object.bfu_use_socket_custom_Name = BoolProperty(
        name="Socket custom name",
        description='Use a custom name in Unreal Engine for this socket?',
        default=False
        )

    bpy.types.Object.bfu_socket_custom_Name = StringProperty(
        name="",
        description='',
        default="MySocket"
        )

    class BFU_OT_CopyRegularCamerasButton(Operator):
        bl_label = "Copy Regular Cameras for Unreal"
        bl_idname = "object.copy_regular_cameras_command"
        bl_description = "Copy Regular Cameras Script command"

        def execute(self, context):
            objs = context.selected_objects
            result = bfu_utils.GetImportCameraScriptCommand(objs, False)
            if result[0]:
                bfu_basics.setWindowsClipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}

    class BFU_OT_CopyCineCamerasButton(Operator):
        bl_label = "Copy Cine Cameras for Unreal"
        bl_idname = "object.copy_cine_cameras_command"
        bl_description = "Copy Cine Cameras Script command"

        def execute(self, context):
            objs = context.selected_objects
            result = bfu_utils.GetImportCameraScriptCommand(objs, True)
            if result[0]:
                bfu_basics.setWindowsClipboard(result[1])
                self.report({'INFO'}, result[2])
            else:
                self.report({'WARNING'}, result[2])
            return {'FINISHED'}

    class BFU_OT_ConvertToCollisionButtonBox(Operator):
        bl_label = "Convert to box (UBX)"
        bl_idname = "object.converttoboxcollision"
        bl_description = (
            "Convert selected mesh(es) to Unreal" +
            " collision ready for export (Boxes type)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("Box")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have be" +
                    " converted to UE4 Box collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}

    class BFU_OT_ConvertToCollisionButtonCapsule(Operator):
        bl_label = "Convert to capsule (UCP)"
        bl_idname = "object.converttocapsulecollision"
        bl_description = (
            "Convert selected mesh(es) to Unreal collision" +
            " ready for export (Capsules type)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("Capsule")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have be converted" +
                    " to UE4 Capsule collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}

    class BFU_OT_ConvertToCollisionButtonSphere(Operator):
        bl_label = "Convert to sphere (USP)"
        bl_idname = "object.converttospherecollision"
        bl_description = (
            "Convert selected mesh(es)" +
            " to Unreal collision ready for export (Spheres type)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("Sphere")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have" +
                    " be converted to UE4 Sphere collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}

    class BFU_OT_ConvertToCollisionButtonConvex(Operator):
        bl_label = "Convert to convex shape (UCX)"
        bl_idname = "object.converttoconvexcollision"
        bl_description = (
            "Convert selected mesh(es) to Unreal" +
            " collision ready for export (Convex shapes type)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("Convex")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have be" +
                    " converted to UE4 Convex Shape collisions.")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the collision)")
            return {'FINISHED'}

    class BFU_OT_ConvertToStaticSocketButton(Operator):
        bl_label = "Convert to StaticMesh socket"
        bl_idname = "object.converttostaticsocket"
        bl_description = (
            "Convert selected Empty(s) to Unreal sockets" +
            " ready for export (StaticMesh)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("ST_Socket")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have be" +
                    " converted to UE4 Socket. (Static)")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects." +
                    " (Active object is the owner of the socket)")
            return {'FINISHED'}

    class BFU_OT_ConvertToSkeletalSocketButton(Operator):
        bl_label = "Convert to SkeletalMesh socket"
        bl_idname = "object.converttoskeletalsocket"
        bl_description = (
            "Convert selected Empty(s)" +
            " to Unreal sockets ready for export (SkeletalMesh)")

        def execute(self, context):
            ConvertedObj = bfu_utils.Ue4SubObj_set("SKM_Socket")
            if len(ConvertedObj) > 0:
                self.report(
                    {'INFO'},
                    str(len(ConvertedObj)) +
                    " object(s) of the selection have" +
                    " be converted to UE4 Socket. (Skeletal)")
            else:
                self.report(
                    {'WARNING'},
                    "Please select two objects. " +
                    "(Active object is the owner of the socket)")
            return {'FINISHED'}

    class BFU_OT_CopySkeletalSocketButton(Operator):
        bl_label = "Copy Skeletal Mesh socket for Unreal"
        bl_idname = "object.copy_skeletalsocket_command"
        bl_description = "Copy Skeletal Socket Script command"

        def execute(self, context):
            obj = context.object
            if obj:
                if obj.type == "ARMATURE":
                    bfu_basics.setWindowsClipboard(bfu_utils.GetImportSkeletalMeshSocketScriptCommand(obj))
                    self.report(
                        {'INFO'},
                        "Skeletal sockets copied. Paste in Unreal Engine Skeletal Mesh assets for import sockets. (Ctrl+V)")
            return {'FINISHED'}

    class BFU_OT_ComputAllLightMap(Operator):
        bl_label = "Calculate all surface area"
        bl_idname = "object.computalllightmap"
        bl_description = (
            "Click to calculate the surface of the all object in the scene"
            )

        def execute(self, context):
            updated = bfu_utils.UpdateAreaLightMapList()
            self.report(
                {'INFO'},
                "The light maps of " + str(updated) +
                " object(s) have been updated."
                )
            return {'FINISHED'}

    def draw(self, context):

        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout
        scene = bpy.context.scene
        obj = context.object

        def ActiveModeIs(targetMode):
            # Return True is active mode ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.mode == targetMode:
                    return True
            return False

        def ActiveTypeIs(targetType):
            # Return True is active type ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.type == targetType:
                    return True
            return False

        def ActiveTypeIsNot(targetType):
            # Return True is active type ==
            obj = bpy.context.active_object
            if obj is not None:
                if obj.type != targetType:
                    return True
            return False

        def FoundTypeInSelect(targetType, include_active=True):
            # Return True if a specific type is found
            select = bpy.context.selected_objects
            if not include_active:
                if bpy.context.active_object:
                    if bpy.context.active_object in select:
                        select.remove(bpy.context.active_object)

            for obj in select:
                if obj.type == targetType:
                    return True
            return False

        ready_for_convert_collider = False
        ready_for_convert_socket = False

        bfu_ui_utils.LayoutSection(layout, "bfu_camera_expanded", "Camera")
        if scene.bfu_camera_expanded:
            copy_camera_buttons = layout.column()
            copy_camera_buttons.operator("object.copy_regular_cameras_command", icon="COPYDOWN")
            copy_camera_buttons.operator("object.copy_cine_cameras_command", icon="COPYDOWN")

        bfu_ui_utils.LayoutSection(layout, "bfu_collision_socket_expanded", "Collision and Socket")
        if scene.bfu_collision_socket_expanded:
            if not ActiveModeIs("OBJECT"):
                layout.label(text="Switch to Object Mode.", icon='INFO')
            else:
                if FoundTypeInSelect("MESH", False):
                    if ActiveTypeIsNot("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        layout.label(text="Click on button for convert to collider.", icon='INFO')
                        ready_for_convert_collider = True
                    else:
                        layout.label(text="Select with [SHIFT] the collider owner.", icon='INFO')

                elif FoundTypeInSelect("EMPTY", False):
                    if ActiveTypeIsNot("ARMATURE") and len(bpy.context.selected_objects) > 1:
                        layout.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_socket = True
                    else:
                        layout.label(text="Select with [SHIFT] the socket owner.", icon='INFO')
                else:
                    layout.label(text="Select your collider Object(s) or socket Empty(s).", icon='INFO')

            convertButtons = layout.row().split(factor=0.80)
            convertStaticCollisionButtons = convertButtons.column()
            convertStaticCollisionButtons.enabled = ready_for_convert_collider
            convertStaticCollisionButtons.operator("object.converttoboxcollision", icon='MESH_CUBE')
            convertStaticCollisionButtons.operator("object.converttoconvexcollision", icon='MESH_ICOSPHERE')
            convertStaticCollisionButtons.operator("object.converttocapsulecollision", icon='MESH_CAPSULE')
            convertStaticCollisionButtons.operator("object.converttospherecollision", icon='MESH_UVSPHERE')

            convertButtons = layout.row().split(factor=0.80)
            convertStaticSocketButtons = convertButtons.column()
            convertStaticSocketButtons.enabled = ready_for_convert_socket
            convertStaticSocketButtons.operator(
                "object.converttostaticsocket",
                icon='OUTLINER_DATA_EMPTY')

            if addon_prefs.useGeneratedScripts:

                ready_for_convert_skeletal_socket = False
                if not ActiveModeIs("OBJECT"):
                    if not ActiveTypeIs("ARMATURE"):
                        if not FoundTypeInSelect("EMPTY"):
                            layout.label(text="Switch to Object Mode.", icon='INFO')
                else:
                    if FoundTypeInSelect("EMPTY"):
                        if ActiveTypeIs("ARMATURE") and len(bpy.context.selected_objects) > 1:
                            layout.label(text="Switch to Pose Mode.", icon='INFO')
                        else:
                            layout.label(text="Select with [SHIFT] the socket owner. (Armature)", icon='INFO')
                    else:
                        layout.label(text="Select your socket Empty(s).", icon='INFO')

                if ActiveModeIs("POSE") and ActiveTypeIs("ARMATURE") and FoundTypeInSelect("EMPTY"):
                    if len(bpy.context.selected_pose_bones) > 0:
                        layout.label(text="Click on button for convert to Socket.", icon='INFO')
                        ready_for_convert_skeletal_socket = True
                    else:
                        layout.label(text="Select the owner bone.", icon='INFO')

                convertButtons = self.layout.row().split(factor=0.80)
                convertSkeletalSocketButtons = convertButtons.column()
                convertSkeletalSocketButtons.enabled = ready_for_convert_skeletal_socket
                convertSkeletalSocketButtons.operator(
                    "object.converttoskeletalsocket",
                    icon='OUTLINER_DATA_EMPTY')

            if obj is not None:
                if obj.type == "EMPTY":
                    socketName = layout.column()
                    socketName.prop(obj, "bfu_use_socket_custom_Name")
                    socketNameText = socketName.column()
                    socketNameText.enabled = obj.bfu_use_socket_custom_Name
                    socketNameText.prop(obj, "bfu_socket_custom_Name")

            copy_skeletalsocket_buttons = layout.column()
            copy_skeletalsocket_buttons.enabled = False
            copy_skeletalsocket_buttons.operator(
                "object.copy_skeletalsocket_command",
                icon='COPYDOWN')
            if obj is not None:
                if obj.type == "ARMATURE":
                    copy_skeletalsocket_buttons.enabled = True

        bfu_ui_utils.LayoutSection(layout, "bfu_lightmap_expanded", "Light Map")
        if scene.bfu_lightmap_expanded:
            checkButton = layout.column()
            checkButton.operator("object.computalllightmap", icon='TEXTURE')


class BFU_PT_BlenderForUnrealDebug(bpy.types.Panel):
    # Debug panel for get dev info and test

    bl_idname = "BFU_PT_BlenderForUnrealDebug"
    bl_label = "Debug"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    bpy.types.Object.bfu_use_socket_custom_Name = BoolProperty(
        name="Socket custom name",
        description='Use a custom name in Unreal Engine for this socket?',
        default=False
        )

    bpy.types.Object.bfu_socket_custom_Name = StringProperty(
        name="",
        description='',
        default="MySocket"
        )

    def draw(self, context):
        addon_prefs = bfu_basics.GetAddonPrefs()
        layout = self.layout
        scene = bpy.context.scene
        obj = context.object
        layout.label(text="This panel is only for Debug", icon='INFO')
        if obj:
            layout.label(text="Full path name as Static Mesh:")
            layout.label(text="GetObjExportDir(local):" + bfu_utils.GetObjExportDir(obj, False))
            layout.label(text="GetObjExportDir:" + bfu_utils.GetObjExportDir(obj, True))
            layout.label(text="GetObjExportName:" + bfu_utils.GetObjExportName(obj))
            layout.label(text="GetObjExportFileName:" + bfu_utils.GetObjExportFileName(obj))
            if obj.type == "CAMERA":
                layout.label(text="CameraPositionForUnreal (Loc):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[0]))
                layout.label(text="CameraPositionForUnreal (Rot):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[1]))
                layout.label(text="CameraPositionForUnreal (Scale):" + str(bfu_utils.EvaluateCameraPositionForUnreal(obj)[2]))


class BFU_PT_Export(bpy.types.Panel):
    # Is Export panel

    bl_idname = "BFU_PT_Export"
    bl_label = "Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine"

    # Prefix
    bpy.types.Scene.static_mesh_prefix_export_name = bpy.props.StringProperty(
        name="StaticMesh Prefix",
        description="Prefix of staticMesh",
        maxlen=32,
        default="SM_")

    bpy.types.Scene.skeletal_mesh_prefix_export_name = bpy.props.StringProperty(
        name="SkeletalMesh Prefix ",
        description="Prefix of SkeletalMesh",
        maxlen=32,
        default="SKM_")

    bpy.types.Scene.skeleton_prefix_export_name = bpy.props.StringProperty(
        name="skeleton Prefix ",
        description="Prefix of skeleton",
        maxlen=32,
        default="SK_")

    bpy.types.Scene.alembic_prefix_export_name = bpy.props.StringProperty(
        name="Alembic Prefix ",
        description="Prefix of Alembic (SkeletalMesh in unreal)",
        maxlen=32,
        default="SKM_")

    bpy.types.Scene.anim_prefix_export_name = bpy.props.StringProperty(
        name="AnimationSequence Prefix",
        description="Prefix of AnimationSequence",
        maxlen=32,
        default="Anim_")

    bpy.types.Scene.pose_prefix_export_name = bpy.props.StringProperty(
        name="AnimationSequence(Pose) Prefix",
        description="Prefix of AnimationSequence with only one frame",
        maxlen=32,
        default="Pose_")

    bpy.types.Scene.camera_prefix_export_name = bpy.props.StringProperty(
        name="Camera anim Prefix",
        description="Prefix of camera animations",
        maxlen=32,
        default="Cam_")

    # Sub folder
    bpy.types.Scene.anim_subfolder_name = bpy.props.StringProperty(
        name="Animations sub folder name",
        description=(
            "The name of sub folder for animations New." +
            " You can now use ../ for up one directory."),
        maxlen=512,
        default="Anim")

    # File path
    bpy.types.Scene.export_static_file_path = bpy.props.StringProperty(
        name="StaticMesh export file path",
        description="Choose a directory to export StaticMesh(s)",
        maxlen=512,
        default=os.path.join("//", "ExportedFbx", "StaticMesh"),
        subtype='DIR_PATH')

    bpy.types.Scene.export_skeletal_file_path = bpy.props.StringProperty(
        name="SkeletalMesh export file path",
        description="Choose a directory to export SkeletalMesh(s)",
        maxlen=512,
        default=os.path.join("//", "ExportedFbx", "SkeletalMesh"),
        subtype='DIR_PATH')

    bpy.types.Scene.export_alembic_file_path = bpy.props.StringProperty(
        name="Alembic export file path",
        description="Choose a directory to export Alembic(s)",
        maxlen=512,
        default=os.path.join("//", "ExportedFbx", "Alembic"),
        subtype='DIR_PATH')

    bpy.types.Scene.export_camera_file_path = bpy.props.StringProperty(
        name="Camera export file path",
        description="Choose a directory to export Camera(s)",
        maxlen=512,
        default=os.path.join("//", "ExportedFbx", "Sequencer"),
        subtype='DIR_PATH')

    bpy.types.Scene.export_other_file_path = bpy.props.StringProperty(
        name="Other export file path",
        description="Choose a directory to export text file and other",
        maxlen=512,
        default=os.path.join("//", "ExportedFbx"),
        subtype='DIR_PATH')

    # File name
    bpy.types.Scene.file_export_log_name = bpy.props.StringProperty(
        name="Export log name",
        description="Export log name",
        maxlen=64,
        default="ExportLog.txt")

    bpy.types.Scene.file_import_asset_script_name = bpy.props.StringProperty(
        name="Import asset script Name",
        description="Import asset script name",
        maxlen=64,
        default="ImportAssetScript.py")

    bpy.types.Scene.file_import_sequencer_script_name = bpy.props.StringProperty(
        name="Import sequencer script Name",
        description="Import sequencer script name",
        maxlen=64,
        default="ImportSequencerScript.py")

    bpy.types.Scene.unreal_import_module = bpy.props.StringProperty(
        name="Unreal import module",
        description="Which module (plugin name) to import to. Default is 'Game', meaning it will be put into your project's /Content/ folder. If you wish to import to a plugin (for example a plugin called 'myPlugin'), just write its name here",
        maxlen=512,
        default='Game')

    bpy.types.Scene.unreal_import_location = bpy.props.StringProperty(
        name="Unreal import location",
        description="Unreal assets import location inside the module",
        maxlen=512,
        default='ImportedFbx')

    class BFU_MT_NomenclaturePresets(bpy.types.Menu):
        bl_label = 'Nomenclature Presets'
        preset_subdir = 'blender-for-unrealengine/nomenclature-presets'
        preset_operator = 'script.execute_preset'
        draw = bpy.types.Menu.draw_preset

    from bl_operators.presets import AddPresetBase

    class BFU_OT_AddNomenclaturePreset(AddPresetBase, Operator):
        bl_idname = 'object.add_nomenclature_preset'
        bl_label = 'Add or remove a preset for Nomenclature'
        bl_description = 'Add or remove a preset for Nomenclature'
        preset_menu = 'BFU_MT_NomenclaturePresets'

        # Common variable used for all preset values
        preset_defines = [
                            'obj = bpy.context.object',
                            'scene = bpy.context.scene'
                         ]

        # Properties to store in the preset
        preset_values = [
                            'scene.static_mesh_prefix_export_name',
                            'scene.skeletal_mesh_prefix_export_name',
                            'scene.skeleton_prefix_export_name',
                            'scene.alembic_prefix_export_name',
                            'scene.anim_prefix_export_name',
                            'scene.pose_prefix_export_name',
                            'scene.camera_prefix_export_name',
                            'scene.anim_subfolder_name',
                            'scene.export_static_file_path',
                            'scene.export_skeletal_file_path',
                            'scene.export_alembic_file_path',
                            'scene.export_camera_file_path',
                            'scene.export_other_file_path',
                            'scene.file_export_log_name',
                            'scene.file_import_asset_script_name',
                            'scene.file_import_sequencer_script_name',
                            # Import location:
                            'scene.unreal_import_module',
                            'scene.unreal_import_location',
                        ]

        # Directory to store the presets
        preset_subdir = 'blender-for-unrealengine/nomenclature-presets'

    class BFU_OT_ShowAssetToExport(Operator):
        bl_label = "Show asset(s)"
        bl_idname = "object.showasset"
        bl_description = "Click to show assets that are to be exported."

        def execute(self, context):

            obj = context.object
            if obj:
                if obj.type == "ARMATURE":
                    bfu_utils.UpdateActionCache(obj)

            assets = bfu_utils.GetFinalAssetToExport()
            popup_title = "Assets list"
            if len(assets) > 0:
                popup_title = str(len(assets))+' asset(s) will be exported.'
            else:
                popup_title = 'No exportable assets were found.'

            def draw(self, context):
                col = self.layout.column()
                for asset in assets:
                    row = col.row()
                    if asset.obj is not None:
                        if asset.action is not None:
                            if (type(asset.action) is bpy.types.Action):
                                # Action name
                                action = asset.action.name
                            elif (type(asset.action) is bpy.types.AnimData):
                                # Nonlinear name
                                action = asset.obj.bfu_anim_nla_export_name
                            else:
                                action = "..."
                            row.label(
                                text="- ["+asset.obj.name+"] --> " +
                                action+" ("+asset.asset_type+")")
                        else:
                            if asset.asset_type != "Collection StaticMesh":
                                row.label(
                                    text="- "+asset.obj.name +
                                    " ("+asset.asset_type+")")
                            else:
                                row.label(
                                    text="- "+asset.obj +
                                    " ("+asset.asset_type+")")

                    else:
                        row.label(text="- ("+asset.asset_type+")")
            bpy.context.window_manager.popup_menu(
                draw,
                title=popup_title,
                icon='PACKAGE')
            return {'FINISHED'}

    class BFU_OT_CheckPotentialErrorPopup(Operator):
        bl_label = "Check potential errors"
        bl_idname = "object.checkpotentialerror"
        bl_description = "Check potential errors"
        text = "none"

        def execute(self, context):
            correctedProperty = bfu_check_potential_error.CorrectBadProperty()
            bfu_check_potential_error.UpdateNameHierarchy()
            bfu_check_potential_error.UpdateUnrealPotentialError()
            bpy.ops.object.openpotentialerror("INVOKE_DEFAULT", correctedProperty=correctedProperty)
            return {'FINISHED'}

    class BFU_OT_OpenPotentialErrorPopup(Operator):
        bl_label = "Open potential errors"
        bl_idname = "object.openpotentialerror"
        bl_description = "Open potential errors"
        correctedProperty: bpy.props.IntProperty(default=0)

        class BFU_OT_FixitTarget(Operator):
            bl_label = "Fix it !"
            bl_idname = "object.fixit_objet"
            bl_description = "Correct target error"
            errorIndex: bpy.props.IntProperty(default=-1)

            def execute(self, context):
                result = bfu_check_potential_error.TryToCorrectPotentialError(self.errorIndex)
                self.report({'INFO'}, result)
                return {'FINISHED'}

        class BFU_OT_SelectObjectButton(Operator):
            bl_label = "Select(Object)"
            bl_idname = "object.select_error_objet"
            bl_description = "Select target Object."
            errorIndex: bpy.props.IntProperty(default=-1)

            def execute(self, context):
                bfu_check_potential_error.SelectPotentialErrorObject(self.errorIndex)
                return {'FINISHED'}

        class BFU_OT_SelectVertexButton(Operator):
            bl_label = "Select(Vertex)"
            bl_idname = "object.select_error_vertex"
            bl_description = "Select target Vertex."
            errorIndex: bpy.props.IntProperty(default=-1)

            def execute(self, context):
                bfu_check_potential_error.SelectPotentialErrorVertex(self.errorIndex)
                return {'FINISHED'}

        class BFU_OT_SelectPoseBoneButton(Operator):
            bl_label = "Select(PoseBone)"
            bl_idname = "object.select_error_posebone"
            bl_description = "Select target Pose Bone."
            errorIndex: bpy.props.IntProperty(default=-1)

            def execute(self, context):
                bfu_check_potential_error.SelectPotentialErrorPoseBone(self.errorIndex)
                return {'FINISHED'}

        class BFU_OT_OpenPotentialErrorDocs(Operator):
            bl_label = "Open docs"
            bl_idname = "object.open_potential_error_docs"
            bl_description = "Open potential error docs."
            octicon: StringProperty(default="")

            def execute(self, context):
                os.system(
                    "start \"\" " +
                    "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/How-avoid-potential-errors" +
                    "#"+self.octicon)
                return {'FINISHED'}

        def execute(self, context):
            return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_popup(self, width=1020)

        def check(self, context):
            return True

        def draw(self, context):

            layout = self.layout
            if len(bpy.context.scene.potentialErrorList) > 0:
                popup_title = (
                    str(len(bpy.context.scene.potentialErrorList)) +
                    " potential error(s) found!")
            else:
                popup_title = "No potential error to correct!"

            if self.correctedProperty > 0:
                potentialErrorInfo = (
                    str(self.correctedProperty) +
                    "- properties corrected.")
            else:
                potentialErrorInfo = "- No properties to correct."

            layout.label(text=popup_title)
            layout.label(text="- Hierarchy names updated")
            layout.label(text=potentialErrorInfo)
            layout.separator()
            row = layout.row()
            col = row.column()
            for x in range(len(bpy.context.scene.potentialErrorList)):
                error = bpy.context.scene.potentialErrorList[x]

                myLine = col.box().split(factor=0.85)
                # ----
                if error.type == 0:
                    msgType = 'INFO'
                    msgIcon = 'INFO'
                elif error.type == 1:
                    msgType = 'WARNING'
                    msgIcon = 'ERROR'
                elif error.type == 2:
                    msgType = 'ERROR'
                    msgIcon = 'CANCEL'
                # ----

                # Text
                TextLine = myLine.column()
                errorFullMsg = msgType+": "+error.text
                splitedText = errorFullMsg.split("\n")

                for text, Line in enumerate(splitedText):
                    if (text < 1):

                        FisrtTextLine = TextLine.row()
                        if (error.docsOcticon != "None"):  # Doc button
                            props = FisrtTextLine.operator(
                                "object.open_potential_error_docs",
                                icon="HELP",
                                text="")
                            props.octicon = error.docsOcticon

                        FisrtTextLine.label(text=Line, icon=msgIcon)
                    else:
                        TextLine.label(text=Line)

                # Select and fix button
                ButtonLine = myLine.column()
                if (error.correctRef != "None"):
                    props = ButtonLine.operator(
                        "object.fixit_objet",
                        text=error.correctlabel)
                    props.errorIndex = x
                if (error.object is not None):
                    if (error.selectObjectButton):
                        props = ButtonLine.operator(
                            "object.select_error_objet")
                        props.errorIndex = x
                    if (error.selectVertexButton):
                        props = ButtonLine.operator(
                            "object.select_error_vertex")
                        props.errorIndex = x
                    if (error.selectPoseBoneButton):
                        props = ButtonLine.operator(
                            "object.select_error_posebone")
                        props.errorIndex = x

    class BFU_OT_ExportForUnrealEngineButton(Operator):
        bl_label = "Export for Unreal Engine"
        bl_idname = "object.exportforunreal"
        bl_description = "Export all assets of this scene."

        def execute(self, context):
            scene = bpy.context.scene

            def isReadyForExport():

                def GetIfOneTypeCheck():
                    if (scene.static_export
                            or scene.static_collection_export
                            or scene.skeletal_export
                            or scene.anin_export
                            or scene.alembic_export
                            or scene.camera_export):
                        return True
                    else:
                        return False

                if not bfu_basics.CheckPluginIsActivated("io_scene_fbx"):
                    self.report(
                        {'WARNING'},
                        'Add-on FBX format is not activated!' +
                        ' Edit > Preferences > Add-ons > And check "FBX format"')
                    return False

                if not GetIfOneTypeCheck():
                    self.report(
                        {'WARNING'},
                        "No asset type is checked.")
                    return False

                if not len(bfu_utils.GetFinalAssetToExport()) > 0:
                    self.report(
                        {'WARNING'},
                        "Not found assets with" +
                        " \"Export recursive\" properties " +
                        "or collection to export.")
                    return False

                if not bpy.data.is_saved:
                    # Primary check	if file is saved
                    # to avoid windows PermissionError
                    self.report(
                        {'WARNING'},
                        "Please save this .blend file before export.")
                    return False

                if bbpl.scene_utils.is_tweak_mode():
                    # Need exit Tweakmode because the Animation data is read only.
                    self.report(
                        {'WARNING'},
                        "Exit Tweakmode in NLA Editor. [Tab]")
                    return False

                return True

            if not isReadyForExport():
                return {'FINISHED'}

            scene.UnrealExportedAssetsList.clear()
            counter = bps.utils.CounterTimer()
            bfu_check_potential_error.UpdateNameHierarchy()
            bfu_export_asset.ExportForUnrealEngine(self)
            bfu_write_text.WriteAllTextFiles()

            self.report(
                {'INFO'},
                "Export of " +
                str(len(scene.UnrealExportedAssetsList)) +
                " asset(s) has been finalized in " +
                str(round(counter.get_time(), 2)) +
                "seconds. Look in console for more info.")
            print(
                "=========================" +
                " Exported asset(s) " +
                "=========================")
            print("")
            lines = bfu_write_text.WriteExportLog().splitlines()
            for line in lines:
                print(line)
            print("")
            print(
                "=========================" +
                " ... " +
                "=========================")

            return {'FINISHED'}

    class BFU_OT_CopyImportAssetScriptCommand(Operator):
        bl_label = "Copy import script (Assets)"
        bl_idname = "object.copy_importassetscript_command"
        bl_description = "Copy Import Asset Script command"

        def execute(self, context):
            scene = context.scene
            bfu_basics.setWindowsClipboard(bfu_utils.GetImportAssetScriptCommand())
            self.report(
                {'INFO'},
                "command for "+scene.file_import_asset_script_name +
                " copied")
            return {'FINISHED'}

    class BFU_OT_CopyImportSequencerScriptCommand(Operator):
        bl_label = "Copy import script (Sequencer)"
        bl_idname = "object.copy_importsequencerscript_command"
        bl_description = "Copy Import Sequencer Script command"

        def execute(self, context):
            scene = context.scene
            bfu_basics.setWindowsClipboard(bfu_utils.GetImportSequencerScriptCommand())
            self.report(
                {'INFO'},
                "command for "+scene.file_import_sequencer_script_name +
                " copied")
            return {'FINISHED'}

    # Categories :
    bpy.types.Scene.static_export = bpy.props.BoolProperty(
        name="StaticMesh(s)",
        description="Check mark to export StaticMesh(s)",
        default=True
        )

    bpy.types.Scene.static_collection_export = bpy.props.BoolProperty(
        name="Collection(s) ",
        description="Check mark to export Collection(s)",
        default=True
        )

    bpy.types.Scene.skeletal_export = bpy.props.BoolProperty(
        name="SkeletalMesh(s)",
        description="Check mark to export SkeletalMesh(s)",
        default=True
        )

    bpy.types.Scene.anin_export = bpy.props.BoolProperty(
        name="Animation(s)",
        description="Check mark to export Animation(s)",
        default=True
        )

    bpy.types.Scene.alembic_export = bpy.props.BoolProperty(
        name="Alembic animation(s)",
        description="Check mark to export Alembic animation(s)",
        default=True
        )

    bpy.types.Scene.camera_export = bpy.props.BoolProperty(
        name="Camera(s)",
        description="Check mark to export Camera(s)",
        default=True
        )

    # Additional file
    bpy.types.Scene.text_ExportLog = bpy.props.BoolProperty(
        name="Export Log",
        description="Check mark to write export log file",
        default=True
        )

    bpy.types.Scene.text_ImportAssetScript = bpy.props.BoolProperty(
        name="Import assets script",
        description="Check mark to write import asset script file",
        default=True
        )

    bpy.types.Scene.text_ImportSequenceScript = bpy.props.BoolProperty(
        name="Import sequence script",
        description="Check mark to write import sequencer script file",
        default=True
        )

    bpy.types.Scene.text_AdditionalData = bpy.props.BoolProperty(
        name="Additional data",
        description=(
            "Check mark to write additional data" +
            " like parameter or anim tracks"),
        default=True
        )

    # exportProperty
    bpy.types.Scene.bfu_export_selection_filter = bpy.props.EnumProperty(
        name="Selection filter",
        items=[
            ('default', "No Filter", "Export as normal all objects with the recursive export option.", 0),
            ('only_object', "Only selected", "Export only the selected object(s)", 1),
            ('only_object_action', "Only selected and active action",
                "Export only the selected object(s) and active action on this object", 2),
            ],
        description=(
            "Choose what need be export from asset list."),
        default="default"
        )

    def draw(self, context):
        scene = context.scene
        scene = context.scene
        addon_prefs = bfu_basics.GetAddonPrefs()

        # Categories :
        layout = self.layout

        # Presets
        row = self.layout.row(align=True)
        row.menu('BFU_MT_NomenclaturePresets', text='Export Presets')
        row.operator('object.add_nomenclature_preset', text='', icon='ADD')
        row.operator(
            'object.add_nomenclature_preset',
            text='',
            icon='REMOVE').remove_active = True

        bfu_ui_utils.LayoutSection(layout, "bfu_nomenclature_properties_expanded", "Nomenclature")
        if scene.bfu_nomenclature_properties_expanded:

            # Prefix
            propsPrefix = self.layout.row()
            propsPrefix = propsPrefix.column()
            propsPrefix.prop(scene, 'static_mesh_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'skeletal_mesh_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'skeleton_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'alembic_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'anim_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'pose_prefix_export_name', icon='OBJECT_DATA')
            propsPrefix.prop(scene, 'camera_prefix_export_name', icon='OBJECT_DATA')

            # Sub folder
            propsSub = self.layout.row()
            propsSub = propsSub.column()
            propsSub.prop(scene, 'anim_subfolder_name', icon='FILE_FOLDER')

            if addon_prefs.useGeneratedScripts:
                unreal_import_module = propsSub.column()
                unreal_import_module.prop(
                    scene,
                    'unreal_import_module',
                    icon='FILE_FOLDER')
                unreal_import_location = propsSub.column()
                unreal_import_location.prop(
                    scene,
                    'unreal_import_location',
                    icon='FILE_FOLDER')

            # File path
            filePath = self.layout.row()
            filePath = filePath.column()
            filePath.prop(scene, 'export_static_file_path')
            filePath.prop(scene, 'export_skeletal_file_path')
            filePath.prop(scene, 'export_alembic_file_path')
            filePath.prop(scene, 'export_camera_file_path')
            filePath.prop(scene, 'export_other_file_path')

            # File name
            fileName = self.layout.row()
            fileName = fileName.column()
            fileName.prop(scene, 'file_export_log_name', icon='FILE')
            if addon_prefs.useGeneratedScripts:
                fileName.prop(
                    scene,
                    'file_import_asset_script_name',
                    icon='FILE')
                fileName.prop(
                    scene,
                    'file_import_sequencer_script_name',
                    icon='FILE')

        bfu_ui_utils.LayoutSection(layout, "bfu_export_filter_properties_expanded", "Export filters")
        if scene.bfu_export_filter_properties_expanded:

            # Assets
            row = layout.row()
            col = row.column()
            AssetsCol = row.column()
            AssetsCol.label(text="Asset types to export", icon='PACKAGE')
            AssetsCol.prop(scene, 'static_export')
            AssetsCol.prop(scene, 'static_collection_export')
            AssetsCol.prop(scene, 'skeletal_export')
            AssetsCol.prop(scene, 'anin_export')
            AssetsCol.prop(scene, 'alembic_export')
            AssetsCol.prop(scene, 'camera_export')
            layout.separator()

            # Additional file
            FileCol = row.column()
            FileCol.label(text="Additional file", icon='PACKAGE')
            FileCol.prop(scene, 'text_ExportLog')
            FileCol.prop(scene, 'text_ImportAssetScript')
            FileCol.prop(scene, 'text_ImportSequenceScript')
            if addon_prefs.useGeneratedScripts:
                FileCol.prop(scene, 'text_AdditionalData')

            # exportProperty
            export_by_select = layout.row()
            export_by_select.prop(scene, 'bfu_export_selection_filter')

        bfu_ui_utils.LayoutSection(layout, "bfu_export_process_properties_expanded", "Export process")
        if scene.bfu_export_process_properties_expanded:

            # Feedback info :
            AssetNum = len(bfu_utils.GetFinalAssetToExport())
            AssetInfo = layout.row().box().split(factor=0.75)
            AssetFeedback = str(AssetNum) + " Asset(s) will be exported."
            AssetInfo.label(text=AssetFeedback, icon='INFO')
            AssetInfo.operator("object.showasset")

            # Export button :
            checkButton = layout.row(align=True)
            checkButton.operator("object.checkpotentialerror", icon='FILE_TICK')
            checkButton.operator("object.openpotentialerror", icon='LOOP_BACK', text="")

            exportButton = layout.row()
            exportButton.scale_y = 2.0
            exportButton.operator("object.exportforunreal", icon='EXPORT')

        bfu_ui_utils.LayoutSection(layout, "bfu_script_tool_expanded", "Copy Import Script")
        if scene.bfu_script_tool_expanded:
            if addon_prefs.useGeneratedScripts:
                copyButton = layout.row()
                copyButton.operator("object.copy_importassetscript_command")
                copyButton.operator("object.copy_importsequencerscript_command")
                layout.label(text="Click on one of the buttons to copy the import command.", icon='INFO')
                layout.label(text="Then paste it into the cmd console of unreal.")
                layout.label(text="You need activate python plugins in Unreal Engine.")

            else:
                layout.label(text='(Generated scripts are deactivated.)')


class BFU_PT_CorrectAndImprov(bpy.types.Panel):
    # Is Clipboard panel

    bl_idname = "BFU_PT_CorrectAndImprov"
    bl_label = "Correct and improv"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Unreal Engine 4 bis"
    bl_parent_id = "BFU_PT_BlenderForUnrealObject"

    class BFU_OT_CorrectExtremUV(Operator):
        bl_label = "Correct extrem UV For Unreal"
        bl_idname = "object.correct_extrem_uv"
        bl_description = (
            "Correct extrem UV island of the selected object" +
            " for better use in real time engines"
            )
        bl_options = {'REGISTER', 'UNDO'}

        stepScale: bpy.props.IntProperty(
            name="Step scale",
            default=2,
            min=1,
            max=100)

        def execute(self, context):
            if bpy.context.active_object.mode == "EDIT":
                bfu_utils.CorrectExtremeUV(stepScale=self.stepScale)
                self.report(
                    {'INFO'},
                    "UV corrected!")
            else:
                self.report(
                    {'WARNING'},
                    "Move to Edit mode for correct extrem UV.")
            return {'FINISHED'}


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

    BFU_PT_BlenderForUnrealTool,
    BFU_PT_BlenderForUnrealTool.BFU_OT_CopyRegularCamerasButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_CopyCineCamerasButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToCollisionButtonBox,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToCollisionButtonCapsule,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToCollisionButtonSphere,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToCollisionButtonConvex,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToStaticSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ConvertToSkeletalSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_CopySkeletalSocketButton,
    BFU_PT_BlenderForUnrealTool.BFU_OT_ComputAllLightMap,

    # BFU_PT_BlenderForUnrealDebug, # Unhide for dev

    BFU_PT_Export,
    BFU_PT_Export.BFU_MT_NomenclaturePresets,
    BFU_PT_Export.BFU_OT_AddNomenclaturePreset,
    BFU_PT_Export.BFU_OT_ShowAssetToExport,
    BFU_PT_Export.BFU_OT_CheckPotentialErrorPopup,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup.BFU_OT_FixitTarget,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectObjectButton,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectVertexButton,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup.BFU_OT_SelectPoseBoneButton,
    BFU_PT_Export.BFU_OT_OpenPotentialErrorPopup.BFU_OT_OpenPotentialErrorDocs,
    BFU_PT_Export.BFU_OT_ExportForUnrealEngineButton,
    BFU_PT_Export.BFU_OT_CopyImportAssetScriptCommand,
    BFU_PT_Export.BFU_OT_CopyImportSequencerScriptCommand,

    BFU_PT_CorrectAndImprov.BFU_OT_CorrectExtremUV
)


def menu_func(self, context):
    layout = self.layout
    col = layout.column()
    col.separator(factor=1.0)
    col.operator(BFU_PT_CorrectAndImprov.BFU_OT_CorrectExtremUV.bl_idname)


def register():
    """
    Register.
    """
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

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

    bpy.types.VIEW3D_MT_uv_map.append(menu_func)


def unregister():
    """
    unregister.
    """
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    bpy.utils.unregister_class(BFU_OT_ObjExportAction)
    bpy.utils.unregister_class(BFU_OT_SceneCollectionExport)

    bpy.types.VIEW3D_MT_uv_map.remove(menu_func)
