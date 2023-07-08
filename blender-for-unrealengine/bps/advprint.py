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
#  xavierloux.com
# ----------------------------------------------


import sys
import time


class ProgressionBarClass():

    def _get_name(self):
        return self.__name

    def _set_name(self, value):
        if not isinstance(value, str):
            raise TypeError("name must be set to an String")
        self.__name = value

    name = property(_get_name, _set_name)

    def _get_length(self):
        return self.__length

    def _set_length(self, value):
        if not isinstance(value, int):
            raise TypeError("length must be set to an Integer")
        self.__length = value

    length = property(_get_length, _set_length)

    previous_step = 0.0

    def _get_total_step(self):
        return self.__total_step

    def _set_total_step(self, value):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise TypeError("total_step must be set to an Integer or Float")

        self.__total_step = value

    total_step = property(_get_total_step, _set_total_step)

    # Visual
    show_block = True
    show_steps = True
    show_percentage = True

    def __init__(self):
        self.__name = "My progression bar"
        self.__length = 20  # modify this to change the length
        self.__previous_step = 0.0
        self.__total_step = 1.0  # from 0 to 1
        self.__counter_start = time.perf_counter()

    def update_progress(self, progress):
        job_title = self.__name
        length = self.__length
        total_step = self.__total_step
        self.__previous_step = progress  # Update the previous step.

        is_done = False
        if progress >= total_step:
            is_done = True

        # Write message.
        msg = "\r{0}:".format(job_title)

        if self.show_block:
            block = int(round(length*progress/total_step))
            msg += " [{0}]".format("#"*block + "-"*(length-block))

        if self.show_steps:
            msg += " {0}/{1}".format(progress, total_step)

        if is_done:
            msg += " DONE IN {0}s\r\n".format(round(time.perf_counter()-self.__counter_start, 3))

        else:
            if self.show_percentage:
                msg += " {0}%".format(round((progress*100)/total_step, 2))

        sys.stdout.write(msg)
        sys.stdout.flush()


def print_separation(number=60):
    """
    Prints a separation line consisting of '#' characters.

    Args:
        number (int, optional): The number of '#' characters in the line. Defaults to 60.
    """
    print("# {0} #".format("-" * number))


def print_title(text, number=60):
    """
    Prints a title surrounded by a line of '#' characters.

    Args:
        text (str): The text of the title.
        number (int, optional): The total number of characters in the line. Defaults to 60.
    """
    remain_number = len(text) - number - 2
    print("# {0} {1} {2} #".format("-" * remain_number, text, "-" * remain_number))
