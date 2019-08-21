# coding=utf-8
# Copyright (C) 2015-2016 Chintalagiri Shashank
#
# This file is a stripped down version of it's counterpart in Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from six.moves import xrange

import os
import numpy

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['agg.path.chunksize'] = 10000
from matplotlib import pyplot

FNULL = open(os.devnull, 'w')


def finish_graph(outpath, xscale='linear', yscale='linear',
                 xlabel='', ylabel='', ymax=None, ymin=None):
    f = pyplot.gcf()
    f.set_size_inches(8, 6)
    pyplot.xscale(xscale)
    pyplot.yscale(yscale)
    pyplot.grid(True, which='major', color='0.3', linestyle='-', linewidth=0.2)
    pyplot.grid(True, which='minor', color='0.3')
    pyplot.xlabel(xlabel, fontsize=20)
    pyplot.ylabel(ylabel, fontsize=20)
    pyplot.tick_params(axis='both', which='major', labelsize=16)
    pyplot.tick_params(axis='both', which='minor', labelsize=8)
    if (ymax, ymin) is not (None, None):
        pyplot.ylim((ymin, ymax))
    pyplot.tight_layout()
    pyplot.savefig(outpath, dpi=300)
    pyplot.close()
    return outpath


def make_graph(outpath, plotdata_y, plotdata_x=None,
               color='black', lw=1, marker=None,
               xscale='linear', yscale='linear',
               xlabel='', ylabel='', ymax=None, ymin=None,
               linestyle='-'):
    """
    Renders a graph of the data provided as a ``.png`` file, saved to the
    path specified by ``outpath``. This function uses :mod:`matplotlib.pyplot`.

    :param outpath: The path to the output file
    :type outpath: str
    :param plotdata_y: The y-axis data to plot
    :type plotdata_y: list
    :param plotdata_x: The x-axis data to plot, or None if
                       a plotdata_y is a sequence
    :type plotdata_x: :class:`list` or None
    :param color: The color of the curve, default ``black``.
                  See matplotlib docs.
    :type color: str
    :param lw: The linewidth of the curve, default ``2``.
               See matplotlib docs.
    :type lw: int
    :param marker: The marker to be used, default ``None``.
                   See matplotlib docs.
    :type marker: str
    :param xscale: The scale of the x axis, default ``linear``.
                   See matplotlib docs.
    :type xscale: str
    :param yscale: The scale of the y axis, default ``linear``.
                   See matplotlib docs.
    :type yscale: str
    :param xlabel: The x-axis label, default ``''``
    :type xlabel: str
    :param ylabel: The y-axis label, default ``''``
    :type ylabel: str
    :return: The output path.
    """
    pyplot.plot(plotdata_x, plotdata_y, color=color, lw=lw,
                marker=marker, linestyle=linestyle)
    return finish_graph(outpath, xscale, yscale, xlabel, ylabel, ymax, ymin)


def make_multigraph(outpath, plotdata_ys, plotdata_x=None,
                    colors=None, lws=None, markers=None,
                    xscale='linear', yscale='linear',
                    xlabel='', ylabel='', ymax=None, ymin=None):
    if colors is None:
        colors = ['black'] * len(plotdata_ys)
    if lws is None:
        lws = [0.7] * len(plotdata_ys)
    if markers is None:
        markers = [None] * len(plotdata_ys)
    for idx in range(len(plotdata_ys)):
        pyplot.plot(plotdata_x, plotdata_ys[idx],
                    color=colors[idx], lw=lws[idx], marker=markers[idx])
    return finish_graph(outpath, xscale, yscale, xlabel, ylabel, ymax, ymin)


def get_optimum_bins(plotdata_y):
    """
    Histogram Binwidth Optimization Method

    ::

        Shimazaki and Shinomoto, Neural Comput 19 1503-1527, 2007
        2006 Author Hideaki Shimazaki, Matlab
        Department of Physics, Kyoto University
        shimazaki at ton.scphys.kyoto-u.ac.jp

    This implementation based on the version in python
    written by Érbet Almeida Costa

    :param plotdata_y: The data for which a histogram is to be made
    :return: The optimal number of bins

    .. warning:: This function fails if the provided data lacks a proper
                 distribution, such as if there are only 4 distinct values
                 in the output. Figure out why and how to fix it. In the
                 meanwhile, specify bins manually to not let this function
                 be called.
    """

    max_p = max(plotdata_y)
    min_p = min(plotdata_y)

    n_min = 2
    n_max = 50
    n = range(n_min, n_max)

    # Number of Bins array
    n = numpy.array(n)
    # Bin Size Vector
    d = (max_p - min_p) / n

    c = numpy.zeros(shape=(numpy.size(d), 1))

    # Computation of the cost function
    for i in xrange(numpy.size(n)):
        edges = numpy.linspace(min_p, max_p, n[i]+1)  # Bin edges
        ki = pyplot.hist(plotdata_y, edges)     # Count # of events in bins
        ki = ki[0]
        k = numpy.mean(ki)                      # Mean of event count
        v = sum((ki - k) ** 2) / n[i]           # Variance of event count
        if d[i] == 0:
            c[i] = 10000
        else:
            c[i] = (2 * k - v) / ((d[i]) ** 2)  # The cost Function

    # Optimal Bin Size Selection
    cmin = min(c)
    idx = numpy.where(c == cmin)
    idx = int(idx[0])
    pyplot.close()
    return n[idx]


def make_histogram(outpath, plotdata_y, bins=None, color='red',
                   xlabel='', ylabel='', x_range=None):
    """
    Renders a histogram of the data provided as a ``.png`` file,
    saved to the path specified by ``outpath``.
    This function uses :mod:`matplotlib.pyplot`.

    .. seealso:: :func:`get_optimum_bins`

    :param outpath: The path to the output file
    :type outpath: str
    :param plotdata_y: The y-axis data to plot
    :type plotdata_y: list
    :param bins: Number of bins to use. If None, uses the optimum.
                 See matplotlib docs.
    :type bins: int or None
    :param color: The color of the curve, default ``red``.
                  See matplotlib docs.
    :type color: str
    :param xlabel: The x-axis label, default ``''``
    :type xlabel: str
    :param ylabel: The y-axis label, default ``''``
    :type ylabel: str
    :param x_range: The x-axis range, if not the default.
                    See matplotlib docs for range.
    :type x_range: tuple
    :return: The output path.
    """
    if bins is None:
        bins = get_optimum_bins(plotdata_y)
    pyplot.hist(plotdata_y, bins=bins, color=color, range=x_range)
    pyplot.grid(True, which='major', linestyle='-')
    pyplot.grid(True, which='minor')
    pyplot.xlabel(xlabel, fontsize=20)
    pyplot.ylabel(ylabel, fontsize=20)
    pyplot.tick_params(axis='both', which='major', labelsize=16)
    pyplot.tick_params(axis='both', which='minor', labelsize=8)
    pyplot.tight_layout()
    pyplot.savefig(outpath)
    pyplot.close()
    return outpath
