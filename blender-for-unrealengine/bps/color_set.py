# ====================== BEGIN GPL LICENSE BLOCK ============================
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	 See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.	 If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#
# ======================= END GPL LICENSE BLOCK =============================

# ----------------------------------------------
#  BPS -> BleuRaven Python Script
#  BleuRaven.fr
#  XavierLoux.com
# ----------------------------------------------

# This use ANSI color codes. 
# You can found it all here -> https://gist.github.com/JBlond/2fea43a3049b38287e5e9cefc87b2124
# This file use the code of rene-d -> https://gist.github.com/rene-d/9e584a7dd2935d0f461904b9f2950007



# SGR color constants
# rene-d 2018

class Colors:
    """ ANSI color codes """

    # Color
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"

    #Style
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


@staticmethod
def black(string):
    return Colors.BLACK + string + Colors.END

@staticmethod
def red(string):
    return Colors.RED + string + Colors.END

@staticmethod
def green(string):
    return Colors.GREEN + string + Colors.END

@staticmethod
def brown(string):
    return Colors.BROWN + string + Colors.END

@staticmethod
def blue(string):
    return Colors.BLUE + string + Colors.END

@staticmethod
def purple(string):
    return Colors.PURPLE + string + Colors.END

@staticmethod
def cyan(string):
    return Colors.CYAN + string + Colors.END

@staticmethod
def light_gray(string):
    return Colors.LIGHT_GRAY + string + Colors.END

@staticmethod
def dark_gray(string):
    return Colors.DARK_GRAY + string + Colors.END

@staticmethod
def light_red(string):
    return Colors.LIGHT_RED + string + Colors.END

@staticmethod
def light_green(string):
    return Colors.LIGHT_GREEN + string + Colors.END

@staticmethod
def yellow(string):
    return Colors.YELLOW + string + Colors.END

@staticmethod
def light_blue(string):
    return Colors.LIGHT_BLUE + string + Colors.END

@staticmethod
def light_purple(string):
    return Colors.LIGHT_PURPLE + string + Colors.END

@staticmethod
def light_cyan(string):
    return Colors.LIGHT_CYAN + string + Colors.END

@staticmethod
def light_white(string):
    return Colors.LIGHT_WHITE + string + Colors.END

@staticmethod
def bold(string):
    return Colors.BOLD + string + Colors.END

@staticmethod
def faint(string):
    return Colors.FAINT + string + Colors.END

@staticmethod
def italic(string):
    return Colors.ITALIC + string + Colors.END

@staticmethod
def underline(string):
    return Colors.UNDERLINE + string + Colors.END

@staticmethod
def blink(string):
    return Colors.BLINK + string + Colors.END

@staticmethod
def negative(string):
    return Colors.NEGATIVE + string + Colors.END

@staticmethod
def crossed(string):
    return Colors.CROSSED + string + Colors.END