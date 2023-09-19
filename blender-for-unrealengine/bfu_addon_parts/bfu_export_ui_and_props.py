import os
import bpy

from bpy.props import (
        StringProperty,
        )

from bpy.types import (
        Operator,
        )

from ..export import bfu_export_asset
from .. import bfu_write_text
from .. import bfu_basics
from .. import bfu_utils
from .. import bfu_check_potential_error
from .. import bfu_ui_utils

from .. import bbpl
from .. import bps


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

            def draw(self):
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

# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------

classes = (
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
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
