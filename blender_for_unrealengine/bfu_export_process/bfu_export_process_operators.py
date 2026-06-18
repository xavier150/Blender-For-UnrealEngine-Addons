# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  Blender For UnrealEngine
#  https://github.com/xavier150/Blender-For-UnrealEngine-Addons
# ----------------------------------------------


import bpy
from typing import List, Set, Any
from .. import bpl
from .. import bbpl
from .. import bfu_export_nomenclature
from .. import bfu_utils
from .. import bfu_assets_manager
from ..bfu_assets_manager.bfu_asset_manager_type import AssetToSearch, AssetToExport, AssetDataSearchMode
from .. import bfu_cached_assets
from .. import bfu_check_potential_error
from .. import bfu_export
from .. import bfu_export_text_files
from .. import bfu_export_logs
from .. import bfu_export_filter
from . import bfu_export_process_utils


class BFU_OT_ExportForUnrealEngineButton(bpy.types.Operator):
    bl_label = "Export for Unreal Engine"
    bl_idname = "object.exportforunreal"
    bl_description = "Export all assets of this scene."

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        scene = context.scene
        if not scene:
            self.report({'WARNING'}, "No active scene found.")
            return {'CANCELLED'}

        def is_ready_for_export(final_asset_list_to_export: List[AssetToExport]) -> bool:

            def GetIfOneTypeCheck():
                all_assets = bfu_assets_manager.bfu_asset_manager_utils.get_all_asset_class()
                for assets in all_assets:
                    assets: bfu_assets_manager.bfu_asset_manager_type.BFU_BaseAssetClass
                    if assets.can_export_asset_type():
                        return True

                use_static_collection_export = bfu_export_filter.bfu_export_filter_props.scene_use_static_collection_export(scene)
                use_animation_export = bfu_export_filter.bfu_export_filter_props.scene_use_animation_export(scene)

                if (use_static_collection_export or use_animation_export):
                    return True
                else:
                    return False

            if not bbpl.basics.check_plugin_is_activated("io_scene_fbx"):
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


            if not len(final_asset_list_to_export) > 0:
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

        final_asset_cache = bfu_cached_assets.bfu_cached_assets_blender_class.get_final_asset_cache()
        final_asset_list_to_export = final_asset_cache.get_final_asset_list(AssetToSearch.ALL_ASSETS, AssetDataSearchMode.FULL, force_cache_update=True)

        if not is_ready_for_export(final_asset_list_to_export):
            return {'FINISHED'}

        # Clear logs before export
        bfu_export_logs.clear_all_logs()

        counter = bpl.utils.CounterTimer()
        bfu_check_potential_error.bfu_check_utils.process_general_fix()
        exported_asset_log = bfu_export.bfu_export_asset.process_export(self, final_asset_list_to_export)
        bfu_export_text_files.bfu_export_text_files_process.write_all_data_files(exported_asset_log)
        

        
        asset_list = str(len(exported_asset_log))
        report_text = f"Export of {asset_list} asset(s) has been finalized in " + counter.get_str_time() + " Look in console for more info."
        self.report({'INFO'}, report_text)

        bfu_export_process_utils.print_exported_asset_detail(exported_asset_log)

        # Clear logs after export
        bfu_export_logs.clear_all_logs()

        return {'FINISHED'}

class BFU_OT_CopyImportAssetScriptCommand(bpy.types.Operator):
    bl_label = "Copy import script (Assets)"
    bl_idname = "object.copy_importassetscript_command"
    bl_description = "Copy Import Asset Script command"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        scene = context.scene
        if not scene:
            self.report({'WARNING'}, "No active scene found.")
            return {'CANCELLED'}
    
        bbpl.basics.set_windows_clipboard(bfu_utils.get_import_asset_script_command())
        file_import_asset_script_name = bfu_export_nomenclature.bfu_export_nomenclature_props.get_file_import_asset_script_name(scene)
        self.report({'INFO'}, "command for "+file_import_asset_script_name + " copied")
        return {'FINISHED'}

class BFU_OT_CopyImportSequencerScriptCommand(bpy.types.Operator):
    bl_label = "Copy import script (Sequencer)"
    bl_idname = "object.copy_importsequencerscript_command"
    bl_description = "Copy Import Sequencer Script command"

    def execute(self, context: bpy.types.Context) -> Set[Any]:
        scene = context.scene
        if not scene:
            self.report({'WARNING'}, "No active scene found.")
            return {'CANCELLED'}

        bbpl.basics.set_windows_clipboard(bfu_utils.get_import_sequencer_script_command())
        file_import_sequencer_script_name = bfu_export_nomenclature.bfu_export_nomenclature_props.get_file_import_sequencer_script_name(scene)
        self.report({'INFO'}, "command for "+file_import_sequencer_script_name + " copied")
        return {'FINISHED'}


def get_preset_values() -> List[str]:
    preset_values: List[str] = []
    return preset_values

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
    BFU_OT_ExportForUnrealEngineButton,
    BFU_OT_CopyImportAssetScriptCommand,
    BFU_OT_CopyImportSequencerScriptCommand,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
