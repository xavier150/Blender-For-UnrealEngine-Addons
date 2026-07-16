# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import List, Optional, Tuple
from .bfu_collision_types import CollisionShapeType
from . import bfu_collision_mesh_shape
from . import bfu_collision_props
from .. import bfu_unreal_utils
from .. import bfu_export_control
from .. import bfu_addon_prefs
from .. import bbpl


name_for_collision_material = "UE_Collision"

def is_a_collision(obj: bpy.types.Object) -> bool:
    '''
    Return True is object is an Collision.
    https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/FBX/StaticMeshes/#collision
    '''
    prefix_list: List[str] = CollisionShapeType.get_prefix_list()

    if isinstance(obj.data, bpy.types.Mesh):
        if obj.name.startswith(tuple(prefix_list)):
            return True
    return False

def get_all_scene_collision_objs() -> List[bpy.types.Object]:
    # Get any collision objects from bpy.context.scene.objects or List if valid.
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    
    objs = scene.objects
    prefix_list: List[str] = CollisionShapeType.get_prefix_list()

    collision_objs: List[bpy.types.Object] = []
    for obj in objs:
        if isinstance(obj.data, bpy.types.Mesh):
            if obj.name.startswith(tuple(prefix_list)):
                collision_objs.append(obj)

    return collision_objs

def fix_scene_collision_export_type() -> int:
    # Corrects bad properties
    objs: List[bpy.types.Object] = get_all_scene_collision_objs()
    return fix_collision_export_type(objs)

def fix_collision_export_type(obj_list: List[bpy.types.Object]) -> int:
    # Corrects bad properties
    fixed_collisions_export = 0
    for obj in obj_list:
        if bfu_export_control.bfu_export_control_utils.is_export_self(obj):
            bfu_export_control.bfu_export_control_utils.set_auto(obj)
            fixed_collisions_export += 1
    return fixed_collisions_export

def fix_scene_collision_names() -> int:
    # Updates hierarchy names
    objs: List[bpy.types.Object] = get_all_scene_collision_objs()
    return fix_collision_names(objs)

def fix_collision_names(obj_list: List[bpy.types.Object]) -> int:
    # Updates hierarchy names
    fixed_collision_names = 0
    
    for obj in obj_list:
        for member in CollisionShapeType:
            if obj.name.startswith(member.get_unreal_engine_prefix()):
                fixed_collision_names += update_collision_names(member, [obj])
                
    return fixed_collision_names

def fix_scene_collision_materials() -> int:
    # Updates hierarchy names
    objs = get_all_scene_collision_objs()
    return fix_collision_materials(objs)

def fix_collision_materials(obj_list: List[bpy.types.Object]) -> int:
    fixed_collision_materials: int = 0

    # Force material update
    create_collision_material()

    for obj in obj_list:
        if check_need_apply_collision_material(obj):
            apply_collision_material_to_object(obj)
            fixed_collision_materials += 1
    return fixed_collision_materials

def update_collision_names(collision_shape: CollisionShapeType, obj_list: List[bpy.types.Object]) -> int:
    # Update collision names for Unreal Engine.

    update_length: int = 0
    for obj in obj_list:
        ownerObj = obj.parent

        if ownerObj is not None:
            if obj != ownerObj:

                if isinstance(obj.data, bpy.types.Mesh):
                    prefix_name: str = collision_shape.get_unreal_engine_prefix()

                    new_name = bfu_unreal_utils.generate_name_for_unreal_engine(prefix_name+ownerObj.name, obj.name)
                    if new_name != obj.name:
                        obj.name = new_name 
                        update_length += 1
    return update_length

def fix_scene_collisions() -> Tuple[int, int, int]:
    objs: List[bpy.types.Object] = get_all_scene_collision_objs()
    fixed_collisions_export = fix_collision_export_type(objs)
    fixed_collision_names = fix_collision_names(objs)
    fixed_collision_materials = fix_collision_materials(objs)
    return fixed_collisions_export, fixed_collision_names, fixed_collision_materials

def create_unrealengine_collision_from_selection(collision_shape: CollisionShapeType, selected_the_new_objects: bool = True) -> List[bpy.types.Object]:
    # Create Unreal Engine Collisions Shapes from selected objects
    if not bpy.context.selected_objects:
        print("No objects selected.")
        return []

    object_names: List[str] = [obj.name for obj in bpy.context.selected_objects]
    new_collision_objects: List[bpy.types.Object] = []
    new_collision_object_names: List[str] = create_unrealengine_collision(collision_shape, object_names)
    for name in new_collision_object_names:
        obj = bpy.data.objects.get(name)
        if obj is not None:
            new_collision_objects.append(obj)

    if len(new_collision_objects) == 0:
        print("No valid mesh object found in selection.")
        return []
    else:
        if selected_the_new_objects:
            bbpl.utils.select_specific_object_list(new_collision_objects[0], new_collision_objects)

    return new_collision_objects

def create_unrealengine_collision(collision_shape: CollisionShapeType, object_names: List[str]) -> List[str]:
    # Create Unreal Engine Collisions Shapes from object names

    # Better to use name to avoid rna loosed reference
    new_collision_object_names: List[str] = []
    for obj_name in object_names:
        obj: Optional[bpy.types.Object] = bpy.data.objects.get(obj_name)
        if obj and isinstance(obj.data, bpy.types.Mesh): # pyright: ignore[reportUnnecessaryIsInstance]
            # Create a new object
            new_obj = bpy.data.objects.new(name=obj.name + "_ColTemp", object_data=obj.data.copy())
            new_obj.parent = obj
            new_obj.matrix_world = obj.matrix_world.copy()
            new_obj.data = obj.data.copy()
            obj.users_collection[0].objects.link(new_obj) # Link in the same collection as the original object
            convert_to_unrealengine_collision(obj, [new_obj], collision_shape)
            new_collision_object_names.append(new_obj.name)

    return new_collision_object_names


def convert_select_to_unrealengine_collision(collision_shape: CollisionShapeType) -> List[bpy.types.Object]:
    # Convert selected objects to Unreal Engine Collisions Shapes

    if not bpy.context.selected_objects:
        print("No objects selected.")
        return []
    if not bpy.context.active_object:
        print("No active object found!")
        return []
    if len(bpy.context.selected_objects) < 2:
        print("Please select two objects. (Active object is the owner of the collision)")
        return []

    # Sequence to list
    return convert_to_unrealengine_collision(bpy.context.active_object, list(bpy.context.selected_objects), collision_shape)

def convert_to_unrealengine_collision(
    collision_owner: bpy.types.Object, 
    objs_to_convert: List[bpy.types.Object], 
    collision_shape: CollisionShapeType,
    apply_collision_shape_on_mesh: bool = True
) -> List[bpy.types.Object]:
    # Convert objects to Unreal Engine Collisions Shapes
    

    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")
    
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    def deselect_all_except_active() -> None:
        if bpy.context.selected_objects:
            for obj in bpy.context.selected_objects:
                if obj != bpy.context.active_object:
                    obj.select_set(False)


    converted_objs: List[bpy.types.Object] = []

    for obj in objs_to_convert:
        deselect_all_except_active()
        obj.select_set(True)
        if obj != collision_owner:

            if isinstance(obj.data, bpy.types.Mesh):

                if apply_collision_shape_on_mesh:
                    keep_original: bool = bfu_collision_props.get_scene_keep_original_geometry(scene)
                    use_world_space: bool = bfu_collision_props.get_scene_use_world_space_for_collision(scene)
                    use_pca_approximation: bool = bfu_collision_props.get_scene_use_fast_bounding_box_approximation(scene)
                    if collision_shape.value == CollisionShapeType.BOX.value:
                        # BOX collision shape need a strict Box shape
                        bfu_collision_mesh_shape.convert_to_box_shape(obj, use_world_space=use_world_space, use_pca_approximation=use_pca_approximation, keep_original=keep_original)
                    else:
                        bfu_collision_mesh_shape.convert_to_convex_hull_shape(obj, keep_original=keep_original)


                obj.modifiers.clear()
                apply_collision_material_to_object(obj)

                prefix_name: str = collision_shape.get_unreal_engine_prefix()

                if is_a_collision(obj):
                    # Update the name if needed
                    obj.name = bfu_unreal_utils.generate_name_for_unreal_engine(obj.name, obj.name)
                else:
                    # Set a new name using the owner name as reference
                    obj.name = bfu_unreal_utils.generate_name_for_unreal_engine(prefix_name+collision_owner.name, obj.name)
                obj.show_wire = True
                obj.show_transparent = True
                obj.display.show_shadows = False
                obj.display_type = 'SOLID'
                obj.color = addon_prefs.collisionColor


                saved_matrix = obj.matrix_world.copy()
                obj.parent = collision_owner
                obj.matrix_world = saved_matrix
                converted_objs.append(obj)

    deselect_all_except_active()
    for obj in objs_to_convert:
        obj.select_set(True)  # Resets previous selected object
    return converted_objs


def get_or_create_collision_material() -> bpy.types.Material:
    mat = bpy.data.materials.get(name_for_collision_material)
    if mat is None:
        mat = create_collision_material()
    return mat

def create_collision_material() -> bpy.types.Material:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    mat = bpy.data.materials.get(name_for_collision_material)
    if mat is None:
        mat = bpy.data.materials.new(name=name_for_collision_material)
    update_collision_material(mat)
    return mat

def update_collision_material(mat: bpy.types.Material) -> None:
    addon_prefs = bfu_addon_prefs.get_addon_preferences()

    # Viewport display settings
    mat.diffuse_color = addon_prefs.collisionColor
    mat.metallic = 0.0
    mat.roughness = 0.5
    mat.specular_intensity = 0.5
    
    # sets up the nodes to create a transparent material
    # with GLSL mat in Cycle
    mat.use_nodes = True
    node_tree = mat.node_tree
    if node_tree:
        nodes = node_tree.nodes

        # Clear and create the output node
        nodes.clear()
        out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (0, 0)

        # Add a mix shader node and connect it to the output
        mix = nodes.new('ShaderNodeMixShader')
        mix.location = (-200, 0)
        fac_input = mix.inputs[0]
        if isinstance(fac_input, bpy.types.NodeSocketFloatFactor):
            fac_input.default_value = addon_prefs.collisionColor[3]  # Alpha value
        node_tree.links.new(mix.outputs['Shader'], out.inputs[0])

        # Add transparent shader for Cycles use
        trans = nodes.new('ShaderNodeBsdfTransparent')
        trans.location = (-400, 100)
        node_tree.links.new(trans.outputs['BSDF'], mix.inputs[1])

        # Add diffuse and transparent shaders and connect them to the mix shader
        diff = nodes.new('ShaderNodeBsdfDiffuse')
        diff.location = (-400, -100)
        colour_input = diff.inputs[0]
        if isinstance(colour_input, bpy.types.NodeSocketColor):
            colour_input.default_value = addon_prefs.collisionColor
        node_tree.links.new(diff.outputs['BSDF'], mix.inputs[2])

def get_current_visibility_state() -> bool:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    # Get the current visibility state of all collision objects in the scene
    prefix_list: List[str] = CollisionShapeType.get_prefix_list()
    visibility_states: List[bool] = [obj.hide_viewport for obj in scene.objects if obj.name.startswith(tuple(prefix_list))]
    if not visibility_states:
        return False  # No collision objects found, default to False

    if all(visibility_states):
        return True  # All collision objects are hidden

    if not any(visibility_states):
        return False  # All collision objects are visible

    # Mixed visibility states, return False as a default
    return False

def apply_collision_material_to_objects(obj_list: List[bpy.types.Object]) -> None:
    # Apply the collision material to a List of objects
    mat = get_or_create_collision_material()
    for obj in obj_list:
        if isinstance(obj.data, bpy.types.Mesh):
            obj.data.materials.clear()
            obj.active_material_index = 0
            obj.data.materials.append(mat)

def apply_collision_material_to_object(obj: bpy.types.Object) -> None:
    if isinstance(obj.data, bpy.types.Mesh):
        obj.data.materials.clear()
        obj.active_material_index = 0
        obj.data.materials.append(get_or_create_collision_material())

def check_need_apply_collision_material(obj: bpy.types.Object) -> bool:
    # Check if the object needs to have the collision material applied
    if isinstance(obj.data, bpy.types.Mesh):
        if len(obj.data.materials) != 1:
            return True
        if obj.data.materials[0] is None:
            return True
        current_mat = obj.data.materials[0]
        if current_mat is None:
            return True
        if current_mat.name != name_for_collision_material:
            return True
    return False

def toggle_collision_visibility() -> None:
    scene = bpy.context.scene
    if scene is None:
        raise ValueError("No active scene found!")

    new_visibility: bool = not get_current_visibility_state()

    prefix_list: List[str] = CollisionShapeType.get_prefix_list()
    for obj in scene.objects:
        if isinstance(obj.data, bpy.types.Mesh):
            if obj.name.startswith(tuple(prefix_list)):
                obj.hide_viewport = new_visibility

def select_collision_from_current_selection() -> List[bpy.types.Object]:
    # Select all collision objects related to the current selection
    if not bpy.context.selected_objects:
        print("No objects selected.")
        return []

    collision_objs_to_select: List[bpy.types.Object] = []
    prefix_list: List[str] = CollisionShapeType.get_prefix_list()

    for obj in bpy.context.selected_objects:
        # Check if the object itself is a collision object
        if obj.name.startswith(tuple(prefix_list)):
            collision_objs_to_select.append(obj)
        
        # Check children for collision objects
        for child in obj.children_recursive:
            if child.name.startswith(tuple(prefix_list)):
                collision_objs_to_select.append(child)

    # Select the found collision objects
    if len(collision_objs_to_select) > 0:
        return bbpl.utils.select_specific_object_list(collision_objs_to_select[0], collision_objs_to_select)
    else:
        return []