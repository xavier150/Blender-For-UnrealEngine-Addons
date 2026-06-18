# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import bpy
from typing import Any, Set, List
from . import bfu_collision_utils
from .bfu_collision_types import CollisionShapeType

# Operators to create a collision shape from the selected mesh

class BFU_OT_CreateCollisionFromSelectionBox(bpy.types.Operator):
    bl_label = "Create Box Collision from selection (UBX)"
    bl_idname = "object.createboxcollisionfromselection"
    bl_description = ("Create a Box collision shape from the selected mesh (Box type, UBX prefix)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        created_obj = bfu_collision_utils.create_unrealengine_collision_from_selection(CollisionShapeType.BOX)
        if len(created_obj) > 0:
            self.report({'INFO'}, f"{len(created_obj)} object(s) copied and converted to Unreal Engine Box collisions.")
        else:
            self.report({'WARNING'}, "Please select at least one mesh object.")
        return {'FINISHED'}
    
class BFU_OT_CreateCollisionFromSelectionCapsule(bpy.types.Operator):
    bl_label = "Create Capsule Collision from selection (UCP)"
    bl_idname = "object.createcapsulecollisionfromselection"
    bl_description = ("Create a Capsule collision shape from the selected mesh (Capsule type, UCP prefix)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        created_obj = bfu_collision_utils.create_unrealengine_collision_from_selection(CollisionShapeType.CAPSULE)
        if len(created_obj) > 0:
            self.report({'INFO'}, f"{len(created_obj)} object(s) copied and converted to Unreal Engine Capsule collisions.")
        else:
            self.report({'WARNING'}, "Please select at least one mesh object.")
        return {'FINISHED'}
    
class BFU_OT_CreateCollisionFromSelectionSphere(bpy.types.Operator):
    bl_label = "Create Sphere Collision from selection (USP)"
    bl_idname = "object.createspherecollisionfromselection"
    bl_description = ("Create a Sphere collision shape from the selected mesh (Sphere type, USP prefix)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        created_obj = bfu_collision_utils.create_unrealengine_collision_from_selection(CollisionShapeType.SPHERE)
        if len(created_obj) > 0:
            self.report({'INFO'}, f"{len(created_obj)} object(s) copied and converted to Unreal Engine Sphere collisions.")
        else:
            self.report({'WARNING'}, "Please select at least one mesh object.")
        return {'FINISHED'}
    
class BFU_OT_CreateCollisionFromSelectionConvex(bpy.types.Operator):
    bl_label = "Create Convex Collision from selection (UCX)"
    bl_idname = "object.createconvexcollisionfromselection"
    bl_description = ("Create a Convex collision shape from the selected mesh (Convex type, UCX prefix)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        created_obj = bfu_collision_utils.create_unrealengine_collision_from_selection(CollisionShapeType.CONVEX)
        if len(created_obj) > 0:
            self.report({'INFO'}, f"{len(created_obj)} object(s) copied and converted to Unreal Engine Convex Shape collisions.")
        else:
            self.report({'WARNING'}, "Please select at least one mesh object.")
        return {'FINISHED'}


# Operators to convert selected meshes to Unreal Engine collision shapes

class BFU_OT_ConvertToCollisionButtonBox(bpy.types.Operator):
    bl_label = "Convert to Box (UBX)"
    bl_idname = "object.converttoboxcollision"
    bl_description = ("Convert selected mesh(es) to Unreal collision ready for export (Boxes type)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        converted_obj = bfu_collision_utils.convert_select_to_unrealengine_collision(CollisionShapeType.BOX)
        if len(converted_obj) > 0:
            self.report({'INFO'}, f"{len(converted_obj)} object(s) of the selection have been converted to Unreal Engine Box collisions.")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
        return {'FINISHED'}

class BFU_OT_ConvertToCollisionButtonCapsule(bpy.types.Operator):
    bl_label = "Convert to Capsule (UCP)"
    bl_idname = "object.converttocapsulecollision"
    bl_description = ("Convert selected mesh(es) to Unreal collision ready for export (Capsules type)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        converted_obj = bfu_collision_utils.convert_select_to_unrealengine_collision(CollisionShapeType.CAPSULE)
        if len(converted_obj) > 0:
            self.report({'INFO'}, f"{len(converted_obj)} object(s) of the selection have been converted to Unreal Engine Capsule collisions.")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
        return {'FINISHED'}

class BFU_OT_ConvertToCollisionButtonSphere(bpy.types.Operator):
    bl_label = "Convert to Sphere (USP)"
    bl_idname = "object.converttospherecollision"
    bl_description = ("Convert selected mesh(es) to Unreal collision ready for export (Spheres type)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        converted_obj = bfu_collision_utils.convert_select_to_unrealengine_collision(CollisionShapeType.SPHERE)
        if len(converted_obj) > 0:
            self.report({'INFO'}, f"{len(converted_obj)} object(s) of the selection have been converted to Unreal Engine Sphere collisions.")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
        return {'FINISHED'}

class BFU_OT_ConvertToCollisionButtonConvex(bpy.types.Operator):
    bl_label = "Convert to Convex Shape (UCX)"
    bl_idname = "object.converttoconvexcollision"
    bl_description = ("Convert selected mesh(es) to Unreal collision ready for export (Convex shapes type)")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        converted_obj = bfu_collision_utils.convert_select_to_unrealengine_collision(CollisionShapeType.CONVEX)
        if len(converted_obj) > 0:
            self.report({'INFO'}, f"{len(converted_obj)} object(s) of the selection have been converted to Unreal Engine Convex Shape collisions.")
        else:
            self.report({'WARNING'}, "Please select two objects. (Active object is the owner of the collision)")
        return {'FINISHED'}

# Additional operator to toggle the visibility of all collision objects in the scene

class BFU_OT_ToggleCollisionVisibility(bpy.types.Operator):
    bl_label = "Toggle Collision Visibility"
    bl_idname = "object.toggle_collision_visibility"
    bl_description = "Toggle the visibility of all collision objects in the scene"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        bfu_collision_utils.toggle_collision_visibility()
        return {'FINISHED'}

class BFU_OT_SelectCollisionFromCurrentSelection(bpy.types.Operator):
    bl_label = "Select Collision from Current Selection"
    bl_idname = "object.select_collision_from_current_selection"
    bl_description = "Select all collision objects related to the current selection"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        new_selected_objects: List[bpy.types.Object] = bfu_collision_utils.select_collision_from_current_selection()
        if len(new_selected_objects) > 0:
            self.report({'INFO'}, f"{len(new_selected_objects)} collision object(s) related to the current selection have been selected.")
        else:
            self.report({'WARNING'}, "No collision objects found related to the current selection.")
        return {'FINISHED'}

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_CreateCollisionFromSelectionBox,
    BFU_OT_CreateCollisionFromSelectionCapsule,
    BFU_OT_CreateCollisionFromSelectionSphere,
    BFU_OT_CreateCollisionFromSelectionConvex,

    BFU_OT_ConvertToCollisionButtonBox,
    BFU_OT_ConvertToCollisionButtonCapsule,
    BFU_OT_ConvertToCollisionButtonSphere,
    BFU_OT_ConvertToCollisionButtonConvex,

    BFU_OT_SelectCollisionFromCurrentSelection,
    BFU_OT_ToggleCollisionVisibility,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
