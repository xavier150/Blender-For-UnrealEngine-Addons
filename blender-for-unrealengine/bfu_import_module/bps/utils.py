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

import time

class CounterTimer():
    """
    A simple timer.
    """

    def __init__(self):
        """
        Initialize the CounterTimer.
        """
        self.start = time.perf_counter()

    def reset_time(self):
        """
        Reset the timer.
        """
        self.start = time.perf_counter()

    def get_time(self):
        """
        Get the elapsed time since the timer started.

        Returns:
            float: Elapsed time in seconds.
        """
        return time.perf_counter() - self.start
        
    def get_str_time(self):
        """
        Get the elapsed str time since the timer started.

        Returns:
            str: Elapsed time formatted as a string.
        """
        elapsed_time = self.get_time()
        if elapsed_time < 60:
            return f"{elapsed_time:.2f} secondes"
        elif elapsed_time < 3600:
            minutes, seconds = divmod(elapsed_time, 60)
            return f"{int(minutes)} minutes et {seconds:.2f} secondes"
        else:
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{int(hours)} heures, {int(minutes)} minutes et {seconds:.2f} secondes"
        
def format_property_name(name):
    """
    Formats a property name from snake_case to Title Case and replaces underscores with spaces.
    
    Parameters:
    name (str): The property name in snake_case.
    
    Returns:
    str: The formatted property name in Title Case with spaces.
    """
    # Split the name at underscores, capitalize each part, and join them with spaces
    formatted_name = ' '.join(word.capitalize() for word in name.split('_'))
    return formatted_name