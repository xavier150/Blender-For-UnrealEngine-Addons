from . import edit_files

def update_export_fbx_bin(file_path, version):
    add_new_import(file_path)
    edit_files.add_quaternion_import(file_path)
    set_app_name(file_path)
    set_addon_version_name(file_path)
    add_animdata_custom_curves(file_path)
    if version > (3,6,0):
        add_num_custom_curve_values(file_path) #Not supported in Blender 3.6 <- and older
    add_set_custom_curve_for_ue(file_path)

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

def set_addon_version_name(file_path):

    search_line = '''
    from . import bl_info
    addon_ver = bl_info["version"]
    del bl_info'''

    search_line_4_0 = '''
    import addon_utils
    import sys
    addon_ver = addon_utils.module_bl_info(sys.modules[__package__])['version']'''
    
    new_line = '''
    addon_ver = (1.0.0)''' #TO DO! Need read value in bl_info in __init__.py

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

