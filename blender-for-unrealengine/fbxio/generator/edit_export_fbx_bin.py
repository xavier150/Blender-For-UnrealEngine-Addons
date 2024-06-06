from . import edit_files

def update_export_fbx_bin(file_path):
    add_new_import(file_path)

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


    mathutils_content = '''from mathutils import Vector, Matrix
'''
    new_mathutils_content = '''from mathutils import Vector, Matrix, Quaternion
'''

    edit_files.replace_after_lines(file_path, mathutils_content, new_mathutils_content)

