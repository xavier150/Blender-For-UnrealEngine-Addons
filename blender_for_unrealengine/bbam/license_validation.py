# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BBAM -> BleuRaven Blender Addon Manager
#  https://github.com/xavier150/BBAM
# ----------------------------------------------

import os
import re
import sys
from typing import List, Sequence, Set, Tuple


SPDX_LICENSE_PREFIX = "SPDX:"
SPDX_LICENSE_IDENTIFIER_PATTERN = re.compile(
    r"^[ \t]*#[ \t]*SPDX-License-Identifier:[ \t]*(?P<identifier>[^#\r\n]+?)[ \t]*$",
    re.MULTILINE,
)


def get_spdx_license_identifiers(licenses: Sequence[object]) -> Set[str]:
    identifiers: Set[str] = set()

    for license_value in licenses:
        if not isinstance(license_value, str):
            raise ValueError("Manifest licenses must be strings.")
        if not license_value.startswith(SPDX_LICENSE_PREFIX):
            raise ValueError(
                f"Manifest license '{license_value}' must start with "
                f"'{SPDX_LICENSE_PREFIX}'."
            )

        identifier = license_value[len(SPDX_LICENSE_PREFIX):].strip()
        if not identifier:
            raise ValueError("Manifest SPDX licenses must include an identifier.")
        identifiers.add(identifier)

    if not identifiers:
        raise ValueError("At least one SPDX license must be configured in the manifest.")

    return identifiers

def get_normalized_exclude_paths(exclude_paths: Sequence[object]) -> Set[str]:
    normalized_paths: Set[str] = set()

    for exclude_path in exclude_paths:
        if not isinstance(exclude_path, str):
            raise ValueError("License validation exclude paths must be strings.")

        normalized_path = os.path.normpath(exclude_path.strip())
        if not normalized_path or normalized_path == ".":
            raise ValueError("License validation exclude paths cannot be empty.")
        if (
            os.path.isabs(normalized_path)
            or normalized_path == os.pardir
            or normalized_path.startswith(os.pardir + os.sep)
        ):
            raise ValueError(
                f"License validation exclude path '{exclude_path}' "
                "must be relative to the add-on root."
            )

        normalized_paths.add(normalized_path)

    return normalized_paths

def is_path_excluded(relative_path: str, exclude_paths: Set[str]) -> bool:
    normalized_path = os.path.normpath(relative_path)
    return any(
        normalized_path == exclude_path
        or normalized_path.startswith(exclude_path + os.sep)
        for exclude_path in exclude_paths
    )

def validate_spdx_license_headers(
    addon_path: str,
    licenses: Sequence[object],
    exclude_paths: Sequence[object] = (),
    file_extensions: Tuple[str, ...] = (".py",),
) -> bool:
    try:
        expected_identifiers = get_spdx_license_identifiers(licenses)
        normalized_exclude_paths = get_normalized_exclude_paths(exclude_paths)
    except ValueError as error:
        print(f"License validation failed: {error}", file=sys.stderr)
        return False

    missing_headers: List[str] = []
    mismatched_headers: List[Tuple[str, Set[str]]] = []
    unreadable_files: List[Tuple[str, str]] = []

    for root, directories, files in os.walk(addon_path):
        directories.sort()
        directories[:] = [
            directory
            for directory in directories
            if not is_path_excluded(
                os.path.relpath(os.path.join(root, directory), addon_path),
                normalized_exclude_paths,
            )
        ]

        for filename in sorted(files):
            if not filename.endswith(file_extensions):
                continue

            file_path = os.path.join(root, filename)
            relative_path = os.path.relpath(file_path, addon_path)
            if is_path_excluded(relative_path, normalized_exclude_paths):
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as source_file:
                    content = source_file.read()
            except (OSError, UnicodeError) as error:
                unreadable_files.append((relative_path, str(error)))
                continue

            file_identifiers = {
                match.group("identifier").strip()
                for match in SPDX_LICENSE_IDENTIFIER_PATTERN.finditer(content)
            }
            if not file_identifiers:
                missing_headers.append(relative_path)
            elif file_identifiers.isdisjoint(expected_identifiers):
                mismatched_headers.append((relative_path, file_identifiers))

    if not missing_headers and not mismatched_headers and not unreadable_files:
        expected = ", ".join(sorted(expected_identifiers))
        return True

    expected = ", ".join(sorted(expected_identifiers))
    print(
        f"SPDX license validation failed. Expected one of: {expected}",
        file=sys.stderr,
    )
    for relative_path in missing_headers:
        print(
            f"  Missing 'SPDX-License-Identifier' in: {relative_path}",
            file=sys.stderr,
        )
    for relative_path, identifiers in mismatched_headers:
        actual = ", ".join(sorted(identifiers))
        print(
            f"  Unexpected SPDX license in {relative_path}: {actual}",
            file=sys.stderr,
        )
    for relative_path, error in unreadable_files:
        print(f"  Could not read {relative_path}: {error}", file=sys.stderr)

    return False