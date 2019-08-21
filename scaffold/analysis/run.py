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
Docstring for run
"""

try:
    from pathlib import Path
    Path().expanduser()
except (ImportError, AttributeError):
    from pathlib2 import Path

import acquire

BASE_FOLDER = Path('../')
if not BASE_FOLDER.is_absolute():
    BASE_FOLDER = Path.cwd().joinpath(BASE_FOLDER)
BASE_FOLDER = BASE_FOLDER.resolve()
OUT_FOLDER = BASE_FOLDER / 'plots'

SOURCES = [#('full', acquire.IQDataSet),
           #('crop', acquire.IQDataSet),
           #('adidac.5', acquire.CSVDataSet),
           #('adidac.5.bindump', acquire.CSVBinDump),
           # ('tidac.1', acquire.CSVDataSet),
           # ('tidac.1.bindump', acquire.CSVBinDump),
           #('preship', acquire.CSVDataSet),
           # ('preship.bindump', acquire.CSVBinDump),
           # ('olddac.0', acquire.CSVDataSet),
           # ('olddac.0.bindump', acquire.CSVBinDump),
            ('nvm.prelim', acquire.CSVDataSet)
           ]


def main():
    print("Using data from {0}".format(BASE_FOLDER / 'data'))
    for waveform in acquire.all_waveforms(BASE_FOLDER / 'data', SOURCES):
        waveform.process_waveform()
        print("Rendering plots for {0}".format(waveform.name))
        waveform.render_plots(OUT_FOLDER)


if __name__ == '__main__':
    main()
