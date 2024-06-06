from . import edit_files

def update_fbx_utils(file_path):
    add_new_import(file_path)
    
def add_new_import(file_path):
    # 4.1 and older
    search_lines1 = '''
import math
import time
'''

    content_to_add = '''import re
'''
    edit_files.add_after_lines(file_path, search_lines1, content_to_add)

    mathutils_content = '''from mathutils import Vector, Matrix
'''
    new_mathutils_content = '''from mathutils import Vector, Matrix, Quaternion
'''

    edit_files.replace_after_lines(file_path, mathutils_content, new_mathutils_content)
