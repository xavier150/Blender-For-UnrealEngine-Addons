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
import fnmatch
import math

from . import bbpl
from . import bfu_basics
from . import bfu_assets_manager
from . import bfu_utils
from . import bfu_cached_asset_list

from . import bfu_collision
from . import bfu_socket
from . import bfu_camera
from . import bfu_alembic_animation
from . import bfu_groom
from . import bfu_spline
from . import bfu_skeletal_mesh
from . import bfu_static_mesh




def process_general_fix():
    fixed_collisions = bfu_collision.bfu_collision_utils.fix_export_type_on_collision()
    fixed_collision_names = bfu_collision.bfu_collision_utils.fix_name_on_collision()
    fixed_sockets = bfu_socket.bfu_socket_utils.fix_export_type_on_socket()
    fixed_socket_names = bfu_socket.bfu_socket_utils.fix_name_on_socket()

    fix_info = {
        "Fixed Collision(s)": fixed_collisions,
        "Fixed Collision Names(s)": fixed_collision_names,
        "Fixed Socket(s)": fixed_sockets,
        "Fixed Socket Names(s)": fixed_socket_names,
    }

    return fix_info
    



def GetVertexWithZeroWeight(Armature, Mesh):
    vertices = []
    
    # Créez un ensemble des noms des os de l'armature pour une recherche plus rapide
    armature_bone_names = set(bone.name for bone in Armature.data.bones)
    
    
    for vertex in Mesh.data.vertices: #MeshVertex(bpy_struct)
        cumulateWeight = 0
        
        if vertex.groups:
            for group_elem in vertex.groups: #VertexGroupElement(bpy_struct)
                if group_elem.weight > 0:
                    group_index = group_elem.group
                    group_len = len(Mesh.vertex_groups)
                    if group_index <= group_len:
                        group = Mesh.vertex_groups[group_elem.group]
                        
                        # Utilisez l'ensemble des noms d'os pour vérifier l'appartenance à l'armature
                        if group.name in armature_bone_names:
                            cumulateWeight += group_elem.weight
        
        if cumulateWeight == 0:
            vertices.append(vertex)
    
    return vertices


def ContainsArmatureModifier(obj):
    for mod in obj.modifiers:
        if mod.type == "ARMATURE":
            return True
    return False

def GetSkeletonMeshs(obj):
    meshs = []
    if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
        childs = bfu_utils.GetExportDesiredChilds(obj)
        for child in childs:
            if child.type == "MESH":
                meshs.append(child)
    return meshs


def update_unreal_potential_error():
    # Find and reset list of all potential error in scene

    addon_prefs = bfu_basics.GetAddonPrefs()
    potential_errors = bpy.context.scene.potentialErrorList
    potential_errors.clear()

    # prepares the data to avoid unnecessary loops
    obj_to_check = []
    final_asset_cache = bfu_cached_asset_list.GetfinalAssetCache()
    final_asset_list_to_export = final_asset_cache.GetFinalAssetList()
    for Asset in final_asset_list_to_export:
        if Asset.obj in bfu_utils.GetAllobjectsByExportType("export_recursive"):
            if Asset.obj not in obj_to_check:
                obj_to_check.append(Asset.obj)
            for child in bfu_utils.GetExportDesiredChilds(Asset.obj):
                if child not in obj_to_check:
                    obj_to_check.append(child)

    mesh_type_to_check = []
    for obj in obj_to_check:
        if obj.type == 'MESH':
            mesh_type_to_check.append(obj)

    mesh_type_without_col = []  # is Mesh Type To Check Without Collision
    for obj in mesh_type_to_check:
        if not bfu_utils.CheckIsCollision(obj):
            mesh_type_without_col.append(obj)

    def check_unit_scale():
        # Check if the unit scale is equal to 0.01.
        if addon_prefs.notifyUnitScalePotentialError:
            if not bfu_utils.get_scene_unit_scale_is_close(0.01):
                str_unit_scale = str(bfu_utils.get_scene_unit_scale())
                my_po_error = potential_errors.add()
                my_po_error.name = bpy.context.scene.name
                my_po_error.type = 1
                my_po_error.text = (f'Scene "{bpy.context.scene.name}" has a Unit Scale equal to {str_unit_scale}.')
                my_po_error.text += ('\nFor Unreal, a unit scale equal to 0.01 is recommended.')
                my_po_error.text += ('\n(You can disable this potential error in the addon preferences.)')
                my_po_error.object = None
                my_po_error.correctRef = "SetUnrealUnit"
                my_po_error.correctlabel = 'Set Unreal Unit'

    def check_scene_frame_rate():
        # Check Scene Frame Rate.
        scene = bpy.context.scene
        denominator = scene.render.fps_base
        numerator = scene.render.fps

        # Ensure denominator and numerator are at least 1 and int 32
        new_denominator = max(round(denominator), 1)
        new_numerator = max(round(numerator), 1)

        if denominator != new_denominator or numerator != new_numerator:
            message = ('Frame rate denominator and numerator must be an int32 over zero.\n'
                    'Float denominator and numerator is not supported in Unreal Engine Sequencer.\n'
                    f'- Denominator: {denominator} -> {new_denominator}\n'
                    f'- Numerator: {numerator} -> {new_numerator}')

            my_po_error = potential_errors.add()
            my_po_error.name = bpy.context.scene.name
            my_po_error.type = 2
            my_po_error.text = (message)
            my_po_error.docsOcticon = 'scene-frame-rate'


    def check_obj_type():
        # Check if objects use a non-recommended type

        non_recommended_types = {"SURFACE", "META", "FONT"}
        for obj in obj_to_check:
            if obj.type in non_recommended_types:
                my_po_error = potential_errors.add()
                my_po_error.name = obj.name
                my_po_error.type = 1
                my_po_error.text = (
                    f'Object "{obj.name}" is a {obj.type}. The object of the type '
                    'SURFACE, META, and FONT is not recommended.'
                )
                my_po_error.object = obj
                my_po_error.correctRef = "ConvertToMesh"
                my_po_error.correctlabel = 'Convert to mesh'

    def check_shape_keys():
        destructive_modifiers = {"ARMATURE"}

        for obj in mesh_type_to_check:
            shape_keys = obj.data.shape_keys
            if shape_keys is not None and len(shape_keys.key_blocks) > 0:
                # Check that no modifiers is destructive for the key shapes
                for modif in obj.modifiers:
                    if modif.type in destructive_modifiers:
                        my_po_error = potential_errors.add()
                        my_po_error.name = obj.name
                        my_po_error.type = 2
                        my_po_error.object = obj
                        my_po_error.itemName = modif.name
                        my_po_error.text = (
                            f'In object "{obj.name}", the modifier "{modif.type}" '
                            f'named "{modif.name}" can destroy shape keys. '
                            'Please use only the Armature modifier with shape keys.'
                        )
                        my_po_error.correctRef = "RemoveModifier"
                        my_po_error.correctlabel = 'Remove modifier'

                # Check shape key ranges for Unreal Engine compatibility
                unreal_engine_shape_key_max = 5
                unreal_engine_shape_key_min = -5
                for key in shape_keys.key_blocks:
                    # Min check
                    if key.slider_min < unreal_engine_shape_key_min:
                        my_po_error = potential_errors.add()
                        my_po_error.name = obj.name
                        my_po_error.type = 1
                        my_po_error.object = obj
                        my_po_error.itemName = key.name
                        my_po_error.text = (
                            f'In object "{obj.name}", the shape key "{key.name}" '
                            'is out of bounds for Unreal. The minimum range must not be less than {unreal_engine_shape_key_min}.'
                        )
                        my_po_error.correctRef = "SetKeyRangeMin"
                        my_po_error.correctlabel = f'Set min range to {unreal_engine_shape_key_min}'

                    # Max check
                    if key.slider_max > unreal_engine_shape_key_max:
                        my_po_error = potential_errors.add()
                        my_po_error.name = obj.name
                        my_po_error.type = 1
                        my_po_error.object = obj
                        my_po_error.itemName = key.name
                        my_po_error.text = (
                            f'In object "{obj.name}", the shape key "{key.name}" '
                            'is out of bounds for Unreal. The maximum range must not exceed {unreal_engine_shape_key_max}.'
                        )
                        my_po_error.correctRef = "SetKeyRangeMax"
                        my_po_error.correctlabel = f'Set max range to {unreal_engine_shape_key_max}'

    def check_uv_maps():
        # Check that the objects have at least one UV map valid
        for obj in mesh_type_without_col:
            if len(obj.data.uv_layers) < 1:
                my_po_error = potential_errors.add()
                my_po_error.name = obj.name
                my_po_error.type = 1
                my_po_error.text = (f'Object "{obj.name}" does not have any UV Layer.')
                my_po_error.object = obj
                my_po_error.correctRef = "CreateUV"
                my_po_error.correctlabel = 'Create Smart UV Project'

    def check_bad_static_mesh_exported_like_skeletal_mesh():
        # Check if the correct object is defined as exportable
        for obj in mesh_type_to_check:
            for modif in obj.modifiers:
                if modif.type == "ARMATURE" and obj.bfu_export_type == "export_recursive":
                    my_po_error = potential_errors.add()
                    my_po_error.name = obj.name
                    my_po_error.type = 1
                    my_po_error.text = (
                        f'In object "{obj.name}", the modifier "{modif.type}" '
                        f'named "{modif.name}" will not be applied when exported '
                        'with StaticMesh assets.\nNote: with armature, if you want to export '
                        'objects as skeletal mesh, you need to set only the armature as '
                        'export_recursive, not the child objects.'
                    )
                    my_po_error.object = obj

    def check_armature_scale():
        # Check if the ARMATURE use the same value on all scale axes
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                if obj.scale.z != obj.scale.y or obj.scale.z != obj.scale.x:
                    my_po_error = potential_errors.add()
                    my_po_error.name = obj.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'In object "{obj.name}", the scale values are not consistent across all axes.'
                    )
                    my_po_error.text += (
                        f'\nScale x: {obj.scale.x}, y: {obj.scale.y}, z: {obj.scale.z}'
                    )
                    my_po_error.object = obj

    def check_armature_number():
        # Check if the number of ARMATURE modifiers or constraints is exactly 1
        for obj in obj_to_check:
            meshs = GetSkeletonMeshs(obj)
            for mesh in meshs:
                # Count the number of ARMATURE modifiers and constraints
                armature_modifiers = sum(1 for mod in mesh.modifiers if mod.type == "ARMATURE")
                armature_constraints = sum(1 for const in mesh.constraints if const.type == "ARMATURE")

                # Check if the total number of ARMATURE modifiers and constraints is greater than 1
                if armature_modifiers + armature_constraints > 1:
                    my_po_error = potential_errors.add()
                    my_po_error.name = mesh.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'In object "{mesh.name}", {armature_modifiers} Armature modifier(s) and '
                        f'{armature_constraints} Armature constraint(s) were found. '
                        'Please use only one Armature modifier or one Armature constraint.'
                    )
                    my_po_error.object = mesh

                # Check if no ARMATURE modifiers or constraints are found
                if armature_modifiers + armature_constraints == 0:
                    my_po_error = potential_errors.add()
                    my_po_error.name = mesh.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'In object "{mesh.name}", no Armature modifiers or constraints were found. '
                        'Please use one Armature modifier or one Armature constraint.'
                    )
                    my_po_error.object = mesh

    def check_armature_mod_data():
        # Check the parameters of ARMATURE modifiers
        for obj in mesh_type_to_check:
            for mod in obj.modifiers:
                if mod.type == "ARMATURE":
                    if mod.use_deform_preserve_volume:
                        my_po_error = potential_errors.add()
                        my_po_error.name = obj.name
                        my_po_error.type = 2
                        my_po_error.text = (
                            f'In object "{obj.name}", the ARMATURE modifier '
                            f'named "{mod.name}" has the Preserve Volume parameter set to True. '
                            'This parameter must be set to False.'
                        )
                        my_po_error.object = obj
                        my_po_error.itemName = mod.name
                        my_po_error.correctRef = "PreserveVolume"
                        my_po_error.correctlabel = 'Set Preserve Volume to False'

    def check_armature_const_data():
        # Check the parameters of ARMATURE constraints
        for obj in mesh_type_to_check:
            for const in obj.constraints:
                if const.type == "ARMATURE":
                    # TO DO.
                    pass  

    def check_armature_bone_data():
        # Check the parameters of the ARMATURE bones
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                for bone in obj.data.bones:
                    if (not obj.bfu_export_deform_only or
                            (bone.use_deform and obj.bfu_export_deform_only)):

                        if bone.bbone_segments > 1:
                            my_po_error = potential_errors.add()
                            my_po_error.name = obj.name
                            my_po_error.type = 1
                            my_po_error.text = (
                                f'In object "{obj.name}", the bone named "{bone.name}" '
                                'has the Bendy Bones / Segments parameter set to more than 1. '
                                'This parameter must be set to 1.'
                            )
                            my_po_error.text += (
                                '\nBendy bones are not supported by Unreal Engine, '
                                'so it is better to disable it if you want the same '
                                'animation preview in Unreal and Blender.'
                            )
                            my_po_error.object = obj
                            my_po_error.itemName = bone.name
                            my_po_error.selectPoseBoneButton = True
                            my_po_error.correctRef = "BoneSegments"
                            my_po_error.correctlabel = 'Set Bone Segments to 1'
                            my_po_error.docsOcticon = 'bendy-bone'

    def check_armature_valid_child():
        # Check that the skeleton has at least one valid mesh child to export
        for obj in obj_to_check:
            export_as_proxy = bfu_utils.GetExportAsProxy(obj)
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                childs = bfu_utils.GetExportDesiredChilds(obj)
                valid_child = sum(1 for child in childs if child.type == "MESH")

                if export_as_proxy and bfu_utils.GetExportProxyChild(obj) is not None:
                    valid_child += 1

                if valid_child < 1:
                    my_po_error = potential_errors.add()
                    my_po_error.name = obj.name
                    my_po_error.type = 2
                    my_po_error.text = (
                        f'Object "{obj.name}" is an Armature and does not have '
                        'any valid children.'
                    )
                    my_po_error.object = obj

    def check_armature_child_with_bone_parent():
        # Check if a mesh child is parented to a bone, which will cause import issues
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                childs = bfu_utils.GetExportDesiredChilds(obj)
                for child in childs:
                    if child.type == "MESH" and child.parent_type == 'BONE':
                        my_po_error = potential_errors.add()
                        my_po_error.name = child.name
                        my_po_error.type = 2
                        my_po_error.text = (
                            f'Object "{child.name}" uses Parent Bone to parent. '
                            '\nIf you use Parent Bone to parent your mesh to your armature, the import will fail.'
                        )
                        my_po_error.object = child
                        my_po_error.docsOcticon = 'armature-child-with-bone-parent'

    def check_armature_multiple_roots():
        # Check if the skeleton has multiple root bones
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                root_bones = bfu_utils.GetArmatureRootBones(obj)

                if len(root_bones) > 1:
                    my_po_error = potential_errors.add()
                    my_po_error.name = obj.name
                    my_po_error.type = 1
                    my_po_error.text = (
                        f'Object "{obj.name}" has multiple root bones. '
                        'Unreal only supports a single root bone.'
                    )
                    my_po_error.text += '\nA custom root bone will be added at export.'
                    my_po_error.text += f' {len(root_bones)} root bones found: '
                    my_po_error.text += ', '.join(root_bone.name for root_bone in root_bones)
                    my_po_error.object = obj

    def check_armature_no_deform_bone():
        # Check that the skeleton has at least one deform bone
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                if obj.bfu_export_deform_only:
                    has_deform_bone = any(bone.use_deform for bone in obj.data.bones)
                    if not has_deform_bone:
                        my_po_error = potential_errors.add()
                        my_po_error.name = obj.name
                        my_po_error.type = 2
                        my_po_error.text = (
                            f'Object "{obj.name}" does not have any deform bones. '
                            'Unreal will import it as a StaticMesh.'
                        )
                        my_po_error.object = obj

    def check_marker_overlay():
        # Check that there is no overlap with the markers in the scene timeline
        used_frames = []
        for marker in bpy.context.scene.timeline_markers:
            if marker.frame in used_frames:
                my_po_error = potential_errors.add()
                my_po_error.type = 2
                my_po_error.text = (
                    f'In the scene timeline, the frame "{marker.frame}" contains overlapping markers.'
                    '\nTo avoid camera conflicts in the generation of the sequencer, '
                    'you must use a maximum of one marker per frame.'
                )
            else:
                used_frames.append(marker.frame)

    def check_vertex_group_weight():
        # Check that all vertices have a weight
        for obj in obj_to_check:
            meshes = GetSkeletonMeshs(obj)
            for mesh in meshes:
                if mesh.type == "MESH" and ContainsArmatureModifier(mesh):
                    # Get vertices with zero weight
                    vertices_with_zero_weight = GetVertexWithZeroWeight(obj, mesh)
                    if vertices_with_zero_weight:
                        my_po_error = potential_errors.add()
                        my_po_error.name = mesh.name
                        my_po_error.type = 1
                        my_po_error.text = (
                            f'Object "{mesh.name}" contains {len(vertices_with_zero_weight)} '
                            'vertices with zero cumulative valid weight.'
                        )
                        my_po_error.text += (
                            '\nNote: Vertex groups must have a bone with the same name to be valid.'
                        )
                        my_po_error.object = mesh
                        my_po_error.selectVertexButton = True
                        my_po_error.selectOption = "VertexWithZeroWeight"

    def check_zero_scale_keyframe():
        # Check that animations do not use an invalid scale value
        for obj in obj_to_check:
            if bfu_skeletal_mesh.bfu_skeletal_mesh_utils.is_skeletal_mesh(obj):
                animation_asset_cache = bfu_cached_asset_list.GetAnimationAssetCache(obj)
                animations_to_export = animation_asset_cache.GetAnimationAssetList()
                for action in animations_to_export:
                    for fcurve in action.fcurves:
                        if fcurve.data_path.split(".")[-1] == "scale":
                            for key in fcurve.keyframe_points:
                                x_curve, y_curve = key.co
                                if y_curve == 0:
                                    bone_name = fcurve.data_path.split('"')[1]
                                    my_po_error = potential_errors.add()
                                    my_po_error.type = 2
                                    my_po_error.text = (
                                        f'In action "{action.name}" at frame {x_curve}, '
                                        f'the bone named "{bone_name}" has a zero value in the scale '
                                        'transform. This is invalid in Unreal.'
                                    )

    check_unit_scale()
    check_scene_frame_rate()
    check_obj_type()
    check_shape_keys()
    check_uv_maps()
    check_bad_static_mesh_exported_like_skeletal_mesh()
    check_armature_scale()
    check_armature_number()
    check_armature_mod_data()
    check_armature_const_data()
    check_armature_bone_data()
    check_armature_valid_child()
    check_armature_multiple_roots()
    check_armature_child_with_bone_parent()
    check_armature_no_deform_bone()
    check_marker_overlay()
    check_vertex_group_weight()
    check_zero_scale_keyframe()

    return potential_errors


def select_potential_error_object(errorIndex):
    # Select potential error

    bbpl.utils.safe_mode_set('OBJECT', bpy.context.active_object)
    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object

    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_viewport = False
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # show collection for select object
    for collection in bpy.data.collections:
        for ColObj in collection.objects:
            if ColObj == obj:
                bfu_basics.SetCollectionUse(collection)
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorVertex(errorIndex):
    # Select potential error
    select_potential_error_object(errorIndex)
    bbpl.utils.safe_mode_set('EDIT')

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    bbpl.utils.safe_mode_set('OBJECT')
    if error.selectOption == "VertexWithZeroWeight":
        for vertex in GetVertexWithZeroWeight(obj.parent, obj):
            vertex.select = True
    bbpl.utils.safe_mode_set('EDIT')
    bpy.ops.view3d.view_selected()
    return obj


def SelectPotentialErrorPoseBone(errorIndex):
    # Select potential error
    select_potential_error_object(errorIndex)
    bbpl.utils.safe_mode_set('POSE')

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    obj = error.object
    bone = obj.data.bones[error.itemName]

    # Make bone visible if hide in a layer
    for x, layer in enumerate(bone.layers):
        if not obj.data.layers[x] and layer:
            obj.data.layers[x] = True

    bpy.ops.pose.select_all(action='DESELECT')
    obj.data.bones.active = bone
    bone.select = True

    bpy.ops.view3d.view_selected()
    return obj


def TryToCorrectPotentialError(errorIndex):
    # Try to correct potential error

    scene = bpy.context.scene
    error = scene.potentialErrorList[errorIndex]
    global successCorrect
    successCorrect = False

    local_view_areas = bbpl.scene_utils.move_to_global_view()

    MyCurrentDataSave = bbpl.utils.UserSceneSave()
    MyCurrentDataSave.save_current_scene()

    bbpl.utils.safe_mode_set('OBJECT', MyCurrentDataSave.user_select_class.user_active)

    print("Start correct")

    def SelectObj(obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    # Correction list

    if error.correctRef == "SetUnrealUnit":
        bpy.context.scene.unit_settings.scale_length = 0.01
        successCorrect = True

    if error.correctRef == "ConvertToMesh":
        obj = error.object
        SelectObj(obj)
        bpy.ops.object.convert(target='MESH')
        successCorrect = True

    if error.correctRef == "SetKeyRangeMin":
        obj = error.object
        key = obj.data.shape_keys.key_blocks[error.itemName]
        key.slider_min = -5
        successCorrect = True

    if error.correctRef == "SetKeyRangeMax":
        obj = error.object
        key = obj.data.shape_keys.key_blocks[error.itemName]
        key.slider_max = 5
        successCorrect = True

    if error.correctRef == "CreateUV":
        obj = error.object
        SelectObj(obj)
        if bbpl.utils.safe_mode_set("EDIT", obj):
            bpy.ops.uv.smart_project()
            successCorrect = True
        else:
            successCorrect = False

    if error.correctRef == "RemoveModfier":
        obj = error.object
        mod = obj.modifiers[error.itemName]
        obj.modifiers.remove(mod)
        successCorrect = True

    if error.correctRef == "PreserveVolume":
        obj = error.object
        mod = obj.modifiers[error.itemName]
        mod.use_deform_preserve_volume = False
        successCorrect = True

    if error.correctRef == "BoneSegments":
        obj = error.object
        bone = obj.data.bones[error.itemName]
        bone.bbone_segments = 1
        successCorrect = True

    if error.correctRef == "InheritScale":
        obj = error.object
        bone = obj.data.bones[error.itemName]
        bone.use_inherit_scale = True
        successCorrect = True

    # ----------------------------------------Reset data
    MyCurrentDataSave.reset_select_by_name()
    MyCurrentDataSave.reset_scene_at_save()
    bbpl.scene_utils.move_to_local_view(local_view_areas)

    # ----------------------------------------

    if successCorrect:
        scene.potentialErrorList.remove(errorIndex)
        print("end correct, Error: " + error.correctRef)
        return "Corrected"
    print("end correct, Error not found")
    return "Correct fail"


class BFU_OT_UnrealPotentialError(bpy.types.PropertyGroup):
    type: bpy.props.IntProperty(default=0)  # 0:Info, 1:Warning, 2:Error
    object: bpy.props.PointerProperty(type=bpy.types.Object)
    ###
    selectObjectButton: bpy.props.BoolProperty(default=True)
    selectVertexButton: bpy.props.BoolProperty(default=False)
    selectPoseBoneButton: bpy.props.BoolProperty(default=False)
    ###
    selectOption: bpy.props.StringProperty(default="None")  # 0:VertexWithZeroWeight
    itemName: bpy.props.StringProperty(default="None")
    text: bpy.props.StringProperty(default="Unknown")
    correctRef: bpy.props.StringProperty(default="None")
    correctlabel: bpy.props.StringProperty(default="Fix it !")
    correctDesc: bpy.props.StringProperty(default="Correct target error")
    docsOcticon: bpy.props.StringProperty(default="None")


classes = (
    BFU_OT_UnrealPotentialError,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.potentialErrorList = bpy.props.CollectionProperty(type=BFU_OT_UnrealPotentialError)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.potentialErrorList
