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
Docstring for acquire
"""

import re
import csv
from decimal import Decimal
from scipy import signal
from bitarray import bitarray
try:
    from pathlib import Path
    Path().expanduser()
except (ImportError, AttributeError):
    from pathlib2 import Path

import render
import process


class Renderable(object):
    def __init__(self, parent, fidx):
        self.parent = parent
        self.fidx = fidx

        self._x_data = []
        self._y_data = []

        self.points = []

    @property
    def name(self):
        return '{0}.{1}'.format(self.parent.name, self.fidx)

    def process_waveform(self):
        raise NotImplementedError

    def render_plots(self, outfolder):
        raise NotImplementedError

    def _outfolder(self, outfolder):
        if not isinstance(outfolder, Path):
            outfolder = Path(outfolder)
        outfolder.mkdir(parents=True, exist_ok=True)
        return outfolder


class BinDump(Renderable):
    def __init__(self, parent, fidx):
        super(BinDump, self).__init__(parent, fidx)
        self._bit_data = None
        self._xor_data = None

    def process_waveform(self):
        self._x_data, self._y_data = map(list, zip(*self.points))
        self._xor_data = [p.tolist()[::-1] for p in self._y_data]
        self._xor_data = [[int(p[i] != p[i + 1]) for i in range(len(p) - 1)] for p in self._xor_data]
        self._xor_bit_data = list(map(list, zip(*self._xor_data)))
        self._y_data = [[int(b) for b in p.tolist()[::-1]] for p in self._y_data]
        self._bit_data = list(map(list, zip(*self._y_data)))

    def render_plots(self, outfolder):
        outfolder = self._outfolder(outfolder)

        for b in range(16):
            outpath = outfolder / (self.name + '.b{0}.png'.format(b))
            render.make_graph(outpath=str(outpath), plotdata_x=self._x_data,
                              plotdata_y=self._bit_data[b], marker=None, lw=0.5)

        for b in range(15):
            outpath = outfolder / (self.name + '.x{0}-{1}.png'.format(b, b+1))
            render.make_graph(outpath=str(outpath), plotdata_x=self._x_data,
                              plotdata_y=self._xor_bit_data[b], marker=None, lw=0.5)


class Waveform(Renderable):
    def __init__(self, parent, fidx):
        super(Waveform, self).__init__(parent, fidx)
        self.x_units = None
        self.x_title = None
        self.y_units = None
        self.y_title = None

        self._fd_data = []
        self._sd_data = []

    def process_waveform(self):
        self._x_data, self._y_data = map(list, zip(*self.points))
        self._fd_data = process.get_fd(self._y_data)
        self._sd_data = process.get_sd(self._y_data)

    def render_plots(self, outfolder):
        outfolder = self._outfolder(outfolder)

        outpath = outfolder / (self.name + '.w.png')
        render.make_graph(outpath=str(outpath), plotdata_x=self._x_data,
                          plotdata_y=self._y_data, marker='.', linestyle='None')

        outpath = outfolder / (self.name + '.fdw.png')
        render.make_graph(outpath=str(outpath),
                          plotdata_x=self._x_data[1:], plotdata_y=self._fd_data[1:],
                          color='blue')

        outpath = outfolder / (self.name + '.sdw.png')
        render.make_graph(outpath=str(outpath),
                          plotdata_x=self._x_data[2:], plotdata_y=self._sd_data[2:],
                          color='red')

        outpath = outfolder / (self.name + '.allw.png')
        render.make_multigraph(outpath=str(outpath), plotdata_x=self._x_data[2:],
                               plotdata_ys=[signal.detrend(self._y_data[2:]),
                                            self._fd_data[2:], self._sd_data[2:]],
                               colors=['black', 'blue', 'red'])

        outpath = outfolder / (self.name + '.h.png')
        render.make_histogram(outpath=str(outpath), plotdata_y=self._y_data[2:],
                              color='grey')

        outpath = outfolder / (self.name + '.fdh.png')
        render.make_histogram(outpath=str(outpath), plotdata_y=self._fd_data[2:],
                              color='blue')

        outpath = outfolder / (self.name + '.sdh.png')
        render.make_histogram(outpath=str(outpath), plotdata_y=self._sd_data[2:],
                              color='red')


class DataSet(object):
    def __init__(self, uri):
        self._uri = None
        self.uri = uri
        self._waveforms = []
        self._acquire()

    def _acquire(self):
        raise NotImplementedError

    @property
    def uri(self):
        return self._uri.as_uri()

    @uri.setter
    def uri(self, value):
        if not isinstance(value, Path):
            value = Path(value)
        self._uri = value

    @property
    def filename(self):
        return self._uri.name

    @property
    def name(self):
        return self._uri.stem

    @property
    def waveforms(self):
        return self._waveforms


class CSVDataSet(DataSet):
    def _acquire(self):
        with self._uri.open() as f:
            state = 'PRELIM'
            reader = csv.reader(f)
            for row in reader:
                row = [x.strip() for x in row]
                if not len(row):
                    continue
                if state == 'PRELIM':
                    nch = len(row) - 1
                    for i in range(nch):
                        self._waveforms.append(Waveform(self, i))
                    state = 'DATA'
                if state == 'DATA':
                    x_data = Decimal(row[0])
                    for i in range(nch):
                        y_data = float(row[i + 1])
                        self._waveforms[i].points.append((x_data, y_data))
                    continue


class CSVBinDump(DataSet):
    def _acquire(self):
        with self._uri.open() as f:
            state = 'PRELIM'
            reader = csv.reader(f)
            for row in reader:
                row = [x.strip() for x in row]
                if not len(row):
                    continue
                if state == 'PRELIM':
                    nch = len(row) - 1
                    for i in range(nch):
                        self._waveforms.append(BinDump(self, i))
                    state = 'DATA'
                if state == 'DATA':
                    x_data = Decimal(row[0])
                    for i in range(nch):
                        y_data = bitarray(row[i + 1].zfill(16))
                        self._waveforms[i].points.append((x_data, y_data))
                    continue


class IQDataSet(DataSet):
    regex_nch = re.compile(r'^channels_(?P<nch>\d+)$')
    regex_name = re.compile(r'^field_(?P<name>\S+)$')
    regex_unit = re.compile(r'^unit_(?P<unit>\S+)$')

    def _acquire(self):
        with self._uri.open() as f:
            state = 'NCH'
            reader = csv.reader(f)
            for row in reader:
                row = [x.strip() for x in row]
                if not len(row):
                    continue
                if state == 'Data':
                    x_data = Decimal(row[0])
                    for i in range(nch):
                        y_data = int(Decimal(row[i + 1]))
                        self._waveforms[i].points.append((x_data, y_data))
                    continue
                if state == 'NCH':
                    m = self.regex_nch.match(row[0])
                    if m:
                        nch = int(m.group('nch'))
                        for i in range(nch):
                            self._waveforms.append(Waveform(self, i))
                        state = 'Names'
                    continue
                if state == 'Names':
                    m = self.regex_name.match(row[0])
                    if m:
                        x_name = m.group('name')
                        for i in range(nch):
                            self._waveforms[i].x_name = x_name
                            m = self.regex_name.match(row[i + 1])
                            self._waveforms[i].y_name = m.group('name')
                        state = 'Units'
                    continue
                if state == "Units":
                    m = self.regex_unit.match(row[0])
                    if m:
                        x_unit = m.group('unit')
                        for i in range(nch):
                            self._waveforms[i].x_unit = x_unit
                            m = self.regex_unit.match(row[i + 1])
                            self._waveforms[i].y_unit = m.group('unit')
                        state = 'Data'
                    continue


def all_datasets(folder, parsers=None):
    if isinstance(parsers, list):
        for branch, parser in parsers:
            print(branch, parser)
            dfolder = folder / branch
            datafiles = list(dfolder.glob('**/*.csv'))
            for datafile in datafiles:
                yield parser(datafile)
    else:
        datafiles = list(folder.glob('**/*.csv'))
        for datafile in datafiles:
            yield parsers(datafile)


def all_waveforms(folder, parsers=None):
    for dataset in all_datasets(folder, parsers):
        for waveform in dataset.waveforms:
            yield waveform
