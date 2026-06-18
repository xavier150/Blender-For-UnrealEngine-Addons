# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import re
import subprocess
from typing import Optional, List
import sys

# Compatibility fix for Python 3.7 - subprocess type annotations
if sys.version_info >= (3, 8):
    # Python 3.8+ supports subscriptable subprocess.CompletedProcess natively
    pass
else:
    # Python 3.7 monkey patch
    _original_completed_process = subprocess.CompletedProcess
    
    class CompletedProcess:
        def __class_getitem__(cls, item):
            return _original_completed_process
    
    # Only patch if not already done (avoid reload issues)
    if not hasattr(subprocess.CompletedProcess, '__class_getitem__'):
        subprocess.CompletedProcess = CompletedProcess

def build_extension(
    src: str,
    dst: str,
    blender_executable_path: str
) -> subprocess.CompletedProcess[str]:
    """
    Builds an extension using Blender's executable with specified source and destination paths.

    Parameters:
        src (str): Path to the source directory of the extension.
        dst (str): Destination path for the built extension.
        blender_executable_path (str): Path to the Blender executable.

    Returns:
        subprocess.CompletedProcess: The result of the subprocess command execution.
    """
    command: List[str] = [
        blender_executable_path,
        '--background',
        '--factory-startup',
        '--command', 'extension', 'build',
        '--source-dir', src,
        '--output-filepath', dst,
    ]


    result = subprocess.run(command, capture_output=True, text=True)
    return result

def get_build_file(
    build_result: subprocess.CompletedProcess[str]
) -> Optional[str]:
    """
    Extracts the path of the created build file from the build result output.

    Parameters:
        build_result (subprocess.CompletedProcess): The result of the build command.

    Returns:
        str: The path of the created build file, if found; otherwise, None.
    """
    match = re.search(r'created: "([^"]+)"', build_result.stdout)
    if match:
        return match.group(1)
    return None

def validate_extension(
    path: str, 
    blender_executable_path: str
) -> subprocess.CompletedProcess[str]:
    """
    Validates the built extension using Blender's executable.

    Parameters:
        path (str): Path to the extension file to validate.
        blender_executable_path (str): Path to the Blender executable.
    """
    validate_command = [
        blender_executable_path,
        '--background',
        '--factory-startup',
        '--command', 'extension', 'validate', 
        path,
    ]

    result = subprocess.run(validate_command, capture_output=True, text=True)
    return result