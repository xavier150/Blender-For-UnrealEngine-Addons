# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List, Set, Dict

from . import bfu_check_list
from . import bfu_check_props
from .. import bbpl
from .. import bfu_basics

from .. import bfu_collision
from .. import bfu_socket
from .. import bfu_export_logs

def get_potential_errors() -> List[bfu_check_props.BFU_OT_UnrealPotentialError]:
    scene = bpy.context.scene
    return scene.bfu_export_potential_errors

def get_potential_issue_by_index(index: int) -> bfu_check_props.BFU_OT_UnrealPotentialError:
    scene = bpy.context.scene
    return scene.bfu_export_potential_errors[index]

def remove_potential_by_index(index: int):
    scene = bpy.context.scene
    scene.bfu_export_potential_errors.remove(index)

def clear_potential_errors():
    scene = bpy.context.scene
    scene.bfu_export_potential_errors.clear()

def process_general_fix()-> Dict[str, str]:
    time_log = bfu_export_logs.bfu_process_time_logs_utils.start_time_log("Clean before export")
    fixed_collisions_export, fixed_collision_names, fixed_collision_materials = bfu_collision.bfu_collision_utils.fix_scene_collisions()
    fixed_sockets_export, fixed_socket_names = bfu_socket.bfu_socket_utils.fix_scene_sockets()

    fix_info: Dict[str, str] = {
        "Fixed Collision(s)": str(fixed_collisions_export + fixed_collision_names + fixed_collision_materials),
        "Fixed Socket(s)": str(fixed_sockets_export + fixed_socket_names),
    }

    time_log.end_time_log()
    return fix_info

def get_vertices_with_zero_weight(Armature: bpy.types.Object, Mesh: bpy.types.Object) -> List[bpy.types.MeshVertex]:
    vertices: List[bpy.types.MeshVertex] = []

    # Create a set of armature bone names for faster lookup
    armature_bone_names: Set[str] = set(bone.name for bone in Armature.data.bones)

    for vertex in Mesh.data.vertices:  # MeshVertex(bpy_struct)
        cumulateWeight = 0

        if vertex.groups:
            for group_elem in vertex.groups:  # VertexGroupElement(bpy_struct)
                if group_elem.weight > 0:
                    group_index = group_elem.group
                    group_len = len(Mesh.vertex_groups)
                    if group_index <= group_len:
                        group = Mesh.vertex_groups[group_elem.group]
                        
                        # Use the set of bone names to check membership in the armature
                        if group.name in armature_bone_names:
                            cumulateWeight += group_elem.weight
        
        if cumulateWeight == 0:
            vertices.append(vertex)
    
    return vertices

def select_potential_issue_object(issue_index):
    # Select potential error

    bbpl.utils.safe_mode_set('OBJECT', bpy.context.active_object)
    scene = bpy.context.scene
    my_po_error = get_potential_issue_by_index(issue_index)

    obj = my_po_error.object

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

def select_potential_issue_vertices(issue_index):
    # Select potential error
    select_potential_issue_object(issue_index)
    bbpl.utils.safe_mode_set('EDIT')

    scene = bpy.context.scene
    my_po_error = get_potential_issue_by_index(issue_index)
    obj = my_po_error.object
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')

    bbpl.utils.safe_mode_set('OBJECT')
    if my_po_error.select_option == "VertexWithZeroWeight":
        for vertex in get_vertices_with_zero_weight(obj.parent, obj):
            vertex.select = True
    bbpl.utils.safe_mode_set('EDIT')
    bpy.ops.view3d.view_selected()
    return obj

def select_potential_issue_pose_bone(issue_index):
    # Select potential error
    select_potential_issue_object(issue_index)
    bbpl.utils.safe_mode_set('POSE')

    scene = bpy.context.scene
    my_po_error = get_potential_issue_by_index(issue_index)
    obj = my_po_error.object
    bone = obj.data.bones[my_po_error.item_name]

    # Make bone visible if hide in a layer
    for x, layer in enumerate(bone.layers):
        if not obj.data.layers[x] and layer:
            obj.data.layers[x] = True

    bpy.ops.pose.select_all(action='DESELECT')
    obj.data.bones.active = bone
    bone.select = True

    bpy.ops.view3d.view_selected()
    return obj

def try_to_correct_potential_issues(issue_index):
    # Try to correct potential error

    scene = bpy.context.scene
    my_po_error = get_potential_issue_by_index(issue_index)
    global success_correct
    success_correct = False

    local_view_areas = bbpl.scene_utils.move_to_global_view()

    MyCurrentDataSave = bbpl.save_data.scene_save.UserSceneSave()
    MyCurrentDataSave.save_current_scene()

    bbpl.utils.safe_mode_set('OBJECT', MyCurrentDataSave.user_select_class.user_active)

    print("Start correct")

    def SelectObj(obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

    # Correction list

    if my_po_error.correct_ref == "SetUnitScaleForFBX":
        bpy.context.scene.unit_settings.scale_length = 0.01
        success_correct = True

    if my_po_error.correct_ref == "SetUnitScaleForGLTF":
        bpy.context.scene.unit_settings.scale_length = 1.0
        success_correct = True

    if my_po_error.correct_ref == "ConvertToMesh":
        obj = my_po_error.object
        SelectObj(obj)
        bpy.ops.object.convert(target='MESH')
        success_correct = True

    if my_po_error.correct_ref == "SetKeyRangeMin":
        obj = my_po_error.object
        key = obj.data.shape_keys.key_blocks[my_po_error.item_name]
        key.slider_min = -5
        success_correct = True

    if my_po_error.correct_ref == "SetKeyRangeMax":
        obj = my_po_error.object
        key = obj.data.shape_keys.key_blocks[my_po_error.item_name]
        key.slider_max = 5
        success_correct = True

    if my_po_error.correct_ref == "CreateUV":
        obj = my_po_error.object
        SelectObj(obj)
        if bbpl.utils.safe_mode_set("EDIT", obj):
            bpy.ops.uv.smart_project()
            success_correct = True
        else:
            success_correct = False

    if my_po_error.correct_ref == "RemoveModfier":
        obj = my_po_error.object
        mod = obj.modifiers[my_po_error.item_name]
        obj.modifiers.remove(mod)
        success_correct = True

    if my_po_error.correct_ref == "PreserveVolume":
        obj = my_po_error.object
        mod = obj.modifiers[my_po_error.item_name]
        mod.use_deform_preserve_volume = False
        success_correct = True

    if my_po_error.correct_ref == "BoneSegments":
        obj = my_po_error.object
        bone = obj.data.bones[my_po_error.item_name]
        bone.bbone_segments = 1
        success_correct = True

    if my_po_error.correct_ref == "InheritScale":
        obj = my_po_error.object
        bone = obj.data.bones[my_po_error.item_name]
        bone.use_inherit_scale = True
        success_correct = True

    if my_po_error.correct_ref == "Self":
        # Call the correction method from the appropriate checker.
        # Better and need use that for all future correction methods.
        success_correct = bfu_check_list.run_issue_correction(my_po_error)


    # ----------------------------------------Reset data
    MyCurrentDataSave.reset_select(use_names = True)
    MyCurrentDataSave.reset_scene_at_save()
    bbpl.scene_utils.move_to_local_view()

    # ----------------------------------------

    if success_correct:
        print("end correct, Error: " + my_po_error.correct_ref)
        remove_potential_by_index(issue_index)
        return "Corrected"
    print("end correct, Error not found")
    return "Correct fail"





