# SPDX-FileCopyrightText: Xavier Loux (BleuRaven)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# ----------------------------------------------
#  BPL -> BleuRaven Python Library
#  https://github.com/xavier150/BPL
# ----------------------------------------------

import os

def clear_console() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')