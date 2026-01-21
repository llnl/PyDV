# Copyright (c) Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
# See top-level LICENSE AND COPYRIGHT files for dates and other details.
# LLNL-CODE-507071
# All rights reserved.

# This file is part of PDV.  For details, see <URL describing code and
# how to download source>. Please also read "Additional BSD Notice".

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# Redistributions of source code must retain the above copyright
# notice, this list of conditions and the disclaimer below.
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the disclaimer (as noted below)
# in the documentation and/or other materials provided with the
# distribution.  Neither the name of the LLNS/LLNL nor the names of
# its contributors may be used to endorse or promote products derived
# from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL LAWRENCE
# LIVERMORE NATIONAL SECURITY, LLC, THE U.S. DEPARTMENT OF ENERGY OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

# Additional BSD Notice

# 1. This notice is required to be provided under our contract with
# the U.S.  Department of Energy (DOE).  This work was produced at
# Lawrence Livermore National Laboratory under Contract
# No. DE-AC52-07NA27344 with the DOE.

# 2. Neither the United States Government nor Lawrence Livermore
# National Security, LLC nor any of their employees, makes any
# warranty, express or implied, or assumes any liability or
# responsibility for the accuracy, completeness, or usefulness of any
# information, apparatus, product, or process disclosed, or represents
# that its use would not infringe privately-owned rights.

# 3.  Also, reference herein to any specific commercial products,
# process, or services by trade name, trademark, manufacturer or
# otherwise does not necessarily constitute or imply its endorsement,
# recommendation, or favoring by the United States Government or
# Lawrence Livermore National Security, LLC.  The views and opinions
# of authors expressed herein do not necessarily state or reflect
# those of the United States Government or Lawrence Livermore National
# Security, LLC, and shall not be used for advertising or product
# endorsement purposes.


import json
import traceback
import sys
import re
import copy
from multiprocessing import Pool, cpu_count
import subprocess
import h5py

from distutils.version import LooseVersion

import numpy as np
import scipy
import scipy.special
import scipy.integrate
import scipy.interpolate
import scipy.ndimage

import matplotlib.pyplot as plt

try:
    from matplotlib import style
    stylesLoaded = True
except:
    stylesLoaded = False

# HPC Import
try:
    import curve

# Package Import
except ImportError:
    from pydv import curve

try:
    import pact.pdb as pdb
    pdbLoaded = True
except:
    pdbLoaded = False


def makecurve(x=np.empty(0),
              y=np.empty(0),
              name='',
              filename='',
              xlabel='',
              ylabel='',
              title='',
              record_id='',
              step=False,
              step_original_x=np.empty(0),
              step_original_y=np.empty(0),
              xticks_labels=None,
              plotname='',
              color='',
              edited=False,
              scatter=False,
              linespoints=False,
              linewidth=None,
              linestyle='-',
              drawstyle='default',
              dashes=None,
              hidden=False,
              ebar=None,
              erange=None,
              marker='.',
              markerstyle=None,
              markersize=3,
              markerfacecolor=None,
              markeredgecolor=None,
              plotprecedence=0,
              legend_show=True,
              math_interp_left=None,
              math_interp_right=None,
              math_interp_period=None):
    """
    Generate a curve from two lists of numbers.

    >>> c1 = pydvpy.makecurve([1, 2, 3, 4], [5, 10, 15, 20])

    >>> c2 = pydvpy.makecurve([1, 2, 3, 4], [7, 8, 9, 10], 'Line')

    :param x: list of x values
    :type x: list
    :param y: list of y values
    :type y: list
    :param name: the name of the new curve
    :type name: str
    :param filename: the name of the file containing this curves data.
    :type filename: str
    :param xlabel: the xlabel of the data.
    :type xlabel: str
    :param ylabel: the ylabel of the data.
    :type ylabel: str
    :param title: the title of the data.
    :type title: str
    :param record_id: the Sina record id of the data.
    :type record_id: str
    :param step: whether this is a step curve.
    :type step: bool
    :param step_original_x: list of original x values for step function
    :type step_original_x: list
    :param step_original_y: list of original y values for step function
    :type step_original_y: list
    :param xticks_labels: Dictionary of x tick labels if x data are strings.
    :type xticks_labels: dict
    :param plotname: The plot name of the curve.
    :type plotname: str
    :param color: The color of the curve.
    :type color: str
    :param edited: Internally check if curve has been edited to update on plot.
    :type edited: bool
    :param scatter: Plot this as a scatter plot.
    :type scatter: bool
    :param linespoints: Plot this as a line with point markers.
    :type linespoints: bool
    :param linewidth: The line width of the curve.
    :type linewidth: int
    :param linestyle: The line style of the curve.
    :type linestyle: str
    :param drawstyle: The draw style of the curve.
    :type drawstyle: str
    :param dashes: Line style has dashes.
    :type dashes: bool
    :param hidden: Hide curve on plot.
    :type hidden: bool
    :param ebar: The error bar of the data [y0, y1, x0, x1].
    :type ebar: list
    :param erange: The error range fill between of the data [y0, y1].
    :type erange: list
    :param marker: The marker type.
    :type marker: str
    :param markerstyle: The marker style.
    :type markerstyle: str
    :param markersize: The marker size.
    :type markersize: int
    :param markerfacecolor: The marker face color.
    :type markerfacecolor: str
    :param markeredgecolor: The marker edge color.
    :type markeredgecolor: str
    :param plotprecedence: The order of the curve.
    :type plotprecedence: int
    :param legend_show: Show the curve in the legend.
    :type legend_show: bool
    :param math_interp_left: `numpy.interp()` `left` parameter for internal curve math methods
    :type math_interp_left: float
    :param math_interp_right: `numpy.interp()` `right` parameter for internal curve math methods
    :type math_interp_right: float
    :param math_interp_period: `numpy.interp()` `period` parameter for internal curve math methods
    :type math_interp_period: float
    :return: curve -- the curve generated from the x and y list of values.
    :rtype: curve.Curve
    """
    if len(x) != len(y):
        print(f"Curve {name} doesn't have the same length: len(x)={len(x)} and len(y)={len(y)} ")
        name += " !!!ERROR:len(x)!=len(y)!!!"
    c = curve.Curve(x=x,
                    y=y,
                    name=name,
                    filename=filename,
                    xlabel=xlabel,
                    ylabel=ylabel,
                    title=title,
                    record_id=record_id,
                    step=step,
                    step_original_x=step_original_x,
                    step_original_y=step_original_y,
                    xticks_labels=xticks_labels,
                    plotname=plotname,
                    color=color,
                    edited=edited,
                    scatter=scatter,
                    linespoints=linespoints,
                    linewidth=linewidth,
                    linestyle=linestyle,
                    drawstyle=drawstyle,
                    dashes=dashes,
                    hidden=hidden,
                    ebar=ebar,
                    erange=erange,
                    marker=marker,
                    markerstyle=markerstyle,
                    markersize=markersize,
                    markerfacecolor=markerfacecolor,
                    markeredgecolor=markeredgecolor,
                    plotprecedence=plotprecedence,
                    legend_show=legend_show,
                    math_interp_left=math_interp_left,
                    math_interp_right=math_interp_right,
                    math_interp_period=math_interp_period)

    return c


def span(xmin, xmax, numpts=100):
    """
    Generates a straight line of slope 1 and y intercept 0 in the specified domain with an optional number
    of points.

    >>> c = pydvpy.span(1, 10)

    :param xmin: The minimum x value
    :type xmin: float
    :param xmax: The maximum x value
    :type xmax: float
    :param numpts: The number of points used to plot the line
    :type numpts: int
    :returns: curve -- the curve object representing the straight line.
    """
    spacing = (float(xmax) - float(xmin)) / (float(numpts) - 1.0)
    fxmin = float(xmin)
    x = []
    for i in range(numpts):
        x.append(fxmin)
        fxmin += spacing
    c = makecurve(x=x,
                  y=x,
                  name=f'Straight Line (m: 1.0 b: 0.0 xmin: {xmin} xmax: {xmax})')

    return c


def get_styles():
    """
    Get the list of available plot styles.

    :return: list -- the list of available style names or an empty list if no styles exist.
    """
    if stylesLoaded:
        return plt.style.available

    return list()


def _convert_to_curvelist(curvelist):
    """
    Convert curve(s) to list of curves

    :param curvelist: The list of curves
    :type curvelist: list
    :returns: curves -- the list of curves
    """
    curves = list()

    if isinstance(curvelist, list):
        curves.extend(curvelist)
    else:
        curves.append(curvelist)

    return curves


def create_plot(curvelist,
                fname=None,
                ftype='png',
                title='',
                xlabel='',
                ylabel='',
                legend=False,
                stylename='ggplot',
                xls=False,
                yls=False,
                fwidth=None,
                fheight=None):
    """Create a plot of the curves in the curvelist using the curve attributes.

    >>> curves = pydvpy.read('testData.txt')

    >>> plot1, fig1, ax1 = pydvpy.create_plot(curves, fname='myPlot1')

    >>> plot2, fig2, ax2 = pydvpy.create_plot(curves, fname='myPlot2', ftype='pdf', title='My Plot',
                                              xlabel='X', ylabel='Y', legend=True,
                                              stylename='ggplot', fwidth=10.1, fheight=11.3)

    See `makecurve()` for available curve attributes. Some of these are not applicable to plotting but the ones that
    are, have the same/similar name to their plotting counterparts. To see the curve attributes, one can execute:

    >>> print(curvelist[0].__dict__)  # this will also contain the x and y data so it will be a long print statement

    >>> print(curvelist[0].color)  # specific attribute

    To set a curve attribute:

    >>> curvelist[0].color = "blue"

    :param curvelist: The list of curves to plot
    :type curvelist: list
    :param fname: The filename of the plot not including the file type, defaults to None which doesn't save anything
    :type fname: str, optional
    :param ftype: The save format of the plot, defaults to 'png'
    :type ftype: str, optional
    :param title: The title of the plot, defaults to ''
    :type title: str, optional
    :param xlabel: The x label of the plot, defaults to ''
    :type xlabel: str, optional
    :param ylabel: The y label of the plot, defaults to ''
    :type ylabel: str, optional
    :param legend: Include a legend in the plot, defaults to False
    :type legend: bool, optional
    :param stylename: The style of the plot, defaults to 'ggplot'
    :type stylename: str, optional
    :param xls: Show x-axis in log scale, defaults to False
    :type xls: bool, optional
    :param yls: Show y-axis in log scale, defaults to False
    :type yls: bool, optional
    :param fwidth: The width of the figure in inches, defaults to None which is the default width of 6.4 inches
    :type fwidth: float, optional
    :param fheight: the height of the figure in inches, defaults to None which is the default height of 4.8 inches
    :type fheight: float, optional
    :returns:
        - plt (:py:class:`matplotlib.pyplot`) - The plot object
        - figure (:py:class:`matplotlib.pyplot.figure`) - The figure object
        - axis (:py:class:`matplotlib.pyplot.axes`) - The axis object
    """
    if stylesLoaded:
        styles = get_styles()

        try:
            idx = styles.index(stylename)
            style.use(styles[idx])
        except:
            if len(styles) > 0:
                style.use(styles[0])

    plt.clf()
    plt.cla()
    axis = plt.gca()

    if (xls):
        axis.set_xscale('log')
    if (yls):
        axis.set_yscale('log')

    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        if not cur.hidden:
            xdat = np.array(cur.x)
            ydat = np.array(cur.y)

            if (yls):
                ydat = np.where(ydat < 0, 1e-301, ydat)  # custom ydata clipping
            if (xls):
                xdat = np.where(xdat < 0, 1e-301, xdat)  # custom ydata clipping

            if cur.ebar is not None:
                c = plt.errorbar(xdat, ydat, yerr=[cur.ebar[0], cur.ebar[1]],
                                 xerr=[cur.ebar[2], cur.ebar[3]], fmt='-')
            elif cur.erange is not None:
                c = plt.plot(xdat, ydat)
                plt.fill_between(xdat, ydat - cur.erange[0], ydat + cur.erange[1],
                                 alpha=0.4, color=c[0].get_color())
            else:
                c = plt.plot(xdat, ydat)

            if cur.linespoints:
                plt.setp(c[0], marker=cur.marker, markersize=cur.markersize, linestyle=cur.linestyle)
            elif cur.scatter:
                plt.setp(c[0], marker=cur.marker, markersize=cur.markersize, linestyle=' ')
            else:
                plt.setp(c[0], linestyle=cur.linestyle)

            if cur.linewidth:
                plt.setp(c[0], lw=cur.linewidth)
                plt.setp(c[0], mew=cur.linewidth)

            plt.setp(c[0], label=cur.name)

            if cur.color != '':
                plt.setp(c, color=cur.color)
            else:
                cur.color = c[0].get_color()

            if cur.dashes is not None:
                c[0].set_dashes(cur.dashes)

    if legend:
        plt.legend(fancybox=True, numpoints=1, loc=1, ncol=1).get_frame().set_alpha(0.5)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    # Change figure size
    figure = plt.gcf()
    if fwidth is not None:
        figure.set_figwidth(float(fwidth), True)
    if fheight is not None:
        figure.set_figheight(float(fheight), True)

    if fname is not None:
        try:
            plt.savefig(fname + '.' + ftype, format=ftype)
        except:
            print('Error: Could not save image to ' + fname + ' of type ' + ftype)

    return plt, figure, axis


def save(fname, curvelist, verbose=False, save_labels=False):
    """
    Saves the given Curve or list of Curves to a file named fname.

    >>> curves = list()

    >>> curves.append(pydvpy.makecurve([1, 2, 3, 4], [5, 10, 15, 20]))

    >>> pydvpy.save('myfile.txt', curves) OR

    >>> pydvpy.save('myfile.txt', curves[0])

    :param fname: ULTRA filename
    :type fname: str
    :param curvelist: The curve or list of curves to save
    :type curvelist: Curve or list
    :param verbose: prints the error stacktrace when True
    :type verbose: bool
    """
    curves = _convert_to_curvelist(curvelist)

    try:
        with open(fname, "w") as f:
            for cur in curves:
                if save_labels:
                    print('# ' + cur.name + ' # xlabel ' + cur.xlabel + ' # ylabel ' + cur.ylabel + '\n')
                    f.write('# ' + cur.name + ' # xlabel ' + cur.xlabel + ' # ylabel ' + cur.ylabel + '\n')
                else:
                    f.write('# ' + cur.name + '\n')
                for dex in range(len(cur.x)):
                    f.write(' ' + str(cur.x[dex]) + ' ' + str(cur.y[dex]) + '\n')
    except:
        print('Error: Can not write to: ' + fname)
        if verbose:
            traceback.print_exc(file=sys.stdout)
    finally:
        if f:
            f.close()


def savecsv(fname, curvelist, verbose=False):
    """
    Saves the Curve or list of Curves to file in comma separated values (csv) format. Assumes
    all curves have the same x basis.

    >>> curves = list()

    >>> curves.append(pydvpy.makecurve([1, 2, 3, 4], [5, 10, 15, 20]))

    >>> pydvpy.savecsv('myfile.csv', curves)

    :param fname: ULTRA filename
    :type fname: str
    :param curvelist: The Curve or list of Curves to save
    :type curvelist: list
    :param verbose: prints the error stacktrace when True
    :type verbose: bool
    """
    curves = _convert_to_curvelist(curvelist)

    try:
        f = open(fname, 'w')
        s = '# time'
        for cur in curves:
            s += ', ' + cur.name
        s += '\n'
        f.write(s)
        for i in range(len(curvelist[0].x)):
            s = str(curvelist[0].x[i])
            for j in range(len(curvelist)):
                s += ', ' + str(curvelist[j].y[i])
            s += '\n'
            f.write(s)
    except:
        print('Error: Can not write to: ' + fname)
        if verbose:
            traceback.print_exc(file=sys.stdout)
    finally:
        if f:
            f.close()


def read(fname, gnu=False, xcol=0, verbose=False, pattern=None, matches=None):
    """
    Read the file and add parsed curves to a curvelist

    >>> curves = pydvpy.read('testData.txt')

    >>> curves = pydvpy.read('testData.txt', False, 0, False, '*_name', 20)

    :param fname: ULTRA filename
    :type fname: str
    :param gnu: optional, flag to determine if the file is a column oriented (.gnu) file.
    :type gnu: bool
    :param xcol: optional, x-column number for column oriented (.gnu) files
    :type xcol: int
    :param verbose: optional, prints the error stacktrace when True
    :type verbose: bool
    :param pattern: optional, the regular expression pattern
    :type pattern: str
    :param matches: optional, maximum number of times to match pattern, if specified
    :type matches: int
    :returns: list -- the list of curves from the file matching pattern, if specified

    """
    if str(fname).endswith(".csv"):
        return readcsv(fname=fname, xcol=xcol, verbose=verbose)
    elif str(fname).endswith(".json"):
        return readsina(fname=fname, verbose=verbose)
    elif str(fname).endswith(".hdf5") or str(fname).endswith(".h5") or str(fname).endswith(".hdf"):
        return readsinahdf5(fname, verbose=verbose)
    elif gnu or str(fname).endswith(".gnu"):
        return __loadcolumns(fname, xcol)
    elif pdbLoaded:
        try:
            fpdb = pdb.open(fname, 'r')
            return __loadpdb(fname, fpdb)
        except:
            pass

    regex = None

    if pattern:
        regex = re.compile(r"%s" % pattern)

    try:

        # first get the lines that contain the candidate ULTRA curves
        try:  # using grep and wc. Much faster
            locs = _get_linelocs_from_text_ultra_grep(fname)
        except:  # opening file directly
            locs = _get_linelocs_from_text_ultra(fname)

        # Parallel curve read using Pool()
        with Pool(processes=cpu_count()) as pool:

            # Create input tuples for each # line from locs above. Use -1 because last loc idx is end of file
            input_tuples = list(map(lambda idx: (fname, locs, idx, regex), range(len(locs) - 1)))

            curve_list = list(filter(None, pool.map(_get_curve_from_text_ultra_perproc, input_tuples)))

    except IOError:
        print('could not load file: {}'.format(fname))
        if verbose:
            traceback.print_exc(file=sys.stdout)
    except ValueError:
        print('invalid pydv file: {}'.format(fname))
        if verbose:
            traceback.print_exc(file=sys.stdout)

    return curve_list


def filtercurves(curvelist, pattern):
    """
    Filters the list of curves based on the regular expression pattern.

    >>> curves = pydvpy.filtercurves(curves, "*_name")

    :param curvelist: the list of curves
    :type curvelist: Curve
    :param pattern: the regular expression pattern
    :type pattern: str
    :return: list -- The list of filtered curves from curvelist based on the regular expression pattern
    """
    results = list()
    regex = re.compile(r"%s" % pattern)

    for c in curvelist:
        if regex.search(c.name) is not None:
            results.append(c)

    return results


def readcsv(fname, xcol=0, verbose=False):
    """
    Load a csv (comma separated values) data file, add parsed curves to
    a curvelist. '#' is the comment character.  First uncommented line must
    be the column labels.  We assume the first column is the x-data, every
    other column is y-data.  We also assume all columns are the same length.

    >>> curves = readcsv('testData.csv')

    :param fname: csv filename
    :type fname: str
    :param xcol: x-column number for column oriented (.gnu) files
    :type xcol: int
    :param verbose: prints the error stacktrace when True
    :type verbose: bool
    :returns: list -- the list of curves from the csv file
    """

    curvelist = list()

    try:
        f = open(fname, 'r')
    except IOError:
        print('readcsv: could not load file: ' + fname)
        if verbose:
            traceback.print_exc(file=sys.stdout)
        return curvelist

    try:
        lines = f.readlines()
        iLine = 0
        for line in lines:
            if line[0] != '#':
                break
            iLine += 1
        if iLine == 0 and False:  # FIXME make condition to catch no labels
            print('WARNING: columns have no labels, labels will be assigned...someday')
        alllabels = lines[iLine]  # this line has the labels on it.
        colLabels = alllabels.split(',')
        colLabels = [w.strip() for w in colLabels]
        for w in colLabels:  # if someone made labels with quotes, kill the quotes
            if '"' in w:
                w.replace('"', '')
        # check that we have a label for every column
        if len(colLabels) != len(lines[iLine].split(',')) and iLine > 0:
            raise RuntimeError('Sorry, right now PDV requires you to have a label for every column.')
        # We assume some column is the x-data, every other column
        # is y-data
        iLine += 1  # go to next line after header labels
        # CSV Data is in x and y pairs
        if xcol == 'paired':
            xcol = 0
            paired = True
        # CSV Data has a single shared x column
        else:
            xcol = int(xcol)
            paired = False
        numcurves = len(lines[iLine].split(',')) - 1

        # Make the curves, append them to self.curvelist.
        # First, get data into lists of numbers
        # numDataLines = len(lines) - iLine
        localCurves = []
        for i in range(numcurves + 1):
            localCurves.append([])  # FIGURE OUT COOL WAY TO DO THIS LATER: localCurves = (numcurves+1)*[[]]
        # turn the strings into numbers
        for line in lines[iLine:]:
            nums = [np.nan if not n or n == '\n' else float(n) for n in line.split(',')]
            # print 'nums = ', nums, 'numcurves = ', numcurves
            assert len(nums) == numcurves + 1
            if xcol >= numcurves:
                print('xcolumn is %d, larger than the number of curves' % xcol,
                      'in the file, use "setxcolumn" to fix that')
            for colID in range(numcurves + 1):
                localCurves[colID].append(nums[colID])
        # convert lists to numpy arrays
        for colID in range(numcurves):
            localCurves[colID] = np.array(localCurves[colID])
        # Make Curve objects, add to self.curvelist
        if paired:
            for colID in range(0, numcurves + 1, 2):
                colLabels[colID] = colLabels[colID][:-4]  # ' [x]'
                x = np.array(localCurves[colID])
                x = x[~np.isnan(x)]
                y = np.array(localCurves[colID + 1])
                y = y[~np.isnan(y)]
                c = makecurve(x=x,
                              y=y,
                              name=colLabels[colID],
                              filename=fname)
                print("Appended curve: ", colLabels[colID], len(c.x), len(c.y))
                curvelist.append(c)
        else:
            for colID in range(numcurves + 1):
                if colID != xcol:
                    c = makecurve(x=localCurves[xcol],
                                  y=localCurves[colID],
                                  name=colLabels[colID],
                                  filename=fname)
                    print("Appended curve: ", colLabels[colID], len(c.x), len(c.y))
                    curvelist.append(c)
        # tidy up
        f.close()
    # anticipate failure!
    except ValueError as e:
        print(e)
        print('readcsv: invalid pydv file: ' + fname)
        if verbose:
            traceback.print_exc(file=sys.stdout)

    return curvelist


def readsina(fname, verbose=False, hdf5_path=None):
    """
    Load a Sina JSON data file, add parsed curves to a curvelist.

    We assume JSON conforming to the Sina schema, with each curve defined in a curve_set. We assume
    there is only one record, and if there are more then we only read the first one. We also assume
    only one independent variable per curve_set; if there are more than one, then PyDV may exhibit
    undefined behavior. Can also read curve_sets within libraries in library_data.

    >>> curves = readsina('testData.json')

    :param fname: Sina JSON filename
    :type fname: str
    :param verbose: prints the error stacktrace when True
    :type verbose: bool
    :param hdf5_path: File path for HDF5 sina file. Should not be set by user, only used internally, defaults to None.
    :type hdf5_path: str, optional.
    :returns: list: the list of curves from the sina file
    """
    def add_curve_set(curve_sets, record_id, order_options, library=''):

        curves = {}
        listed_order = []
        for curve_set_name, curve_set in curve_sets.items():
            for name_ind, v_ind in curve_set['independent'].items():
                independent_name = name_ind
                independent_value = v_ind['value']
                for name, v in curve_set['dependent'].items():
                    # TODO: Save the name x and y names with the curves
                    dependent_variable_name = name
                    if order_options:
                        full_name = curve_set_name + '__SINA_DEP__' + dependent_variable_name
                    else:
                        full_name = curve_set_name + '__SINA_DEP__' + dependent_variable_name + \
                            '__SINA_INDEP__' + independent_name
                    dependent_variable_value = v['value']
                    curve_name = dependent_variable_name + ' vs ' + independent_name + " (" + \
                        curve_set_name + ")"
                    if library != '':
                        curve_name += ' ' + library
                        full_name += '__LIBRARY__' + library
                    c = makecurve(x=independent_value,
                                  y=dependent_variable_value,
                                  name=curve_name,
                                  filename=fname if hdf5_path is None else hdf5_path,
                                  xlabel=independent_name,
                                  ylabel=dependent_variable_name,
                                  title=curve_name,
                                  record_id=record_id)
                    c.step = False
                    c.xticks_labels = {}
                    if verbose:
                        print(f"Appended curve: {curve_name}, len x,y: {len(c.x)},{len(c.y)}")
                    curves[full_name] = c
                    listed_order.append(full_name)

        if order_options:
            try:
                curves_lst_temp = [curves[name] for name in order_options]
            except KeyError:
                print('readsina: mismatch between dependent variable names in the curve_sets and the '
                      'ordering specified in SINA_timeplot_order. Using default ordering instead.')
                curves_lst_temp = [curves[name] for name in listed_order]
                if verbose:
                    traceback.print_exc(File=sys.stdout)
        else:
            curves_lst_temp = [curves[name] for name in listed_order]

        return curves_lst_temp

    def cycle_thru_recs(sina_file):
        curves_lst = []

        for rec in sina_file['records']:

            record_id = rec.get('id', rec.get("local_id", ""))
            curve_sets = rec.get('curve_sets', {})
            library_data = rec.get('library_data', {})
            order_options = rec.get('data', {}).get('SINA_timeplot_order', {}).get('value', [])

            curves_lst_temp = add_curve_set(curve_sets, record_id, order_options)
            curves_lst.extend(curves_lst_temp)

            for library in library_data:
                if 'curve_sets' in library_data[library]:
                    curve_sets = library_data[library].get('curve_sets', {})
                    order_options = library_data[library].get('data',
                                                              {}).get('SINA_timeplot_order',
                                                                      {}).get('value', [])
                    curves_lst_temp = add_curve_set(curve_sets, record_id, order_options, library=library)
                    curves_lst.extend(curves_lst_temp)
        return curves_lst

    try:
        # Load the curve data from the curve_sets
        try:
            if not isinstance(fname, dict):
                with open(fname, 'r') as fp:
                    curves_lst = cycle_thru_recs(json.load(fp))
            else:
                curves_lst = cycle_thru_recs(fname)
        except KeyError:
            print('readsina: Sina file {} is malformed'.format(fname))
            if verbose:
                traceback.print_exc(file=sys.stdout)
            return []

    except IOError:
        print('readsina: could not load file: {}'.format(fname))
        if verbose:
            traceback.print_exc(file=sys.stdout)
        return []

    return curves_lst


def readsinahdf5(hdf5_path, verbose=False):
    # def load_document_hdf5(hdf5_path): Taken from sina/utils.py
    """
    Retrieves records and relationships from HDF5
    """
    reconstructed_doc = {}

    def coerce_numpy_to_json(val):
        # There's no single quick way to do this when numpy and hdf5 combine,
        # so we have a manual method...
        if isinstance(val, bytes):
            val = val.decode("utf-8")
        if isinstance(val, h5py.Empty):
            val = dict()
        if isinstance(val, np.integer):
            val = int(val)
        elif isinstance(val, np.floating):
            val = float(val)
        elif isinstance(val, np.ndarray):
            is_word = len(np.shape(val)) == 1 and isinstance(val[0], bytes)
            val = [x.decode("utf-8") if isinstance(x, bytes)
                   else x for x in val.tolist()]
            if is_word:
                val = ''.join(val)
            elif np.shape(val)[0] == 1:
                val = val[0]
        return val

    def add_arbitrary_path_to_dict(some_path, val):
        chunk = reconstructed_doc
        layers = some_path.split("/")
        for depth, layer in enumerate(layers):
            if not layer:
                continue
            if layer not in chunk:
                chunk[layer] = dict()
            if depth == len(layers) - 1:
                if isinstance(val, list):
                    chunk[layer] = [coerce_numpy_to_json(x) for x in val]
                else:
                    chunk[layer] = coerce_numpy_to_json(val)
            else:
                chunk = chunk[layer]

    def yoink_dataset_or_recurse(path, chunk):
        if isinstance(chunk, h5py.Group):
            for key, val in chunk.items():
                # Recovery for common wonky HDF5 issue
                if (isinstance(val, h5py.Group) and '0' in val.keys() and key in ("value", "tags")):
                    add_arbitrary_path_to_dict(path + "/" + key, [chunk[key][x][()] for x in val])
                else:
                    yoink_dataset_or_recurse(path + "/" + key, val)
        else:
            add_arbitrary_path_to_dict(path, chunk[()])
    with h5py.File(hdf5_path, 'r') as src:
        yoink_dataset_or_recurse("", src)
    # Now we have to (temporarily!) smooth the object->list thing between our hdf5
    # and JSON entries...
    reconstructed_doc["records"] = ([x for x in reconstructed_doc["records"].values()]
                                    if "records" in reconstructed_doc else list())
    # reconstructed_doc["relationships"] = ([x for x in reconstructed_doc["relationships"].values()]
    #                                       if "relationships" in reconstructed_doc else list())

    return readsina(reconstructed_doc, hdf5_path=hdf5_path)


########################################################
################## Math Functions  #####################  # noqa e266
########################################################

def cos(curvelist):
    """
    Take the cosine of y values of a Curve or list of Curves.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.cos(curves) OR

     >>> pydvpy.cos(curves[0])

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.cos(cur.y)


def cosx(curvelist):
    """
    Take the cosine of x values of a Curve or list of Curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.cosx(curves) OR

    >>> pydvpy.cosx(curves[0])

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.cos(cur.x)


def cosh(curvelist):
    """
    Take the hyperbolic cosine of y values of a Curve or list of Curves.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.cosh(curves) OR

     >>> pydvpy.cosh(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.cosh(cur.y)


def coshx(curvelist):
    """
    Take the hyperbolic cosine of x values of a Curve or list of Curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.coshx(curves) OR

    >>> pydvpy.coshx(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.cosh(cur.x)


def acosh(curvelist):
    """
    Take the hyperbolic arccosine of y values of a Curve or list of Curves.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.acosh(curves) OR

     >>> pydvpy.acosh(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.arccosh(cur.y)


def acoshx(curvelist):
    """
    Take the hyperbolic arccosine of x values of a Curve or list of Curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.acoshx(curves) OR

    >>> pydvpy.acoshx(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.arccosh(cur.x)


def acos(curvelist):
    """
    Take the arccosine of y values of a Curve or list of Curves

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.acos(curves) OR

     >>> pydvpy.acos(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.arccos(cur.y)


def acosx(curvelist):
    """
    Take the arccosine of x values of a Curve or list of Curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.acosx(curves) OR

    >>> pydvpy.acosx(curves[0])

    :param curvelist: The Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.arccos(cur.x)


def sin(curvelist):
    """
    Take the sine of y values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.sin(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.sin(cur.y)


def sinx(curvelist):
    """
    Take the sine of x values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.sinx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.sin(cur.x)


def sinh(curvelist):
    """
    Take the hyperbolic sine of y values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.sinh(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.sinh(cur.y)


def sinhx(curvelist):
    """
    Take the hyperbolic sine of x values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.sinhx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.sinh(cur.x)


def asinh(curvelist):
    """
    Take the hyperbolic arcsine of y values of a single curve or curves in a list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.asinh(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.asinh(cur.y)


def asinhx(curvelist):
    """
    Take the hyperbolic arcsine of x values of a single curve or curves in a list.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.asinhx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.asinh(cur.x)


def asin(curvelist):
    """
    Take the arcsine of y values of a single curve or curves in a list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.asin(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.asin(cur.y)


def asinx(curvelist):
    """
    Take the arcsine of x values of a single curve or curves in a list.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.asinx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.asin(cur.x)


def tan(curvelist):
    """
    Take the tangent of y values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.tan(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.tan(cur.y)


def tanx(curvelist):
    """
    Take the tangent of x values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.tanx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.tan(cur.x)


def tanh(curvelist):
    """
    Take the hyperbolic tangent of y values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.tanh(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.tanh(cur.y)


def tanhx(curvelist):
    """
    Take the hyperbolic tangent of x values of a single curve or multiple curves in list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.tanhx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.tanh(cur.x)


def atan(curvelist):
    """
    Take the arctangent of y values of a single curve or curves in a list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.atan(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.atan(cur.y)


def atanx(curvelist):
    """
    Take the arctangent of x values of a single curve or curves in a list.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.atanx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.atan(cur.x)


def atanh(curvelist):
    """
    Take the hyperbolic arctangent of y values of a single curve or curves in a list.

     >>> curves = pydvpy.read('testData.txt')

     >>> pydvpy.atanh(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.atanh(cur.y)


def atanhx(curvelist):
    """
    Take the hyperbolic arctangent of x values of a single curve or curves in a list.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.atanhx(curves)

    :param curvelist: A single curve or a list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.atanh(cur.x)


def atan2(c1, c2, t=None):
    """
    Perform the atan2 method for a pair of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.atan2(curves[0], curves[1])   OR

    >>> pydvpy.atan2(curves[0], curves[1], tuple(['A', 'B']))

    :param c1: the first curve
    :type c1: curve
    :param c2: the second curve
    :type c2: curve
    :param t: A tuple containing exactly two values to insert into the name string for the new curve
    :type t: tuple
    :return: curve -- a new curve with the results from this operation
    """
    if t is None:
        t = tuple([c1.name, c2.name])

    c = makecurve(x=np.array(c1.x),
                  y=np.arctan2(c1.y, c2.y),
                  name='atan2(%s,%s)' % t)

    return c


def add(curvelist):
    """
    Add one or more curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> c = pydvpy.add(curves)

    :param curvelist: The list of curves
    :type curvelist: list
    :returns: curve -- the curve containing the sum of the curves in curvelist
    """

    numcurves = len(curvelist)
    if numcurves > 1:
        name = curvelist[0].name
        sendline = 'curvelist[' + str(0) + ']'
        for i in range(1, numcurves):
            name += ' + ' + curvelist[i].name
            sendline += '+ curvelist[' + str(i) + ']'

        c = eval(sendline)
        c.name = name

        if c.x is None or len(c.x) < 2:
            print('Error: curve overlap is insufficient')
            return 0

        return c
    elif numcurves == 1:
        return curvelist[0]
    else:
        return curvelist


def subtract(curvelist):
    """
    Take difference of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> c = pydvpy.subtract(curves)

    :param curvelist: The list of curves
    :type curvelist: list
    :returns: curve -- the curve containing the difference of the curves
    """

    numcurves = len(curvelist)
    if numcurves > 1:
        name = curvelist[0].name
        sendline = 'curvelist[' + str(0) + ']'
        for i in range(1, numcurves):
            name += ' - ' + curvelist[i].name
            sendline += '- curvelist[' + str(i) + ']'

        c = eval(sendline)
        c.name = name

        if c.x is None or len(c.x) < 2:
            print('Error: curve overlap is insufficient')
            return 0

        return c
    elif numcurves == 1:
        return curvelist[0]
    else:
        return curvelist


def multiply(curvelist):
    """
    Take product of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> c = pydvpy.multiply(curves)

    :param curvelist: The list of curves
    :type curvelist: list
    :returns: Curve -- the curve containing the product of the curves
    """
    numcurves = len(curvelist)
    if numcurves > 1:
        name = __toCurveString(curvelist[0])
        sendline = 'curvelist[' + str(0) + ']'
        for i in range(1, numcurves):
            name += ' * ' + __toCurveString(curvelist[i])
            sendline += '* curvelist[' + str(i) + ']'

        c = eval(sendline)
        c.name = name

        if c.x is None or len(c.x) < 2:
            print('Error: curve overlap is insufficient')
            return 0

        return c
    elif numcurves == 1:
        return curvelist[0]
    else:
        return curvelist


def divide(curvelist):
    """
    Take quotient of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> c = pydvpy.divide(curves)

    :param curvelist: The list of curves
    :type curvelist: list
    :returns: curve -- the curve containing the quotient of the curves
    """
    numcurves = len(curvelist)
    if numcurves > 1:
        name = __toCurveString(curvelist[0])
        sendline = 'curvelist[' + str(0) + ']'
        for i in range(1, numcurves):
            name += ' / ' + __toCurveString(curvelist[i])
            sendline += '/ curvelist[' + str(i) + ']'

        c = eval(sendline)
        c.name = name

        if c.x is None or len(c.x) < 2:
            print('Error: curve overlap is insufficient')
            return 0

        return c
    elif numcurves == 1:
        return curvelist[0]
    else:
        return curvelist


def divx(curvelist, value):
    """
    Divide x values of the curve(s) by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.divx(curves, 4)

    :param curvelist: The curve or curvelist
    :type curvelist: Curve or list
    :param value: The divisor
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if float(value) == 0:
            value = 1.e-10
        c.x /= float(value)


def divy(curvelist, value):
    """
    Divide y values of the curve(s) by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.divy(curves, 4)

    :param curvelist: The curve or curvelist
    :type curvelist: Curve or list
    :param value: The divisor
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if float(value) == 0:
            value = 1.e-10
        c.y /= float(value)


def dx(curvelist, value):
    """
    Shift x values of a curve or list of curves by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.dx(curves, 4) OR

    >>> pydvpy.dx(curves[0], 4)


    :param curvelist: A curve or curvelist
    :type curvelist: Curve or list
    :param value: The amount to shift the x values by
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x += float(value)


def dy(curvelist, value):
    """
    Shift y values of a curve or list of curves by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.dy(curves, 4) OR

    >>> pydvpy.dy(curves[0], 4)


    :param curvelist: A curve or curvelist
    :type curvelist: Curve or list
    :param value: The amount to shift the y values by
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y += float(value)


def mx(curvelist, value):
    """
    Scale x values of a curve or list of curves by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.mx(curves, 4) OR

    >>> pydvpy.mx(curves[0], 4)


    :param curvelist: A curve or curvelist
    :type curvelist: Curve or list
    :param value: The amount to scale the x values by
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x *= float(value)


def my(curvelist, value):
    """
    Scale y values of a curve or list of curves by a constant value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.my(curves, 4) OR

    >>> pydvpy.my(curves[0], 4)


    :param curvelist: A curve or curvelist
    :type curvelist: Curve or list
    :param value: The amount to scale the y values by
    :type value: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y *= float(value)


def l1(c1, c2, xmin=None, xmax=None):
    """
    Make a new curve that is the L1 norm of curve c1 and  curve c2.
    The L1-norm is the integral(\|c1 - c2\|) over the interval [xmin, xmax].  # noqa w605

    >>> c = pydvpy.l1(curve1, curve2)

    >>> c2 = pydvpy.l1(curve1, curve2, 1.1, 10.9)

    :param c1: The first curve
    :type c1: Curve
    :param c2: The second curve
    :type c2: Curve
    :param xmin: the minimum x value to perform the L1 norm
    :type xmin: float
    :param xmax: the maximum x value to perform the L1 norm
    :type xmax: float
    :returns Curve: A new curve that is the L1 norm of c1 and c2
    """
    c = c1 - c2
    c.y = np.abs(c.y)

    if xmin is not None and xmax is not None:
        if xmax <= xmin:
            raise RuntimeError("xmin > xmax or xmin == xmax in l1")
    else:
        xmin = np.min(c.x)
        xmax = np.max(c.x)

    d = integrate(c, xmin, xmax)
    d[0].name = "L1 of " + __toCurveString(c1) + " and " + __toCurveString(c2)

    return d[0]


def l2(c1, c2, xmin=None, xmax=None):
    """
    Make a new curve that is the L2 norm of curve c1 and curve c2.
    The L2-norm is (integral((c1 - c2)**2)**(1/2) over the interval [xmin, xmax].

    >>> c = pydvpy.l2(curve1, curve2)

    >>> c2 = pydvpy.l2(curve1, curve2, 3.1, 30.9)

    :param c1: The first curve
    :type c1: Curve
    :param c2: The second curve
    :type c2: Curve
    :param xmin: the minimum x value to perform the L2 norm
    :type xmin: float
    :param xmax: the maximum x value to perform the L2 norm
    :type xmax: float
    :returns Curve: A new curve that is the L2 norm of c1 and c2
    """
    c = c1 - c2
    c.y = np.abs(c.y)
    c = c**2.0

    if xmin is not None and xmax is not None:
        if xmax <= xmin:
            raise RuntimeError("xmin > xmax or xmin == xmax in l2")
    else:
        xmin = np.min(c.x)
        xmax = np.max(c.x)

    d = integrate(c, xmin, xmax)
    d[0] = d[0]**(0.5)
    d[0].name = "L2 of " + __toCurveString(c1) + " and " + __toCurveString(c2)

    return d[0]


def norm(c1, c2, p, xmin=None, xmax=None):
    """
    Make a new curve that is the p-norm of curve c1 and curve c2.

    >>> curves = pydvpy.read('testData.txt')

    >>> c = pydvpy.norm(curves[0], curves[1], 'inf')

    >>> curves.append(c)

    :param c1: The first curve
    :type c1: Curve
    :param c2: The second curve
    :type c2: Curve
    :param p: the order (e.g., 'inf', '3', '5')
    :type p: str
    :param xmin: the minimum x value to perform the p-norm
    :type xmin: float
    :param xmax: the maximum x value to perform the p-norm
    :type xmax: float
    :returns Curve: A new curve that is the p-norm of c1 and c2
    """
    c = c1 - c2
    c.y = np.abs(c.y)

    if p.lower() != "inf":
        N = int(p)
        c = c**N

    if xmin is not None and xmax is not None:
        if xmax <= xmin:
            raise RuntimeError("xmin > xmax or xmin == xmax in norm")
    else:
        xmin = np.min(c.x)
        xmax = np.max(c.x)

    if p.lower() == "inf":
        Linf = 0.0
        for xi, yi in zip(c.x, c.y):
            if xmin <= xi <= xmax:
                Linf = max(Linf, yi)
        d = c
        d.y = np.array([Linf] * c.y.shape[0])
        d.name = "Linf of " + __toCurveString(c1) + " and " + __toCurveString(c2)

        return d
    else:
        d = integrate(c, xmin, xmax)
        d[0] = d[0]**(1.0 / N)
        d[0].name = "L%d of " % N + __toCurveString(c1) + " and " + __toCurveString(c2)

        return d[0]


def abs(curvelist):
    """
    Take the absolute value of the y values of the Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.abs(curves) OR

    >>> pydvpy.abs(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.abs(cur.y)


def absx(curvelist):
    """
    Take the absolute value of the x values of the Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.absx(curves) OR

    >>> pydvpy.absx(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.abs(cur.x)


def log(curvelist, keep=True):
    """
    Take the natural logarithm of y values of the Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.log(curves) OR

    >>> pydvpy.log(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param keep: flag to determine whether or not to discard zero or negative y-values before taking the log.
                 keep is True by default.
    :type keep: optional, boolean
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if not keep:
            skiplist = np.where(c.y <= 0)[0]
            if len(skiplist) > 0:
                c.y = np.delete(c.y, skiplist)
                c.x = np.delete(c.x, skiplist)

        c.y = np.log(c.y)
        if c.name[:3] == 'exp':
            c.name = c.name[4:-1]  # Pop off the exp( from the front and the ) from the back
        else:
            c.name = 'log(' + c.name + ')'


def logx(curvelist, keep=True):
    """
    Take the natural logarithm of x values of the Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.logx(curves) OR

    >>> pydvpy.logx(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param keep: flag to determine whether or not to discard zero or negative x-values before taking the log.
                 keep is True by default.
    :type keep: optional, boolean
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if not keep:
            skiplist = np.where(c.x <= 0)[0]
            if len(skiplist) > 0:
                c.y = np.delete(c.y, skiplist)
                c.x = np.delete(c.x, skiplist)

        c.x = np.log(c.x)
        if c.name[:4] == 'expx':
            c.name = c.name[5:-1]  # Pop off the expx( from the front and the ) from the back
        else:
            c.name = 'logx(' + c.name + ')'


def log10(curvelist, keep=True):
    """
    Take the base 10 logarithm of y values of a Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.log10(curves) OR

    >>> pydvpy.log10(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param keep: flag to determine whether or not to discard zero
                 or negative y-values before taking the base 10 logarithm.
                 keep is True by default.
    :type keep: optional, boolean
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if not keep:
            skiplist = np.where(c.y <= 0)[0]
            if len(skiplist) > 0:
                c.y = np.delete(c.y, skiplist)
                c.x = np.delete(c.x, skiplist)

        c.y = np.log10(c.y)
        c.name = 'log10(' + c.name + ')'


def log10x(curvelist, keep=True):
    """
    Take the base 10 logarithm of x values of a Curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.log10x(curves) OR

    >>> pydvpy.log10x(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param keep: flag to determine whether or not to discard zero
                 or negative y-values before taking the base 10 logarithm.
                 keep is True by default.
    :type keep: optional, boolean
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if not keep:
            skiplist = np.where(c.x <= 0)[0]
            if len(skiplist) > 0:
                c.y = np.delete(c.y, skiplist)
                c.x = np.delete(c.x, skiplist)

        c.x = np.log10(c.x)
        c.name = 'log10x(' + c.name + ')'


def exp(curvelist):
    """
    Exponentiate y values of the Curve or list of curves (e**y).

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.exp(curves) OR

    >>> pydvpy.exp(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.exp(cur.y)


def expx(curvelist):
    """
    Exponentiate x values of the Curve or list of curves (e**x).

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.expx(curves) OR

    >>> pydvpy.expx(curves[0])

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.exp(cur.x)


def powa(curvelist, a):
    """
    Raise a fixed value, a, to the power of the y values of the Curve or list of curves. y = a^y

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.powa(curves, 2) OR

    >>> pydvpy.powa(curves[0], 2)

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param a: the fixed value
    :type a: float
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.power(float(a), cur.y)


def powax(curvelist, a):
    """
    Raise a fixed value, a, to the power of the x values of the Curve or curves. x = a^x

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.powax(curves, 4.2) OR

    >>> pydvpy.powax(curves[0], 4.2)

    :param curvelist: the Curve or list of curves
    :type curvelist: Curve or list
    :param a: the fixed value
    :type a: float
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.power(float(a), cur.x)


def powr(curvelist, a):
    """
    Raise a the y values of a curve or list of curves to a fixed power, y = y^a.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.powr(curves, 4.2) OR

    >>> pydvpy.powr(curves[0], 4.2)

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    :param a: the fixed value
    :type a: float
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.power(cur.y, float(a))


def powrx(curvelist, a):
    """
    Raise a the x values of a curve or list of curves to a fixed power, x = x^a.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.powrx(curves, 4.2) OR

    >>> pydvpy.powrx(curves[0], 4.2)

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    :param a: the fixed value
    :type a: float
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.power(cur.x, float(a))


def sqr(curvelist):
    """
    Take the square of the y values in a curve or list of curves.

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.square(cur.y)


def sqrx(curvelist):
    """
    Take the square of the x values in a curve or list of curves.

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.square(cur.x)


def sqrt(curvelist):
    """
    Take the square root of the y values in a curve or list of curves.

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.y = np.sqrt(cur.y)


def sqrtx(curvelist):
    """
    Take the square root of the x values in a curve or list of curves.

    :param curvelist: the curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        cur.x = np.sqrt(cur.x)


def xmax(curvelist, max):
    """
    Filter out points in the curve or list of curves whose x values are greater than limit.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param max: The maximum value
    :type max: float
    """

    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(c.x <= float(max))
        c.x = c.x[mask]
        c.y = c.y[mask]


def xmin(curvelist, min):
    """
    Filter out points in the curve or list of curves whose x values are less than min.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param min: The minimum value
    :type min: float
    """

    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(c.x >= float(min))
        c.x = c.x[mask]
        c.y = c.y[mask]


def xminmax(curvelist, min, max):
    """
    Filter out points in the curve or list of curves whose x values are
    less than min or greater than max.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param min: The minimum value
    :type  min: float
    :param max: The maximum value
    :type max: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(np.logical_and(c.x >= float(min), c.x <= float(max)))
        c.x = c.x[mask]
        c.y = c.y[mask]


def ymax(curvelist, max):
    """
    Filter out points in the curve or list of curves whose y values are greater than limit.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param max: The maximum value
    :type max: float
    """

    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(c.y <= float(max))
        c.x = c.x[mask]
        c.y = c.y[mask]


def ymin(curvelist, min):
    """
    Filter out points in the curve or list of curves whose y values are less than min.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param min: The minimum value
    :type min: float
    """

    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(c.y >= float(min))
        c.x = c.x[mask]
        c.y = c.y[mask]


def yminmax(curvelist, min, max):
    """
    Filter out points in the curve or list of curves whose y values are
    less than min or greater than max.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param min: The minimum value
    :type  min: float
    :param max: The maximum value
    :type max: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        mask = np.where(np.logical_and(c.y >= float(min), c.y <= float(max)))
        c.x = c.x[mask]
        c.y = c.y[mask]


def yn(curvelist, n):
    """
    Take the Bessel function of the second kind of order n for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param n: The order
    :type n: int
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.yn(int(n), c.y)


def ynx(curvelist, n):
    """
    Take the Bessel function of the second kind of order n for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param n: The order
    :type n: int
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.yn(int(n), c.x)


def y0(curvelist):
    """
    Take the Bessel function of the second kind of the zeroth order for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.y0(c.y)


def y0x(curvelist):
    """
    Take the Bessel function of the second kind of the zeroth order for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.y0(c.x)


def y1(curvelist):
    """
    Take the Bessel function of the second kind of the first order for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.y1(c.y)


def y1x(curvelist):
    """
    Take the Bessel function of the second kind of the first order for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.y1(c.x)


def jn(curvelist, n):
    """
    Take the Bessel function of the first kind of the nth order for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param n: The order
    :type n: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.jn(float(n), c.y)


def jnx(curvelist, n):
    """
    Take the Bessel function of the first kind of the nth order for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    :param n: The order
    :type n: float
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.jn(int(n), c.x)


def j0(curvelist):
    """
    Take the Bessel function of the first kind of the zeroth order for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.j0(c.y)


def j0x(curvelist):
    """
    Take the Bessel function of the first kind of the zeroth order for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.j0(c.x)


def j1(curvelist):
    """
    Take the Bessel function of the first kind of the first order for the y values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = scipy.special.j1(c.y)


def j1x(curvelist):
    """
    Take the Bessel function of the first kind of the first order for the x values of
    curves in curvelist.

    :param curvelist: The curve or list of curves
    :type curvelist: curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = scipy.special.j1(c.x)


def recip(curvelist):
    """
    Take the reciprocal of the y values of the curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.recip(curves[1])

    >>> pydvpy.create_plot(curves, legend=True, stylename='ggplot')

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = np.reciprocal(c.y)


def recipx(curvelist):
    """
    Take the reciprocal of the x values of the curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.dx(curves, 2)

    >>> pydvpy.recipx(curves)

    >>> pydvpy.create_plot(curves, legend=True, stylename='ggplot')

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    :return:
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.x = np.reciprocal(c.x)


def integrate(curvelist, low=None, high=None):
    """
     Take the integral of the curve or curves in curvelist.

    :param curvelist: A curve or list of curves
    :type curvelist: curve or list
    :param low: The lower limit
    :type low: float
    :param high: The maximum limit
    :type high: float
    :return: list -- the list of integrated curves
    """
    curves = _convert_to_curvelist(curvelist)
    ncurves = list()

    for c in curves:
        nc = c.copy()
        nc.plotname = ''
        nc.color = ''

        if low is None:
            nc.name = 'Integrate ' + c.plotname
        else:
            nc.name = 'Integrate %s [%.1f,%.1f]' % (c.plotname, low, high)

        if low is None:
            low = min(nc.x)

        if high is None:
            high = max(nc.x)

        r = __get_sub_range(nc.x, low, high)
        nc.x = nc.x[r[0]:r[1] + 1]
        nc.y = nc.y[r[0]:r[1] + 1]
        try:
            nc.y = np.array(scipy.integrate.cumtrapz(nc.y, nc.x, initial=0.0))
        except:
            nc.y = np.array(scipy.integrate.cumulative_trapezoid(nc.y, nc.x, initial=0.0))

        ncurves.append(nc)

    return ncurves


def alpha(ac, ig, res, npts=-1):
    if npts == -1:
        npts = len(ac.y)

    ai = curve.Curve.__mul__(ac, ig)
    num = convolveb(ai, res, npts)
    denom = convolveb(ig, res, npts)
    alpha_measured = curve.Curve.__div__(num, denom)

    alpha_measured.name = "Measured alpha"
    alpha_measured.plotname = ''
    return alpha_measured


def gaussian(amp, wid, center, num=100, nsd=3):
    """
    Generate a gaussian function.

    >>> curve = pydvpy.gaussian(5, 10, 0)

    >>> pydvpy.create_plot(curve, legend=True, stylename='ggplot')

    :param amp: amplitude
    :type amp: float
    :param wid: width
    :type wid: float
    :param center: center
    :type center: float
    :param num: optional, number of points
    :type num: int
    :param nsd: optional, number of half-widths
    :type nsd: float
    :return: Curve -- representing the gaussian function
    """
    crv_min = center - (nsd * wid)
    crv_max = center + (nsd * wid)
    cc = span(crv_min, crv_max, num)

    dd = cc.y - center
    cc.y = dd * dd * -1
    cc.y = np.exp(cc.y / (wid * wid))
    cc.y = cc.y * amp

    cc.name = f"Gaussian (a: {amp} w: {wid} c: {center})"
    return cc


def getymax(c, xmin=None, xmax=None):
    """
    Get the maximum y-value for the curve within the specified domain.

    :param c: the curve
    :type Curve:
    :param xmin: the minimum x-value for the sub-domain
    :type xmin: float, optional
    :param xmax: the maximum x-value for the sub-domain
    :type xmax: float, optional
    :return: str -- curve name
             list -- a list of tuples where each tuple contains the x-value and
             the max y-value.
    """
    xl = c.x[0] if xmin is None else xmin
    xr = c.x[-1] if xmax is None else xmax
    domain = list(c.x[np.where(np.logical_and(c.x >= xl, c.x <= xr))])
    domain.extend([xl, xr])
    domain = list(set(domain))
    domain.sort()
    y_interp = np.interp(domain, c.x, c.y,
                         left=c.math_interp_left,
                         right=c.math_interp_right,
                         period=c.math_interp_period)

    indices = np.where(y_interp == np.max(y_interp))[0]

    xypairs = list()
    for index in indices:
        xypairs.append((domain[index], y_interp[index]))

    return __toCurveString(c), xypairs


def getymin(c, xmin=None, xmax=None):
    """
    Get the minimum y-value for the curve within the specified domain.

    :param c: the curve
    :type Curve:
    :param xmin: the minimum x-value for the sub-domain
    :type xmin: float, optional
    :param xmax: the maximum x-value for the sub-domain
    :type xmax: float, optional
    :return: str -- curve name
             list -- a list of tuples where each tuple contains the x-value and
             the min y-value.
    """
    xl = c.x[0] if xmin is None else xmin
    xr = c.x[-1] if xmax is None else xmax
    domain = list(c.x[np.where(np.logical_and(c.x >= xl, c.x <= xr))])
    domain.extend([xl, xr])
    domain = list(set(domain))
    domain.sort()
    y_interp = np.interp(domain, c.x, c.y,
                         left=c.math_interp_left,
                         right=c.math_interp_right,
                         period=c.math_interp_period)

    indices = np.where(y_interp == np.min(y_interp))[0]

    xypairs = list()
    for index in indices:
        xypairs.append((domain[index], y_interp[index]))

    return __toCurveString(c), xypairs


def cumsum(c1):
    """
    Creates a new curve which is the cumulative sum of the original curve

    :param c1: The original curve
    :type c1: Curve

    :return: Curve -- the cumulative sum of the original curve
    """
    nc = makecurve(x=c1.x,
                   y=np.cumsum(c1.y),
                   name='cumsum(' + __toCurveString(c1) + ')')

    return nc


def correlate(c1, c2, mode='valid'):
    """
    Computes the cross-correlation of two 1D sequences (c1.y and c2.y) as defined by numpy.correlate.

    :param c1: The first curve with 1D input sequence c1.y
    :type c1: Curve
    :param c2: The second curve with 1D input sequence c2.y
    :type c2: Curve
    :param mode:
        full:
          By default, mode is 'full'.  This returns the convolution
          at each point of overlap, with an output shape of (N+M-1,). At
          the end-points of the convolution, the signals do not overlap
          completely, and boundary effects may be seen.

        same:
          Mode 'same' returns output of length ``max(M, N)``.  Boundary
          effects are still visible.

        valid:
          Mode 'valid' returns output of length
          ``max(M, N) - min(M, N) + 1``.  The convolution product is only given
          for points where the signals overlap completely.  Values outside
          the signal boundary have no effect.
    :type mode: 'full'(default), 'same' or 'valid'
    :return: Curve -- the cross-correlation of c1.y and c2.y
    """
    ic1, step = curve.interp1d(c1, len(c1.x), True)
    c2npts = (max(c2.x) - min(c2.x)) / step
    ic2 = curve.interp1d(c2, c2npts)

    y = np.correlate(ic1.y, ic2.y, mode)
    start = min([min(ic1.x), min(ic2.x)])
    stop = max([max(ic1.x), max(ic2.x)])
    x = np.linspace(start, stop, num=len(y))

    nc = makecurve(x=x,
                   y=y,
                   name='correlate(' + __toCurveString(c1) + ', ' + __toCurveString(c2) + ')')

    return nc


def theta(xmin, x0, xmax, numpts=100):
    """
    Generate a unit step distribution.

    :param xmin: The left most point
    :type xmin: Union[int,float]
    :param x0: The step point
    :type x0: Union[int,float]
    :param xmax: The right most point
    :type xmax: Union[int,float]
    :param numpts: Number of points, defaults to 100
    :type numpts: Union[int,float], optional
    :return: The curve
    :rtype: curve.Curve
    """

    numpts = round(numpts / 2)

    firstx = np.linspace(xmin, x0, num=numpts)
    firsty = [0] * len(firstx)

    secondx = np.linspace(x0, xmax, num=numpts)
    secondy = [1] * len(secondx)

    x = np.concatenate((firstx, secondx), axis=None)
    y = firsty + secondy

    c = makecurve(x=x,
                  y=y,
                  name=f'Theta {xmin} {x0} {xmax}')

    return c


def normalize(c):
    """
    Normalize a curve.

    :param c: The curve to normalize
    :type c: curve.Curve
    :return: The normalized curve
    :rtype: curve.Curve
    """
    norm_c = c.normalize()
    c = makecurve(x=norm_c.x,
                  y=norm_c.y,
                  name=f'Normalized {norm_c.plotname}')
    return c


def hypot(c1, c2):
    """
    Calculate harmonic average of two curves, sqrt(a^2+b^2).

    :param c1: The first curve
    :type c1: curve.Curve
    :param c2: The second curve
    :type c2: curve.Curve
    :return: The harmonic average of two curves, sqrt(a^2+b^2)
    :rtype: curve.Curve
    """

    if not np.array_equal(c1.x, c2.x):
        raise ValueError('Curves must have the same x values')

    y = np.sqrt(c1.y**2 + c2.y**2)
    c = makecurve(x=c1.x,
                  y=y,
                  name=f'hypot {__toCurveString(c1)} {__toCurveString(c2)}')

    return c


def convolve(c1, c2, npts=100, norm=True, debug=False):
    print("Use convolvec for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))")
    print("Use convolveb for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))")
    return


def convolvec(c1, c2, npts=100, npts_interp=100, debug=False):
    """
    Computes the convolution of the two given curves:
    -
    -   ``(g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))``
    -
    This computes the integrals directly which avoid padding and aliasing
    problems associated with FFT methods (it is however slower).

    :param c1: (N,) The first curve g(t)
    :type c1: Curve
    :param c2: (M,) The second curve h(t)
    :type c2: Curve
    :param npts: the number of points to divide the combined domain of the curves to give delx
    :type npts: int
    :param npts_interp: the number of points to interpolate at each delx step
    :type npts_interp: int
    :param debug: Used only in CLI, plots curves and c2 h(x-t) as it moves
    :type debug: bool
    :return: Curve -- the convolution of the two curves c1 and c2 using integration and no normalization
    """

    return convolve_int(c1, c2, False, npts, npts_interp, debug)


def convolveb(c1, c2, npts=100, npts_interp=100, debug=False):
    """
    Computes the convolution of the two given curves:
    -
    -   ``(g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))``
    -
    This computes the integrals directly which avoid padding and aliasing
    problems associated with FFT methods (it is however slower).

    :param c1: (N,) The first curve g(t)
    :type c1: Curve
    :param c2: (M,) The second curve h(t)
    :type c2: Curve
    :param npts: the number of points to divide the combined domain of the curves to give delx
    :type npts: int
    :param npts_interp: the number of points to interpolate at each delx step
    :type npts_interp: int
    :param debug: Used only in CLI, plots curves and c2 h(x-t) as it moves
    :type debug: bool
    :return: Curve -- the convolution of the two curves c1 and c2 using integration and normalizing by c2
    """

    return convolve_int(c1, c2, True, npts, npts_interp, debug)


def convolve_int(c1, c2, norm=True, npts=100, npts_interp=100, debug=False):
    """
    Computes the convolution of the two given curves:
    -
    -   norm=False: ``(g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))``
    -   norm=True : ``(g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))``
    -
    This computes the integrals directly which avoid padding and aliasing
    problems associated with FFT methods (it is however slower).

    :param c1: (N,) The first curve g(t)
    :type c1: Curve
    :param c2: (M,) The second curve h(t)
    :type c2: Curve
    :param norm: if true then normalize c2 h(t) before integration. Used in convolc
    :type norm: bool
    :param npts: the number of points to divide the combined domain of the curves to give delx
    :type npts: int
    :param npts_interp: the number of points to interpolate at each delx step
    :type npts_interp: int
    :param debug: Used only in CLI, plots curves and c2 h(x-t) as it moves
    :type debug: bool
    :return: nc: Curve -- the convolution of the two curves c1 and c2
    """

    c1_copy = copy.deepcopy(c1)  # g(t)
    c2_copy = copy.deepcopy(c2)  # h(t)

    c2_original = copy.deepcopy(c2)

    c2_copy.x = np.flip(c2_copy.x) * float(-1)
    c2_copy.y = np.flip(c2_copy.y)

    dom_c1 = getdomain(c1_copy)
    dom_c2 = getdomain(c2_copy)

    # Start of g(t)
    xmn = dom_c1[0][1]
    # End of g(t) + domain of h(t)
    xmx = dom_c1[0][2] + (dom_c2[0][2] - dom_c2[0][1])

    # Moving end of h(t) to start of g(t)
    c2_copy.x += float(xmn) - dom_c2[0][2]

    # Delta x is domain of combined domains
    delx = (xmx - xmn) / (npts)

    def _integ(cr1, cr2, xcur, xval, yval, iter):

        while iter < npts:

            # Current overlap of g(t) and h(t)
            overlap = list(cr1.x[np.where(np.logical_and(cr1.x >= cr2.x[0], cr1.x <= cr2.x[-1]))])
            overlap.extend(list(cr2.x[np.where(np.logical_and(cr2.x >= xmn, cr2.x <= cr1.x[-1]))]))
            overlap = list(set(overlap))
            overlap.sort()

            # np.linespace() between first and last overlap
            overlap_interp_points = np.linspace(overlap[0], overlap[-1], npts_interp) if overlap else overlap

            # Adding np.linespace() points to original overlap points
            overlap.extend(overlap_interp_points)
            overlap = list(set(overlap))
            overlap.sort()

            new_y1 = np.interp(overlap, cr1.x, cr1.y)
            new_y2 = np.interp(overlap, cr2.x, cr2.y)
            new_y = new_y1 * new_y2

            area = scipy.integrate.trapezoid(new_y, overlap)

            cr2.x += delx
            xval.append(xcur)
            yval.append(area)
            iter += 1
            xcur += delx
            # return _integ(cr1, cr2, xcur + delx, xval, yval, iter)

        return xval, yval

    x, y = _integ(c1_copy, c2_copy, float(xmn) - dom_c2[0][2], [], [], 0)

    namestr = f'Conv {c1.plotname} * {c2.plotname}'
    if norm:
        namestr = f'(Conv {c1.plotname} * {c2.plotname})/Area({c2.plotname})'
        area0 = scipy.integrate.trapezoid(c2_original.y, c2_original.x)
        y /= area0

    nc = makecurve(x=x,
                   y=y,
                   name=namestr)

    return nc


def fft(c, n=None, axis=-1, norm=None):
    """
    Compute the one-dimensional discrete Fourier Transform for the x- or y-values of c.

    This function computes the one-dimensional *n*-point discrete Fourier
    Transform (DFT) with the efficient Fast Fourier Transform (FFT)
    algorithm [CT].

    Raises IndexError: if `axes` is larger than the last axis of `a`.

    Notes: FFT (Fast Fourier Transform) refers to a way the discrete Fourier
    Transform (DFT) can be calculated efficiently, by using symmetries in the
    calculated terms.  The symmetry is highest when `n` is a power of 2, and
    the transform is therefore most efficient for these sizes.

    The DFT is defined, with the conventions used in this implementation, in
    the documentation for the `numpy.fft` module.

    Citation: Cooley, James W., and John W. Tukey, 1965, "An algorithm for the
            machine calculation of complex Fourier series," *Math. Comput.*
            19: 297-301.

    >>> curves = pydvpy.read('testData.txt')

    >>> realcurve, imagcurve = pydvpy.fft(curves[0])

    :param c: Curve with x- or y-values as input array, can be complex.
    :type c: Curve
    :param n: Length of the transformed axis of the output. If `n` is smaller than
              the length of the input, the input is cropped. If it is larger, the input is padded with zeros.
              If `n` is not given, the length of the input along the axis specified by `axis` is used.
    :type n: int, optional
    :param axis: Axis over which to compute the FFT.  If not given, the last axis is used.
    :type axis: int, optional
    :param norm: Normalization mode (see `numpy.fft`). Default is None.
    :type norm: None, "ortho", optional
    :return: Curve tuple -- Two curves with the real and imaginary parts.
    """
    numpy1_10 = LooseVersion(np.__version__) >= LooseVersion("1.10.0")
    cnorm = c.normalize()
    clen = len(c.x)

    if numpy1_10:
        complex_array = np.fft.fft(cnorm.y, n, axis, norm)
        complex_array = np.fft.fftshift(complex_array)
    else:
        complex_array = np.fft.fft(cnorm.y, n, axis)
        complex_array = np.fft.fftshift(complex_array)

    val = 1.0 / (float(max(cnorm.x) - min(cnorm.x)) / 2.0)
    x = np.fft.fftfreq(clen, d=val)
    x = np.fft.fftshift(x)
    y1 = complex_array.real
    y2 = complex_array.imag

    nc1 = makecurve(x=x,
                    y=y1,
                    name='Real part FFT ' + __toCurveString(c))
    nc2 = makecurve(x=x,
                    y=y2,
                    name='Imaginary part FFT ' + __toCurveString(c))
    my(nc2, -1)

    return nc1, nc2


def derivative(c, eo=1):
    """
    Take the derivative of the curve.

    >>> curves = pydvpy.read('testData.txt')

    >>> newCurve = pydvpy.derivative(curves[0])

    :param c: The curve
    :type c: Curve
    :param eo: edge_order, gradient is calculated using N-th order accurate differences at the boundaries.
               Default: 1.
    :type eo: int, optional
    :return: A new curve representing the derivate of c
    """
    nc = makecurve(x=c.x,
                   y=np.gradient(c.y, c.x, edge_order=eo),
                   name='Derivative ' + __toCurveString(c))

    return nc


def diffMeasure(c1, c2, tol=1e-8):
    """
    Compare two curves. For the given curves a fractional difference measure and its average are computed.

    >>> curves = pydvpy.read('testData.txt')

    >>> c1, c2  = pydvpy.diffMeasure(curves[0], curves[1])

    >>> curves.append(c1)

    >>> curves.append(c2)

    >>> pydvpy.create_plot(curves, legend=True)

    :param c1: The first curve
    :type c1: Curve
    :param c2: The second curve
    :type c2: Curve
    :param tol: The tolerance
    :type tol: float
    :return: tuple -- Two curves representing the fractional difference measure and its average
    """
    ic1, ic2 = curve.getinterp(c1, c2,
                               c1.math_interp_left, c1.math_interp_right, c1.math_interp_period,
                               c2.math_interp_left, c2.math_interp_right, c2.math_interp_period)
    f1 = tol * (np.max(ic1.y) - np.min(ic1.y))
    f2 = tol * (np.max(ic2.y) - np.min(ic2.y))
    ydiff = np.abs(ic1.y - ic2.y)
    yden = (np.abs(ic1.y) + f1) + (np.abs(ic2.y) + f2)
    dx = np.max(ic1.x) - np.min(ic1.x)
    x = np.array(ic1.x)
    cdiffy = np.array(ydiff / yden)
    cdiffy[np.isnan(cdiffy)] = 0  # corner case where both curves are all zeros since f1 and f2 will also be 0

    try:
        yint = scipy.integrate.cumtrapz(cdiffy, x, initial=0.0)
    except:
        yint = scipy.integrate.cumulative_trapezoid(cdiffy, x, initial=0.0)
    cinty = np.array(yint / dx)

    cdiff = makecurve(x=x,
                      y=cdiffy,
                      name='FD = $|$' + __toCurveString(c1) + ' - ' + __toCurveString(c2) +  # noqaw504
                           '$|$/($|$' + __toCurveString(c1) + '$|$ + $|$' + __toCurveString(c2) + '$|$)')
    cint = makecurve(x=x,
                     y=cinty,
                     name='Integral(FD)/dX')

    return cdiff, cint


########################################################
##################  Curve Related  #####################  # noqa e266
########################################################

def vs(c1, c2):
    """
    Create a new curve that will plot as the range of the first curve against
    the range of the second curve.

    >>> curves = pydvpy.read('testData.txt')

    >>> c1 = pydvpy.vs(curves[0], curves[1])

    >>> curves.append(c1)

    >>> pydvpy.create_plot(curves, legend=True)

    :param c1: The first curve
    :type c1: Curve
    :param c2: The second curve
    :type c2: Curve
    :return: Curve -- the new curve
    """
    newfilename = ''
    newrecord_id = ''
    if c1.filename == c2.filename:
        newfilename = c1.filename
        if c1.record_id == c2.record_id:
            newrecord_id = c1.record_id
    ic1, ic2 = curve.getinterp(c1, c2,
                               c1.math_interp_left, c1.math_interp_right, c1.math_interp_period,
                               c2.math_interp_left, c2.math_interp_right, c2.math_interp_period)

    nc = makecurve(x=np.array(ic2.y),
                   y=np.array(ic1.y),
                   name=__toCurveString(c1) + ' vs ' + __toCurveString(c2),
                   filename=newfilename,
                   xlabel=c2.ylabel,
                   ylabel=c1.ylabel,
                   record_id=newrecord_id)

    return nc


def subsample(curvelist, stride=2, verbose=False):
    """
    Subsample the curve or list of curves, i.e., reduce to every nth value.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.subsample(curves, 4)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    :param stride: The step size through the array
    :type stride: int
    :param verbose: If True additional information will be printed to stdout
    :type verbose: bool
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        n = len(c.x)
        xss = c.x[0:n:int(stride)]
        yss = c.y[0:n:int(stride)]
        c.x = xss
        c.y = yss

        if verbose:
            print("Reduced %s from %i -> %i values." % (c.name, n, len(c.x)))


def smooth(curvelist, factor=1):
    """
    Smooth the curve to the given degree.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.smooth(curves, 4)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    :param factor: The smooth factor
    :type factor: int
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        if len(c.x) < 2:
            return 0

        x = list()
        y = list()

        for i in range(len(c.x)):
            tfactor = factor

            if i - factor < 0 and i < (len(c.x) - 1) / 2:
                tfactor = i
            elif i + factor >= len(c.x):
                tfactor = len(c.x) - 1 - i

            xsum = 0
            ysum = 0

            for j in range(-tfactor, tfactor + 1):
                xsum += c.x[i + j]
            for j in range(-factor, factor + 1):
                if 0 <= i + j < len(c.x):
                    ysum += c.y[i + j]
                elif i + j < 0:
                    ysum += c.y[0]
                else:
                    ysum += c.y[-1]

            x.append(xsum / (2 * tfactor + 1))
            y.append(ysum / (2 * factor + 1))

        c.x = np.array(x)
        c.y = np.array(y)


def errorbar(scur, cury1, cury2, curx1=None, curx2=None, mod=1):
    """
    Plot error bars on the given curve.

    >>> curves = list()

    >>> curves.append(pydvpy.span(1,10))

    >>> curves.append(pydvpy.span(1,10))

    >>> curves.append(pydvpy.span(1,10))

    >>> pydvpy.dy(curves[0], 0.25)

    >>> pydvpy.dy(curves[2], -0.25)

    >>> pydvpy.errorbar(curves[1], curves[0], curves[2])

    >>> pydvpy.create_plot(curves, legend=True)

    :param scur: The given curve
    :type scur: Curve
    :param cury1: y-error-curve
    :type cury1: Curve
    :param cury2: y+error-curve
    :type cury2: Curve
    :param curx1: x-error-curve
    :type curx1: Curve
    :param curx2: x+error-curve
    :type curx2: Curve
    :param mod: point-skip
    :type mod: int
    """
    ebar = [np.zeros(len(scur.x)), np.zeros(len(scur.x)), np.zeros(len(scur.x)), np.zeros(len(scur.x))]
    y = np.interp(scur.x, cury1.x, cury1.y)
    lowy = np.where(scur.y - y <= 0, y, scur.y)

    ebar[0] = np.array(lowy)
    ebar[1] = np.interp(scur.x, cury2.x, cury2.y)

    if curx1 is not None and curx2 is not None:
        ebar[2] = np.interp(scur.x, curx1.x, curx1.y)
        ebar[3] = np.interp(scur.x, curx2.x, curx2.y)

    for i in range(len(ebar[0])):
        if (i % int(mod) != 0) and (i != len(ebar[0]) - 1):
            ebar[0][i] = None
            ebar[1][i] = None
            ebar[2][i] = None
            ebar[3][i] = None

    scur.ebar = ebar
    scur.erange = None


def errorrange(scur, cury1, cury2):
    """
    Plot shaded error region on given curve.

    >>> curves = list()

    >>> curves.append(pydvpy.span(1,10))

    >>> curves.append(pydvpy.span(1,10))

    >>> curves.append(pydvpy.span(1,10))

    >>> pydvpy.dy(curves[0], 0.25)

    >>> pydvpy.dy(curves[2], -0.25)

    >>> pydvpy.errorrange(curves[1], curves[0], curves[2])

    >>> pydvpy.create_plot(curves, legend=True)

    :param scur: The given curve
    :type scur: Curve
    :param cury1: y-error-curve
    :type cury1: Curve
    :param cury2: y+error-curve
    :type cury2: Curve
    """

    errorbar(scur, cury1, cury2)
    scur.erange = [scur.ebar[0], scur.ebar[1]]
    scur.ebar = None


def fit(c, n=1, logx=False, logy=False):
    """
    Make a new curve that is a polynomial fit to curve c.

    >>> curves = list()

    >>> curves.append(pydvpy.span(1,10))

    >>> pydvpy.sin(curves)

    >>> curves.append(pydvpy.fit(curves[0], 2))

    >>> pydvpy.create_plot(curves, legend=True)

    :param c: The curve to fit
    :type c: Curve
    :param n: Degree of the fitting polynomial
    :type n: int
    :param logx: Take the log(x-values) before fitting if True
    :type logx: bool
    :param logy: Take the log(y-values) before fitting if True
    :type logy: bool
    :return: Curve -- The fitting polynomial
    """
    x = c.x
    y = c.y

    if logx:
        x = np.log10(x)

    if logy:
        y = np.log10(y)

    coeffs = np.polyfit(x, y, n)
    if len(coeffs) == 2:
        print("slope = ", coeffs[0], " intercept = ", coeffs[1])
    else:
        print("coefficients are: ", coeffs)

    if n == 1:
        oString = "1st "
    elif n == 2:
        oString = "2nd "
    elif n == 3:
        oString = "3rd "
    else:
        oString = "%dth " % n

    x = np.array(x)
    y = np.polyval(coeffs, x)

    if logx:
        x = 10.0**x

    if logy:
        y = 10.0**y

    nc = makecurve(x=x,
                   y=y,
                   name=oString + 'order fit to ' + __toCurveString(c))

    return nc


def getdomain(curvelist):
    """
    Get domain of the curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> domains = pydvpy.getdomain(curves)

    >>> plotname, minx, maxx = domains[0]

    :param curvelist: The given curve or list of curves
    :type curvelist: Curve or list
    :return: list -- A list of tuples where each tuple contains the curve name, minimum x, and maximum x
    """
    domains = list()
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        domains.append((__toCurveString(c), min(c.x), max(c.x)))

    return domains


def sum(curvelist):
    """
    Return sum of the x and y values of each curve.

    >>> curves = pydvpy.read('testData.txt')

    >>> sums = pydvpy.sum(curves)

    >>> plotname, sumx, sumy = sums[0]

    :param curvelist: The given curve or list of curves
    :type curvelist: Curve or list
    :return: list -- A list of tuples where each tuple contains the curve name, sum of x-values, and sum of y-values
    """
    sums = list()
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        sums.append((__toCurveString(c), np.sum(c.x), np.sum(c.y)))

    return sums


def area(curvelist):
    """
    Return area of each curve.

    >>> curves = pydvpy.read('testData.txt')

    >>> areas = pydvpy.area(curves)

    >>> plotname, area = areas[0]

    :param curvelist: The given curve or list of curves
    :type curvelist: Curve or list
    :return: list -- A list of tuples where each tuple contains the curve name and area
    """
    areas = list()
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        try:
            areas.append((__toCurveString(c), scipy.integrate.simpson(c.y, c.x)))
        except:
            areas.append((__toCurveString(c), np.trapz(c.y, c.x)))

    return areas


def disp(c, domain=True, format="g"):
    """
    Create a string formatted list of the curve's x-values if domain is True, otherwise y-values.

    >>> c = pydvpy.span(1, 10)

    >>> yvalues = pydvpy.disp(c, False)

    :param c: The given curve
    :type curvelist: Curve
    :param domain: if True, display the x-values of the curve. Otherwise, display the y-values of the curve
    :type domain: bool, optional
    :param format: String format for the data
    :type format: str, optional
    :return: list -- The list of x- or y-values as strings
    """
    ss = list()

    for i in range(len(c.x)):
        if domain:
            ss.append(f'x[{i:d}]: {c.x[i]:{format}}')
        else:
            ss.append(f'y[{i:d}]: {c.y[i]:{format}}')

    return ss


def getnumpoints(curve):
    """
    Return the given curve's number of points.

    :param curve: The given curve
    :return: int -- the number of points in curve
    """
    return len(curve.x)


def stats(curve):
    """
    Print statistics of the given curve.

    :param curve: The given curve
    """

    def find_mode(array):

        try:
            mode = scipy.stats.mode(array, keepdims=True)
        except:
            mode = scipy.stats.mode(array)
        if mode.count[0] == 1 and len(array) != 1:
            return np.nan, np.nan
        else:
            return mode.mode[0], mode.count[0]

    numx, countx = find_mode(curve.x)
    numy, county = find_mode(curve.y)

    print('\nCurve ' + curve.plotname)
    print('\n\t         X:\t              Y:')
    print(f'\n\tlength:    {len(curve.x):<15.10g}\t{len(curve.y):<15.10g}')
    print(f'\tmean:      {np.mean(curve.x):<15.10g}\t{np.mean(curve.y):<15.10g}')
    print(f'\tmedian:    {np.median(curve.x):<15.10g}\t{np.median(curve.y):<15.10g}')
    print(f'\tmode:      {numx:<15.10g}\t{numy:<15.10g}')
    print(f'\t    count: {countx:<15.10g}\t{county:<15.10g}')
    print(f'\tstd:       {np.std(curve.x):<15.10g}\t{np.std(curve.y):<15.10g}')
    print(f'\tskew:      {scipy.stats.skew(curve.x):<15.10g}\t{scipy.stats.skew(curve.y):<15.10g}')
    print(f'\tkurtosis:  {scipy.stats.kurtosis(curve.x):<15.10g}\t{scipy.stats.kurtosis(curve.y):<15.10g}')  # noqae501
    print(f'\tmin:       {np.min(curve.x):<15.10g}\t{np.min(curve.y):<15.10g}')
    print(f'\t25%:       {np.quantile(curve.x,.25):<15.10g}\t{np.quantile(curve.y,.25):<15.10g}')
    print(f'\t50%:       {np.quantile(curve.x,.50):<15.10g}\t{np.quantile(curve.y,.50):<15.10g}')
    print(f'\t75%:       {np.quantile(curve.x,.75):<15.10g}\t{np.quantile(curve.y,.75):<15.10g}')
    print(f'\tmax:       {np.max(curve.x):<15.10g}\t{np.max(curve.y):<15.10g}')
    print(f'\tsum:       {np.sum(curve.x):<15.10g}\t{np.sum(curve.y):<15.10g}')


def getrange(curvelist):
    """
    Get the range of the curve or list of curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> ranges = pydvpy.getrange(curves)

    >>> plotname, miny, maxy = ranges[0]

    :param curvelist: The given curve or list of curves
    :type curvelist: Curve or list
    :return: list -- A list of tuples where each tuple contains the curve name, minimum y, and maximum y
    """
    ranges = list()
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        ranges.append((__toCurveString(c), min(c.y), max(c.y)))

    return ranges


def getx(c, value, xmin=None, xmax=None):
    """
    Get the x values of the curve for a given y.

    >>> curves = pydvpy.read('testData.txt')

    >>> vals = pydvpy.getx(curves[0], 4)

    >>> x, y = vals[0]

    :param c: The curve
    :type c: Curve
    :param value: y value
    :type value: float
    :return: list -- A list of tuples where each tuple contains the x value, and the given y
    """
    xypairs = list()
    r = __get_sub_range(c.x, xmin, xmax)

    if float(value) < np.amin(c.y) or float(value) > np.amax(c.y):
        raise ValueError('y-value out of range')

    if r[0] < r[1]:
        for i in range(r[0], r[1] + 1):
            if c.y[i] == float(value):  # value exists in curve
                xypairs.append((c.x[i], float(value)))
            else:  # value does not exist in curve
                ymax = c.y[i]
                if i + 1 < len(c.y):
                    ymax = c.y[i + 1]

                if c.y[i] < float(value) < ymax:
                    x = np.interp(float(value), [c.y[i], ymax], [c.x[i], c.x[i + 1]])
                    xypairs.append((x, float(value)))
                elif ymax < float(value) < c.y[i]:
                    x = np.interp(float(value), [ymax, c.y[i]], [c.x[i + 1], c.x[i]])
                    xypairs.append((x, float(value)))
    else:

        # User range is in between actual curve points
        # c.x xmin xmax c.x
        xl = c.x[0] if xmin is None else xmin
        xr = c.x[-1] if xmax is None else xmax
        range_x = np.linspace(xl, xr, num=1000)
        y_interp = np.interp(range_x, c.x, c.y)
        for x, y in zip(range_x, y_interp):
            if y == value:
                xypairs.append((x, y))

        # User range has only one curve point in between
        # xmin c.x xmax
        if r[0] == r[1]:
            if c.y[r[0]] == float(value):  # value exists in curve
                xypairs.append((c.x[r[0]], float(value)))

    return xypairs


def gety(c, value):
    """
    Get the y values of the curve for a given x.

    >>> curves = pydvpy.read('testData.txt')

    >>> vals = pydvpy.gety(curves[0], 2)

    >>> x, y = vals[0]

    :param c: The curve
    :type c: Curve
    :param value: x value
    :type value: float
    :return: list -- A list of tuples where each tuple contains the y value, and the given x
    """
    xypairs = list()

    xypairs.append((float(value), np.interp(float(value), c.x, c.y,
                                            left=c.math_interp_left,
                                            right=c.math_interp_right,
                                            period=c.math_interp_period)))

    return xypairs


def line(m, b, xmin, xmax, numpts=100):
    """
    Generate a line with y = mx + b and an optional number of points.

    >>> curves = list()

    >>> curves.append(pydvpy.line(2, 5, 0, 10))

    >>> pydvpy.create_plot(curves, legend=True, stylename='ggplot')

    :param m: The slope
    :type m: float
    :param b: The y-intercept
    :type b: float
    :param xmin: The minimum x value
    :type xmin: float
    :param xmax: The maximum x value
    :type xmax: float
    :param numpts: The number of points to use for the new line
    :type numpts: int
    :return: Curve -- The curve representing the newly created line
    """
    m = float(m)
    b = float(b)
    xmin = float(xmin)
    xmax = float(xmax)
    numpts = int(numpts)

    spacing = (xmax - xmin) / (numpts - 1)
    x = list()
    y = list()

    for i in range(numpts):
        x.append(xmin)
        y.append(xmin * m + b)
        xmin += spacing

    nc = makecurve(x=x,
                   y=y,
                   name=f'Straight Line (m: {m} b: {b} xmin: {xmin} xmax: {xmax})')

    return nc


def delta(xmn, x0, xmx, npts=100):
    """
    Procedure: Generate a Dirac delta distribution such that
               Int(xmin, xmax, dt*delta(t - x0)) = 1

    :param xmn: The minimum x location
    :type xmn: float
    :param x0: The location of the unit impulse
    :type x0: float
    :param xmx: The maximum x location
    :type xmx: float
    :param npts: The number of points for the curve
    :type npts: int
    :return: The Dirac delta distribution
    :rtype: curve.Curve
    """
    # From Ultra
    dxt = xmx - xmn
    dxi = dxt / npts
    dxl = x0 - xmn
    dnl = dxl / dxi
    xv1 = (dxi * dnl) + xmn
    xv2 = xv1 + dxi
    ds = dxi**2
    yv1 = (xv2 - x0) / ds
    yv2 = (x0 - xv1) / ds
    # dxr = xmx - x0
    numl = dnl - 1
    numr = (npts - 2) - numl

    crvl = line(0, 0, xmn, xv1 - dxi, numl)
    crvr = line(0, 0, xv2 + dxi, xmx, numr)
    crvm = makecurve(x=[xv1, xv2],
                     y=[yv1, yv2])

    x = np.concatenate([crvl.x, crvm.x, crvr.x])
    y = np.concatenate([crvl.y, crvm.y, crvr.y])

    c = makecurve(x=x,
                  y=y,
                  name=f'Dirac Delta {xmn} {x0} {xmx}')

    return c


def makeextensive(curvelist):
    """
    Set the y-values such that ``y[i] *= (x[i+1] - x[i])``

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.makeextensive(curves)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        for i in range(1, len(c.y)):
            c.y[i] *= (c.x[i] - c.x[i - 1])

        c.y[0] = c.y[1]
        c.name = 'mkext(' + c.name + ')'


def makeintensive(curvelist):
    """
    Set the y-values such that y[i] /= (x[i+1] - x[i]).

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.makeintensive(curves)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        for i in range(1, len(c.y)):
            d = c.x[i] - c.x[i - 1] if (c.x[i] - c.x[i - 1]) != 0 else 0.000000001
            c.y[i] /= d

        c.y[0] = c.y[1]
        c.name = 'mkint(' + c.name + ')'


def dupx(curvelist):
    """
    Duplicate the x-values such that y = x for each of the given curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.dupx(curves)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        c.y = np.copy(c.x)


def sort(curve):
    """
    Sort the specified curve so that their points are plotted in order of ascending x values.

     >>> c = pydvpy.span(1, 10)

     >>> pydvpy.sort(c)

    :param curve: The curve to sort
    :type curve: Curve
    """
    index_array = np.argsort(curve.x)

    curve.x = curve.x[index_array]
    curve.y = curve.y[index_array]


def rev(curve):
    """
    Swap x and y values for the specified curves. You may want to sort after this one.

     >>> c = pydvpy.span(1, 10)

     >>> pydvpy.rev(c)

    :param curve: The curve to sort
    :type curve: Curve
    """
    x = np.copy(curve.y)
    y = np.copy(curve.x)

    curve.x = x
    curve.y = y


def random(curve):
    """
    Generate random y values between -1 and 1 for the specified curves.

     >>> c = pydvpy.span(1, 10)

     >>> pydvpy.random(c)

    :param curve: The curve to sort
    :type curve: Curve
    """
    curve.y = np.random.uniform(-1, 1, len(curve.y))


def xindex(curvelist):
    """
    Create curves with y-values vs. integer index values.

    >>> curves = pydvpy.read('testData.txt')

    >>> pydvpy.xindex(curves)

    >>> pydvpy.create_plot(curves, legend=True)

    :param curvelist: The curve or list of curves
    :type curvelist: Curve or list
    """
    curves = _convert_to_curvelist(curvelist)

    for c in curves:
        stop = len(c.y)
        c.x = np.linspace(1, stop, num=stop)


def appendcurves(curvelist):
    """
    Merge two or more curves over the union of their domains. Where domains overlap, take the
    average of the curve's y-values.

    >>> curves = pydvpy.read('testData.txt')

    >>> newcurve = pydvpy.appendcurve(curves)

    :param curvelist: the specified curves
    :type curvelist: list
    :return: Curve -- the merging of the two curves c1 and c2
    """
    if len(curvelist) < 2:
        if len(curvelist) == 1:
            return curvelist[0]
        else:
            return
    else:
        nc = curve.append(curvelist[0], curvelist[1])

        for i in range(2, len(curvelist)):
            nc = curve.append(nc, curvelist[i])

    suffix = ''
    for c in curvelist:
        suffix += "%s" % c.plotname

    nc.name = 'Append(' + suffix + ')'

    return nc


def max_curve(curvelist):
    """
    Construct a curve from the maximum y values of the intersection of the curves domain.

    :param curvelist: the specified curves
    :return: Curve -- a new curve with the maximum y-values over the intersection of the
             domains of the specified curves.
    """
    # Get union of domains
    if len(curvelist) <= 1:
        return None
    else:
        ux = set(curvelist[0].x).union(set(curvelist[1].x))
        for i in range(2, len(curvelist)):
            ux = set(curvelist[i].x).union(ux)

    ux = list(ux)
    ux.sort()

    # Create curve label suffix
    name_suffix = ''
    for i in range(len(curvelist)):
        name_suffix += "%s" % curvelist[i].plotname

    # Calculate max
    x = np.array(ux)

    all_data = []
    for cur in curvelist:
        all_data.append(np.interp(x, cur.x, cur.y,
                                  left=cur.math_interp_left,
                                  right=cur.math_interp_right,
                                  period=cur.math_interp_period))

    nc = makecurve(x=x,
                   y=np.max(all_data, axis=0),
                   name='Max(' + name_suffix + ')')

    return nc


def min_curve(curvelist):
    """
    Construct a curve from the minimum y values of the intersection of the curves domain.

    :param curvelist: the specified curves
    :return: Curve -- a new curve with the minimum y-values over the intersection of the
             domains of the specified curves.
    """
    # Get union of domains
    if len(curvelist) <= 1:
        return None
    else:
        ux = set(curvelist[0].x).union(set(curvelist[1].x))
        for i in range(2, len(curvelist)):
            ux = set(curvelist[i].x).union(ux)

    ux = list(ux)
    ux.sort()

    # Create curve label suffix
    name_suffix = ''
    for i in range(len(curvelist)):
        name_suffix += "%s" % curvelist[i].plotname

    # Calculate min
    x = np.array(ux)

    all_data = []
    for cur in curvelist:
        all_data.append(np.interp(x, cur.x, cur.y,
                                  left=cur.math_interp_left,
                                  right=cur.math_interp_right,
                                  period=cur.math_interp_period))

    nc = makecurve(x=x,
                   y=np.min(all_data, axis=0),
                   name='Min(' + name_suffix + ')')

    return nc


def average_curve(curvelist):
    """
    Average the specified curves over the intersection of their domains.

    :param curvelist: the specified curves
    :return: Curve -- a new curve with the average values over the intersection of the domains of the specified curves.
    """
    # Get union of domains
    if len(curvelist) <= 1:
        return None
    else:
        ux = set(curvelist[0].x).union(set(curvelist[1].x))
        for i in range(2, len(curvelist)):
            ux = set(curvelist[i].x).union(ux)

    ux = list(ux)
    ux.sort()

    # Create curve label suffix
    name_suffix = ''
    for i in range(len(curvelist)):
        name_suffix += "%s" % curvelist[i].plotname

    # Calculate average
    x = np.array(ux)

    all_data = []
    for cur in curvelist:
        all_data.append(np.interp(x, cur.x, cur.y,
                                  left=cur.math_interp_left,
                                  right=cur.math_interp_right,
                                  period=cur.math_interp_period))

    nc = makecurve(x=x,
                   y=np.mean(all_data, axis=0),
                   name='Average(' + name_suffix + ')')

    return nc


########################################################
################## Private Methods #####################  # noqa e266
########################################################

def __fft(c):
    """
    Compute the Fast Fourier Transform of a real curve.

    :param c: The curve
    :type c: Curve
    :return: tuple - two curves, one with the real part and the other with the imaginary part for their y-values.
    """
    cnorm = c.normalize()
    clen = len(c.x)

    complex_array = np.fft.fft(cnorm.y)

    nc1y = complex_array.real
    nc1x = np.linspace(min(cnorm.x), max(cnorm.x), len(nc1y))

    nc2y = complex_array.imag
    nc2x = np.linspace(min(cnorm.x), max(cnorm.x), clen)

    nc1 = makecurve(x=nc1x,
                    y=nc1y,
                    name='Real part FFT ' + __toCurveString(c))
    nc2 = makecurve(x=nc2x,
                    y=nc2y,
                    name='Imaginary part FFT ' + __toCurveString(c))

    my(nc2, -1)

    return nc1, nc2


def __ifft(cr, ci):
    """
    Compute the 1D inverse discrete Fourier Transform.

    :param cr: Curve containing the real part of a complex number as it's y-values.
    :type c: Curve
    :param ci: Curve containing the imaginary part of a complex number as it's y-values
    :type c: Curve
    :return: tuple - two curves, one with the real part and the other with the imaginary part for their y-values.
    """
    carray = cr.y + 1j * ci.y

    numpy1_10 = LooseVersion(np.__version__) >= LooseVersion("1.10.0")

    if numpy1_10:
        complex_array = np.fft.ifft(carray)
    else:
        complex_array = np.fft.ifft(carray)

    # nc1.x = np.array(cr.x)
    nc1y = complex_array.real
    nc1x = np.linspace(min(cr.x), max(cr.x), len(nc1y))

    # nc2.x = np.array(ci.x)
    nc2y = complex_array.imag
    nc2x = np.linspace(min(ci.x), max(ci.x), len(nc2y))

    nc1 = makecurve(x=nc1x,
                    y=nc1y,
                    name='Real part iFFT ' + __toCurveString(cr))
    nc2 = makecurve(x=nc2x,
                    y=nc2y,
                    name='Imaginary part iFFT ' + __toCurveString(ci))

    return nc1, nc2


def __complex_times(ra, ia, rb, ib):
    """
    Perform the complex product of the given pairs of curves representing the real and imaginary components.

    :param ra: Curve containing the real part
    :type ra: Curve
    :param ia: Curve containing the imaginary part
    :type ia: Curve
    :param rb: Curve containing the real part
    :type rb: Curve
    :param ib: Curve containing the imaginary part
    :type ib: Curve
    :return: tuple - pair of curves representing the complex conjugate
    """
    rs1 = ra * rb
    rs2 = ia * ib
    is1 = ra * ib
    is2 = ia * rb
    sa = rs1 - rs2
    sb = is1 + is2

    return sa, sb


def __get_sub_range(x, low, high):
    """
    Returns a tuple with the index of the first value in x greater than low and
    the index of the first value in x less than high.

    :param x: The array of x-values
    :type x: array
    :param low: The lower definite integral interval value
    :type low: float
    :param high: The upper definite integral interval value
    :type high: float
    :return: tuple -- a tuple with the indices of the first value in x that is
                      greater than low and the first value in x less than high.
                      If low or high is not specified, the corresponding return
                      will be None.
    """
    min_idx = np.where(x >= low)[0][0] if low is not None else 0
    max_idx = np.where(x <= high)[0][-1] if high is not None else len(x) - 1
    return min_idx, max_idx


def __toCurveString(c):
    """
    Returns the string description of the curve.

    :param c: The curve
    :type c: Curve
    :return: str -- The curve's name if not empty, otherwise, the curve's plotname
    """
    if c.name:
        return c.name

    return c.plotname


def __loadcolumns(fname, xcol):
    """
     Load a column oriented text data file, add parsed curves to the curvelist.
     '#' is the comment character.  The last comment line must be the column
     labels.  We assume the first column is the x-data, every other column is y-data.
     We also assume all columns are the same length.

    :param fname: The column oriented (.gnu) file
    :type fname: str
    :param xcol: x-column number for column oriented (.gnu) files
    :type xcol: int
    :returns: list -- the list of curves from the file
    """
    curvelist = []

    try:
        f = open(fname, 'r')
        lines = f.readlines()
        iLine = 0
        for line in lines:
            if line.strip()[0] != '#':
                break
            iLine += 1
        if iLine == 0:
            print('WARNING: columns have no labels, labels will be assigned...someday')
        alllabels = lines[iLine - 1][1:]  # drop leading '#' character
        if '"' in alllabels:
            colLabels = [x for x in alllabels.split('"')[1:-1] if len(x.replace(" ", "")) > 0]
        else:
            colLabels = alllabels.split()
        # check that we have a label for every column
        if len(colLabels) != len(lines[iLine].split()) and iLine > 0:
            raise RuntimeError('Sorry, right now PyDV requires you to have a label for every column.')
        # We assume some column is the x-data, every other column
        # is y-data
        numcurves = len(lines[iLine].split()) - 1

        # Make the curves, append them to self.curvelist.
        # First, get data into lists of numbers
        # numDataLines = len(lines) - iLine
        localCurves = []
        for i in range(numcurves + 1):
            localCurves.append([])
        # FIGURE OUT COOL WAY TO DO THIS LATER: localCurves = (numcurves+1)*[[]]
        for line in lines[iLine:]:
            nums = [float(n) for n in line.split()]
            assert len(nums) == numcurves + 1
            for colID in range(numcurves + 1):
                localCurves[colID].append(nums[colID])
        # convert lists to numpy arrays
        for colID in range(numcurves):
            localCurves[colID] = np.array(localCurves[colID])
        # Make Curve objects, add to curvelist
        for colID in range(numcurves + 1):
            if colID != xcol:
                c = makecurve(x=localCurves[xcol],
                              y=localCurves[colID],
                              name=colLabels[colID],
                              filename=fname)
                print("Appended curve: ", colLabels[colID], len(c.x), len(c.y))
                curvelist.append(c)
        # tidy up
        f.close()
    # anticipate failure!
    except IOError:
        traceback.print_exc(file=sys.stdout)
        print('could not load file: ' + fname)
    except ValueError:
        print('invalid pydv file: ' + fname)

    return curvelist


def __loadpdb(fname, fpdb):
    curvelist = []

    try:
        curveList = fpdb.ls('curve*')
        if (len(curveList) == 0):
            raise ValueError
        for cname in curveList:
            curveid = fpdb.read(cname).strip('\x00').split('|')
            if (len(curveid) != 8):
                raise IOError
            current = makecurve(x=np.array(fpdb.read(curveid[3])),
                                y=np.array(fpdb.read(curveid[4])),
                                name=fpdb.read(curveid[1]).strip('\x00'),
                                filename=fname)
            curvelist.append(current)

            fpdb.close()
    except IOError:
        print('could not load file: ' + fname)
    except ValueError:
        print('invalid pydv file: ' + fname)

    return curvelist


def _get_linelocs_from_text_ultra_grep(fname):

    # first find all the character offsets of the # lines in the ULTRA file
    stdout_val = subprocess.check_output(['/usr/bin/grep',
                                          '--byte-offset',
                                          '--only-matching',
                                          '--text',
                                          '^#',
                                          fname],
                                         stderr=subprocess.STDOUT).decode('utf8')
    locs = [int(line.strip().split(':')[0]) for line in stdout_val.split('\n')[:-1]]  # last is just empty newline

    # now get the last character offset in the ULTRA file
    stdout_val = subprocess.check_output(['/usr/bin/wc',
                                          '-c',
                                          fname],
                                         stderr=subprocess.PIPE).decode('utf8')
    locs.append(int(stdout_val.split()[0]))  # append end of file byte location

    return locs


def _get_linelocs_from_text_ultra(fname):
    # These are byte locations not actual line locations, each standard ASCII character is one byte.

    with open(fname, 'r') as openfile:

        loc = 0  # byte tracker for whole file
        locs = []  # location list of titles or comments

        for line in openfile:

            if line.strip()[:1] == '#':  # title or comment
                locs.append(loc)  # append title or comment byte location to location list

            loc += len(line)  # add number of bytes in line to byte tracker

        locs.append(loc)  # append end of file byte location to location list

        return locs


def _get_curve_from_text_ultra_perproc(input_tuple):
    fname, locs, idx, regex = input_tuple

    # Defaults
    xlabel = ''
    ylabel = ''
    step = False
    step_original_x = np.empty(0)
    step_original_y = np.empty(0)
    xticks_labels = {}

    try:
        with open(fname, 'r') as openfile:

            # Finds byte location
            openfile.seek(locs[idx])

            # ONLY reads content of single curve based on byte location
            content = openfile.read(locs[idx + 1] - locs[idx])

            # Creates a list of lines that splits on newline and creates x y pairs
            lcont = list(filter(lambda line: len(line) > 0, map(lambda line: line.strip(), content.split('\n'))))

            if len(lcont) < 2:  # at least one data point
                return None

            ##############
            # Curve name #
            ##############
            name = lcont[0].split("# xlabel")[0].split("# ylabel")[0].split("#xlabel")[0].split("#ylabel")[0][1:].strip() # noqae501
            if regex:
                if regex.search(name):
                    print(f'Found match: {name}')
                else:
                    return None

            #################
            # x and y label #
            #################
            split_line_label = re.split(r'#', str.strip(lcont[0]))
            for split in split_line_label:
                if re.search('[a-zA-Z]', split):
                    if 'xlabel' in split:
                        xlabel = split.replace('xlabel', '').strip()
                    if 'ylabel' in split:
                        ylabel = split.replace('ylabel', '').strip()

            ########
            # DATA #
            ########

            # xticklabel or horizontal data
            if len(lcont[1].split()) > 2:

                # horizontal data see tests/diff_formats.txt format 3a and format 3b
                try:

                    float(lcont[1].rsplit(None, 1)[0].split()[0])

                    # Split the horizontal data into x y pairs
                    pairs = []
                    for line in lcont[1:]:
                        numbers = [x for x in line.split() if x]
                        line_pairs = ['{} {}'.format(numbers[i], numbers[i + 1]) for i in range(0, len(numbers), 2)]
                        pairs.extend(line_pairs)

                    lcont = [lcont[0]]
                    lcont.extend(pairs)

                # X tick label data see tests/diff_formats.txt My curve6
                except ValueError:
                    pass

            # Splits newline x y pairs into individual x y
            if lcont[-1] != 'end':
                v = [item for s in lcont[1:] for item in s.rsplit(None, 1)]
            else:
                v = [item for s in lcont[1:-1] for item in s.rsplit(None, 1)]

            xvals = v[::2]
            yvals = v[1::2]

            # Numerical data
            try:
                float(xvals[0])

            # X tick label data
            except:

                xticks = list(set(xvals))
                xticks.sort()
                xticks_dict = {}

                for i, xtick in enumerate(xticks):
                    xticks_dict[xtick] = i

                xvals = [xticks_dict[xtick] for xtick in xvals]

                xticks_labels = xticks_dict

            # Step Data
            if len(xvals) != len(yvals):
                step_original_x = np.array(xvals, dtype=float)
                step_original_y = np.array(yvals, dtype=float)

                yvals.append(yvals[-1])
                xvals = np.array(xvals, dtype=float).repeat(2)[1:]
                yvals = np.array(yvals, dtype=float).repeat(2)[:-1]
                step = True

            # Numerical Data
            else:
                xvals = np.array(xvals, dtype=float)
                yvals = np.array(yvals, dtype=float)

            return makecurve(x=xvals, y=yvals, name=name, filename=fname,
                             xlabel=xlabel, ylabel=ylabel,
                             step=step, step_original_x=step_original_x, step_original_y=step_original_y,
                             xticks_labels=xticks_labels)
    except Exception as e:
        print(str(e))
        return None


########################################################
################# Curve Comparisons ####################  # noqa e266
########################################################

def overlap_interp(cr1, cr2, npts_interp=0):
    """
    Get the a set of overlapping interpolated curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> cr1_interp, cr2_interp = pydvpy.overlap_interp(curves[0], curves[1], npts_interp=100)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts_interp: The number of points in the interpolation
    :type npts_interp: int
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
    """
    # Current overlap of cr1 and cr2
    overlap = list(cr1.x[np.where(np.logical_and(cr1.x >= cr2.x[0], cr1.x <= cr2.x[-1]))])
    overlap.extend(list(cr2.x[np.where(np.logical_and(cr2.x >= cr1.x[0], cr2.x <= cr1.x[-1]))]))
    overlap = list(set(overlap))
    overlap.sort()

    if npts_interp:
        # np.linespace() between first and last overlap
        overlap_interp_points = np.linspace(overlap[0], overlap[-1], npts_interp)

        # Adding np.linespace() points to original overlap points
        overlap.extend(overlap_interp_points)
        overlap = list(set(overlap))
        overlap.sort()

    new_y1 = np.interp(overlap, cr1.x, cr1.y)
    new_y2 = np.interp(overlap, cr2.x, cr2.y)

    cr1_interp = makecurve(x=np.array(overlap),
                           y=new_y1,
                           name=cr1.name + " overlap_interp")
    cr2_interp = makecurve(x=np.array(overlap),
                           y=new_y2,
                           name=cr2.name + " overlap_interp")

    return cr1_interp, cr2_interp


def AvgDiff(cr1, cr2, npts=0, tol=1e80):
    """
    Calculate the difference between the overlapping interpolated curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed = pydvpy.AvgDiff(curves[0],
            curves[1], npts=0, tol=1e80)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts: The number of points in the interpolation
    :type npts: int
    :param tol: The tolerance for failure
    :type tol: float
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
        - differences (:py:class:`Curve`) - The differences curve cr1_interp - cr2_interp
        - avgDiff (:py:class:`float`) - The average difference
        - maxDiff (:py:class:`float`) - The maximum difference
        - failed_curve (:py:class:`Curve`) - The failed points curve
        - failed (:py:class:`bool`) - If the `differences` failed the tolerance or not
    """
    cr1_interp, cr2_interp = overlap_interp(cr1, cr2, npts)

    differences = cr1_interp - cr2_interp
    avgDiff = np.mean(differences.y)
    maxDiff = np.max(differences.y)
    differences = makecurve(x=differences.x,
                            y=differences.y,
                            name=f"Differences avgDiff={avgDiff:.6e} maxDiff={maxDiff:.6e}")

    failed_points = np.where(differences.y > tol)
    failed_curve = makecurve(x=differences.x[failed_points],
                             y=differences.y[failed_points],
                             name=f"Failed points npts={len(failed_points[0])} with tol={tol}")
    failed_curve.scatter = True

    if failed_points[0].size:
        failed = True
    else:
        failed = False

    return cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed


def AbsDiff(cr1, cr2, npts=0, tol=1e80):
    """
    Calculate the absolute difference between the overlapping interpolated curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed = pydvpy.AbsDiff(curves[0],
            curves[1], npts=0, tol=1e80)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts: The number of points in the interpolation
    :type npts: int
    :param tol: The tolerance for failure
    :type tol: float
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
        - differences (:py:class:`Curve`) - The differences curve
        - avgDiff (:py:class:`float`) - The average difference
        - maxDiff (:py:class:`float`) - The maximum difference
        - failed_curve (:py:class:`Curve`) - The failed points curve
        - failed (:py:class:`bool`) - If the `differences` failed the tolerance or not
    """
    cr1_interp, cr2_interp = overlap_interp(cr1, cr2, npts)

    differences = cr1_interp - cr2_interp
    differences.y = np.abs(differences.y)
    avgDiff = np.mean(differences.y)
    maxDiff = np.max(differences.y)
    differences = makecurve(x=differences.x,
                            y=differences.y,
                            name=f"Differences avgDiff={avgDiff:.6e} maxDiff={maxDiff:.6e}")

    failed_points = np.where(differences.y > tol)
    failed_curve = makecurve(x=differences.x[failed_points],
                             y=differences.y[failed_points],
                             name=f"Failed points npts={len(failed_points[0])} with tol={tol}")
    failed_curve.scatter = True

    if failed_points[0].size:
        failed = True
    else:
        failed = False

    return cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed


def RelDiff(cr1, cr2, npts=0, tol=1e80):
    """
    Calculate the relative difference between the overlapping interpolated curves.

    >>> curves = pydvpy.read('testData.txt')

    >>> cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed = pydvpy.RelDiff(curves[0],
            curves[1], npts=0, tol=1e80)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts: The number of points in the interpolation
    :type npts: int
    :param tol: The tolerance for failure
    :type tol: float
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
        - differences (:py:class:`Curve`) - The differences curve
        - avgDiff (:py:class:`float`) - The average difference
        - maxDiff (:py:class:`float`) - The maximum difference
        - failed_curve (:py:class:`Curve`) - The failed points curve
        - failed (:py:class:`bool`) - If the `differences` failed the tolerance or not
    """
    cr1_interp, cr2_interp = overlap_interp(cr1, cr2, npts)

    c1max = np.max(cr1.y)
    c1min = np.min(cr1.y)

    c2max = np.max(cr2.y)
    c2min = np.min(cr2.y)

    c1diff = c1max - c1min
    c2diff = c2max - c2min

    c1Adj = tol * c1diff
    c2Adj = tol * c2diff

    c1new = np.abs(cr1_interp.y) + c1Adj
    c2new = np.abs(cr2_interp.y) + c2Adj

    absDiff = np.abs(cr1_interp.y - cr2_interp.y)

    scale = c1new + c2new + 1e-80

    relDiff = absDiff / scale

    avgDiff = np.mean(relDiff)
    maxDiff = np.max(relDiff)
    differences = makecurve(x=cr1_interp.x,
                            y=relDiff,
                            name=f"Differences avgDiff={avgDiff:.6e} maxDiff={maxDiff:.6e}")

    failed_points = np.where(relDiff > tol)
    failed_curve = makecurve(x=differences.x[failed_points],
                             y=differences.y[failed_points],
                             name=f"Failed points npts={len(failed_points[0])} with tol={tol}")
    failed_curve.scatter = True

    if failed_points[0].size:
        failed = True
    else:
        failed = False

    return cr1_interp, cr2_interp, differences, avgDiff, maxDiff, failed_curve, failed


def AbsAndRelDiff(cr1, cr2, npts=0, abs_tol=1e80, rel_tol=1e80):
    """
    Calculate the absolute and relative difference between the overlapping interpolated curves.
    Returns the updated AND statement for `failed` along with curves from AbsDiff and RelDiff

    >>> curves = pydvpy.read('testData.txt')

    >>> (cr1_interp, cr2_interp,
         differences_Abs, avgDiff_Abs, maxDiff_Abs, failed_curve_Abs, failed_Abs
         differences_Rel, avgDiff_Rel, maxDiff_Rel, failed_curve_Rel, failed_Rel
         failed_AND) = pydvpy.AbsAndRelDiff(curves[0], curves[1], npts=0, abs_tol=1e80, rel_tol=1e80)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts: The number of points in the interpolation
    :type npts: int
    :param abs_tol: The tolerance for absolute difference failure
    :type abs_tol: float
    :param rel_tol: The tolerance for relative difference failure
    :type rel_tol: float
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
        - differences_Abs (:py:class:`Curve`) - The differences curve for AbsDiff
        - avgDiff_Abs (:py:class:`float`) - The average difference for AbsDiff
        - maxDiff_Abs (:py:class:`float`) - The maximum difference for AbsDiff
        - failed_curve_Abs (:py:class:`Curve`) - The failed points curve for AbsDiff
        - failed_Abs (:py:class:`bool`) - If the `differences` failed the tolerance or not for AbsDiff
        - differences_Rel (:py:class:`Curve`) - The differences curve for RelDiff
        - avgDiff_Rel (:py:class:`float`) - The average difference for RelDiff
        - maxDiff_Rel (:py:class:`float`) - The maximum difference for RelDiff
        - failed_curve_Rel (:py:class:`Curve`) - The failed points curve for RelDiff
        - failed_Rel (:py:class:`bool`) - If the `differences` failed the tolerance or not for RelDiff
        - failed_AND (:py:class:`bool`) - If the `differences` failed the tolerance or not for AbsDiff AND RelDiff
    """

    (cr1_interp, cr2_interp,
     differences_Abs, avgDiff_Abs,
     maxDiff_Abs, failed_curve_Abs,
     failed_Abs) = AbsDiff(cr1, cr2, npts, abs_tol)

    (cr1_interp, cr2_interp,
     differences_Rel, avgDiff_Rel,
     maxDiff_Rel, failed_curve_Rel,
     failed_Rel) = RelDiff(cr1, cr2, npts, rel_tol)

    if failed_Abs and failed_Rel:
        failed_AND = True
    else:
        failed_AND = False

    return (cr1_interp, cr2_interp,
            differences_Abs, avgDiff_Abs, maxDiff_Abs, failed_curve_Abs, failed_Abs,
            differences_Rel, avgDiff_Rel, maxDiff_Rel, failed_curve_Rel, failed_Rel,
            failed_AND)


def AbsOrRelDiff(cr1, cr2, npts=0, abs_tol=1e80, rel_tol=1e80):
    """
    Calculate the absolute and relative difference between the overlapping interpolated curves.
    Returns the updated OR statement for `failed` along with curves from AbsDiff and RelDiff

    >>> curves = pydvpy.read('testData.txt')

    >>> (cr1_interp, cr2_interp,
         differences_Abs, avgDiff_Abs, maxDiff_Abs, failed_curve_Abs, failed_Abs
         differences_Rel, avgDiff_Rel, maxDiff_Rel, failed_curve_Rel, failed_Rel
         failed_OR) = pydvpy.AbsOrRelDiff(curves[0], curves[1], npts=0, abs_tol=1e80, rel_tol=1e80)

    :param cr1: The first curve
    :type cr1: Curve
    :param cr2: The second curve
    :type cr2: Curve
    :param npts: The number of points in the interpolation
    :type npts: int
    :param abs_tol: The tolerance for absolute difference failure
    :type abs_tol: float
    :param rel_tol: The tolerance for relative difference failure
    :type rel_tol: float
    :returns:
        - cr1_interp (:py:class:`Curve`) - The first overlapping interpolated curve
        - cr2_interp (:py:class:`Curve`) - The second overlapping interpolated curve
        - differences_Abs (:py:class:`Curve`) - The differences curve for AbsDiff
        - avgDiff_Abs (:py:class:`float`) - The average difference for AbsDiff
        - maxDiff_Abs (:py:class:`float`) - The maximum difference for AbsDiff
        - failed_curve_Abs (:py:class:`Curve`) - The failed points curve for AbsDiff
        - failed_Abs (:py:class:`bool`) - If the `differences` failed the tolerance or not for AbsDiff
        - differences_Rel (:py:class:`Curve`) - The differences curve for RelDiff
        - avgDiff_Rel (:py:class:`float`) - The average difference for RelDiff
        - maxDiff_Rel (:py:class:`float`) - The maximum difference for RelDiff
        - failed_curve_Rel (:py:class:`Curve`) - The failed points curve for RelDiff
        - failed_Rel (:py:class:`bool`) - If the `differences` failed the tolerance or not for RelDiff
        - failed_OR (:py:class:`bool`) - If the `differences` failed the tolerance or not for AbsDiff OR RelDiff
    """

    (cr1_interp, cr2_interp,
     differences_Abs, avgDiff_Abs,
     maxDiff_Abs, failed_curve_Abs,
     failed_Abs) = AbsDiff(cr1, cr2, npts, abs_tol)

    (cr1_interp, cr2_interp,
     differences_Rel, avgDiff_Rel,
     maxDiff_Rel, failed_curve_Rel,
     failed_Rel) = RelDiff(cr1, cr2, npts, rel_tol)

    if failed_Abs or failed_Rel:
        failed_OR = True
    else:
        failed_OR = False

    return (cr1_interp, cr2_interp,
            differences_Abs, avgDiff_Abs, maxDiff_Abs, failed_curve_Abs, failed_Abs,
            differences_Rel, avgDiff_Rel, maxDiff_Rel, failed_curve_Rel, failed_Rel,
            failed_OR)


def addPoint(curvelist, x, y):
    """
    Appends both x and y coordinates to the end of each list of values of a Curve.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curves = pydvpy.addPoint(curves, x=10, y=11) OR

     >>> new_curves = pydvpy.addPoint(curves[0], x=10, y=11)

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param x: The point to append to the x array
    :type x: float
    :param y: The point to append to the y array
    :type y: float
    :return: Curve -- A list of new curves with the appended point
    """
    new_curves = list()
    for cur in curvelist:
        new_curves.append(makecurve(x=np.append(cur.x, x),
                                    y=np.append(cur.y, y),
                                    name=f"{cur.name} appended x={x} and y={y}"))
    return new_curves


def getxi(curvelist, i):
    """
    Returns a discrete data point from the xData array

     >>> curves = pydvpy.read('testData.txt')

     >>> xvals = pydvpy.getxi(curves, 42) OR

     >>> xvals = pydvpy.getxi(curves[0], 42)

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param i: The index of the point to return
    :type i: int
    :return: list -- A list of x values at the given index
    """
    xvals = list()

    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        xvals.append(cur.x[i])

    return xvals


def getyi(curvelist, i):
    """
    Returns a discrete data point from the yData array

     >>> curves = pydvpy.read('testData.txt')

     >>> yvals = pydvpy.getyi(curves, 42) OR

     >>> yvals = pydvpy.getyi(curves[0], 42)

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param i: The index of the point to return
    :type i: int
    :return: list -- A list of y values at the given index
    """
    yvals = list()

    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        yvals.append(cur.y[i])

    return yvals


def crop_and_interp(curvelist, npts=None, idomian=None):
    """
    Returns new curves that are cropped and interpolated.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curves = pydvpy.crop_and_interp(curves, 100, [24, 42]) OR

     >>> new_curves = pydvpy.crop_and_interp(curves[0], 100, [24, 42])

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param npts: Number of extra points for interpolation
    :type npts: int
    :param idomain: Index domain for cropped curve
    :type idomain: list
    :return: Curve -- A list of new curves that are cropped and interpolated
    """
    new_curves = list()
    for cur in curvelist:
        name = cur.name
        if idomian is None:
            id = [0, len(cur.x)]
        else:
            name += f" Cropped indices={idomian}"
            id = idomian
        if npts is not None:
            name += f" Interpolated npts={npts}"
            new_x = np.linspace(cur.x[id[0]], cur.x[id[1]], num=npts)
        else:
            new_x = cur.x[id[0]:id[1]]
        new_y = np.interp(new_x, cur.x, cur.y)

        new_curves.append(makecurve(x=new_x,
                                    y=new_y,
                                    name=name))
    return new_curves


def shift(curvelist, x=0, y=0):
    """
    Shifts curves by an x and y value.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curves = pydvpy.shift(curves, x=10, y=11) OR

     >>> new_curves = pydvpy.shift(curves[0], x=10, y=11)

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param x: The point to shift the x array
    :type x: float
    :param y: The point to shift the y array
    :type y: float
    :return: Curve -- A list of new curves with the shifted x and y values
    """
    new_curves = list()
    for cur in curvelist:
        new_curves.append(makecurve(x=cur.x + x,
                                    y=cur.y + y,
                                    name=f"{cur.name} shifted by X={x} and Y={y}"))
    return new_curves


def swapCoords(curvelist):
    """
    Swap x and y values for the specified curves.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curves = pydvpy.swapCoords(curves) OR

     >>> new_curves = pydvpy.swapCoords(curves[0])

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :return: Curve -- A list of new curves with the swapped x and y values
    """
    new_curves = list()
    for cur in curvelist:
        new_curves.append(makecurve(x=cur.y,
                                    y=cur.x,
                                    name=f"{cur.name} swapped coordinates"))
    return new_curves


def ClipValues(curvelist, ymin, ymax):
    """
    Clip the y values for the specified curves using np.clip().

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curves = pydvpy.ClipValues(curves, ymin=3, ymax=7) OR

     >>> new_curves = pydvpy.ClipValues(curves[0], ymin=3, ymax=7)

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :param ymin: The minimum y value
    :type ymin: float
    :param ymax: The maximum y value
    :type ymax: float
    :return: Curve -- A list of new curves with the clipped y values
    """
    new_curves = list()
    for cur in curvelist:
        newy = np.clip(cur.y, ymin, ymax)
        new_curves.append(makecurve(x=cur.x,
                                    y=newy,
                                    name=f"{cur.name} clipped ymin={ymin} and ymax={ymax}"))
    return new_curves


def LinearFit(c, x):
    """
    This method takes in a value for x and uses linear interpolation to return
    the cooresponding y value for the given data

    >>> curves = pydvpy.read('testData.txt')

    >>> vals = pydvpy.LinearFit(curves[0], 2)

    >>> x, y = vals[0]

    :param c: The curve
    :type c: Curve
    :param value: x value
    :type value: float
    :return: list -- A list of tuples where each tuple contains the y value, and the given x
    """
    xypairs = list()

    def findSegment(x):
        iLeft = 0
        iRight = len(c.x) - 1
        while 1:
            if (iRight - iLeft) <= 1:
                return iLeft
            i = (iLeft + iRight) // 2
            if x < c.x[i]:
                iRight = i
            else:
                iLeft = i

    i = findSegment(x)
    slope = (c.y[i + 1] - c.y[i]) / (c.x[i + 1] - c.x[i])
    y = slope * (x - c.x[i]) + c.y[i]
    xypairs.append((float(x), y))
    return xypairs


def PolyFit(c, value, order):
    """
    Using a Polynomial Fit, get the y values of the curve for a given x.

    >>> curves = pydvpy.read('testData.txt')

    >>> vals = pydvpy.PolyFit(curves[0], 2)

    >>> x, y = vals[0]

    :param c: The curve
    :type c: Curve
    :param value: x value
    :type value: float
    :param order: Order of polynomial
    :type order: int
    :return: list -- A list of tuples where each tuple contains the y value, and the given x
    """
    xypairs = list()
    poly = np.poly1d(np.polyfit(c.x, c.y, order))
    y = poly(value)
    xypairs.append((float(value), y))
    return xypairs


def SplineFit(c, value, order, smooth):
    """
    Using a Spline Fit, get the y values of the curve for a given x.

    >>> curves = pydvpy.read('testData.txt')

    >>> vals = pydvpy.SplineFit(curves[0], 2, 3)

    >>> x, y = vals[0]

    :param c: The curve
    :type c: Curve
    :param value: x value
    :type value: float
    :param order: Order for spline
    :type order: int
    :param smooth: Smoothing condition for spline
    :type smooth: int
    :return: list -- A list of tuples where each tuple contains the y value, and the given x
    """
    xypairs = list()
    spline = scipy.interpolate.splrep(c.x, c.y, k=order, s=smooth)
    y = scipy.interpolate.splev(value, spline, der=0)
    xypairs.append((float(value), y))
    return xypairs


def MovingAvg(c, npts):
    """
    This filter returns a smooth a curve using a moving average technique.
    The function takes N points and reassigns each point in a curve as
    the average of the N points around it.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curve = pydvpy.MovingAvg(curves[0], 5)

    :param c: The Curve
    :type c: Curve
    :param npts: Number of points for the moving average
    :type npts: int
    :return: Curve -- A new smoothed curve
    """
    xset = c.x
    yset = c.y
    newvals = []
    avgvals = []
    count = 0
    avgsum = 0
    for i in range(npts // 2):
        avgvals.append(yset[count])
        avgsum += yset[count]
        count += 1

    for i in range(len(yset)):
        if count < len(yset):
            avgvals.append(yset[count])
            avgsum += yset[count]
            count += 1
        newvals.append(avgsum / len(avgvals))
        if len(avgvals) == npts or count >= len(yset):
            avgsum -= avgvals.pop(0)

    return makecurve(x=xset,
                     y=newvals,
                     name=f"{c.name} MovingAvg npts={npts}")


def GuassianFilter(c, sigma):
    """
    This smooths a curve using a Gaussian filter.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curve = pydvpy.GuassianFilter(curves[0], 5)

    :param c: The Curve
    :type c: Curve
    :param sigma: Standard deviation for Gaussian kernel
    :type sigma: float
    :return: Curve -- A new smoothed curve
    """
    return makecurve(x=c.x,
                     y=scipy.ndimage.gaussian_filter(c.y, sigma),
                     name=f"{c.name} GuassianFilter sigma={sigma}")


def UniformFilter(c, npts):
    """
    This smooths a curve using a Uniform filter.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curve = pydvpy.UniformFilter(curves[0], 5)

    :param c: The Curve
    :type c: Curve
    :param npts: The sizes of the uniform filter
    :type npts: int
    :return: Curve -- A new smoothed curve
    """
    return makecurve(x=c.x,
                     y=scipy.ndimage.uniform_filter(c.y, size=npts),
                     name=f"{c.name} UniformFilter npts={npts}")


def MedianFilter(c, npts):
    """
    This smooths a curve using a Median filter.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curve = pydvpy.MedianFilter(curves[0], 5)

    :param c: The Curve
    :type c: Curve
    :param npts: The sizes of the median filter
    :type npts: int
    :return: Curve -- A new smoothed curve
    """
    return makecurve(x=c.x,
                     y=scipy.ndimage.median_filter(c.y, size=npts),
                     name=f"{c.name} MedianFilter npts={npts}")


def TimeShift(cbase, cset, tol=1e80, pairID=0, version=0):
    """
    This filter will take a curve and return a time shifted curve.
    It uses the slope of the baseline curve to find the time offset
    for each point of the new curve such that the new curve would
    match the baseline. It uses the time offset at the point with
    the largest slope.
    This only works well for small offsets.
    It zeros out the slope when the baseline and new curve have slopes
    of opposite sign when searching for the max slope.

     >>> curves = pydvpy.read('testData.txt')

     >>> new_curve = pydvpy.TimeShift(curves[0], curves[1], tol=1e80, pairID=0, version=0)

    :param cbase: The base Curve
    :type cbase: Curve
    :param cset: The set Curve
    :type cset: Curve
    :param tol: The tolerance for the shift
    :type tol: float
    :param pairID: The pair ID for the curve names
    :type pairID: float
    :param version: The version for the curve names
    :type version: float
    :return: Curve -- A new time shifted curve
    """
    def moving_average(a, n=3):
        y = np.copy(a)
        for i in range(n // 2):
            y = np.insert(y, 0, a[0])
            y = np.append(y, a[-1])
        ret = np.cumsum(y, dtype=float)
        ret = np.insert(ret, 0, 0.)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n:] / n

    smthWindow = 5

    xbase = cbase.x
    ybase = cbase.y
    xset = cset.x
    yset = cset.y
    # find index into xbase of the values in xset
    indx = np.digitize(xset, xbase) - 1
    # keep values in bounds so points off the xbase array
    # will use the index of the first (0) or last (len(xbase)-2) interval in xbase
    indx = np.clip(indx, 0, len(xbase) - 2)

    slopebase = (ybase[1:] - ybase[:-1]) / (xbase[1:] - xbase[:-1] + 1e-20)  # len of xbase - 1
    yintrp = np.interp(xset, xbase, ybase)  # len of xset
    residual = yset - yintrp
    delta_t = residual / (slopebase[indx] + 1e-20)

    # smooth the slopes before finding the max value.
    # noe indices of smthslopebase match those of cset arrays
    smthslopebase = moving_average(slopebase[indx], smthWindow)

    # find the slope of the new curve and smooth it
    slopeset = (yset[1:] - yset[:-1]) / (xset[1:] - xset[:-1] + 1e-20)  # len of xset - 1
    smthslopeset = moving_average(slopeset, smthWindow)
    smthslopeset = np.append(smthslopeset, smthslopeset[-1])  # extend to length of xset

    # set slope to zero when base and set have different signs
    # The delta_t is likely a poor choice if this is true
    smthslopebase = np.where(smthslopebase * smthslopeset > 0, smthslopebase, 0.0)

    # Use the delta_t at the point with the largest slope (abs value)
    maxslopebase = np.argmax(np.abs(smthslopebase))
    delta_t = residual[maxslopebase] / (slopebase[indx])[maxslopebase]
    #
    # this gives least squares delta_t
    # delta_t = np.sum(residual*slopebase[indx] )/np.sum(np.power(slopebase[indx],2))

    if np.abs(delta_t) > tol:
        # result.setOutcome(False)
        delta_t = np.abs(delta_t) * tol / delta_t
    xshifted = xset + delta_t

    return makecurve(x=xshifted,
                     y=yset,
                     name=f"{cset.name} pairID={pairID} version={version}")


def getfl(curvelist):
    """
    Returns the first and last data point from the yData array

     >>> curves = pydvpy.read('testData.txt')

     >>> first_last = pydvpy.getfl(curves) OR

     >>> first_last = pydvpy.getfl(curves[0])

    :param curvelist: The Curve or list of Curves
    :type curvelist: Curve or list
    :return: list -- A list of y values at the first and last index
    """
    first_last = list()

    curves = _convert_to_curvelist(curvelist)

    for cur in curves:
        first_last.append([cur.y[0], cur.y[-1]])

    return first_last
