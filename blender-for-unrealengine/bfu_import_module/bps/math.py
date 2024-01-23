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


def next_power_of_two(n):
    """
    Computes the next power of two that is greater than or equal to n.

    Args:
        n (int): The input number.

    Returns:
        int: The next power of two greater than or equal to n.
    """
    # decrement n (to handle cases when n itself
    # is a power of 2)
    n = n - 1

    # do till only one bit is left
    while n & n - 1:
        n = n & n - 1  # unset rightmost bit

    # n is now a power of two (less than n)
    return n << 1


def previous_power_of_two(n):
    """
    Computes the previous power of two that is less than or equal to n.

    Args:
        n (int): The input number.

    Returns:
        int: The previous power of two less than or equal to n.
    """
    # do till only one bit is left
    while (n & n - 1):
        n = n & n - 1		# unset rightmost bit

    # n is now a power of two (less than or equal to n)
    return n


def nearest_power_of_two(value):
    """
    Computes the nearest power of two to the given value.

    Args:
        value (int): The input value.

    Returns:
        int: The nearest power of two.
    """
    if value < 2:
        return 2

    a = previous_power_of_two(value)
    b = next_power_of_two(value)

    if value - a < b - value:
        return a
    else:
        return b
