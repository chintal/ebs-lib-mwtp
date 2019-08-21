#!/usr/bin/env python
# encoding: utf-8

# Copyright (C) 2016 Chintalagiri Shashank
#
# This file is part of libmwtp.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Docstring for process
"""


def get_fd(array):
    fdarray = []
    lpoint = 0
    for point in array:
        fdarray.append(point - lpoint)
        lpoint = point
    return fdarray


def get_sd(array):
    sdarray = []
    lpoint = 0
    lfd = 0
    for point in array:
        fd = point - lpoint
        sdarray.append(fd - lfd)
        lpoint = point
        lfd = fd
    return sdarray
