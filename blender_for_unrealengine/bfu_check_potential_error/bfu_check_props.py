# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


from typing import TYPE_CHECKING, List

import bpy
from bpy.app.handlers import persistent


ISSUE_TYPE_LABELS = {0: "INFO", 1: "WARNING", 2: "ERROR"}


def get_preset_values() -> List[str]:
    preset_values = [
        ]
    return preset_values

class BFU_OT_UnrealPotentialError(bpy.types.PropertyGroup):
    type: bpy.props.IntProperty(default=0)  # 0:Info, 1:Warning, 2:Error  # type: ignore
    object: bpy.props.PointerProperty(type=bpy.types.Object)  # type: ignore
    ###
    select_object_button: bpy.props.BoolProperty(default=True)  # type: ignore
    select_vertex_button: bpy.props.BoolProperty(default=False)  # type: ignore
    select_pose_bone_button: bpy.props.BoolProperty(default=False)  # type: ignore
    ###
    select_option: bpy.props.StringProperty(default="None")  # 0:VertexWithZeroWeight  # type: ignore
    item_name: bpy.props.StringProperty(default="None")  # type: ignore
    text: bpy.props.StringProperty(default="Unknown")  # type: ignore
    correct_ref: bpy.props.StringProperty(default="None")  # type: ignore
    correct_label: bpy.props.StringProperty(default="Fix it !")  # type: ignore
    correct_desc: bpy.props.StringProperty(default="Correct target error")  # type: ignore
    docs_octicon: bpy.props.StringProperty(default="None")  # type: ignore

    if TYPE_CHECKING:
        type: int
        object: bpy.types.Object

        select_object_button: bool
        select_vertex_button: bool
        select_pose_bone_button: bool

        select_option: str
        item_name: str
        text: str
        correct_ref: str
        correct_label: str
        correct_desc: str
        docs_octicon: str


class BFU_PotentialErrorsByScene(bpy.types.PropertyGroup):
    errors: bpy.props.CollectionProperty(type=BFU_OT_UnrealPotentialError, options={'SKIP_SAVE'})  # type: ignore


def _scene_results():
    context = bpy.context
    results = context.window_manager.bfu_export_potential_errors
    scene_key = str(context.scene.session_uid)
    return results, scene_key


def get_scene_potential_errors():
    results, scene_key = _scene_results()
    scene_results = results.get(scene_key)
    return scene_results.errors if scene_results is not None else None


def add_scene_potential_error() -> BFU_OT_UnrealPotentialError:
    results, scene_key = _scene_results()
    scene_results = results.get(scene_key)
    if scene_results is None:
        scene_results = results.add()
        scene_results.name = scene_key
    return scene_results.errors.add()


@persistent
def clear_loaded_results(_dummy):
    # Loading without UI can reuse the existing window manager.
    for manager in bpy.data.window_managers:
        manager.property_unset("bfu_export_potential_errors")


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_UnrealPotentialError,
    BFU_PotentialErrorsByScene,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.WindowManager.bfu_export_potential_errors = bpy.props.CollectionProperty(
        type=BFU_PotentialErrorsByScene,
        options={'SKIP_SAVE'},
    )
    bpy.app.handlers.load_post.append(clear_loaded_results)


def unregister():
    bpy.app.handlers.load_post.remove(clear_loaded_results)
    clear_loaded_results(None)
    del bpy.types.WindowManager.bfu_export_potential_errors

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
