from . import edit_files

def update_export_fbx_bin(file_path, version, fbx_addon_version):
    add_new_import(file_path)
    edit_files.add_quaternion_import(file_path)
    set_app_name(file_path)
    set_addon_version_name(file_path, fbx_addon_version)
    add_animdata_custom_curves(file_path)
    if version > (3,6,0):
        add_num_custom_curve_values(file_path) #Not supported in Blender 3.6 <- and older
    add_set_custom_curve_for_ue(file_path)
    add_bone_correction_matrix(file_path)
    add_animation_only(file_path)

def add_new_import(file_path):
    # 4.1 and older
    search_lines1 = '''
from itertools import zip_longest
from functools import cache
'''

    # 3.5 and older
    search_lines2 = '''
from itertools import zip_longest, chain
'''

    content_to_add = '''
from .. import __package__ as parent_package
'''

    if edit_files.lines_exist(file_path, search_lines1):
        edit_files.add_after_lines(file_path, search_lines1, content_to_add)
    elif edit_files.lines_exist(file_path, search_lines2):
        edit_files.add_after_lines(file_path, search_lines2, content_to_add)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

def set_app_name(file_path):
    search_line = '''
    app_name = "Blender (stable FBX IO)"'''
    
    new_line = '''
    app_name = "Blender (Blender for UnrealEngine specialized FBX IO)"'''

    if edit_files.lines_exist(file_path, search_line):
        edit_files.replace_lines(file_path, search_line, new_line)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

def set_addon_version_name(file_path, fbx_addon_version):

    search_line = '''
    from . import bl_info
    addon_ver = bl_info["version"]
    del bl_info'''

    search_line_4_0 = '''
    import addon_utils
    import sys
    addon_ver = addon_utils.module_bl_info(sys.modules[__package__])['version']'''
    
    new_line = f'    addon_ver = {fbx_addon_version} # Blender-For-UnrealEngine edited version.' #TO DO! Need read value in bl_info in __init__.py

    if edit_files.lines_exist(file_path, search_line):
        edit_files.replace_lines(file_path, search_line, new_line)
    elif edit_files.lines_exist(file_path, search_line_4_0):
        edit_files.replace_lines(file_path, search_line_4_0, new_line)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

def add_animdata_custom_curves(file_path):
    # 4.1 and older
    search_lines_var = '''
    back_currframe = scene.frame_current
    animdata_ob = {}
    p_rots = {}'''

    var_to_add = '''
    animdata_custom_curves = {}'''

    edit_files.add_after_lines(file_path, search_lines_var, var_to_add)

    search_lines_use = '''
        p_rots[ob_obj] = rot'''

    collect_custom_values = '''
        # Collect custom values per bone
        if scene_data.settings.use_custom_props and ob_obj.is_bone:
            bid = ob_obj.bdata_pose_bone
            rna_properties = {prop.identifier for prop in bid.bl_rna.properties if prop.is_runtime}
            for curve_name in bid.keys():
                if curve_name == '_RNA_UI' or curve_name in rna_properties:
                    continue
                value = bid[curve_name]
                if isinstance(value, float):
                    animdata_custom_curves[curve_name]=(ACNW(ob_obj.key, 'CUSTOM', force_key, force_sek, (curve_name,)), bid)
                    # print("!##BONE CUSTOM", ob_obj.bdata_pose_bone.name, ob_obj.key, curve_name)
'''
    
    associate_custom_values = '''
    # Loop through the data empties to get the root object to associate the custom values
    if scene_data.settings.use_custom_props:
        for root_obj, root_key in scene_data.data_empties.items():
            ACNW = AnimationCurveNodeWrapper
            bid = bpy.data.objects[root_obj.name]
            rna_properties = {prop.identifier for prop in bid.bl_rna.properties if prop.is_runtime}
            for curve_name in bid.keys():
                if curve_name == '_RNA_UI' or curve_name in rna_properties:
                    continue
                value = bid[curve_name]
                if isinstance(value, float):
                    animdata_custom_curves[curve_name]=(ACNW(root_obj.key, 'CUSTOM', force_key, force_sek, (curve_name,)), bid)
                    # print("!##CUSTOM", bid.name, root_obj.key, curve_name)'''

    edit_files.add_after_lines(file_path, search_lines_use, collect_custom_values)
    edit_files.add_after_lines(file_path, collect_custom_values, associate_custom_values)

    search_lines_frame_values_gen = '''
            for camera in animdata_cameras_only:
                yield camera.lens
                yield camera.dof.focus_distance'''
    
    # 3.6 and older
    search_lines_frame_values_gen_3_6 = '''
        for anim_camera_lens, anim_camera_focus_distance, camera in animdata_cameras.values():
            anim_camera_lens.add_keyframe(real_currframe, (camera.lens,))
            anim_camera_focus_distance.add_keyframe(real_currframe, (camera.dof.focus_distance * 1000 * gscale,))'''
    
    # 3.1 and older
    search_lines_frame_values_gen_3_1 = '''
        for anim_camera, camera in animdata_cameras.values():
            anim_camera.add_keyframe(real_currframe, (camera.lens,))'''

    frame_values_gen = '''
            for k, v in animdata_custom_curves.items():
                # TODO: This value will not be updated when property has driver. Fix it.
                yield v[1][k]'''

    frame_values_gen_3_6 = '''
        for k, (anim_curve, value) in animdata_custom_curves.items():
            # TODO: This value will not be updated when property has driver. Fix it.
            anim_curve.add_keyframe(real_currframe, (value,))'''


    if edit_files.lines_exist(file_path, search_lines_frame_values_gen):
        edit_files.add_after_lines(file_path, search_lines_frame_values_gen, frame_values_gen)
    elif edit_files.lines_exist(file_path, search_lines_frame_values_gen_3_6):
        edit_files.add_after_lines(file_path, search_lines_frame_values_gen_3_6, frame_values_gen_3_6)
    elif edit_files.lines_exist(file_path, search_lines_frame_values_gen_3_1):
        edit_files.add_after_lines(file_path, search_lines_frame_values_gen_3_1, frame_values_gen_3_6)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

def add_num_custom_curve_values(file_path):

    search_lines_num_custom_curve_values = '''
    num_camera_values = len(animdata_cameras) * 2  # Focal length (`.lens`) and focus distance'''
        

    num_custom_curve_values = '''
    num_custom_curve_values = len(animdata_custom_curves)  # Only 1 value per custom property'''

    if edit_files.lines_exist(file_path, search_lines_num_custom_curve_values):
        edit_files.add_after_lines(file_path, search_lines_num_custom_curve_values, num_custom_curve_values)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

    search_lines_num_values_per_frame = '''
    num_values_per_frame = num_ob_values + num_shape_values + num_camera_values'''
      

    num_values_per_frame = ''' + num_custom_curve_values'''

    if edit_files.lines_exist(file_path, search_lines_num_values_per_frame):
        edit_files.add_after_lines(file_path, search_lines_num_values_per_frame, num_values_per_frame)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")


    search_lines_split_at_1 = '''split_at = [num_ob_values, num_shape_values, num_camera_values'''
    
    split_at_1 = ''', num_custom_curve_values'''

    if edit_files.lines_exist(file_path, search_lines_split_at_1):
        edit_files.add_after_lines(file_path, search_lines_split_at_1, split_at_1)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")


    search_lines_split_at_2 = '''
    split_at = np.cumsum(split_at[:-1])
    all_ob_values, all_shape_key_values, all_camera_values = np.split(all_values, split_at)'''
    
    split_at_2 = '''
    split_at = np.cumsum(split_at[:-1])
    all_ob_values, all_shape_key_values, all_camera_values, all_custom_curve_values = np.split(all_values, split_at)'''

    if edit_files.lines_exist(file_path, search_lines_split_at_2):
        edit_files.replace_lines(file_path, search_lines_split_at_2, split_at_2)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")

def add_set_custom_curve_for_ue(file_path):

    search_lines_animations_in_fbx_animations_do = '''    animations = {}'''
        

    num_custom_curve_values = '''    # Set custom animation curves for UnrealEngine.
    for (anim_custom_curve, _custom_curve_holder), custom_curve_values in zip(animdata_custom_curves.values(), all_custom_curve_values):
        anim_custom_curve.set_keyframes(real_currframes, custom_curve_values)
        # print(f"anim_custom_curve : {anim_custom_curve.fbx_gname} : {custom_curve_values}")
        all_anims.append(anim_custom_curve)

'''

    edit_files.add_before_lines(file_path, search_lines_animations_in_fbx_animations_do, num_custom_curve_values)

def add_bone_correction_matrix(file_path):

    search_lines_FBXExportSettings_before = '''        add_leaf_bones, bone_correction_matrix, bone_correction_matrix_inv,'''
        

    new_fbx_bone_vars = '''
        reverse_direction_bone_correction_matrix, reverse_direction_bone_correction_matrix_inv,
        use_ue_mannequin_bone_alignment, bone_align_matrix_dict, disable_free_scale_animation,'''

    edit_files.add_after_lines(file_path, search_lines_FBXExportSettings_before, new_fbx_bone_vars)

    search_lines_save_single = '''                secondary_bone_axis='X','''

    num_vars_in_save_single = '''
                mirror_symmetry_right_side_bones=False,
                use_ue_mannequin_bone_alignment=False,
                disable_free_scale_animation=False,'''

    edit_files.add_after_lines(file_path, search_lines_save_single, num_vars_in_save_single)

    
    search_lines_animations_in_fbx_animations_do = '''


    media_settings = FBXExportSettingsMedia('''
        

    num_custom_curve_values = '''
    
    # Calculate reverse direction bone correction matrix for UE Mannequin
    reverse_direction_bone_correction_matrix = None  # Default is None = no change
    reverse_direction_bone_correction_matrix_inv = None
    bone_align_matrix_dict = None
    if mirror_symmetry_right_side_bones:
        reverse_direction_bone_correction_matrix = Matrix.Rotation(-math.pi if secondary_bone_axis[0] == '-' else math.pi, 4, secondary_bone_axis[-1])
        if use_ue_mannequin_bone_alignment:
            import re
            PELVIS_OR_FOOT_NAME_PATTERN = re.compile(r'^(pelvis$|foot[_\.$]|ik_foot_[lr]$)', re.IGNORECASE)
            for arm_obj in [arm_obj for arm_obj in scene.objects if arm_obj.type == 'ARMATURE']:
                map = {}
                for bone in [bone for bone in arm_obj.data.bones if PELVIS_OR_FOOT_NAME_PATTERN.match(bone.name) != None]:
                    target_rot = Quaternion((1.0, 0.0, 0.0), math.radians(90.0))
                    lowerbonename = bone.name.lower()
                    if lowerbonename.startswith('foot'):
                        # To mitigate the instability caused by singularities during XYZ Euler angle transformations of the foot bones,
                        # an offset upward vector is used.
                        if lowerbonename[-1] == 'l':
                            target_rot = Quaternion((1.0, 0.0, 0.0), math.radians(90.0))
                        else:
                            target_rot = Quaternion((1.0, 0.0, 0.0), math.radians(90.0))
                    rot_mat = bone.matrix_local.to_quaternion().rotation_difference(target_rot).to_matrix().to_4x4()
                    map[bone.name] = (rot_mat, rot_mat.inverted_safe())
                if len(map) > 0:
                    if bone_align_matrix_dict == None:
                        bone_align_matrix_dict = {}
                    bone_align_matrix_dict[arm_obj.name] = map
        if bone_correction_matrix:
            reverse_direction_bone_correction_matrix = bone_correction_matrix @ reverse_direction_bone_correction_matrix
        reverse_direction_bone_correction_matrix_inv = reverse_direction_bone_correction_matrix.inverted()'''

    edit_files.add_before_lines(file_path, search_lines_animations_in_fbx_animations_do, num_custom_curve_values)

def add_animation_only(file_path):

    search_lines_use_batch_in_save = '''         use_batch_own_dir=False,'''

    animation_only = '''
         animation_only=False,'''

    edit_files.add_after_lines(file_path, search_lines_use_batch_in_save, animation_only)


    search_lines_use_visible_in_save = '''
        if use_visible:
            ctx_objects = tuple(obj for obj in ctx_objects if obj.visible_get())'''
    
    search_lines_ctx_objects_in_save = '''
            else:
                ctx_objects = context.view_layer.objects'''

    animation_only = '''
        if animation_only:
            ctx_objects = tuple(obj for obj in ctx_objects if not obj.type in BLENDER_OBJECT_TYPES_MESHLIKE)'''

    

    if edit_files.lines_exist(file_path, search_lines_use_visible_in_save):
        edit_files.add_after_lines(file_path, search_lines_use_visible_in_save, animation_only)
    elif edit_files.lines_exist(file_path, search_lines_ctx_objects_in_save):
        edit_files.add_after_lines(file_path, search_lines_ctx_objects_in_save, animation_only)
    else:
        edit_files.print_edit_error(f"Neither set of search lines were found in {file_path}")