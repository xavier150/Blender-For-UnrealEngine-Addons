# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------

import webbrowser
import bpy
from typing import TYPE_CHECKING, Tuple, Any, Set
from .bbpl.blender_layout import layout_doc_button

class BFU_AP_AddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__  # type: ignore

    bake_armature_animations: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Bake Armature animation", "interface.bake_armature_action_name"),
        description=bpy.app.translations.pgettext("Bake Armature animation for export (Export will take more time).", "tooltips.bake_armature_action_desc"),
        default=False,
        )

    add_skeleton_root_bone: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Add root bone", "interface.add_skeleton_root_bone_name"),
        description=bpy.app.translations.pgettext("Remove the armature root bone.", "tooltips.add_skeleton_root_bone_desc"),
        default=False,
        )

    skeleton_root_bone_name: bpy.props.StringProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Skeleton root bone name", "interface.skeleton_root_bone_name_name"),
        description=bpy.app.translations.pgettext("Name of the armature when exported. This is used to change the root bone name. If equal \"Armature\" Unreal Engine will remove the Armature root bone.", "tooltips.skeleton_root_bone_name_desc"),
        default="ArmatureRoot",
        )

    rescale_full_rig_at_export: bpy.props.EnumProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Rescale exported rig", "interface.rescale_full_rig_at_export_name"),
        description=bpy.app.translations.pgettext("This will rescale the full rig at the export with the all constraints.", "tooltips.rescale_full_rig_at_export_desc"),
        items=[
            ("auto",
                bpy.app.translations.pgettext("Auto", "interface.rescale_full_rig_at_export_auto_name"),
                bpy.app.translations.pgettext("Rescale only if the the Unit Scale is not = to 0.01", "tooltips.rescale_full_rig_at_export_auto_desc"),
                "SHADERFX",
                1),
            ("custom_rescale",
                bpy.app.translations.pgettext("Custom Rescale", "interface.rescale_full_rig_at_export_custom_rescale_name"),
                bpy.app.translations.pgettext("You can choose how rescale the rig at the export", "tooltips.rescale_full_rig_at_export_custom_rescale_desc"),
                "MODIFIER",
                2),
            ("dont_rescale",
                bpy.app.translations.pgettext("Dont Rescale", "interface.rescale_full_rig_at_export_dont_rescale_name"),
                bpy.app.translations.pgettext("Will not rescale the rig", "tooltips.rescale_full_rig_at_export_dont_rescale_desc"),
                "CANCEL",
                3)
            ]
        )

    new_rig_scale: bpy.props.FloatProperty(  # type: ignore
        name=bpy.app.translations.pgettext("New scale", "interface.new_rig_scale_name"),
        description=bpy.app.translations.pgettext("The new rig scale. AUTO: [New scale} = 100 * [Unit scale]", "tooltips.new_rig_scale_desc"),
        default=100,
        )

    static_sockets_add_90x: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Export StaticMesh Sockets with +90 degrees on X", "interface.static_sockets_add_90_x_name"),
        description=bpy.app.translations.pgettext("On StaticMesh the sockets are auto imported by unreal with -90 degrees on X", "tooltips.static_sockets_add_90_x_desc"),
        default=True,
        )

    rescale_sockets_at_export: bpy.props.EnumProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Rescale exported sockets", "interface.rescale_sockets_at_export_name"),
        description=bpy.app.translations.pgettext("This will rescale the all sockets at the export.", "tooltips.rescale_sockets_at_export_desc"),
        items=[
            ("auto",
                bpy.app.translations.pgettext("Auto", "interface.rescale_sockets_at_export_auto_name"),
                bpy.app.translations.pgettext("Rescale only if the the Unit Scale is not = to 0.01.", "tooltips.rescale_sockets_at_export_auto_desc"),
                "SHADERFX",
                1),
            ("custom_rescale",
                bpy.app.translations.pgettext("Custom Rescale", "interface.rescale_sockets_at_export_custom_rescale_name"),
                bpy.app.translations.pgettext("You can choose how rescale the sockets at the export.", "tooltips.rescale_sockets_at_export_custom_rescale_desc"),
                "MODIFIER",
                2),
            ("dont_rescale",
                bpy.app.translations.pgettext("Dont Rescale", "interface.rescale_sockets_at_export_dont_rescale_name"),
                bpy.app.translations.pgettext("Will not rescale the sockets. AUTO: 1 ([New scale} = 100 / [Unit scale]", "tooltips.rescale_sockets_at_export_dont_rescale_desc"),
                "CANCEL",
                3)
            ]
        )

    static_sockets_imported_size: bpy.props.FloatProperty(  # type: ignore
        name=bpy.app.translations.pgettext("StaticMesh sockets import size", "interface.static_sockets_imported_size_name"),
        description=bpy.app.translations.pgettext("ize of the socket when imported in Unreal Engine.", "tooltips.static_sockets_imported_size_desc"),
        default=1,
        )

    skeletal_sockets_imported_size: bpy.props.FloatProperty(  # type: ignore
        name=bpy.app.translations.pgettext("SkeletalMesh sockets import size", "interface.skeletal_sockets_imported_size_name"),
        description=bpy.app.translations.pgettext("Size of the socket when imported in Unreal Engine. AUTO: 1 ([New scale} = 100 / [Unit scale])", "tooltips.skeletal_sockets_imported_size_desc"),
        default=1,
        )

    ignore_nla_for_action: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Ignore NLA for Actions", "interface.ignore_nla_for_action_name"),
        description=bpy.app.translations.pgettext("This will export the action and ignore the all layer in Nonlinear Animation.", "tooltips.ignore_nla_for_action_desc"),
        default=False,
        )

    revert_export_path: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Revert all export path at each export.", "interface.revert_export_path_name"),
        description=bpy.app.translations.pgettext("will remove the folder of the all export path at each export.", "tooltips.revert_export_path_desc"),
        default=False,
        )

    show_hidden_linked_properties: bpy.props.BoolProperty(  # type: ignore
        name=('Show Hidden Linked Properties'),
        description=('Show hidden linked properties. (Debug)'),
        default=False,
        )

    use_generated_scripts: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Use generated script for import assets and sequencer.", "interface.use_generated_scripts_name"),
        description=bpy.app.translations.pgettext("If false the all properties that only works with import scripts will be disabled.", "tooltips.use_generated_scripts_desc"),
        default=True,
        )

    collision_color:  bpy.props.FloatVectorProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Collision color", "interface.collision_color_name"),
        description=bpy.app.translations.pgettext("Color of the collision in Blender.", "tooltips.collision_color_desc"),
        subtype='COLOR',
        size=4,
        default=(0, 0.6, 0, 0.11),
        min=0.0, max=1.0,
        )

    notify_unit_scale_potential_error: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Notify UnitScale in potential error check", "interface.notify_unit_scale_potential_error_name"),
        description=bpy.app.translations.pgettext("Notify as potential error if the unit scale is not equal to 0.01.", "tooltips.notify_unit_scale_potential_error_desc"),
        default=True,
        )
    
    #CAMERA

    bake_only_key_visible_in_cut: bpy.props.BoolProperty(  # type: ignore
        name=bpy.app.translations.pgettext("Bake Only Visible Cuts", "interface.bake_only_key_visible_in_cut_name"),
        description=bpy.app.translations.pgettext("Bake camera only when visible in camera cuts.", "tooltips.bake_only_key_visible_in_cut_desc"),
        default=True,
        )
    
    scale_camera_fstop_with_unit_scale: bpy.props.BoolProperty(  # type: ignore
        name="Scale F-Stop by Unit Scale",
        description="Scale camera F-Stop with Unit Scale.",
        default=True,
        )
    
    scale_camera_focus_distance_with_unit_scale: bpy.props.BoolProperty(  # type: ignore
        name="Scale focus distance by Unit Scale",
        description="Scale camera focus distance with Unit Scale.",
        default=True,
        )
    
    if TYPE_CHECKING:
        bake_armature_animations: bool
        add_skeleton_root_bone: bool
        skeleton_root_bone_name: str        
        rescale_full_rig_at_export: str
        new_rig_scale: float
        static_sockets_add_90x: bool
        rescale_sockets_at_export: str
        static_sockets_imported_size: float
        skeletal_sockets_imported_size: float
        ignore_nla_for_action: bool
        revert_export_path: bool
        show_hidden_linked_properties: bool
        use_generated_scripts: bool
        collision_color: Tuple[float, float, float, float]
        notify_unit_scale_potential_error: bool
        bake_only_key_visible_in_cut: bool
        scale_camera_fstop_with_unit_scale: bool
        scale_camera_focus_distance_with_unit_scale: bool

    
    class BFU_OT_NewReleaseInfo(bpy.types.Operator):
        bl_label = "Open Latest Release Page"
        bl_idname = "object.open_latest_release_page"
        bl_description = "Click to open the latest release page."

        release_url: str = "https://github.com/xavier150/Blender-For-UnrealEngine-Addons/releases/latest"

        def execute(self, context: bpy.types.Context) -> Set[Any]:
            webbrowser.open(self.release_url)
            return {'FINISHED'}

    def draw(self, context: bpy.types.Context):
        layout: bpy.types.UILayout = self.layout

        boxColumn = layout.column().split(
            factor=0.5
            )
        ColumnLeft = boxColumn.column()
        ColumnRight = boxColumn.column()

        rootBone = ColumnLeft.box()

        layout_doc_button.add_right_doc_page_operator(rootBone, text="SKELETON & ROOT BONE", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Skeleton-&-Root-bone")
        rootBone.prop(self, "add_skeleton_root_bone")  # type: ignore
        rootBoneName = rootBone.column()
        rootBoneName.enabled = self.add_skeleton_root_bone
        rootBoneName.prop(self, "skeleton_root_bone_name")

        rootBone.prop(self, "rescale_full_rig_at_export")  # type: ignore
        new_rig_scale_ui = rootBone.column()
        new_rig_scale_ui.enabled = self.rescale_full_rig_at_export == "custom_rescale"
        new_rig_scale_ui.prop(self, "new_rig_scale")  # type: ignore

        socket = ColumnLeft.box()
        socket.label(text='SOCKET')  # type: ignore
        socket.prop(self, "static_sockets_add_90x")  # type: ignore
        socket.prop(self, "rescale_sockets_at_export")  # type: ignore
        socket_rescale_ui = socket.column()
        socket_rescale_ui.enabled = self.rescale_sockets_at_export == "custom_rescale"
        socket_rescale_ui.prop(self, "static_sockets_imported_size")  # type: ignore
        socket_rescale_ui.prop(self, "skeletal_sockets_imported_size")  # type: ignore

        camera = ColumnLeft.box()
        layout_doc_button.add_right_doc_page_operator(camera, text="CAMERA", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Cameras")
        camera.prop(self, "bake_only_key_visible_in_cut")  # type: ignore
        layout_doc_button.add_right_doc_page_operator(camera, text="About depth of Field -> ", url="https://github.com/xavier150/Blender-For-UnrealEngine-Addons/wiki/Camera-Depth-of-Field")
        camera.prop(self, "scale_camera_fstop_with_unit_scale")  # type: ignore
        camera.prop(self, "scale_camera_focus_distance_with_unit_scale")  # type: ignore

        data = ColumnRight.box()
        data.label(text='DATA')  # type: ignore
        data.prop(self, "ignore_nla_for_action")  # type: ignore
        data.prop(self, "bake_armature_animations")  # type: ignore
        data.prop(self, "revert_export_path")  # type: ignore

        other = ColumnRight.box()
        other.label(text='OTHER')  # type: ignore
        other.prop(self, "collision_color")  # type: ignore
        other.prop(self, "notify_unit_scale_potential_error")  # type: ignore
        other.prop(self, "show_hidden_linked_properties")  # type: ignore

        script = ColumnRight.box()
        script.label(text='IMPORT SCRIPT')  # type: ignore
        script.prop(self, "use_generated_scripts")  # type: ignore

        updateButton = layout.row()
        updateButton.scale_y = 2.0
        updateButton.operator("object.open_latest_release_page", icon="TIME")  # type: ignore


def get_addon_preferences() -> BFU_AP_AddonPreferences:
    return bpy.context.preferences.addons[__package__].preferences # type: ignore

classes = (
    BFU_AP_AddonPreferences,
    BFU_AP_AddonPreferences.BFU_OT_NewReleaseInfo,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
