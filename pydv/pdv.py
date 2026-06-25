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

import cmd
import os
import re
import sys
import warnings
from threading import Thread

import matplotlib
import numpy

if not os.environ.get("DISPLAY"):
    matplotlib.use("Agg")
else:
    matplotlib.use("QtAgg")
import code
import copy
import csv
import readline
import traceback
import types
from itertools import zip_longest
from numbers import Number

import matplotlib.colors as mclr
import matplotlib.pyplot as plt
import scipy
import scipy.special
import scipy.stats
from PySide6.QtCore import QObject, QtMsgType, Signal, qInstallMessageHandler
from PySide6.QtWidgets import QApplication

# HPC Import
try:
    import pdvplot
    import pdvutil
    import pydvpy

# Package Import
except ImportError:
    from pydv import pdvplot, pdvutil, pydvpy

try:
    from matplotlib import style

    stylesLoaded = True
except:
    stylesLoaded = False

from enum import Enum

warnings.filterwarnings("ignore", category=Warning)

PYDV_DIR = os.path.dirname(os.path.abspath(__file__))
try:
    version_file = os.path.join(PYDV_DIR, "../scripts/version.txt")
    with open(version_file, "r") as fp:
        pydv_version = fp.read().replace("\n", "")

    date_file = os.path.join(PYDV_DIR, "../scripts/date.txt")
    with open(date_file, "r") as fp:
        pydv_date = fp.read()
except:
    version_file = os.path.join(PYDV_DIR, "scripts/version.txt")
    with open(version_file, "r") as fp:
        pydv_version = fp.read().replace("\n", "")

    date_file = os.path.join(PYDV_DIR, "scripts/date.txt")
    with open(date_file, "r") as fp:
        pydv_date = fp.read()


class LogEnum(Enum):
    LOG = 1
    LOGX = 2
    LOG10 = 3
    LOG10X = 4


class Command(cmd.Cmd, object):
    def __init__(self):
        super().__init__()  # Don't ovewrite cmd.Cmd __init__

        # Special cmd.Cmd attributes
        self.prompt = "[PyDV]: "
        self.undoc_header = "Command Shortcuts:"
        self.ruler = "="

        # PyDV attributes
        self.curvelist = list()
        self.filelist = []
        self.plotlist = []
        self.plotfirst = []
        self.oldlist = []
        self.usertexts = []
        self.history = []
        self.histptr = -1
        self.plotedit = False
        self.plotter = None  # pdvplot.Plotter()
        self.app = None
        self.xlabel = ""
        self.ylabel = ""
        self.filename = ""
        self.record_id = ""
        self.title = ""
        self.xlabel_set_from_curve = True
        self.ylabel_set_from_curve = True
        self.filename_set_from_curve = True
        self.record_id_set_from_curve = True
        self.title_set_from_curve = True
        self.bordercolor = None
        self.figcolor = None
        self.plotcolor = None
        self.xtickcolor = None
        self.ytickcolor = None
        self.titlecolor = None
        self.xlabelcolor = None
        self.ylabelcolor = None
        self.xlabelweight = "normal"
        self.ylabelweight = "normal"
        self.xlabelstyle = "normal"
        self.ylabelstyle = "normal"
        self.xlim = None
        self.ylim = None
        self.showkey = True
        self.handlelength = None
        self.key_loc = 1
        self.key_ncol = 1
        self.showgrid = True
        self.showaxis = "on"
        self.showplot = "on"
        self.showminorticks = False
        self.gridcolor = "white"
        self.gridstyle = "solid"
        self.gridwidth = 1.0
        self.showletters = True
        self.showcurveinlegend = False
        self.showrecordidinlegend = False
        self.showfilenameinlegend = False
        self.xlogscale = False
        self.ylogscale = False
        self.titlefont = "large"
        self.xlabelfont = "medium"
        self.ylabelfont = "medium"
        self.axistickfont = "medium"
        self.keyfont = "small"
        self.keycolor = "black"
        self.curvelabelfont = "medium"
        self.annotationfont = "medium"
        self.initrun = None
        self.update = True
        self.guilims = False
        self.geometry = "de"
        self.xticks = "de"
        self.yticks = "de"
        self.xCol = 0  # column to use for x-axis, if doing column format reads
        self.debug = False
        self.redraw = True
        self.xmajortickcolor = "black"
        self.xminortickcolor = "black"
        self.ymajortickcolor = "black"
        self.yminortickcolor = "black"
        self.xtickformat = "de"
        self.ytickformat = "de"
        self.xticklength = 4
        self.xminorticklength = 2
        self.yticklength = 4
        self.yminorticklength = 2
        self.xtickwidth = 1
        self.xminortickwidth = 0.5
        self.ytickwidth = 1
        self.yminortickwidth = 0.5
        self.menulength = 50
        self.namewidth = 40
        self.xlabelwidth = 10
        self.ylabelwidth = 10
        self.filenamewidth = 30
        self.recordidwidth = 10
        self.updatestyle = False
        self.linewidth = None
        self.xtick_labels = {}
        self.xtickrotation = 0
        self.ytickrotation = 0
        self.xtickha = "center"
        self.xtickva = "top"
        self.ytickha = "right"
        self.ytickva = "center"
        self.tightlayout = 0
        self.group = 0
        self.slashes = 100
        self.do_label_done = False

    # Users wanted support for automatically loading some plot attributes. The
    # following commands handle the situations where there are multiple plots or
    # where the user specifies the attributes via the direct commands.
    def set_xlabel(self, label, from_curve=False):
        if "bold" in label:
            if self.xlabelweight == "bold":
                self.xlabelweight = "normal"
            else:
                self.xlabelweight = "bold"
            label = label.replace("bold", "")
        if "italic" in label:
            if self.xlabelstyle == "italic":
                self.xlabelstyle = "normal"
            else:
                self.xlabelstyle = "italic"
            label = label.replace("italic", "")
        if label.strip() == "":
            return

        if not from_curve:
            self.xlabel = label
            self.xlabel_set_from_curve = from_curve if label != "" else True
        else:
            if self.xlabel_set_from_curve:
                not_blank = 0
                for cur in self.plotlist:
                    if cur.xlabel != "":
                        not_blank += 1
                if len(self.plotlist) > 1 and self.xlabel == "" and not_blank == 1 and label != "":
                    self.xlabel = label
                elif len(self.plotlist) > 1 and label != self.xlabel:
                    self.xlabel = ""
                else:
                    self.xlabel = label
                    self.xlabel_set_from_curve = from_curve

    def set_ylabel(self, label, from_curve=False):
        if "bold" in label:
            if self.ylabelweight == "bold":
                self.ylabelweight = "normal"
            else:
                self.ylabelweight = "bold"
            label = label.replace("bold", "")
        if "italic" in label:
            if self.ylabelstyle == "italic":
                self.ylabelstyle = "normal"
            else:
                self.ylabelstyle = "italic"
            label = label.replace("italic", "")
        if label.strip() == "":
            return

        if not from_curve:
            self.ylabel = label
            self.ylabel_set_from_curve = from_curve if label != "" else True
        else:
            if self.ylabel_set_from_curve:
                not_blank = 0
                for cur in self.plotlist:
                    if cur.ylabel != "":
                        not_blank += 1
                if len(self.plotlist) > 1 and self.ylabel == "" and not_blank == 1 and label != "":
                    self.ylabel = label
                elif len(self.plotlist) > 1 and label != self.ylabel:
                    self.ylabel = ""
                else:
                    self.ylabel = label
                    self.ylabel_set_from_curve = from_curve

    def set_title(self, title, from_curve=False):
        if not from_curve:
            self.title = title
            self.title_set_from_curve = from_curve if title != "" else True
        else:
            if self.title_set_from_curve:
                if len(self.plotlist) > 1 and title != self.title:
                    self.title = ""
                else:
                    self.title = title
                    self.title_set_from_curve = from_curve

    def set_filename(self, filename, from_curve=False):
        if not from_curve:
            self.filename = filename
            self.filename_set_from_curve = from_curve if filename != "" else True
        else:
            if self.filename_set_from_curve:
                if len(self.plotlist) > 1 and filename != self.filename:
                    self.filename = ""
                else:
                    self.filename = filename
                    self.filename_set_from_curve = from_curve

    def set_record_id(self, record_id, from_curve=False):
        if not from_curve:
            self.record_id = record_id
            self.record_id_set_from_curve = from_curve if record_id != "" else True
        else:
            if self.record_id_set_from_curve:
                if len(self.plotlist) > 1 and record_id != self.title:
                    self.record_id = ""
                else:
                    self.record_id = record_id
                    self.record_id_set_from_curve = from_curve

    def precmd(self, line):
        """
        Check for special character/operator commands
        """

        pl = []
        for i in range(len(self.plotlist)):
            pl.append(self.plotlist[i].copy())
        self.oldlist = pl

        if not line or not line.split():
            return line

        line = line.split()

        check = line.pop(0)
        need_join_line = False
        if check == "+":
            line = "add " + " ".join(line)
        elif check == "-":
            line = "subtract " + " ".join(line)
        elif check == "/":
            line = "divide " + " ".join(line)
        elif check == "*":
            line = "multiply " + " ".join(line)
        else:
            line.insert(0, check)
            need_join_line = True

        if need_join_line and len(line) > 2:
            need_join_line = False
            check2 = line.pop(1)

            if check2 == "+":
                line = "add " + " ".join(line)
            elif check2 == "-":
                line = "subtract " + " ".join(line)
            elif check2 == "/":
                line = "divide " + " ".join(line)
            elif check2 == "*":
                line = "multiply " + " ".join(line)
            elif check2 == "**":
                line = "powr " + " ".join(line)
            else:
                line.insert(1, check2)
                need_join_line = True

        if need_join_line:
            line = " ".join(line)

        line = line.replace("re-id", "reid")
        line = line.replace("data-id", "dataid")
        line = line.replace("x-log-scale", "xlogscale")
        line = line.replace("y-log-scale", "ylogscale")
        line = line.replace("make-curve", "makecurve")
        line = line.replace("error-bar", "errorbar")
        line = line.replace("error-range", "errorrange")
        line = line.replace("get-range", "getrange")
        line = line.replace("get-domain", "getdomain")
        line = line.replace("diff-measure", "diffMeasure")

        line = line.replace("integrate(", "commander.integrate(").replace("int(", "commander.integrate(")
        line = line.replace("derivative(", "commander.derivative(").replace("der(", "commander.derivative(")
        # print line

        if self.showkey:
            if plt.gca().get_legend() is not None:
                self.key_loc = plt.gca().get_legend()._loc

        if self.plotter is not None:
            if self.plotter.plotChanged:
                self.apply_uichanges()

        return line

    def default(self, line):
        """
        Check for arithmetic calculation
        """

        try:
            pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
            self.plotedit = True
        except:
            self.redraw = False
            print("error - unknown syntax: " + line)
            if self.debug:
                traceback.print_exc(file=sys.stdout)

    def postcmd(self, stop, line):
        """
        Save current state for undo/redo
        """

        if self.plotedit:
            # self.history.pop(-1)
            # pl = []
            # for i in range(len(self.plotlist)):
            #    pl.append(self.plotlist[i].copy())

            # print self.history
            # print pl

            if len(self.history) > self.histptr + 1:
                self.history = self.history[: self.histptr + 1]

            self.histptr += 1
            self.history.append(self.oldlist)  # (self.histptr, self.oldlist)

            if len(self.history) > 15:
                self.history.pop(0)
                self.histptr -= 1

            # print self.history
            # print self.histptr

            self.plotedit = False
        if self.update:
            if self.redraw:
                self.updateplot
        self.redraw = True
        return stop

    def emptyline(self):
        """
        Override cmd empty line function to not repeat last command
        """
        self.redraw = False

    ########################################################################################################
    # normal shortcut commands #
    ########################################################################################################

    def do_q(self, line):
        self.do_quit(line)

    def do_ran(self, line):
        self.do_range(line)

    def do_dom(self, line):
        self.do_domain(line)

    def do_rd(self, line):
        self.do_read(line)

    def do_rdcsv(self, line):
        self.do_readcsv(line)

    def do_rdsina(self, line):
        self.do_readsina(line)

    def do_rdsinah5(self, line):
        self.do_readsinahdf5(line)

    def do_cur(self, line):
        self.do_curve(line)

    def do_era(self, line):
        self.do_erase(line)

    def do_del(self, line):
        self.do_delete(line)

    def do_lst(self, line):
        self.do_list(line)

    def do_lstr(self, line):
        self.do_listr(line)

    def do_sub(self, line):
        self.do_subtract(line)

    def do_div(self, line):
        self.do_divide(line)

    def do_mult(self, line):
        self.do_multiply(line)

    def do_xls(self, line):
        self.do_xlogscale(line)

    def do_yls(self, line):
        self.do_ylogscale(line)

    def do_der(self, line):
        self.do_derivative(line)

    def do_pow(self, line):
        self.do_powr(line)

    def do_power(self, line):
        self.do_powr(line)

    def do_powx(self, line):
        self.do_powrx(line)

    def do_powerx(self, line):
        self.do_powrx(line)

    def do_square(self, line):
        self.do_sqr(line)

    def do_squarex(self, line):
        self.do_sqrx(line)

    def do_convol(self, line):
        self.do_convolve(line)

    def do_convolb(self, line):
        self.do_convolveb(line)

    def do_convolc(self, line):
        self.do_convolvec(line)

    def do_int(self, line):
        self.do_integrate(line)

    def do_geom(self, line):
        self.do_geometry(line)

    def do_xmm(self, line):
        self.do_xminmax(line)

    def do_ymm(self, line):
        self.do_yminmax(line)

    def do_key(self, line):
        self.do_legend(line)

    def do_leg(self, line):
        self.do_legend(line)

    def do_ln(self, line):
        self.do_log(line)

    def do_lnx(self, line):
        self.do_logx(line)

    def do_nc(self, line):
        self.do_newcurve(line)

    def do_mkext(self, line):
        self.do_makeextensive(line)

    def do_mkint(self, line):
        self.do_makeintensive(line)

    def do_system(self, line):
        self.do_shell(line)

    def do_pl(self, line):
        self.do_plotlayout(line)

    def do_help(self, arg):
        """
        Return information about the specified command, variable, or command category.
        If no argument is supplied, return a list of available commands.

        .. code::

            [PyDV]: help [command]

            Ex:
                [PyDV]: help list
        """

        if arg == "+":
            arg = "add"
        elif arg == "-" or arg == "sub":
            arg = "subtract"
        elif arg == "*" or arg == "mult":
            arg = "multiply"
        elif arg == "/" or arg == "div":
            arg = "divide"
        elif arg == "rd":
            arg = "read"
        elif arg == "rdcsv":
            arg = "readcsv"
        elif arg == "rdsina":
            arg = "readsina"
        elif arg == "rdsinah5":
            arg = "readsinahdf5"
        elif arg == "convol":
            arg = "convolve"
        elif arg == "convolb":
            arg = "convolveb"
        elif arg == "convolc":
            arg = "convolvec"
        elif arg == "cur":
            arg = "curve"
        elif arg == "era":
            arg = "erase"
        elif arg == "del":
            arg = "delete"
        elif arg == "ran":
            arg = "range"
        elif arg == "dom":
            arg = "domain"
        elif arg == "lst":
            arg = "list"
        elif arg == "lstr":
            arg = "listr"
        elif arg == "q":
            arg = "quit"
        elif arg == "data-id":
            arg = "dataid"
        elif arg == "re-id":
            arg = "reid"
        elif arg == "x-log-scale" or arg == "xls":
            arg = "xlogscale"
        elif arg == "y-log-scale" or arg == "yls":
            arg = "ylogscale"
        elif arg == "der":
            arg = "derivative"
        elif arg == "pow" or arg == "power":
            arg = "powr"
        elif arg == "powx" or arg == "powerx":
            arg = "powrx"
        elif arg == "make-curve":
            arg = "makecurve"
        elif arg == "error-bar":
            arg = "errorbar"
        elif arg == "int":
            arg = "integrate"
        elif arg == "geom":
            arg = "geometry"
        elif arg == "key":
            arg = "legend"
        elif arg == "leg":
            arg = "legend"
        elif arg == "error-range":
            arg = "errorrange"
        elif arg == "get-domain":
            arg = "getdomain"
        elif arg == "get-range":
            arg = "getrange"
        elif arg == "xmm":
            arg = "xminmax"
        elif arg == "ymm":
            arg = "yminmax"
        elif arg == "ln":
            arg = "log"
        elif arg == "lnx":
            arg = "logx"
        elif arg == "nc":
            arg = "newcurve"
        elif arg == "mkext":
            arg = "makeextensive"
        elif arg == "mkint":
            arg = "makeintensive"
        elif arg == "system":
            arg = "shell"
        elif arg == "pl":
            arg = "plotlayout"

        self.redraw = False  # never need to redraw after a 'help'
        return super(Command, self).do_help(arg)

    def do_shell(self, line):
        """
        Execute shell commands.

        .. code::

            [PyDV]: <shell | system | !> <command>

            Ex:
                [PyDV]: shell echo $PATH
        """

        os.system(line)

    ########################################################################################################
    # command functions #
    ########################################################################################################

    def do_newcurve(self, line):
        """
        Creates a new curve from an expression containing curves that have the **same domain**.
        For convenience, the **numpy** and **scipy** module have been imported into the namespace. **Shortcut: nc**

        * The x-values will be the x-values of the last curve used in the expression due to how PyDV finds curves in a
          loop.

        * The y-values will be the evaluated expression after `newcurve`.

        .. note::

            If you want a more advanced expression or more control over what happens, see the command `custom`.

        .. warning::

            * Currently, `newcurve` is hard-wired to only handle single-letter labels.
              Curve names used in the expression cannot be the @N type we use after
              we run out of letters. Sorry (April 2015).
            * A common error is to forget the .x or .y on the curve label name.
            * All the arrays in your expression have to span the same domain! Currently (4/2015), newcurve
              will generate a curve from different domains (but with the same number of points) with no error
              message, and that curve will almost certainly not be what you intended.

        .. code::

            [PyDV]: newcurve <numpy and/or scipy expression>

            Ex:
                [PyDV]: newcurve scipy.ndimage.gaussian_filter(numpy.sin(a.x*2*numpy.pi)/(b.x**2), sigma=5)
        """

        try:
            # check for obvious input errors
            if not line:
                return 0
            if len(line.split(":")) > 1:
                print("error - NOT HANDLING RANGES YET, not even sure what that would mean yet")
                return 0
            else:  # ok, got through input error checking, let's get to work
                newline = line  # copy the original line, we need the original for labeling

                # replace all the *.x and *.y entries in the line with
                # their actual data arrays in the plotlist.
                import re  # we are going to need regex!

                arrayMarkers = [".x", ".y"]
                for arrayMarker in arrayMarkers:
                    arrayInsts = re.findall(r"\w\%s" % arrayMarker, line)  # finds [a-z].x then [a-z].y
                    for aInst in arrayInsts:
                        plotname = aInst[0]  # BLAGO!! hard wired for single-letter labels
                        cID = pdvutil.getCurveIndex(plotname, self.plotlist)
                        newline = re.sub(
                            r"%s\%s" % (plotname, arrayMarker), "self.plotlist[%d]%s" % (cID, arrayMarker), newline
                        )

                # now newline holds a string that can be evaluated by Python
                newYArray = eval(newline)  # line returns a new numpy.array

                # make newYArray into a legitimate curve
                c = pydvpy.makecurve(
                    x=self.plotlist[cID].x,  # x-values from one of the curves used in the expression
                    y=newYArray,
                    name=line,  # we name the curve with the input 'line'
                    plotname=self.getcurvename(),
                )  # get the next available data ID label
                self.addtoplot(c)

            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_eval(self, line):
        """
        Evaluate mathematical operations on curves.

        .. code::

            [PyDV]: eval <curve-operations>

            Ex:
                [PyDV]: eval a+b
        """

        try:
            line = line.replace("integrate", "commander.integrate").replace("int", "commander.integrate")
            line = line.replace("derivative", "commander.derivative").replace("der", "commander.derivative")

            pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_debug(self, line):
        """
        Turn on debug tracebacks for commands.

        .. code::

            [PyDV]: debug on | off

            Ex:
                [PyDV]: debug on
                [PyDV]: debug off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.debug = False
            elif line == "1" or line.upper() == "ON":
                self.debug = True
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_tightlayout(self, line):
        """
        Turn on plot tight layout. Useful if tick labels are long.

        .. code::

            [PyDV]: tightlayout <on | off>

            Ex:
                [PyDV]: tightlayout on
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.tightlayout = 0
            elif line == "1" or line.upper() == "ON":
                self.tightlayout = 1
            else:
                print("invalid input: requires on or off as argument")
        except:
            if self.tightlayout:
                traceback.print_exc(file=sys.stdout)
        finally:
            self.redraw = True

    def do_undo(self, line):
        """
        Undo the last operation on plotted curves.

        .. code::

            [PyDV]: undo
        """

        try:
            if self.histptr > 0:
                if self.histptr == len(self.history) - 1:
                    pl = []
                    for i in range(len(self.plotlist)):
                        pl.append(self.plotlist[i].copy())
                    self.history.append(pl)
                self.plotlist = self.history[self.histptr]
                # self.history = self.history[:self.histptr]
                self.histptr -= 1

                # print self.history
                # print self.histptr
            else:
                print("error - cannot undo further")
        except:
            pdvutil.print_own_docstring(self)

    def do_redo(self, line):
        """
        Redo the last undo curve operation.

        .. code::

            [PyDV]: redo
        """

        try:
            if self.histptr < len(self.history) - 2:
                self.histptr += 1
                self.plotlist = self.history[self.histptr + 1]

                # print self.history
                # print self.histptr
            else:
                print("error - cannot redo further")
        except:
            pdvutil.print_own_docstring(self)

    def do_add(self, line):
        """
        Take the sum of curves. If the optional *value* is specified it will add the y-values of
        the curves by *value* (equivalent to using the **dy** command). **Shortcut:** +

        .. note::
            Be sure that the x points are in increasing order as PyDV uses numpy.interp().

        .. note::
            Adding curves by a number modifies the curve. If you want to create a new
            curve then copy the original curve first using the copy command.

        .. code::

            [PyDV]: add <curve-list> [value]

            Ex:
                [PyDV]: add a
                [PyDV]: add a:b
                [PyDV]: add c d
                [PyDV]: add c d 7
        """

        try:
            # If adding a number then send to dy
            if any(char.isdigit() for char in line) and not any(char == "@" for char in line):
                # value = float(line.split().pop(-1))
                self.do_dy(line)
            else:
                if len(line.split(":")) > 1:
                    self.do_add(pdvutil.getletterargs(line))
                    return 0
                else:
                    line = line.split()
                    line = " + ".join(line)
                    pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
                self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_subtract(self, line):
        """
        Take the difference of curves. A single curve can be specified, resulting in the
        negating of its y-values. If the optional `value` is specified it will subtract the
        y-values of the curves by `value`.

        .. note::
            Be sure that the x points are in increasing order as PyDV uses numpy.interp().

        .. note::
            Subtracting curves by a number modifies the curve. If you want to create a new
            curve then copy the original curve first using the copy command.

        .. code::

            [PyDV]: <subtract | sub | --> <curve-list> [value]

            Ex:
                [PyDV]: subtract a
                [PyDV]: subtract a:b
                [PyDV]: subtract c d
                [PyDV]: subtract c d 7
        """

        try:
            try:
                nline = line.split()
                value = -1.0 * float(nline.pop(-1))
                nline = " ".join(nline)
                nline = nline + " " + str(value)
                self.do_dy(nline)
            except:
                if len(line.split(":")) > 1:
                    self.do_subtract(pdvutil.getletterargs(line))
                    return 0
                else:
                    line = line.split()
                    if len(line) == 1:
                        line = "-" + line[0]
                    else:
                        line = " - ".join(line)
                    pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_multiply(self, line):
        """
        Take the product of curves. If the optional `value` is specified it will multiply the
        y-values of the curves by `value`.

        .. note::
            Be sure that the x points are in increasing order as PyDV uses numpy.interp().

        .. note::
            Multiplying curves by a number modifies the curve. If you want to create a new
            curve then copy the original curve first using the copy command.

        .. code::

            [PyDV]: <multiply | * | mult> <curve-list> [value]

            Ex:
                [PyDV]: multiply a
                [PyDV]: multiply a:b
                [PyDV]: multiply c d
                [PyDV]: multiply c d 7
        """

        try:
            # If multiplying by a number then send to my
            if any(char.isdigit() for char in line) and not any(char == "@" for char in line):
                # value = float(line.split().pop(-1))
                self.do_my(line)
            else:
                if len(line.split(":")) > 1:
                    self.do_multiply(pdvutil.getletterargs(line))
                    return 0
                else:
                    line = line.split()
                    line = " * ".join(line)
                    pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_divide(self, line):
        """
        Take quotient of curves. If the optional `value` is specified it will divide the
        y-values of the curves by `value`.

        .. note::
            Be sure that the x points are in increasing order as PyDV uses numpy.interp().

        .. note::
            Dividing curves by a number modifies the curve. If you want to create a new
            curve then copy the original curve first using the copy command.

        .. code::

            [PyDV]: <divide | / | div> <curve-list> [value]

            Ex:
                [PyDV]: divide a
                [PyDV]: divide a:b
                [PyDV]: divide c d
                [PyDV]: divide c d 7
        """
        try:
            # If dividing by a number then send to divy
            if any(char.isdigit() for char in line) and not any(char == "@" for char in line):
                # value = float(line.split().pop(-1))
                self.do_divy(line)
            else:
                if len(line.split(":")) > 1:
                    self.do_divide(pdvutil.getletterargs(line))
                    return 0
                else:
                    line = line.split()
                    line = " / ".join(line)
                    pdvutil.parsemath(line, self.plotlist, self, (plt.axis()[0], plt.axis()[1]))
                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_read(self, line):
        """
        Read curves from the specified ASCII file and optionally filter by regex. The next available prefix (see the
        prefix command) is automatically assigned the menu index of the first curve in each data file read. For column
        oriented (.gnu) files optionally specify the x-column number before the file name.

        .. code::

            [PyDV]: <read | rd> [(regex) matches] [x-col] <filename>

            Ex:
                [PyDV]: read my_file.ult
                [PyDV]: read my.*curves my_file.ult
                [PyDV]: read my.*curves 1 my_file.ult
        """

        try:
            line = line.split()
            n = len(line)
            if line[-1].endswith(".csv"):
                self.do_readcsv(" ".join(line))
                return
            elif line[-1].endswith(".json"):
                self.do_readsina(" ".join(line))
                return
            elif line[-1].endswith(".hdf5") or line[-1].endswith(".h5") or line[-1].endswith(".hdf"):
                self.do_readsinahdf5(" ".join(line))
                return

            if n == 1:
                self.load(line[0])
            elif n == 2:
                if line[0].isdigit():
                    self.xCol = int(line[0])
                    self.load(line[1], True)
                else:
                    raise RuntimeError("expecting an x-column number.")
            elif n == 3:
                line[0] = line[0].strip().strip("()")
                matches = int(line[1])
                if matches < 0:
                    matches = None
                self.load(line[2], False, line[0], matches)
            elif n == 4:
                line[0] = line[0].strip().strip("()")
                matches = int(line[1])
                if matches < 0:
                    matches = None
                self.xCol = int(line[2])
                self.load(line[3], True, line[0], matches)
            else:
                print("error - Usage: read [(regex) matches] [x-col] <file-name>")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            self.plotter.updateDialogs()

    def do_readcsv(self, line):
        """
        Read CSV data file. The next available prefix (see the prefix command) is automatically assigned the menu index
        of the first curve in each data file read. For column oriented (.gnu) files optionally specify the x-column
        number before the file name. If the columns are in x and y pairs with `savecsv` command, the [x-col] must be
        specified as `paired`.

        .. code::

            [PyDV]: <readcsv | rdcsv> <filename.csv> [x-col] [paired]

            Ex:
                [PyDV]: readcsv my_file.csv
                [PyDV]: readcsv my_file.csv 2
                [PyDV]: readcsv my_file.csv paired
        """

        try:
            line = line.split()

            if len(line) == 2:
                col = line.pop(-1)
            else:
                col = 0

            self.load_csv(line[0], col)
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            self.plotter.updateDialogs()

    def do_readsina(self, line):
        """
        Read all curves from Sina data file. The next available prefix (see the prefix command) is automatically
        assigned the menu index of the first curve in each data file read.

        .. code::

            [PyDV]: <readsina | rdsina> <filename.json>

            Ex:
                [PyDV]: readsina my_file.json
        """

        try:
            line = line.split()
            self.load_sina(line[0])
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            self.plotter.updateDialogs()

    def do_readsinahdf5(self, line):
        """
        Read all curves from Sina hdf5 data file. The next available prefix (see the prefix command) is automatically
        assigned the menu index of the first curve in each data file read.

        .. code::

            [PyDV]: <readsinahdf5 | rdsinah5> <filename.hdf5>

            Ex:
                [PyDV]: readsinahdf5 my_file.hdf5
        """

        try:
            line = line.split()
            self.load_sinahdf5(line[0])
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            self.plotter.updateDialogs()

    def do_setxcolumn(self, line):
        """
        Set x column for reading column formatted data files (.gnu or .csv).

        .. code::

            [PyDV]: setxcolumn <x column>

            Ex:
                [PyDV]: setxcolumn 1
        """

        try:
            line = line.split()

            if len(line) == 1:
                self.xCol = int(line[0])
            else:
                raise RuntimeError("Expecting 1 argument but received {}".format(len(line)))
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def __menu_curve_math(self, operation, line):
        if len(line.split(":")) > 1:  # check for list notation
            return self.__menu_curve_math(operation, pdvutil.getnumberargs(line, self.filelist))
        else:
            line = line.split()
            curvelist = list()
            for i in range(len(line)):
                curvedex = 0
                if ord("A") <= ord(line[i][0].upper()) <= ord("Z"):  # check for a.% b.% file index notation
                    filedex = ord(line[i][0].upper()) - ord("A")  # file index we want
                    prevfile = ""  # set prevfile to impossible value
                    filecounter = 0
                    while filecounter <= filedex:  # count files up to the one we want
                        if self.curvelist[curvedex].filename != prevfile:  # inc count if name changes
                            prevfile = self.curvelist[curvedex].filename
                            filecounter += 1
                        curvedex += 1  # this will end up being one past what we want
                        if curvedex >= len(self.curvelist):
                            raise RuntimeError("error: in curve list did not find matching file for %s" % line[i])
                    curvedex -= 1  # back curvedex up to point to start of file's curves
                    curvedex += int(line[i].split(".")[-1]) - 1
                elif 0 < int(line[i]) <= len(self.curvelist):
                    curvedex = int(line[i]) - 1
                else:
                    raise RuntimeError("error: curve index out of bounds: " + line[i])

                curvelist.append(self.curvelist[curvedex].copy())

        if len(curvelist) > 1:
            if operation == "add":
                return pydvpy.add(curvelist)
            elif operation == "subtract":
                return pydvpy.subtract(curvelist)
            elif operation == "multiply":
                return pydvpy.multiply(curvelist)
            elif operation == "divide":
                return pydvpy.divide(curvelist)
            else:
                raise ValueError("error: Unknown operation: {}".format(operation))
        else:
            raise RuntimeError("error: Expecting more than 1 curve")

    def do_add_h(self, line):
        """
        Adds curves that have been read from a file but not yet plotted. `list-of-menu-numbers`
        are the index values displayed in the first column of the `menu` command.

        .. code::

            [PyDV]: add_h <list-of-menu-numbers>

            Ex:
                [PyDV]: add_h 1
                [PyDV]: add_h 1:2
                [PyDV]: add_h 3 4
        """

        if not line:
            return 0

        try:
            c = self.__menu_curve_math("add", line)

            if len(c.name) > 20:
                c.name = c.name[:20] + "..."
            c.plotname = ""
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_subtract_h(self, line):
        """
        Subtracts curves that have been read from a file but not yet plotted. `list-of-menu-numbers`
        are the index values displayed in the first column of the `menu` command.

        .. code::

            [PyDV]: subtract_h <list-of-menu-numbers>

            Ex:
                [PyDV]: subtract_h 1
                [PyDV]: subtract_h 1:2
                [PyDV]: subtract_h 3 4
        """

        if not line:
            return 0

        try:
            c = self.__menu_curve_math("subtract", line)

            if len(c.name) > 20:
                c.name = c.name[:20] + "..."
            c.plotname = ""
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_multiply_h(self, line):
        """
        Multiplies curves that have been read from a file but not yet plotted. `list-of-menu-numbers`
        are the index values displayed in the first column of the `menu` command.

        .. code::

            [PyDV]: multiply_h <list-of-menu-numbers>

            Ex:
                [PyDV]: multiply_h 1
                [PyDV]: multiply_h 1:2
                [PyDV]: multiply_h 3 4
        """

        if not line:
            return 0

        try:
            c = self.__menu_curve_math("multiply", line)

            if len(c.name) > 20:
                c.name = c.name[:20] + "..."
            c.plotname = ""
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_divide_h(self, line):
        """
        Divides curves that have been read from a file but not yet plotted. `list-of-menu-numbers`
        are the index values displayed in the first column of the `menu` command.

        .. code::

            [PyDV]: divide_h <list-of-menu-numbers>

            Ex:
                [PyDV]: divide_h 1
                [PyDV]: divide_h 1:2
                [PyDV]: divide_h 3 4
        """

        if not line:
            return 0

        try:
            c = self.__menu_curve_math("divide", line)

            if len(c.name) > 20:
                c.name = c.name[:20] + "..."
            c.plotname = ""
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_curve(self, line):
        """
        Select curves from the menu for plotting.
        A regular expression may be supplied in paranthesis for matching against the curve label to plot.

        Regular expressions are based on the Python regex syntax, not the UNIX syntax.
        In particular, '*' is not the wildcard you might be expecting.

        For an explanation of the regex syntax, type 'help regex'.

        .. code::

            [PyDV]: <curve | cur> [menu (<regex>)] <list-of-menu-numbers>

            Ex:
                [PyDV]: cur 1
                [PyDV]: cur 2:3
                [PyDV]: cur 4 5
                [PyDV]: cur (.*my_curves.*)
        """

        if not line:
            return 0
        try:
            if len(line.split(")")) > 1:  # check for regular expression
                line = line.strip().split(")")
                reg = re.compile(r"")
                for i in range(len(line)):
                    line[i] = line[i].strip().strip("(")
                if line[0].split()[0] == "menu":
                    line[0] = " ".join(line[0].split()[1:])
                try:
                    reg = re.compile(r"%s" % line[0])
                except:
                    print("error: invalid expression")
                    return 0
                self.do_menu(line[0])
                regline = ""
                for i in range(len(self.curvelist)):
                    searchline = self.curvelist[i].name + " " + self.curvelist[i].filename
                    if reg.search(searchline):
                        regline += str(i + 1) + " "
                line[0] = regline
                line = " ".join(line)
                self.do_curve(line)  # call curve again but with regexp results
                self.redraw = True
                return 0
            if "*." in line:
                for fdx in range(len(self.filelist)):
                    if fdx < 26:
                        temp_line = line.replace("*", chr(ord("a") + fdx))
                    else:
                        temp_line = line.replace("*", f"@{fdx + 1}")

                    if len(line.split(":")) > 1:  # check for list notation
                        self.do_curve(pdvutil.getnumberargs(temp_line, self.filelist))
                    else:
                        self.do_curve(temp_line)
                return 0
            elif len(line.split(":")) > 1:  # check for list notation
                # call curve again with list expanded
                self.do_curve(pdvutil.getnumberargs(line, self.filelist))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    curvedex = 0
                    skip = False

                    # check for a.% b.% @#. file index notation
                    if ord("A") <= ord(line[i][0].upper()) <= ord("Z") or "@" in line[i]:
                        if ord("A") <= ord(line[i][0].upper()) <= ord("Z"):
                            filedex = ord(line[i][0].upper()) - ord("A")  # file index we want
                        else:
                            filedex = int(line[i].split(".")[0].replace("@", "")) - 1  # 0 index

                        prevfile = ""  # set prevfile to impossible value
                        filecounter = 0
                        fileend = 0
                        while filecounter <= filedex:  # count files up to the one we want
                            if self.curvelist[curvedex].filename != prevfile:  # inc count if name changes
                                prevfile = self.curvelist[curvedex].filename
                                fileend += self.filelist[filecounter][1]
                                filecounter += 1
                            curvedex += 1  # this will end up being one past what we want
                            if curvedex >= len(self.curvelist):
                                print("error: in curve list did not find matching file for %s" % line[i])
                        curvedex -= 1  # back curvedex up to point to start of file's curves
                        curvedex += int(line[i].split(".")[-1]) - 1
                        if curvedex + 1 > fileend:
                            filestart = fileend - self.filelist[filedex][1] + 1
                            print(f"File {filedex + 1}: {self.filelist[filedex]}: Start {filestart}, End {fileend}")
                            print(f"\tRequested Curve {line[i]}: {curvedex + 1}")
                            print("\tError: curve index out of bounds")
                            skip = True
                    elif 0 < int(line[i]) <= len(self.curvelist):
                        curvedex = int(line[i]) - 1
                    else:
                        print("error: curve index out of bounds: " + line[i])
                        skip = True
                    if not skip:
                        # Deep copy
                        current = copy.deepcopy(self.curvelist[curvedex])
                        try:
                            current.step = self.curvelist[curvedex].step
                        except:
                            current.step = False
                        try:
                            current.xticks_labels = self.curvelist[curvedex].xticks_labels
                        except:
                            current.xticks_labels = None
                        self.addtoplot(current)
                        if len(current.x) == 1 and len(current.y) == 1:
                            current.markerstyle = "o"
                            current.linestyle = "None"
                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_erase(self, line):
        """
        Erase all curves on the screen but leave the limits untouched.

        .. code::

            [PyDV]: <erase | era>

            Ex:
                [PyDV]: erase
        """

        self.plotlist = []
        self.usertexts = []

        self.plotedit = True

    def do_delete(self, line):
        """
        Delete a curve from the graph.

        .. code::

            [PyDV]: <delete | del> <curve-list>

            Ex:
                [PyDV]: delete a
                [PyDV]: delete a:b
                [PyDV]: delete c d
        """

        try:
            if not line:
                return 0
            if len(line.split(":")) > 1:
                self.do_delete(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        self.plotlist.pop(idx)
                    except pdvutil.CurveIndexError:
                        pass

                self.reset_xticks_labels()

                self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_color(self, line):
        """
        Set the color of curves. Color names can be "blue", "red", etc., or "#eb70aa", a 6 digit set of hexadecimal
        red-green-blue values #RRGGBB. The entire set of HTML-standard color names is available. Type `showcolormap`
        to see the available named colors which will show up in the PyDV plotting area (hit return to go back to your
        plots).

        .. code::

            [PyDV]: color <curve-list> <color>

            Ex:
                [PyDV]: color a blue
                [PyDV]: color a:b blue
                [PyDV]: color c d blue
                [PyDV]: color a #aabb33
                [PyDV]: showcolormap
                hit return to go back to your plots
                [PyDV]: color a lime
        """

        if not line:
            return 0
        try:
            line = line.split()
            color = line.pop(-1)
            line = " ".join(line)
            if len(line.split(":")) > 1:
                self.do_color(pdvutil.getletterargs(line) + color)
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    for j in range(len(self.plotlist)):
                        name = self.plotlist[j].plotname
                        if name == line[i].upper():
                            if mclr.is_color_like(color):
                                self.plotlist[j].color = color
                                self.plotlist[j].markeredgecolor = color
                                self.plotlist[j].markerfacecolor = color
                            else:
                                print("error: invalid color " + color)
                                return 0
                            break
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_stats(self, line):
        """
        Show various statistics about the curve.

        .. code::

            [PyDV]: stats <curve-list>

            Ex:
                [PyDV]: stats a
                [PyDV]: stats a:b
                [PyDV]: stats c d
        """
        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_stats(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        pydvpy.stats(cur)

                    except pdvutil.CurveIndexError:
                        pass

                print("\n")
            except:
                pdvutil.print_own_docstring(self)
            finally:
                self.redraw = False

    def do_deltax(self, line):
        """
        Create new curve that calculates difference between its own X points. Delta X vs # of points - 1.

        .. code::

            [PyDV]: deltax <curve>

            Ex:
                [PyDV]: deltax a
                [PyDV]: deltax a:b
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_deltax(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]

                        c = pydvpy.makecurve(
                            x=range(len(cur.x) - 1),
                            y=cur.x[1:] - cur.x[:-1],
                            name=f"{cur.name} Delta X",  # we name the curve with the input 'line'
                            plotname=self.getcurvename(),
                        )  # get the next available data ID label
                        self.addtoplot(c)

                    except pdvutil.CurveIndexError:
                        pass
            except:
                pdvutil.print_own_docstring(self)
            finally:
                self.redraw = True

    def do_deltay(self, line):
        """
        Create new curve that calculates difference between its own Y points. Delta Y vs # of points - 1.

        .. code::

            [PyDV]: deltay <curve>

            Ex:
                [PyDV]: deltay a
                [PyDV]: deltay a:b
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_deltay(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]

                        c = pydvpy.makecurve(
                            x=range(len(cur.y) - 1),
                            y=cur.y[1:] - cur.y[:-1],
                            name=f"{cur.name} Delta Y",  # we name the curve with the input 'line'
                            plotname=self.getcurvename(),
                        )  # get the next available data ID label
                        self.addtoplot(c)

                    except pdvutil.CurveIndexError:
                        pass
            except:
                pdvutil.print_own_docstring(self)
            finally:
                self.redraw = True

    def do_getattributes(self, line):
        """
        Return a curve's attributes, such as: color, style, width, etc.

        .. code::

            [PyDV]: getattributes <curve-list>

            Ex:
                [PyDV]: getattributes a
                [PyDV]: getattributes a:b
                [PyDV]: getattributes c d
        """
        if len(line.split(":")) > 1:
            self.do_getattributes(pdvutil.getletterargs(line))
            return 0
        else:
            if not line:
                return 0
            try:
                line = line.split()
                for c in line:
                    idx = pdvutil.getCurveIndex(c, self.plotlist)
                    cur = self.plotlist[idx]
                    try:
                        cur.step = self.curvelist[idx].step
                    except:
                        cur.step = False
                    try:
                        cur.xticks_labels = self.curvelist[idx].xticks_labels
                    except:
                        cur.xticks_labels = None
                    print("\n")
                    print("    Plot name = {}".format(cur.plotname))
                    print("    Color = {}".format(cur.color))
                    if cur.linestyle == "-":
                        pp_linestyle = "solid"
                    elif cur.linestyle == ":":
                        pp_linestyle = "dot"
                    elif cur.linestyle == "--":
                        pp_linestyle = "dash"
                    elif cur.linestyle == "-.":
                        pp_linestyle = "dashdot"
                    print("    Style = {}".format(pp_linestyle))
                    print("    Curve width = {} ".format(cur.linewidth))
                    print("    Edited = {}".format(cur.edited))
                    print("    Scatter = {}".format(cur.scatter))
                    print("    Linespoints = {}".format(cur.linespoints))
                    print("    Drawstyle = {}".format(cur.drawstyle))
                    print("    Dashes = {}".format(cur.dashes))
                    print("    Hidden = {}".format(cur.hidden))
                    print("    Marker = {}".format(cur.marker))
                    print("    Markersize = {}".format(cur.markersize))
                    print("    Markeredgecolor = {}".format(cur.markeredgecolor))
                    print("    Markerfacecolor = {}".format(cur.markerfacecolor))
                    print("    Ebar = {}".format(cur.ebar))
                    print("    Erange = {}".format(cur.erange))
                    print("    Plotprecedence = {}".format(cur.plotprecedence))
                    print("    Step Function = {}".format(cur.step))
                    print("    X-ticks Labels = {}".format(cur.xticks_labels))
                    print("\n")
            except:
                pdvutil.print_own_docstring(self)
            finally:
                self.redraw = False

    def do_markerfacecolor(self, line):
        """
        Set the markerface color of curves. Color names can be "blue", "red", etc., or "#eb70aa", a 6 digit set of
        hexadecimal red-green-blue values #RRGGBB. The entire set of HTML-standard color names is available. Type
        `showcolormap` to see the available named colors which will show up in the PyDV plotting area (hit return
        to go back to your plots).

        .. code::

            [PyDV]: markerfacecolor <curve-list> <color-name>

            Ex:
                [PyDV]: markerfacecolor a blue
                [PyDV]: markerfacecolor a:b blue
                [PyDV]: markerfacecolor c d blue
                [PyDV]: markerfacecolor a #aabb33
                [PyDV]: showcolormap
                hit return to go back to your plots
                [PyDV]: markerfacecolor a lime
        """

        try:
            if not line:
                return 0
            line = line.split()
            color = line.pop(-1)
            line = " ".join(line)
            if len(line.split(":")) > 1:
                self.do_markerfacecolor(pdvutil.getletterargs(line) + color)
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        if mclr.is_color_like(color):
                            cur.markerfacecolor = color
                        else:
                            print("error: invalid marker face color " + color)
                            return 0
                    except pdvutil.CurveIndexError:
                        pass

            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_markeredgecolor(self, line):
        """
        Set the markeredge color of curves. Color names can be "blue", "red", etc., or "#eb70aa", a 6 digit set of
        hexadecimal red-green-blue values #RRGGBB. The entire set of HTML-standard color names is available. Type
        `showcolormap` to see the available named colors which will show up in the PyDV plotting area (hit return
        to go back to your plots).

        .. code::

            [PyDV]: markeredgecolor <curve-list> <color-name>

            Ex:
                [PyDV]: markeredgecolor a blue
                [PyDV]: markeredgecolor a:b blue
                [PyDV]: markeredgecolor c d blue
                [PyDV]: markeredgecolor a #aabb33
                [PyDV]: showcolormap
                hit return to go back to your plots
                [PyDV]: markeredgecolor a lime
        """

        try:
            if not line:
                return 0
            line = line.split()
            color = line.pop(-1)
            line = " ".join(line)
            if len(line.split(":")) > 1:
                self.do_markeredgecolor(pdvutil.getletterargs(line) + color)
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        if mclr.is_color_like(color):
                            cur.markeredgecolor = color
                        else:
                            print("error: invalid marker edge color " + color)
                            return 0
                    except pdvutil.CurveIndexError:
                        pass

            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_showstyles(self, line):
        """
        Show available matplotlib styles.

        .. code::

            [PyDV]: showstyles
        """

        try:
            if stylesLoaded:
                ss = pydvpy.get_styles()
                print("\n")
                self.print_topics("Style Names (type style <style-name>):", ss, 15, 80)
            else:
                print("\nNo styles available.\n")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_showcolormap(self, line):
        """
        Show the available named colors. Hit return to go back to your plots.

        .. code::

            [PyDV]: showcolormap
        """

        try:
            ax = plt.gca()
            plt.cla()  # wipe current axes

            ratio = 1.0 / 3.0
            count = numpy.ceil(numpy.sqrt(len(mclr.cnames)))
            x_count = count * ratio
            y_count = count / ratio
            x = 0
            y = 0
            w = 1 / x_count
            h = 1 / y_count
            plt.xlim((0.0, 1.0))
            plt.ylim((0.0, 1.0))

            from matplotlib.collections import PatchCollection

            patches = []
            for c in mclr.cnames:
                pos = (x / x_count, y / y_count)
                rectangle = plt.Rectangle(pos, w, h, color=c)
                patches.append(rectangle)
                ax.add_artist(rectangle)  # needed for colors to show up, sigh :-(
                ax.annotate(c, xy=pos, fontsize="xx-small", verticalalignment="bottom", horizontalalignment="left")
                if y >= y_count - 1:
                    x += 1
                    y = 0
                else:
                    y += 1

            p = PatchCollection(patches)
            ax.add_collection(p)
            plt.draw()
            self.plotter.canvas.draw()

            x = input("hit return to go back to your plots: ")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_mx(self, line):
        """
        Scale the x values of the curves by a fixed value.

        .. code::

            [PyDV]: mx <curve-list> <value>

            Ex:
                [PyDV]: mx a 2
                [PyDV]: mx a:b 2
                [PyDV]: mx c d 2
        """

        try:
            self.__mod_curve(line, "mx")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_divx(self, line):
        """
        Divide x values of curves by a constant.

        .. code::

            [PyDV]: divx <curve-list> <value>

            Ex:
                [PyDV]: divx a 7
                [PyDV]: divx a:b 7
                [PyDV]: divx c d 7
                [PyDV]: divx c d 7
        """

        try:
            self.__mod_curve(line, "divx")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_my(self, line):
        """
        Multiply the y values of curves by a constant.

        .. code::

            [PyDV]: my <curve-list> <value>

            Ex:
                [PyDV]: my a 2
                [PyDV]: my a:b 2
                [PyDV]: my c d 2
        """

        try:
            self.__mod_curve(line, "my")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_divy(self, line):
        """
        Divide y values of curves by a constant.

        .. code::

            [PyDV]: divy <curve-list> <value>

            Ex:
                [PyDV]: divy a 7
                [PyDV]: divy a:b 7
                [PyDV]: divy c d 7
                [PyDV]: divy c d 7
        """

        try:
            self.__mod_curve(line, "divy")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_dx(self, line):
        """
        Shift x values of curves by a constant.

        .. code::

            [PyDV]: dx <curve-list> <value>

            Ex:
                [PyDV]: dx a 3
                [PyDV]: dx a:b 3
                [PyDV]: dx c d 3
        """

        try:
            self.__mod_curve(line, "dx")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_dy(self, line):
        """
        Shift y values of curves by a constant.

        .. code::

            [PyDV]: dy <curve-list> <value>

            Ex:
                [PyDV]: dy a 3
                [PyDV]: dy a:b 3
                [PyDV]: dy c d 3
        """

        try:
            self.__mod_curve(line, "dy")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_L2(self, line):
        """
        Take L2 norm of two curves. The L2 norm is `integral( (curve1 - curve2)**2 )**(1/2)` over the interval
        [xmin,xmax]. Also prints value of integral to command-line.

        .. code::

            [PyDV]: L2 <curve1> <curve2> [<xmin> <xmax>]

            Ex:
                [PyDV]: L2 a b
                [PyDV]: L2 a b 4 10
        """

        try:
            """take L2 norm of two curves given as args"""
            args = line.strip().split()
            if len(args) != 2 and len(args) != 4:
                raise RuntimeError("wrong number of args to L2")
            # put a '2' in between curves and xmin, xmax,
            # to indicate the order of norm to take
            args.insert(2, "2")
            # put args back into a line
            line = " ".join(args)
            # then pass to usual "norm" command
            self.do_norm(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_L1(self, line):
        """
        Take L1 norm of two curves. The L1 norm is `integral( |curve1 - curve2| )` over the interval [xmin,xmax].
        Also prints value of integral to command-line.

        .. code::

            [PyDV]: L1 <curve1> <curve2> [<xmin> <xmax>]

            Ex:
                [PyDV]: L1 a b
                [PyDV]: L1 a b 4 10
        """

        try:
            """take L1 norm of two curves given as args"""
            args = line.strip().split()
            if len(args) != 2 and len(args) != 4:
                raise RuntimeError("wrong number of args to L1")
            # put a '1' in between curves and xmin, xmax,
            # to indicate the order of norm to take
            args.insert(2, "1")
            # put args back into a line
            line = " ".join(args)
            # then pass to usual "norm" command
            self.do_norm(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_norm(self, line):
        """
        Makes a new curve that is the norm of two args. Also prints the value of the integral to command line.
        The p-norm is `(integral( (curve1 - curve2)**p )**(1/p)` over the interval [xmin, xmax], where p = order.

        .. code::

            [PyDV]: norm <curve> <curve> <p> <xmin> <xmax>

            Ex:
                [PyDV]: norm a b 2 10 15
        """

        try:
            """take norm of order N of two curves given as args"""
            args = line.strip().split()
            if len(args) != 3 and len(args) != 5:
                raise RuntimeError("wrong number of args to norm")
            # curves a and b will be our operands
            a = self.curvefromlabel(args[0])
            b = self.curvefromlabel(args[1])
            c = a - b  # new numpy.array object
            c.y = abs(c.y)  # absolute value
            if args[2].lower() != "inf":
                N = int(args[2])  # order of the norm
                c = c**N
            if len(args) == 5:
                xmin = float(args[3])
                xmax = float(args[4])
                if xmax <= xmin:
                    raise RuntimeError("xmin > xmax or xmin == xmax in do_norm()")
            else:
                xmin = min(c.x)
                xmax = max(c.x)
            if args[2].lower() == "inf":
                Linf = 0.0
                for xi, yi in zip(c.x, c.y):
                    if xmin <= xi <= xmax:
                        Linf = max(Linf, yi)
                print("Linf norm = {:.4f}".format(Linf))
                d = c
                d.y = numpy.array([Linf] * c.y.shape[0])
                d.name = "Linf of " + a.plotname + " and " + b.plotname
            else:
                d = pydvpy.integrate(c, xmin, xmax)[0]  # d = integral( c**N )
                d = d ** (1.0 / N)
                print("L{:d} norm = {:.4f}".format(N, max(d.y)))
                d.name = "L%d of " % N + a.plotname + " and " + b.plotname
            self.addtoplot(d)
        except:
            pdvutil.print_own_docstring(self)

    def do_max(self, line):
        """
        Makes a new curve with max y values of curves passed in curvelist.

        .. code::

            [PyDV]: max <curve-list>

            Ex:
                [PyDV]: max a
                [PyDV]: max a:b
                [PyDV]: max c d
        """

        try:
            if not line:
                return 0
            if len(line.split(":")) > 1:
                self.do_max(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()

                if len(line) < 2:
                    return

                curves = list()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                nc = pydvpy.max_curve(curves)

                if nc is not None:
                    self.addtoplot(nc)
                    self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_min(self, line):
        """
        Makes a new curve with min y values of curves passed in curvelist.

        .. code::

            [PyDV]: min <curve-list>

            Ex:
                [PyDV]: min a
                [PyDV]: min a:b
                [PyDV]: min c d
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_min(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()

                if len(line) < 2:
                    return

                curves = list()
                for i in range(len(line)):
                    curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    curves.append(self.plotlist[curvidx])

                nc = pydvpy.min_curve(curves)

                if nc is not None:
                    self.addtoplot(nc)
                    self.plotedit = True
            except:
                pdvutil.print_own_docstring(self)

    def do_average(self, line):
        """
        Average the specified curvelist over the intersection of their domains.

        .. code::

            [PyDV]: average <curve-list>

            Ex:
                [PyDV]: average a
                [PyDV]: average a:b
                [PyDV]: average c d
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_average(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()

                if len(line) < 2:
                    return

                curves = list()
                for i in range(len(self.plotlist)):
                    for j in range(len(line)):
                        if self.plotlist[i].plotname == line[j].upper():
                            curves.append(self.plotlist[i])
                            break

                nc = pydvpy.average_curve(curves)

                if nc is not None:
                    self.addtoplot(nc)
                    self.plotedit = True
            except:
                pdvutil.print_own_docstring(self)

    def do_fit(self, line):
        """
        Make new curve that is polynomial fit to argument. n=1 by default, logy means take log(y-values) before fitting,
        logx means take log(x-values) before fitting.

        .. code::

            [PyDV]: fit <curve> [n] [logx] [logy]

            Ex:
                [PyDV]: fit a
                [PyDV]: fit a 2
                [PyDV]: fit a 2 logx
                [PyDV]: fit a 2 logy
        """

        try:
            """fit curve to line: usage is 'fit curve [n] [logx] [logy]', where n=order of fit, default is linear"""
            print("fitting curve: {}".format(line))
            args = line.strip().split()
            if len(args) == 0 or len(args) > 4:
                raise RuntimeError("wrong number of args to fit")

            c = self.curvefromlabel(args[0])
            logx, logy = False, False

            if "logx" in args:
                logx = True
                args.remove("logx")

            if "logy" in args:
                logy = True
                args.remove("logy")

            assert len(args) in (1, 2)
            if len(args) == 2:
                n = int(args[1])
            else:
                n = 1

            nc = pydvpy.fit(c, n, logx, logy)
            nc.plotname = self.getcurvename()
            self.addtoplot(nc)
        except:
            pdvutil.print_own_docstring(self)

    def do_getx(self, line):
        """
        Return the x values for a given y.

        .. code::

            [PyDV]: getx <curve-list> <y-value>

            Ex:
                [PyDV]: getx a 1.2
                [PyDV]: getx a:b 1.2
                [PyDV]: getx c d 1.2
        """

        try:
            self.__mod_curve(line, "getx")
            print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_gety(self, line):
        """
        Return the y values for a given x.

        .. code::

            [PyDV]: gety <curve-list> <x-value>

            Ex:
                [PyDV]: gety a 3.3
                [PyDV]: gety a:b 3.3
                [PyDV]: gety c d 3.3
        """

        try:
            self.__mod_curve(line, "gety")
            print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_getrange(self, line):
        """
        Return range of curves.

        .. code::

            [PyDV]: getrange <curve-list>

            Ex:
                [PyDV]: getrange a
                [PyDV]: getrange a:b
                [PyDV]: getrange c d
        """

        if not line:
            return
        try:
            if len(line.split(":")) > 1:
                self.do_getrange(pdvutil.getletterargs(line))
                return 0
            else:
                print("\n   Get Range")
                line = line.split()
                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        plotname, miny, maxy = pydvpy.getrange(cur)[0]
                        print("\nCurve " + plotname)
                        print("    ymin: %.6e    ymax: %.6e" % (miny, maxy))
                    except pdvutil.CurveIndexError:
                        pass
                print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_getdomain(self, line):
        """
        Return domain of curves.

        .. code::

            [PyDV]: getdomain <curve-list>

            Ex:
                [PyDV]: getdomain a
                [PyDV]: getdomain a:b
                [PyDV]: getdomain c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_getdomain(pdvutil.getletterargs(line))
                return 0
            else:
                print("\n   Get Domain")
                line = line.split()

                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        plotname, minx, maxx = pydvpy.getdomain(cur)[0]
                        print("\nCurve " + plotname)
                        print("    xmin: %.6e    xmax: %.6e" % (minx, maxx))
                    except pdvutil.CurveIndexError:
                        pass
                print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_sum(self, line):
        """
        Calculate the sum of the x and y values of the curves.

        .. code::

            [PyDV]: sum <curve-list>

            Ex:
                [PyDV]: sum a
                [PyDV]: sum a:b
                [PyDV]: sum c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_sum(pdvutil.getletterargs(line))
                return 0
            else:
                print("\nSum:")
                line = line.split()

                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        plotname, sumx, sumy = pydvpy.sum(cur)[0]
                        print(f"\nCurve {cur.plotname}: {plotname}")
                        print(f"\tsumx: {sumx:.6e}, sumy: {sumy:.6e}")
                    except pdvutil.CurveIndexError:
                        pass
                print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_area(self, line):
        """
        Calculate the area of the curves.

        .. code::

            [PyDV]: area <curve-list>

            Ex:
                [PyDV]: area a
                [PyDV]: area a:b
                [PyDV]: area c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_area(pdvutil.getletterargs(line))
                return 0
            else:
                print("\nArea:")
                line = line.split()

                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        plotname, area = pydvpy.area(cur)[0]
                        print(f"\nCurve {cur.plotname}: {plotname}")
                        print(f"\tarea: {area:.6e}")
                    except pdvutil.CurveIndexError:
                        pass
                print("")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_getymax(self, line):
        """
        Return xy-parings of the x values with the corresponding maximum y-value for the
        curve within the specified domain. If no domain is given, then the full domain
        range is used.

        .. code::

            [PyDV]: getymax <curve> [<xmin> <xmax>]

            Ex:
                [PyDV]: getymax a
                [PyDV]: getymax a 2 7
                [PyDV]: getymax a:b
                [PyDV]: getymax a:b 2 7
                [PyDV]: getymax c d
                [PyDV]: getymax c d 2 7
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_getymax(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                xlow = None
                xhi = None

                try:
                    xhi = float(line[-1])
                    line.pop(-1)
                except:
                    xhi = None

                try:
                    xlow = float(line[-1])
                    line.pop(-1)
                except:
                    xlow = None

                if (xlow is None and xhi is not None) or (xlow is not None and xhi is None):
                    raise RuntimeError("<xmin> and <xmax> must BOTH be specified")

                for i in line:
                    idx = pdvutil.getCurveIndex(i, self.plotlist)
                    cur = self.plotlist[idx]
                    plotname, xy_values = pydvpy.getymax(cur, xlow, xhi)
                    print(f" \n{i.upper()} Curve {plotname}")
                    for x, y in xy_values:
                        print("    x: %.6e    y: %.6e\n" % (x, y))
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_getymin(self, line):
        """
        Return xy-parings of the x values with the corresponding minimum y-value for the
        curve within the specified domain. If no domain is given, then the full domain
        range is used.

        .. code::

            [PyDV]: getymin <curve> [<xmin> <xmax>]

            Ex:
                [PyDV]: getymin a
                [PyDV]: getymin a 2 7
                [PyDV]: getymin a:b
                [PyDV]: getymin a:b 2 7
                [PyDV]: getymin c d
                [PyDV]: getymin c d 2 7
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_getymin(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                xlow = None
                xhi = None

                try:
                    xhi = float(line[-1])
                    line.pop(-1)
                except:
                    xhi = None

                try:
                    xlow = float(line[-1])
                    line.pop(-1)
                except:
                    xlow = None

                if (xlow is None and xhi is not None) or (xlow is not None and xhi is None):
                    raise RuntimeError("<xmin> and <xmax> must BOTH be specified")

                for i in line:
                    idx = pdvutil.getCurveIndex(i, self.plotlist)
                    cur = self.plotlist[idx]
                    plotname, xy_values = pydvpy.getymin(cur, xlow, xhi)
                    print(f" \n{i.upper()} Curve {plotname}")
                    for x, y in xy_values:
                        print("    x: %.6e    y: %.6e\n" % (x, y))
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_cumsum(self, line):
        """
        Create new curve which is the cumulative sum of the original curve.

        .. code::

            [PyDV]: cumsum <curve-list>

            Ex:
                [PyDV]: cumsum a
                [PyDV]: cumsum a:b
                [PyDV]: cumsum c d
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_cumsum(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()

                for i in line:
                    idx = pdvutil.getCurveIndex(i, self.plotlist)
                    cur = self.plotlist[idx]
                    nc = pydvpy.cumsum(cur)
                    self.addtoplot(nc)

                    self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_getlabel(self, line):
        """
        Return the given curve's label.

        .. code::

            [PyDV]: getlabel <curve-list>

            Ex:
                [PyDV]: getlabel a
                [PyDV]: getlabel a:b
                [PyDV]: getlabel c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_getlabel(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()

                for i in range(len(self.plotlist)):
                    cur = self.plotlist[i]
                    for j in range(len(line)):
                        if cur.plotname == line[j].upper():
                            print(f"\n {line[j].upper()} Label = {cur.name}")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_sort(self, line):
        """
        Sort the specified curves so that their points are plotted in order of ascending x values.

        .. code::

            [PyDV]: sort <curve-list>

            Ex:
                [PyDV]: sort a
                [PyDV]: sort a:b
                [PyDV]: sort c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_sort(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        j = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[j]
                        pydvpy.sort(cur)
                    except pdvutil.CurveIndexError:
                        pass

            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_rev(self, line):
        """
        Swap x and y values for the specified curves. You may want to `sort` after this one.

        .. code::

            [PyDV]: rev <curve-list>

            Ex:
                [PyDV]: rev a
                [PyDV]: rev a:b
                [PyDV]: rev c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_rev(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        j = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[j]
                        pydvpy.rev(cur)
                    except pdvutil.CurveIndexError:
                        pass
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_random(self, line):
        """
        Generate random y values between -1 and 1 for the specified curves.

        .. code::

            [PyDV]: random <curve-list>

            Ex:
                [PyDV]: random a
                [PyDV]: random a:b
                [PyDV]: random c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_random(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        j = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[j]
                        pydvpy.random(cur)
                    except pdvutil.CurveIndexError:
                        pass
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_disp(self, line):
        """
        Display the y-values in the specified curve(s).

        .. code::

            [PyDV]: disp <curve-list> [format <format>]

            Ex:
                [PyDV]: disp a
                [PyDV]: disp a:b
                [PyDV]: disp c d
                [PyDV]: disp c d format e
                [PyDV]: disp c d format .4f
        """
        format = "g"
        try:
            if len(line.split(":")) > 1:
                self.do_disp(pdvutil.getletterargs(line))
                return 0
            else:
                print("\n")
                line = line.split()
                if "format" in line:
                    format = line[-1]
                    line = line[:-2]  # remove ['format', 'FORMAT']
                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        ss = pydvpy.disp(cur, False, format=format)
                        self.print_topics("Curve %s: %s" % (cur.plotname, cur.name), ss, 15, 100)
                    except pdvutil.CurveIndexError:
                        pass
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_dispx(self, line):
        """
        Display the x-values in the specified curve(s).

        .. code::

            [PyDV]: dispx <curve-list> [format <format>]

            Ex:
                [PyDV]: dispx a
                [PyDV]: dispx a:b
                [PyDV]: dispx c d
                [PyDV]: dispx c d format e
                [PyDV]: dispx c d format .4f
        """
        format = "g"
        try:
            if len(line.split(":")) > 1:
                self.do_dispx(pdvutil.getletterargs(line))
                return 0
            else:
                print("\n")
                line = line.split()
                if "format" in line:
                    format = line[-1]
                    line = line[:-2]  # remove ['format', 'FORMAT']
                for i in range(len(line)):
                    try:
                        idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[idx]
                        ss = pydvpy.disp(cur, format=format)
                        self.print_topics("Curve %s: %s" % (cur.plotname, cur.name), ss, 15, 100)
                    except pdvutil.CurveIndexError:
                        pass
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_getnumpoints(self, line):
        """
        Display the number of points for the given curve.

        .. code::

            [PyDV]: getnumpoints <curve-list>

            Ex:
                [PyDV]: getnumpoints a
                [PyDV]: getnumpoints a:b
                [PyDV]: getnumpoints c d
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_getnumpoints(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    cur = self.plotlist[idx]
                    print(f"\n    {line[i].upper()} Number of points = {pydvpy.getnumpoints(cur)}")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_abs(self, line):
        """
        Take the absolute value of the y values of the curves. Modifies the existing curve.

        .. code::

            [PyDV]: abs <curve-list>

            Ex:
                [PyDV]: abs a
                [PyDV]: abs a:b
                [PyDV]: abs c d
        """

        try:
            self.__func_curve(line, "abs", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_absx(self, line):
        """
        Take the absolute value of the x values of the curves. Modifies the existing curve.

        .. code::

            [PyDV]: absx <curve-list>

            Ex:
                [PyDV]: absx a
                [PyDV]: absx a:b
                [PyDV]: absx c d
        """

        try:
            self.__func_curve(line, "abs", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_log(self, line):
        """
        Take the natural logarithm of the y values of the curves. If the optional argument `keep-neg-vals` is set to
        false, then zero and negative y-values will be discarded. `keep-neg-vals` is true by default.

        .. code::

            [PyDV]: <log | ln> <curve-list> [keep-neg-vals: True | False]

            Ex:
                [PyDV]: log a
                [PyDV]: log a:b
                [PyDV]: log c d
                [PyDV]: log c d True
        """

        try:
            self.__log(line, LogEnum.LOG)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_logx(self, line):
        """
        Take the natural logarithm of the x values of the curves. If the optional argument `keep-neg-vals` is set to
        false, then zero and negative x-values will be discarded. `keep-neg-vals` is true by default.

        .. code::

            [PyDV]: <logx | lnx> <curve-list> [keep-neg-vals: True | False]

            Ex:
                [PyDV]: logx a
                [PyDV]: logx a:b
                [PyDV]: logx c d
                [PyDV]: logx c d True
        """

        try:
            self.__log(line, LogEnum.LOGX)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_log10(self, line):
        """
        Take the base 10 logarithm of the y values of the curves. If the optional argument `keep-neg-vals` is set to
        false, then zero and negative y-values will be discarded. `keep-neg-vals` is true by default.

        .. code::

            [PyDV]: log10 <curve-list> [keep-neg-vals: True | False]

            Ex:
                [PyDV]: log10 a
                [PyDV]: log10 a:b
                [PyDV]: log10 c d
                [PyDV]: log10 c d True
        """

        try:
            self.__log(line, LogEnum.LOG10)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_log10x(self, line):
        """
        Take the base 10 logarithm of the x values of the curves. If the optional argument `keep-neg-vals` is set to
        false, then zero and negative y-values will be discarded. `keep-neg-vals` is true by default.

        .. code::

            [PyDV]: log10x <curve-list> [keep-neg-vals: True | False]

            Ex:
                [PyDV]: log10x a
                [PyDV]: log10x a:b
                [PyDV]: log10x c d
                [PyDV]: log10x c d True
        """

        try:
            self.__log(line, LogEnum.LOG10X)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_exp(self, line):
        """
        Exponentiate y values of curves, e^y.

        .. code::

            [PyDV]: exp <curve-list>

            Ex:
                [PyDV]: exp a
                [PyDV]: exp a:b
                [PyDV]: exp c d
        """

        try:
            self.__func_curve(line, "exp", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_expx(self, line):
        """
        Exponentiate x values of curves, e^x.

        .. code::

            [PyDV]: expx <curve-list>

            Ex:
                [PyDV]: expx a
                [PyDV]: expx a:b
                [PyDV]: expx c d
        """

        try:
            self.__func_curve(line, "exp", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_cos(self, line):
        """
        Take the cosine of the y values of the curves.

        .. code::

            [PyDV]: cos <curve-list>

            Ex:
                [PyDV]: cos a
                [PyDV]: cos a:b
                [PyDV]: cos c d
        """

        try:
            self.__func_curve(line, "cos", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_cosx(self, line):
        """
        Take the cosine of the x values of the curves.

        .. code::

            [PyDV]: cosx <curve-list>

            Ex:
                [PyDV]: cosx a
                [PyDV]: cosx a:b
                [PyDV]: cosx c d
        """

        try:
            self.__func_curve(line, "cos", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sin(self, line):
        """
        Take the sine of the y values of the curve.

        .. code::

            [PyDV]: sin <curve-list>

            Ex:
                [PyDV]: sin a
                [PyDV]: sin a:b
                [PyDV]: sin c d
        """

        try:
            self.__func_curve(line, "sin", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sinx(self, line):
        """
        Take the sine of the x values of the curve.

        .. code::

            [PyDV]: sinx <curve-list>

            Ex:
                [PyDV]: sinx a
                [PyDV]: sinx a:b
                [PyDV]: sinx c d
        """

        try:
            self.__func_curve(line, "sin", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_tan(self, line):
        """
        Take the tangent of y values of curves.

        .. code::

            [PyDV]: tan <curve-list>

            Ex:
                [PyDV]: tan a
                [PyDV]: tan a:b
                [PyDV]: tan c d
        """

        try:
            self.__func_curve(line, "tan", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_tanx(self, line):
        """
        Take the tangent of x values of curves.

        .. code::

            [PyDV]: tanx <curve-list>

            Ex:
                [PyDV]: tanx a
                [PyDV]: tanx a:b
                [PyDV]: tanx c d
        """

        try:
            self.__func_curve(line, "tan", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_acos(self, line):
        """
        Take arccosine of y values of curves

        .. code::

            [PyDV]: acos <curve-list>

            Ex:
                [PyDV]: acos a
                [PyDV]: acos a:b
                [PyDV]: acos c d
        """

        try:
            self.__func_curve(line, "acos", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_acosx(self, line):
        """
        Take arccosine of x values of curves

        .. code::

            [PyDV]: acosx <curve-list>

            Ex:
                [PyDV]: acosx a
                [PyDV]: acosx a:b
                [PyDV]: acosx c d
        """

        try:
            self.__func_curve(line, "acos", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_asin(self, line):
        """
        Take arcsine of y values of curves.

        .. code::

            [PyDV]: asin <curve-list>

            Ex:
                [PyDV]: asin a
                [PyDV]: asin a:b
                [PyDV]: asin c d
        """

        try:
            self.__func_curve(line, "asin", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_asinx(self, line):
        """
        Take arcsine of x values of curves.

        .. code::

            [PyDV]: asinx <curve-list>

            Ex:
                [PyDV]: asinx a
                [PyDV]: asinx a:b
                [PyDV]: asinx c d
        """

        try:
            self.__func_curve(line, "asin", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_atan(self, line):
        """
        Take arctangent of y values of curves.

        .. code::

            [PyDV]: atan <curve-list>

            Ex:
                [PyDV]: atan a
                [PyDV]: atan a:b
                [PyDV]: atan c d
        """

        try:
            self.__func_curve(line, "atan", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_atanx(self, line):
        """
        Take arctangent of x values of curves.

        .. code::

            [PyDV]: atanx <curve-list>

            Ex:
                [PyDV]: atanx a
                [PyDV]: atanx a:b
                [PyDV]: atanx c d
        """

        try:
            self.__func_curve(line, "atan", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_atan2(self, line):
        """
        Take atan2 of two curves.

        .. code::

            [PyDV]: atan2 <curve1> <curve2>

            Ex:
                [PyDV]: atan2 a
                [PyDV]: atan2 a:b
                [PyDV]: atan2 c d
        """

        try:
            letterargs = [x.upper() for x in line.split()]
            assert len(letterargs) == 2
            a, b = None, None
            for p in self.plotlist:
                if p.plotname == letterargs[0]:
                    a = p
                elif p.plotname == letterargs[1]:
                    b = p
            assert a and b
            c = pydvpy.atan2(a, b, tuple(letterargs))
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_cosh(self, line):
        """
        Take hyperbolic cosine of y values of curves.

        .. code::

            [PyDV]: cosh <curve-list>

            Ex:
                [PyDV]: cosh a
                [PyDV]: cosh a:b
                [PyDV]: cosh c d
        """

        try:
            self.__func_curve(line, "cosh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_coshx(self, line):
        """
        Take hyperbolic cosine of x values of curves.

        .. code::

            [PyDV]: coshx <curve-list>

            Ex:
                [PyDV]: coshx a
                [PyDV]: coshx a:b
                [PyDV]: coshx c d
        """

        try:
            self.__func_curve(line, "cosh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sinh(self, line):
        """
        Take the hyperbolic sine of the y values of the curve

        .. code::

            [PyDV]: sinh <curve-list>

            Ex:
                [PyDV]: sinh a
                [PyDV]: sinh a:b
                [PyDV]: sinh c d
        """

        try:
            self.__func_curve(line, "sinh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sinhx(self, line):
        """
        Take the hyperbolic sine of the x values of the curve

        .. code::

            [PyDV]: sinhx <curve-list>

            Ex:
                [PyDV]: sinhx a
                [PyDV]: sinhx a:b
                [PyDV]: sinhx c d
        """

        try:
            self.__func_curve(line, "sinh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_tanh(self, line):
        """
        Take the hyperbolic tangent of y values of curves

        .. code::

            [PyDV]: tanh <curve-list>

            Ex:
                [PyDV]: tanh a
                [PyDV]: tanh a:b
                [PyDV]: tanh c d
        """

        try:
            self.__func_curve(line, "tanh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_tanhx(self, line):
        """
        Take the hyperbolic tangent of x values of curves

        .. code::

            [PyDV]: tanhx <curve-list>

            Ex:
                [PyDV]: tanhx a
                [PyDV]: tanhx a:b
                [PyDV]: tanhx c d
        """

        try:
            self.__func_curve(line, "tanh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_acosh(self, line):
        """
        Take hyperbolic arccosine of y values of curves.

        .. code::

            [PyDV]: acosh <curve-list>

            Ex:
                [PyDV]: acosh a
                [PyDV]: acosh a:b
                [PyDV]: acosh c d
        """

        try:
            self.__func_curve(line, "acosh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_acoshx(self, line):
        """
        Take hyperbolic arccosine of x values of curves.

        .. code::

            [PyDV]: acoshx <curve-list>

            Ex:
                [PyDV]: acoshx a
                [PyDV]: acoshx a:b
                [PyDV]: acoshx c d
        """

        try:
            self.__func_curve(line, "acosh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_asinh(self, line):
        """
        Take hyperbolic arcsine of y values of curves.

        .. code::

            [PyDV]: asinh <curve-list>

            Ex:
                [PyDV]: asinh a
                [PyDV]: asinh a:b
                [PyDV]: asinh c d
        """

        try:
            self.__func_curve(line, "asinh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_asinhx(self, line):
        """
        Take hyperbolic arcsine of x values of curves.

        .. code::

            [PyDV]: asinhx <curve-list>

            Ex:
                [PyDV]: asinhx a
                [PyDV]: asinhx a:b
                [PyDV]: asinhx c d
        """

        try:
            self.__func_curve(line, "asinh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_atanh(self, line):
        """
        Take hyperbolic arctangent of y values of curves.

        .. code::

            [PyDV]: atanh <curve-list>

            Ex:
                [PyDV]: atanh a
                [PyDV]: atanh a:b
                [PyDV]: atanh c d
        """

        try:
            self.__func_curve(line, "atanh", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_atanhx(self, line):
        """
        Take hyperbolic arctangent of x values of curves.

        .. code::

            [PyDV]: atanhx <curve-list>

            Ex:
                [PyDV]: atanhx a
                [PyDV]: atanhx a:b
                [PyDV]: atanhx c d
        """

        try:
            self.__func_curve(line, "atanh", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_j0(self, line):
        """
        Take the zeroth order Bessel function of y values of curves

        .. code::

            [PyDV]: j0 <curve-list>

            Ex:
                [PyDV]: j0 a
                [PyDV]: j0 a:b
                [PyDV]: j0 c d
        """

        try:
            self.__func_curve(line, "j0", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_j0x(self, line):
        """
        Take the zeroth order Bessel function of x values of curves

        .. code::

            [PyDV]: j0x <curve-list>

            Ex:
                [PyDV]: j0x a
                [PyDV]: j0x a:b
                [PyDV]: j0x c d
        """

        try:
            self.__func_curve(line, "j0", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_j1(self, line):
        """
        Take the first order Bessel function of y values of curves

        .. code::

            [PyDV]: j1 <curve-list>

            Ex:
                [PyDV]: j1 a
                [PyDV]: j1 a:b
                [PyDV]: j1 c d
        """

        try:
            self.__func_curve(line, "j1", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_j1x(self, line):
        """
        Take the first order Bessel function of x values of curves

        .. code::

            [PyDV]: j1x <curve-list>

            Ex:
                [PyDV]: j1x a
                [PyDV]: j1x a:b
                [PyDV]: j1x c d
        """

        try:
            self.__func_curve(line, "j1", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_jn(self, line):
        """
        Take the nth order Bessel function of y values of curves

        .. code::

            [PyDV]: jn <curve-list> <n>

            Ex:
                [PyDV]: jn a 4
                [PyDV]: jn a:b 4
                [PyDV]: jn c d 4
        """

        try:
            self.__func_curve(line, "jn", do_x=0, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_jnx(self, line):
        """
        Take the nth order Bessel function of x values of curves

        .. code::

            [PyDV]: jnx <curve-list> <n>

            Ex:
                [PyDV]: jnx a 4
                [PyDV]: jnx a:b 4
                [PyDV]: jnx c d 4
        """

        try:
            self.__func_curve(line, "jn", do_x=1, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_y0(self, line):
        """
        Take the zeroth order Bessel function of the second kind of the y values of the curves.

        .. code::

            [PyDV]: y0 <curve-list>

            Ex:
                [PyDV]: y0 a
                [PyDV]: y0 a:b
                [PyDV]: y0 c d
        """

        try:
            self.__func_curve(line, "y0", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_y0x(self, line):
        """
        Take the zeroth order Bessel function of the second kind of the x values of the curves.

        .. code::

            [PyDV]: y0x <curve-list>

            Ex:
                [PyDV]: y0x a
                [PyDV]: y0x a:b
                [PyDV]: y0x c d
        """

        try:
            self.__func_curve(line, "y0", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_y1(self, line):
        """
        Take the first order Bessel function of the second kind of the y values of the curves.

        .. code::

            [PyDV]: y1 <curve-list>

            Ex:
                [PyDV]: y1 a
                [PyDV]: y1 a:b
                [PyDV]: y1 c d
        """

        try:
            self.__func_curve(line, "y1", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_y1x(self, line):
        """
        Take the first order Bessel function of the second kind of the x values of the curves.

        .. code::

            [PyDV]: y1x <curve-list>

            Ex:
                [PyDV]: y1x a
                [PyDV]: y1x a:b
                [PyDV]: y1x c d
        """

        try:
            self.__func_curve(line, "y1", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_yn(self, line):
        """
        Take the nth order Bessel function of the second kind of y values of curves.

        .. code::

            [PyDV]: yn <curve-list> <n>

            Ex:
                [PyDV]: yn a 3
                [PyDV]: yn a:b 3
                [PyDV]: yn c d 3
        """

        try:
            self.__func_curve(line, "yn", do_x=0, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_ynx(self, line):
        """
        Take the nth order Bessel function of the second kind of x values of curves.

        .. code::

            [PyDV]: ynx <curve-list> <n>

            Ex:
                [PyDV]: ynx a 3
                [PyDV]: ynx a:b 3
                [PyDV]: ynx c d 3
        """

        try:
            self.__func_curve(line, "yn", do_x=1, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_powa(self, line):
        """
        Raise a fixed value, a, to the power of the y values of the curves.

        .. code::

            [PyDV]: powa <curve-list> <a>

            Ex:
                [PyDV]: powa a 2
                [PyDV]: powa a:b 2
                [PyDV]: powa c d 2
        """

        try:
            self.__func_curve(line, "powa", do_x=0, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_powax(self, line):
        """
        Raise a fixed value, a, to the power of the x values of the curves.

        .. code::

            [PyDV]: powax <curve-list> <a>

            Ex:
                [PyDV]: powax a 2
                [PyDV]: powax a:b 2
                [PyDV]: powax c d 2
        """

        try:
            self.__func_curve(line, "powa", do_x=1, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_powr(self, line):
        """
        Raise the y values of the curves to a fixed power p.

        .. code::

            [PyDV]: powr <curve-list> <p>

            Ex:
                [PyDV]: powr a 2
                [PyDV]: powr a:b 2
                [PyDV]: powr c d 2
        """

        try:
            self.__func_curve(line, "powr", do_x=0, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_powrx(self, line):
        """
        Raise the x values of the curves to a fixed power p.

        .. code::

            [PyDV]: powrx <curve-list> <p>

            Ex:
                [PyDV]: powrx a 2
                [PyDV]: powrx a:b 2
                [PyDV]: powrx c d 2
        """

        try:
            self.__func_curve(line, "powr", do_x=1, idx=-1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_recip(self, line):
        """
        Take the reciprocal of the y values of the curves.

        .. code::

            [PyDV]: recip <curve-list>

            Ex:
                [PyDV]: recip a
                [PyDV]: recip a:b
                [PyDV]: recip c d
        """

        try:
            self.__func_curve(line, "recip", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_recipx(self, line):
        """
        Take the reciprocal of the x values of the curves.

        .. code::

            [PyDV]: recipx <curve-list>

            Ex:
                [PyDV]: recipx a
                [PyDV]: recipx a:b
                [PyDV]: recipx c d
        """

        try:
            self.__func_curve(line, "recip", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sqr(self, line):
        """
        Take the square of the y values of the curves.

        .. code::

            [PyDV]: sqr <curve-list>

            Ex:
                [PyDV]: sqr a
                [PyDV]: sqr a:b
                [PyDV]: sqr c d
        """

        try:
            self.__func_curve(line, "sqr", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sqrx(self, line):
        """
        Take the square of the x values of the curves.

        .. code::

            [PyDV]: sqrx <curve-list>

            Ex:
                [PyDV]: sqrx a
                [PyDV]: sqrx a:b
                [PyDV]: sqrx c d
        """

        try:
            self.__func_curve(line, "sqr", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sqrt(self, line):
        """
        Take the square root of the y values of the curves.

        .. code::

            [PyDV]: sqrt <curve-list>

            Ex:
                [PyDV]: sqrt a
                [PyDV]: sqrt a:b
                [PyDV]: sqrt c d
        """

        try:
            self.__func_curve(line, "sqrt", do_x=0)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_sqrtx(self, line):
        """
        Take the square root of the x values of the curves.

        .. code::

            [PyDV]: sqrtx <curve-list>

            Ex:
                [PyDV]: sqrtx a
                [PyDV]: sqrtx a:b
                [PyDV]: sqrtx c d
        """

        try:
            self.__func_curve(line, "sqrt", do_x=1)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_xlabel(self, line):
        """
        Set a label for the x axis

        .. code::

            [PyDV]: xlabel <label-name>

            Ex:
                [PyDV]: xlabel my_x_label
        """

        try:
            self.set_xlabel(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_ylabel(self, line):
        """
        Set a label for the y axis.

        .. code::

            [PyDV]: ylabel <label-name>

            Ex:
                [PyDV]: ylabel my_y_label
        """

        try:
            self.set_ylabel(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_title(self, line):
        """
        Set a title for the plot

        .. code::

            [PyDV]: title <title-name>

            Ex:
                [PyDV]: title my_title
        """

        try:
            self.set_title(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_legend(self, line):
        """
        Show/Hide the legend with on | off or set legend position with ur, ul, ll, lr, cl, cr, uc, lc.
        Specify the number of columns to use in the legend.
        Specify curves to add to or remove from the legend using the `hide` or `show` keywords followed by the ids of
        the curves. Commands after `hide`/`show` will not be processed, so make sure these are the last in the command
        list.

        .. code::

            [PyDV]: <legend | leg | key> <on | off> [position] [<number of columns>] [<show/hide curve ids>]

            Ex:
                [PyDV]: legend on
                [PyDV]: legend on ul
                [PyDV]: legend on ul 2
                [PyDV]: legend on ul 2
                [PyDV]: legend on ul 2 showid a
                [PyDV]: legend on ul 2 showid a:b
                [PyDV]: legend on ul 2 showid c d
                [PyDV]: legend on ul 2 showid all
                [PyDV]: legend on ul 2 hideid a
                [PyDV]: legend on ul 2 hideid a:b
                [PyDV]: legend on ul 2 hideid c d
                [PyDV]: legend on ul 2 hideid all
        """

        try:
            locs = {"best": 0, "ur": 1, "ul": 2, "ll": 3, "lr": 4, "cl": 6, "cr": 7, "lc": 8, "uc": 9, "c": 10}
            line = line.strip().split()

            for i in range(len(line)):
                key = line[i].lower()

                if key in locs:
                    self.key_loc = locs[key]
                elif key == "on":
                    self.showkey = True
                elif key == "off":
                    self.showkey = False
                elif key in ["hide", "show"]:
                    if line[i + 1] == "all":  # show/hide all curves
                        for cur in self.plotlist:
                            cur.legend_show = False if key == "hide" else True
                    else:
                        if ":" in line[i + 1]:
                            ids = list(pdvutil.getletterargs(line[i + 1]).lower().split())
                        else:
                            ids = [line[j] for j in range(i + 1, len(line))]
                        for curve_id in ids:
                            curve = self.plotlist[pdvutil.getCurveIndex(curve_id, self.plotlist)]
                            curve.legend_show = False if key == "hide" else True
                        break
                elif key in ["hideid", "showid"]:
                    if line[i + 1] == "all":  # show/hide all curves
                        for cur in self.plotlist:
                            cur.name = cur.name.replace(f"`{cur.plotname}` ", "")
                            if key == "showid":
                                cur.name = f"`{cur.plotname}` {cur.name}"
                            else:
                                cur.name.replace(f"`{cur.plotname}` ", "")
                    else:
                        if ":" in line[i + 1]:
                            ids = list(pdvutil.getletterargs(line[i + 1]).lower().split())
                        else:
                            ids = [line[j] for j in range(i + 1, len(line))]
                        for curve_id in ids:
                            curve = self.plotlist[pdvutil.getCurveIndex(curve_id, self.plotlist)]
                            curve.name = curve.name.replace(f"`{curve.plotname}` ", "")
                            if key == "showid":
                                curve.name = f"`{curve.plotname}` {curve.name}"
                            else:
                                curve.name.replace(f"`{curve.plotname}` ", "")
                        break
                else:
                    try:
                        self.key_ncol = int(key)
                    except:
                        raise Exception("Invalid argument: %s" % key)
        except:
            pdvutil.print_own_docstring(self)

    def do_menulength(self, line):
        """
        Adjust the number of curves displayed when executing the `menu` command before Enter needs to be pressed.
        If no length is given, the current menu length will be displayed.

        .. code::

            [PyDV]: menulength <integer>

            Ex:
                [PyDV]: menulength
                [PyDV]: menulength 100
        """

        try:
            if len(line) == 0:
                print("menu length is currently", self.menulength)
            else:
                line = line.split()
                length = int(line[0])
                if length <= 0:
                    length = 1
                self.menulength = length
                print("changing menu length to ", self.menulength)
        except:
            pdvutil.print_own_docstring(self)

    def do_namewidth(self, line):
        """
        Change the width of the namewidth column of the `menu` and `list` output. If no width is given, the
        current column width will be displayed.

        .. code::

            [PyDV]: namewidth <integer>

            Ex:
                [PyDV]: namewidth
                [PyDV]: namewidth 100
        """

        try:
            if len(line) == 0:
                print("label column width is currently", self.namewidth)
            else:
                line = line.split()
                width = int(line[0])
                if width < 0:
                    width = 0
                self.namewidth = width
                print("changing label column width to ", self.namewidth)
        except:
            pdvutil.print_own_docstring(self)

    def do_xlabelwidth(self, line):
        """
        Change the width of the xlabel column of the `menu` and `list` output. If no width is given, the
        current column width will be displayed.

        .. code::

            [PyDV]: xlabelwidth <integer>

            Ex:
                [PyDV]: xlabelwidth
                [PyDV]: xlabelwidth 100
        """

        try:
            if len(line) == 0:
                print("xlabel column width is currently", self.xlabelwidth)
            else:
                line = line.split()
                width = int(line[0])
                if width < 0:
                    width = 0
                self.xlabelwidth = width
                print("changing xlabel column width to", self.xlabelwidth)
        except:
            pdvutil.print_own_docstring(self)

    def do_ylabelwidth(self, line):
        """
        Change the width of the ylabel column of the `menu` and `list` output. If no width is given, the
        current column width will be displayed.

        .. code::

            [PyDV]: ylabelwidth <integer>

            Ex:
                [PyDV]: ylabelwidth
                [PyDV]: ylabelwidth 100
        """

        try:
            if len(line) == 0:
                print("label column width is currently", self.ylabelwidth)
            else:
                line = line.split()
                width = int(line[0])
                if width < 0:
                    width = 0
                self.ylabelwidth = width
                print("changing ylabel column width to", self.ylabelwidth)
        except:
            pdvutil.print_own_docstring(self)

    def do_filenamewidth(self, line):
        """
        Change the width of the fname column of the `menu` and `list` output. If no width is given, the
        current column width will be displayed.

        .. code::

            [PyDV]: filenamewidth <integer>

            Ex:
                [PyDV]: filenamewidth
                [PyDV]: filenamewidth 100
        """

        try:
            if len(line) == 0:
                print("file column width is currently", self.filenamewidth)
            else:
                line = line.split()
                width = int(line[0])
                if width < 0:
                    width = 0
                self.filenamewidth = width
                print("changing file column width to", self.filenamewidth)
        except:
            pdvutil.print_own_docstring(self)

    def do_recordidwidth(self, line):
        """
        Change the width of the record_id column of the `menu` and `list` output. If no width is given, the
        current column width will be displayed.

        .. code::

            [PyDV]: recordidwidth <integer>

            Ex:
                [PyDV]: recordidwidth
                [PyDV]: recordidwidth 100
        """

        try:
            if len(line) == 0:
                print("record_id column width is currently", self.recordidwidth)
            else:
                line = line.split()
                width = int(line[0])
                if width < 0:
                    width = 0
                self.recordidwidth = width
                print("changing rec id column width to", self.recordidwidth)
        except:
            pdvutil.print_own_docstring(self)

    def do_handlelength(self, line):
        """
        Adjust the length of the line(s) in the legend.

        .. code::

            [PyDV]: handlelength <length>

            Ex:
                [PyDV]: handlelength 10
        """

        try:
            key = line.strip().split()[0]
            if key.upper() == "NONE":
                self.handlelength = None
            else:
                self.handlelength = max(0, int(key))
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_minorticks(self, line):
        """
        Minor ticks are not visible by default. On will make the minor ticks visible and off will hide the minor ticks.

        .. code::

            [PyDV]: minorticks <on | off>

            Ex:
                [PyDV]: minorticks on
                [PyDV]: minorticks off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showminorticks = False
            elif line == "1" or line.upper() == "ON":
                self.showminorticks = True
            else:
                print("invalid input: requires on, off, 1, or 0 as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_border(self, line):
        """
        Show or hide the plot border. By default, the border color is black.

        .. code::

            [PyDV]: border <on | 1 | off | 0> [color]

            Ex:
                [PyDV]: border on
                [PyDV]: border on blue
                [PyDV]: border off
        """

        try:
            color = None
            line = line.split()
            arg_count = len(line)

            if arg_count == 1:
                show = line[0]
            elif arg_count == 2:
                show = line[0]
                color = line[1]
            else:
                raise RuntimeError("Too many arguments: Expected 1 or 2 but received {}".format(arg_count))

            if show == "0" or show.upper() == "OFF":
                self.bordercolor = None
            elif show == "1" or show.upper() == "ON":
                if arg_count > 1:
                    if mclr.is_color_like(color):
                        self.bordercolor = color
                        self.plotedit = True
                    else:
                        raise RuntimeError("Invalid color {}".format(color))
                else:
                    self.bordercolor = "black"
            else:
                raise RuntimeError("invalid input: requires on, 1, off, or 0 as argument")

        except:
            pdvutil.print_own_docstring(self)

    def do_grid(self, line):
        """
        Show or hide the grid on the graph.

        .. code::

            [PyDV]: grid <on | off>

            Ex:
                [PyDV]: grid on
                [PyDV]: grid off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showgrid = False
            elif line == "1" or line.upper() == "ON":
                self.showgrid = True
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_axis(self, line):
        """
        Show or hide the axis.

        .. code::

            [PyDV]: axis <on | off>

            Ex:
                [PyDV]: axis on
                [PyDV]: axis off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showaxis = "off"
            elif line == "1" or line.upper() == "ON":
                self.showaxis = "on"
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_plot(self, line):
        """
        Show or hide the line plots.

        .. code::

            [PyDV]: plot <on | off>

            Ex:
                [PyDV]: plot on
                [PyDV]: plot off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showplot = "off"
                self.showkey = False  # legend
            elif line == "1" or line.upper() == "ON":
                self.showplot = "on"
                self.showkey = True  # legend
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_recolor(self, line):
        """
        Reset the color of the line plots.

        .. code::

            [PyDV]: recolor
        """

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        j = 0
        for i in range(len(self.plotlist)):
            self.do_color(f"{self.plotlist[i].plotname} {colors[j]}")
            j += 1
            if j == 7:
                j = 0

    def do_merge(self, line):
        """
        Merge ultra files together.

        .. code::

            [PyDV]:  merge <newfile> <myfile1> <myfile2> etc...

            Ex:
                [PyDV]: merge newfile.ult myfile1.ult myfile2.ult
        """

        try:
            line = line.split()
            new_file = line[0]

            if os.path.exists(new_file):
                ans = input(f"{new_file} already exists. Overwrite? [y/n]: ")

                if ans.upper() in ["YES", "Y"]:
                    print(f"Overwriting {new_file}")
                elif ans.upper() in ["NO", "N"]:
                    print(f"Not overwriting {new_file}")
                    return
                else:
                    print("Please try again and type [y/n]")
                    return

            other_files = line[1:]
            with open(new_file, "w") as f1:
                lines = []
                for other_file in other_files:
                    with open(other_file, "r") as f2:
                        lines += f2.readlines()
                        lines += "\n"
                f1.writelines(lines)
        except:
            pdvutil.print_own_docstring(self)

    def do_gridcolor(self, line):
        """
        Set the color of the grid. White is default.

        .. code::

            [PyDV]: gridcolor <color>

            Ex:
                [PyDV]: gridcolor blue
        """

        if not line:
            return 0
        try:
            color = line.strip()
            if mclr.is_color_like(color):
                self.gridcolor = color
                self.plotedit = True
            else:
                print("error: invalid color " + color)
                return 0
        except:
            pdvutil.print_own_docstring(self)

    def do_gridstyle(self, line):
        """
        Set the line style for the grid.

        .. code::

            [PyDV]: gridstyle <style: solid | dash | dot | dashdot>

            Ex:
                [PyDV]: gridstyle solid
                [PyDV]: gridstyle dash
                [PyDV]: gridstyle dot
                [PyDV]: gridstyle dashdot
        """

        if not line:
            return 0

        style = line.strip()

        if style == "solid":
            self.gridstyle = "-"
        elif style == "dot":
            self.gridstyle = ":"
        elif style == "dash":
            self.gridstyle = "--"
        elif style == "dashdot":
            self.gridstyle = "-."
        else:
            pdvutil.print_own_docstring(self)
            return 0

    def do_gridwidth(self, line):
        """
        Set the grid line width in points.

        .. code::

            [PyDV]: gridwidth <width>

            Ex:
                [PyDV]: gridwidth 5
        """

        if not line:
            return 0

        try:
            self.gridwidth = float(line.strip())
        except:
            pdvutil.print_own_docstring(self)

    def do_dataid(self, line):
        """
        Show or hide curve identifiers on plot.

        .. code::

            [PyDV]: dataid <on | off>

            Ex:
                [PyDV]: dataid on
                [PyDV]: dataid off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showletters = False
            elif line == "1" or line.upper() == "ON":
                self.showletters = True
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_xlogscale(self, line):
        """
        Show the x axis on a log scale.

        .. code::

            [PyDV]: <xlogscale | xls> <on | off>

            Ex:
                [PyDV]: xlogscale on
                [PyDV]: xlogscale off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.xlogscale = False
            elif line == "1" or line.upper() == "ON":
                self.xlogscale = True
                plt.xscale("log")
                if self.xlim is not None:
                    xmin = max(1e-2, self.xlim[0])
                    self.xlim = (xmin, max(self.xlim[1], 1000.0 * xmin))
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_ylogscale(self, line):
        """
        Set log scale on or off for the y-axis.

        .. code::

            [PyDV]: <ylogscale | yls> <on | off>

            Ex:
                [PyDV]: ylogscale on
                [PyDV]: ylogscale off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.ylogscale = False
            elif line == "1" or line.upper() == "ON":
                self.ylogscale = True
                plt.yscale("log")
                if self.ylim is not None:
                    ymin = max(1e-2, self.ylim[0])
                    self.ylim = (ymin, max(self.ylim[1], 1000.0 * ymin))
            else:
                print("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_guilims(self, line):
        """
        Set whether or not to use the GUI min/max values for the X and Y limits. Default is off.

        .. code::

            [PyDV]: guilims <on | off>

            Ex:
                [PyDV]: guilims on
                [PyDV]: guilims off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.guilims = False
                self.xlim = None
                self.ylim = None
            elif line == "1" or line.upper() == "ON":
                self.guilims = True
                self.xlim = plt.gca().get_xlim()
                self.ylim = plt.gca().get_ylim()
            else:
                raise RuntimeError("{} is not a valid input.".format(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_update(self, line):
        """
        Update the plot after each command if True. Update the plot is ON by default.

        .. code::

            [PyDV]: update on | off

            Ex:
                [PyDV]: update on
                [PyDV]: update off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.update = False
            elif line == "1" or line.upper() == "ON":
                self.update = True
            else:
                print("invalid input: requires on/1 or off/0 as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_latex(self, line):
        """
        Use LaTeX font rendering.

        .. code::

            [PyDV]: latex <on | off>

            Ex:
                [PyDV]: latex on
                [PyDV]: latex off
        """

        try:
            line = line.strip()

            if line == "0" or line.upper() == "OFF":
                matplotlib.rc("text", usetex=False)
            elif line == "1" or line.upper() == "ON":
                matplotlib.rc("text", usetex=True)
            else:
                print("invalid input: requires on, off, 1, or 0 as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_scatter(self, line):
        """
        Show given curves as points rather than continuous line.

        .. code::

            [PyDV]: scatter <curve-list> <on | off>

            Ex:
                [PyDV]: scatter a on
                [PyDV]: scatter a:b on
                [PyDV]: scatter c d off
        """

        try:
            self.__mod_curve(line, "scatter")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_linespoints(self, line):
        """
        Show given curves as points and a line rather than continuous line.

        .. code::

            [PyDV]: linespoints <curve-list> on | off

            Ex:
                [PyDV]: linespoints a on
                [PyDV]: linespoints a:b on
                [PyDV]: linespoints c d off
        """

        try:
            self.__mod_curve(line, "linespoints")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_lnwidth(self, line):
        """
        Set the line widths of the specified curves. A line width of 0 will give the thinnest line which the host
        graphics system supports.

        .. code::

            [PyDV]: lnwidth <curve-list> <width>

            Ex:
                [PyDV]: lnwidth a 2
                [PyDV]: lnwidth a:b 2
                [PyDV]: lnwidth c d 2
        """

        try:
            self.__mod_curve(line, "lnwidth")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_lnstyle(self, line):
        """
        Set the line style of the specified curves.

        .. code::

            [PyDV]: lnstyle <curve-list> <style: solid | dash | dot | dotdash>

            Ex:
                [PyDV]: lnstyle a solid
                [PyDV]: lnstyle a:b dash
                [PyDV]: lnstyle c d dot
        """

        try:
            self.__mod_curve(line, "lnstyle")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_drawstyle(self, line):
        """
        Set draw style of given curves.

        .. code::

            [PyDV]: drawstyle <curve-list> <style: default | steps | steps-pre | steps-post | steps-mid>

            Ex:
                [PyDV]: drawstyle a steps
                [PyDV]: drawstyle a:b steps-pre
                [PyDV]: drawstyle c d steps-post
        """

        try:
            self.__mod_curve(line, "drawstyle")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_dashstyle(self, line):
        """
        Set the style of dash or dot dash lines. The python list is a list of integers, alternating how many pixels
        to turn on and off, for example:

        [2, 2] : Two pixels on, two off (will result in a dot pattern).

        [4, 2, 2, 2] : 4 on, 2 off, 2 on, 2 off (results in a dash-dot pattern).

        [4, 2, 2, 2, 4, 2] : Gives a dash-dot-dash pattern.

        [4, 2, 2, 2, 2, 2] : Gives a dash-dot-dot pattern.

        See matplotlib 'set_dashes' command for more information.

        .. code::

            [PyDV]: dashstyle <curve-list> <[...]>

            Ex:
                [PyDV]: dashstyle a [2, 2]
                [PyDV]: dashstyle a:b [2, 2]
                [PyDV]: dashstyle c d [2, 2]
        """

        try:
            options = line[line.index("[") :]
            line = line[0 : line.index("[")]
            self.modcurve(line, "dashstyle", options)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_group(self, line):
        """
        Group curves based on name and file if curve names are the same. Max number of same name curves is 14.
        Can also update title to curve name and change labels to filenames if all curves share the same name.
        If `title` is passed, one can adjust the filename label with number of `slashes` as well.
        If `off` is passed, will reset curves back to normal and stop automatic grouping.
        Note: `title` also looks at hidden curves thus need to delete curves (e.g. `del a`).

        .. code::

            [PyDV]: group <title <slashes #> > <off>

            Ex:
                [PyDV]: group
                [PyDV]: group title
                [PyDV]: group title slashes 2
                [PyDV]: group off
        """
        if "off" in line:
            self.group = 0
        else:
            self.group = 1

        if "title" in line:
            title_update = True
        else:
            title_update = False

        if "slashes" in line:
            self.slashes = int(line.split()[-1])

        pn = []
        cn = []
        fn = []
        for cur in self.plotlist:
            pn.append(cur.plotname)
            cn.append(cur._original_name)
            fn.append(cur.filename)

        # Setting Linestyles at the file level
        files = []

        for f in fn:  # ordered set
            if f not in files:
                files.append(f)

        groups = {}

        for f in files:
            temp = []
            for i, plotname in enumerate(pn):
                if fn[i] == f:
                    temp.append(plotname)

            groups[f] = temp

        styles = [
            ("solid", "solid"),  # Same as (0, ()) or '-'
            ("dot", "dot"),  # Same as (0, (1, 1)) or ':'
            ("dash", "dash"),  # Same as '--'
            ("dashdot", "dashdot"),  # Same as '-.'
            ("loosely_dotted", "(0, (1, 10))"),
            ("long_dash_with_offset", "(5, (10, 3))"),
            ("loosely_dashed", "(0, (5, 10))"),
            ("dashed", "(0, (5, 5))"),
            ("loosely_dashdotted", "(0, (3, 10, 1, 10))"),
            ("dashdotted", "(0, (3, 5, 1, 5))"),
            ("densely_dashdotted", "(0, (3, 1, 1, 1))"),
            ("dashdotdotted", "(0, (3, 5, 1, 5, 1, 5))"),
            ("loosely_dashdotdotted", "(0, (3, 10, 1, 10, 1, 10))"),
            ("densely_dashdotdotted", "(0, (3, 1, 1, 1, 1, 1))"),
        ]

        for i, filename in enumerate(groups):
            curves_ = " ".join(groups[filename])
            self.do_lnstyle(curves_ + " " + styles[i % len(styles)][0].replace("'", ""))

        # Setting Colors at the curve level
        curve_names = []

        for curve_name in cn:  # ordered set
            if curve_name not in curve_names:
                curve_names.append(curve_name)
        groups = {}

        for curve_name in curve_names:
            temp = []
            for i, plotname in enumerate(pn):
                if cn[i] == curve_name:
                    temp.append(plotname)

            groups[curve_name] = temp

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        for i, curve_name in enumerate(groups):
            curves_ = " ".join(groups[curve_name])
            self.do_color(curves_ + " " + colors[i % len(colors)].replace("'", ""))

        for cur in self.plotlist:
            path = os.path.normpath(cur.filename)
            path_parts = path.split(os.sep)
            path_section = os.path.join(*path_parts[-self.slashes :])

            if len(curve_names) == 1 and (title_update or self.title == curve_names[0]):
                self.do_label(f"{cur.plotname} {path_section}")
            else:
                if self.slashes != 0:
                    self.do_label(f"{cur.plotname} {cur._original_name} - {path_section}")

        if len(curve_names) == 1 and title_update:
            self.do_title(f"{curve_names[0].strip()}")

        if not self.group or len(files) == 1:
            for i, cur in enumerate(self.plotlist):
                self.do_label(f"{cur.plotname} {cur._original_name}")
                temp_color = colors[i % len(colors)].replace("'", "")
                self.do_color(f"{cur.plotname} {temp_color}")
                self.do_lnstyle(f"{cur.plotname} solid")
            self.slashes = 100

    def do_hide(self, line):
        """
        Hide a curve from the graph.

        .. code::

            [PyDV]: hide <curve-list>

            Ex:
                [PyDV]: hide a
                [PyDV]: hide a:b
                [PyDV]: hide c d
        """

        try:
            line = line + " " + "ON"
            self.__mod_curve(line, "hide")
            self.reset_xticks_labels()
        except:
            pdvutil.print_own_docstring(self)

    def do_show(self, line):
        """
        Show the specified curves hidden by the `hide` command

        .. code::

            [PyDV]: show <curve-list>

            Ex:
                [PyDV]: show a
                [PyDV]: show a:b
                [PyDV]: show c d
        """

        try:
            line = line + " " + "OFF"
            self.__mod_curve(line, "hide")
            self.reset_xticks_labels()
        except:
            pdvutil.print_own_docstring(self)

    def do_style(self, line):
        """
        Use matplotlib style settings from a style specification. The style name of **default** (if available) is
        reserved for reverting back to the default style settings. You can type the command `showstyles` and see
        Matplotlib's Style sheets reference.

        .. code::

            [PyDV]: style <style-name>

            Ex:
                [PyDV]: style classic
        """

        try:
            line = line.split()
            self.plotter.style = line[0]
            self.updatestyle = True
            self.redraw = True
        except:
            pdvutil.print_own_docstring(self)

    def do_range(self, line):
        """
        Set the range for plotting. Using de (for default) will let the curves determine the range.

        .. code::

            [PyDV]: <range | ran> <y-min> <y-max> | de

            Ex:
                [PyDV]: range 3 7
                [PyDV]: range de
        """

        try:
            line = line.split()
            if line and line[0] == "de":
                self.ylim = None
            elif len(line) == 2:
                self.ylim = (float(line[0]), float(line[1]))
            else:
                print("error: exactly two arguments required or de for default")
        except:
            pdvutil.print_own_docstring(self)

    def do_domain(self, line):
        """
        Set the domain for plotting. Using de (for default) will let the curves determine the domain.

        .. code::

            [PyDV]: <domain | dom> <x-min> <x-max>

            Ex:
                [PyDV]: domain 3 7
                [PyDV]: domain de
        """

        try:
            line = line.split()
            if line and line[0] == "de":
                self.xlim = None
            elif len(line) == 2:
                self.xlim = (float(line[0]), float(line[1]))
            else:
                print("error: exactly two arguments required or de for default")
        except:
            pdvutil.print_own_docstring(self)

    def do_list(self, line):
        """
        List the curves that are plotted.
        A regular expression may be supplied for matching against the curve label to be listed.

        Regular expressions are based on the Python regex syntax, not the UNIX syntax.
        In particular, '*' is not the wildcard you might be expecting.

        For an explanation of the regex syntax, type 'help regex'.

        .. code::

            [PyDV]: <list | lst> <label-pattern>

            Ex:
                [PyDV]: list
                [PyDV]: list my.*curves
        """

        try:
            reg = re.compile(r"")
            if line:
                try:
                    reg = re.compile(r"%s" % line)
                except:
                    print("error - invalid regex label-pattern")
                    return 0

            print(
                "{:<5} {:<{namewidth}.{namewidth}} {:<{xlabelwidth}.{xlabelwidth}} {:<{ylabelwidth}.{ylabelwidth}} ".format(  # noqa: E501
                    "curve",
                    "curve_name",
                    "xlabel",
                    "ylabel",
                    namewidth=self.namewidth,
                    xlabelwidth=self.xlabelwidth,
                    ylabelwidth=self.ylabelwidth,
                )
                + "{:<9} {:<9} {:<9} {:<9} {:<{filenamewidth}.{filenamewidth}} {:<{recordidwidth}.{recordidwidth}}".format(  # noqa: E501
                    "xmin",
                    "xmax",
                    "ymin",
                    "ymax",
                    "fname",
                    "record_id",
                    filenamewidth=self.filenamewidth,
                    recordidwidth=self.recordidwidth,
                )
            )
            print(
                "".join(
                    ["-"]
                    * (
                        5
                        + self.namewidth
                        + self.xlabelwidth
                        + self.ylabelwidth
                        + 9
                        + 9
                        + 9
                        + 9
                        + self.filenamewidth
                        + self.recordidwidth
                        + 9
                    )
                )
            )  # last digit is number of columns - 1
            for cur in self.plotlist:
                searchline = cur.name + " " + cur.filename
                if not line or reg.search(searchline):
                    plotname = ""
                    if cur.edited:
                        plotname = "*"
                    plotname = plotname + cur.plotname
                    name = cur.name
                    name = pdvutil.truncate(cur.name.ljust(self.namewidth), self.namewidth)
                    xlabel = cur.xlabel
                    xlabel = xlabel.ljust(self.xlabelwidth)
                    xlabel = pdvutil.truncate(xlabel, self.xlabelwidth)
                    ylabel = cur.ylabel
                    ylabel = ylabel.ljust(self.ylabelwidth)
                    ylabel = pdvutil.truncate(ylabel, self.ylabelwidth)
                    fname = cur.filename
                    fname = fname.ljust(self.filenamewidth)
                    fname = pdvutil.truncate(fname, self.filenamewidth, "right")
                    record_id = cur.record_id
                    record_id = record_id.ljust(self.recordidwidth)
                    record_id = pdvutil.truncate(record_id, self.recordidwidth)
                    xmin = "%.2e" % min(cur.x)
                    xmax = "%.2e" % max(cur.x)
                    ymin = "%.2e" % min(cur.y)
                    ymax = "%.2e" % max(cur.y)
                    print(
                        "{:>5} {} {} {} {:9} {:9} {:9} {:9} {} {}".format(
                            plotname, name, xlabel, ylabel, xmin, xmax, ymin, ymax, fname, record_id
                        )
                    )
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_listr(self, line):
        """
        List the curves that are plotted in the range from start to stop.
        If stop is not specified, it will be set to the end of the curve list.

        .. code::

            [PyDV]: listr <start> [stop]

            Ex:
                [PyDV]: listr 1
                [PyDV]: listr 1 10
        """

        group_plotnames = []
        group_curvenames = []
        group_filenames = []

        try:
            line = line.split()
            argcnt = len(line)
            pllen = len(self.plotlist)
            start = 0
            stop = pllen

            if argcnt == 1:
                start = int(line[0]) - 1
            elif argcnt == 2:
                start = int(line[0]) - 1
                stop = int(line[1])
            else:
                raise RuntimeError("Invalid number of arguments. Received {} expecting 1 or 2.".format(argcnt))

            # Clamp start/stop values in range(0, len(plotlist))
            if start < 0:
                start = 0

            if stop > pllen:
                stop = pllen

            print(
                "{:<5} {:<{namewidth}.{namewidth}} {:<{xlabelwidth}.{xlabelwidth}} {:<{ylabelwidth}.{ylabelwidth}} ".format(  # noqa: E501
                    "curve",
                    "curve_name",
                    "xlabel",
                    "ylabel",
                    namewidth=self.namewidth,
                    xlabelwidth=self.xlabelwidth,
                    ylabelwidth=self.ylabelwidth,
                )
                + "{:<9} {:<9} {:<9} {:<9} {:<{filenamewidth}.{filenamewidth}} {:<{recordidwidth}.{recordidwidth}}".format(  # noqa: E501
                    "xmin",
                    "xmax",
                    "ymin",
                    "ymax",
                    "fname",
                    "record_id",
                    filenamewidth=self.filenamewidth,
                    recordidwidth=self.recordidwidth,
                )
            )
            print(
                "".join(
                    ["-"]
                    * (
                        5
                        + self.namewidth
                        + self.xlabelwidth
                        + self.ylabelwidth
                        + 9
                        + 9
                        + 9
                        + 9
                        + self.filenamewidth
                        + self.recordidwidth
                        + 9
                    )
                )
            )  # last digit is number of columns - 1
            for i in range(start, stop):
                curve = self.plotlist[i]
                plotname = ""
                if curve.edited:
                    plotname = "*"
                plotname = plotname + curve.plotname
                name = curve.name
                name = pdvutil.truncate(curve.name.ljust(self.namewidth), self.namewidth)
                xlabel = curve.xlabel
                xlabel = xlabel.ljust(self.xlabelwidth)
                xlabel = pdvutil.truncate(xlabel, self.xlabelwidth)
                ylabel = curve.ylabel
                ylabel = ylabel.ljust(self.ylabelwidth)
                ylabel = pdvutil.truncate(ylabel, self.ylabelwidth)
                fname = curve.filename
                fname = fname.ljust(self.filenamewidth)
                fname = pdvutil.truncate(fname, self.filenamewidth, "right")
                record_id = curve.record_id
                record_id = record_id.ljust(self.recordidwidth)
                record_id = pdvutil.truncate(record_id, self.recordidwidth)
                xmin = "%.2e" % min(curve.x)
                xmax = "%.2e" % max(curve.x)
                ymin = "%.2e" % min(curve.y)
                ymax = "%.2e" % max(curve.y)
                print(
                    "{:>5} {} {} {} {:9} {:9} {:9} {:9} {} {}".format(
                        plotname, name, xlabel, ylabel, xmin, xmax, ymin, ymax, fname, record_id
                    )
                )

                group_plotnames.append(plotname)
                group_curvenames.append(name)
                group_filenames.append(fname)

        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            return group_plotnames, group_curvenames, group_filenames

    def do_kill(self, line):
        """
        Delete the specified entries from the menu.

        .. code::

            [PyDV]: kill [all | number-list]

            Ex:
                [PyDV]: kill all
                [PyDV]: kill 5:7
        """

        try:
            if not line:
                raise RuntimeError("Argument(s) missing.")

            if "all" in line:
                self.curvelist = list()
            else:
                tmpcurvelist = list()

                for i in range(len(self.curvelist)):
                    if str(i + 1) not in line:
                        tmpcurvelist.append(self.curvelist[i])

                self.curvelist = tmpcurvelist
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False
            self.plotter.updateDialogs()

    def do_menur(self, line):
        """
        List the curves available for plotting in the range from start to stop.
        If stop is not specified, it will be set to the end of the curve list.

        .. code::

            [PyDV]: menur <start> [stop]

            Ex:
                [PyDV]: menur 1
                [PyDV]: menur 1 10
        """

        try:
            line = line.split()
            argcnt = len(line)
            start = 0
            stop = len(self.curvelist)

            if argcnt == 1:
                start = int(line[0]) - 1
            elif argcnt == 2:
                start = int(line[0]) - 1
                stop = int(line[1])
            else:
                raise RuntimeError("Invalid number of arguments. Received {} expecting 1 or 2.".format(argcnt))

            # Clamp start/stop values in range(0, len(curvelist))
            if start < 0:
                start = 0

            if stop > len(self.curvelist):
                stop = len(self.curvelist)

            print(
                "{:>5} {:<{namewidth}.{namewidth}} {:<{xlabelwidth}.{xlabelwidth}} {:<{ylabelwidth}.{ylabelwidth}} ".format(  # noqa: E501
                    "index",
                    "curve_name",
                    "xlabel",
                    "ylabel",
                    namewidth=self.namewidth,
                    xlabelwidth=self.xlabelwidth,
                    ylabelwidth=self.ylabelwidth,
                )
                + "{:<9} {:<9} {:<9} {:<9} {:<{filenamewidth}.{filenamewidth}} {:<{recordidwidth}.{recordidwidth}}".format(  # noqa: E501
                    "xmin",
                    "xmax",
                    "ymin",
                    "ymax",
                    "fname",
                    "record_id",
                    filenamewidth=self.filenamewidth,
                    recordidwidth=self.recordidwidth,
                )
            )
            print(
                "".join(
                    ["-"]
                    * (
                        5
                        + self.namewidth
                        + self.xlabelwidth
                        + self.ylabelwidth
                        + 9
                        + 9
                        + 9
                        + 9
                        + self.filenamewidth
                        + self.recordidwidth
                        + 9
                    )
                )
            )  # last digit is number of columns - 1

            for i in range(start, stop):
                index = str(i + 1)
                name = self.curvelist[i].name
                name = name.ljust(self.namewidth)
                name = pdvutil.truncate(name, self.namewidth)
                xlabel = self.curvelist[i].xlabel
                xlabel = xlabel.ljust(self.xlabelwidth)
                xlabel = pdvutil.truncate(xlabel, self.xlabelwidth)
                ylabel = self.curvelist[i].ylabel
                ylabel = ylabel.ljust(self.ylabelwidth)
                ylabel = pdvutil.truncate(ylabel, self.ylabelwidth)
                fname = self.curvelist[i].filename
                fname = fname.ljust(self.filenamewidth)
                fname = pdvutil.truncate(fname, self.filenamewidth, "right")
                record_id = self.curvelist[i].record_id
                record_id = record_id.ljust(self.recordidwidth)
                record_id = pdvutil.truncate(record_id, self.recordidwidth)
                xmin = "%.2e" % min(self.curvelist[i].x)
                xmax = "%.2e" % max(self.curvelist[i].x)
                ymin = "%.2e" % min(self.curvelist[i].y)
                ymax = "%.2e" % max(self.curvelist[i].y)
                print(
                    "{:>5} {} {} {} {:9} {:9} {:9} {:9} {} {}".format(
                        index, name, xlabel, ylabel, xmin, xmax, ymin, ymax, fname, record_id
                    )
                )
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_menu(self, line):
        """
        List the curves available for plotting.
        A regular expression may be supplied for matching against the curve label to be listed.

        Regular expressions are based on the Python regex syntax, not the UNIX syntax.
        In particular, '*' is not the wildcard you might be expecting.

        For an explanation of the regex syntax, type 'help regex'.

        .. code::

            [PyDV]: menu <label-pattern>

            Ex:
                [PyDV]: menu
                [PyDV]: menu my.*curves
        """

        menu_j = 1
        j = 0
        try:
            reg = re.compile(r"")
            if line:
                try:
                    reg = re.compile(r"%s" % line)
                except:
                    print("error - invalid regex label-pattern")
                    return 0

            print(
                "{:>5} {:<{namewidth}.{namewidth}} {:<{xlabelwidth}.{xlabelwidth}} {:<{ylabelwidth}.{ylabelwidth}} ".format(  # noqa E501
                    "index",
                    "curve_name",
                    "xlabel",
                    "ylabel",
                    namewidth=self.namewidth,
                    xlabelwidth=self.xlabelwidth,
                    ylabelwidth=self.ylabelwidth,
                )
                + "{:<9} {:<9} {:<9} {:<9} {:<{filenamewidth}.{filenamewidth}} {:<{recordidwidth}.{recordidwidth}}".format(  # noqa E501
                    "xmin",
                    "xmax",
                    "ymin",
                    "ymax",
                    "fname",
                    "record_id",
                    filenamewidth=self.filenamewidth,
                    recordidwidth=self.recordidwidth,
                )
            )
            print(
                "".join(
                    ["-"]
                    * (
                        5
                        + self.namewidth
                        + self.xlabelwidth
                        + self.ylabelwidth
                        + 9
                        + 9
                        + 9
                        + 9
                        + self.filenamewidth
                        + self.recordidwidth
                        + 9
                    )
                )
            )  # last digit is number of columns - 1
            for i in range(len(self.curvelist)):
                searchline = self.curvelist[i].name + " " + self.curvelist[i].filename
                if not line or reg.search(searchline):
                    index = str(i + 1)
                    name = self.curvelist[i].name
                    name = name.ljust(self.namewidth)
                    name = pdvutil.truncate(name, self.namewidth)
                    xlabel = self.curvelist[i].xlabel
                    xlabel = xlabel.ljust(self.xlabelwidth)
                    xlabel = pdvutil.truncate(xlabel, self.xlabelwidth)
                    ylabel = self.curvelist[i].ylabel
                    ylabel = ylabel.ljust(self.ylabelwidth)
                    ylabel = pdvutil.truncate(ylabel, self.ylabelwidth)
                    fname = self.curvelist[i].filename
                    fname = fname.ljust(self.filenamewidth)
                    fname = pdvutil.truncate(fname, self.filenamewidth, "right")
                    record_id = self.curvelist[i].record_id
                    record_id = record_id.ljust(self.recordidwidth)
                    record_id = pdvutil.truncate(record_id, self.recordidwidth)
                    xmin = "%.2e" % min(self.curvelist[i].x)
                    xmax = "%.2e" % max(self.curvelist[i].x)
                    ymin = "%.2e" % min(self.curvelist[i].y)
                    ymax = "%.2e" % max(self.curvelist[i].y)
                    print(
                        "{:>5} {} {} {} {:9} {:9} {:9} {:9} {} {}".format(
                            index, name, xlabel, ylabel, xmin, xmax, ymin, ymax, fname, record_id
                        )
                    )
                    j += 1
                if j == self.menulength * menu_j:
                    menu_j += 1
                    stop = input(
                        f"Press Enter to see the next {self.menulength} curves OR n and then enter for no. "
                        "Change menu length with `menulength #` after exiting the menu display screen.\n"
                    )
                    if stop in ["n", "no", "N", "NO"]:
                        break
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def help_regex(self):
        help(re)

    def do_drop(self, line):
        """
        Start the Python Interactive Console.

        .. code::

            [PyDV]: drop

            Ex:
                [PyDV]: drop

        Afterwards:

        .. code:: python

            >>> import matplotlib.pyplot as plt
            >>> plt.ion()
            >>> my_fig = plt.gcf()  # get figure object
            >>> my_axis = plt.gca()  # get axis object
            >>> my_axis.plot([1, 2], [5, 6])
            >>> Ctrl+D  # to go back into pydv

        Back in PyDV:

        .. code::

            [PyDV]: quit  # only if you want to quit pydv

        """
        self.redraw = False
        return True

    def do_quit(self, line):
        """
        Quit PyDV.

        .. code::

            [PyDV]: <quit | q>

            Ex:
                [PyDV]: q
        """

        try:
            readline.write_history_file(os.getenv("HOME") + "/.pdvhistory")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.quit_helper.quit_signal.emit()
            sys.exit(0)

    def do_image(self, line):
        """
        Save the current figure to an image file. All parameters are optional. The default value
        for `filename=plot`, the default value for `filetype=pdf` and the default value for
        `transparent=False`. `dpi` is the resolution in dots per inch and the default value is
        the figure's dpi value. Width and height are in pixels.

        .. code::

            [PyDV]: image [filename=plot] [filetype=pdf: png | ps | pdf | svg] [transparent=False: True | False] [dpi] [width] [height]

            Ex:
                [PyDV]: image my_plot png
                [PyDV]: image my_plot png True
                [PyDV]: image my_plot png True 100
                [PyDV]: image my_plot png True 100 1920 1080
        """  # noqa: E501

        try:
            line = line.split()
            optcnt = len(line)
            filename = "plot"
            filetype = "pdf"
            transparent = False
            dpi = "figure"
            current_width, current_height = plt.gcf().get_size_inches()

            if optcnt >= 1:
                filename = line[0]

            if optcnt >= 2:
                filetype = line[1]

            if optcnt >= 3:
                if line[2].lower() == "true":
                    transparent = True

            if optcnt >= 4:
                dpi = float(line[3])

            if optcnt >= 5:
                width = int(line[4]) * 1 / dpi
                height = int(line[5]) * 1 / dpi
                plt.gcf().set_size_inches(width, height)
            else:
                plt.gcf().set_size_inches(6, 4.41)

            plt.savefig(fname=filename + "." + filetype, dpi=dpi, format=filetype, transparent=transparent)

            plt.gcf().set_size_inches(current_width, current_height)  # reset
        except:
            pdvutil.print_own_docstring(self)

    def do_save(self, line):
        """
        Saves plotted curves to a file in ULTRA format. Can also save x and y labels which can be read back in.

        .. code::

            [PyDV]: save <filename> <curve-list> [savelabels]

            Ex:
                [PyDV]: save my_saved_file.ult a
                [PyDV]: save my_saved_file.ult b d
                [PyDV]: save my_saved_file.ult b:d
                [PyDV]: save my_saved_file.ult b:d savelabels
        """

        if not line:
            return 0
        try:
            line = line.split()
            filename = line.pop(0)
            line = " ".join(line)
            if len(line.split(":")) > 1:
                self.do_save(filename + " " + pdvutil.getletterargs(line))
                return 0
            else:
                f = open(filename, "w")
                save_labels = False
                if "savelabels" in line:
                    save_labels = True
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        if save_labels:
                            f.write("# " + cur.name + " # xlabel " + cur.xlabel + " # ylabel " + cur.ylabel + "\n")
                        else:
                            f.write("# " + cur.name + "\n")
                        for dex in range(len(cur.x)):
                            f.write(" " + str(cur.x[dex]) + " " + str(cur.y[dex]) + "\n")
                    except RuntimeError as rte:
                        print("I/O error: {}".format(rte))
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_savecsv(self, line):
        """
        Saves plotted curves to file in comma separated values (CSV) format. Assumes all curves have the same x basis.

        .. code::

            [PyDV]: savecsv <filename> <curve-list>

            Ex:
                [PyDV]: savecsv my_saved_file.csv b
                [PyDV]: savecsv my_saved_file.csv b d
                [PyDV]: savecsv my_saved_file.csv b:d
        """

        if not line:
            return 0
        try:
            line = line.split()
            filename = line.pop(0)
            line = " ".join(line)
            if len(line.split(":")) > 1:
                self.do_savecsv(filename + " " + pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                cols = []
                names = []
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        cols.append(cur.x.tolist())
                        cols.append(cur.y.tolist())
                        names.append(cur.name + " [x]")
                        names.append(cur.name + " [y]")
                    except RuntimeError as rte:
                        print("I/O error: {}".format(rte))

                with open(filename, "w+") as f:
                    writer = csv.writer(f)
                    writer.writerow(names)
                    for values in zip_longest(*cols):
                        writer.writerow(values)

        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_annot(self, line):
        """
        Display text on the plot at point (x, y). List of annotations can be seen with `listannot`.

        .. code::

            [PyDV]: annot <text> <x> <y>

            Ex:
                [PyDV]: annot mytext 1 2
        """

        if not line:
            return 0
        try:
            argline = line.split()
            xloc = argline[-2]
            yloc = argline[-1]
            argdex = line.find(xloc)
            line = line[:argdex]
            self.usertexts.append([float(xloc), float(yloc), line])
        except:
            pdvutil.print_own_docstring(self)

    def do_listannot(self, line):
        """
        List current annotations.

        .. code::

            [PyDV]: listannot
        """

        try:
            for i in range(len(self.usertexts)):
                dex = str(i + 1).rjust(5)
                xloc = "%.4f" % self.usertexts[i][0]
                xloc.ljust(5)
                yloc = "%.4f" % self.usertexts[i][1]
                yloc.ljust(5)
                annot = self.usertexts[i][2]
                annot = pdvutil.truncate(annot.ljust(50), 50)
                print("%s   %s  %s   %s" % (dex, xloc, yloc, annot))
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_delannot(self, line):
        """
        Delete annotations from list. List of annotations can be seen with `listannot`.

        .. code::

            [PyDV]: delannot <number-list-of-annotations>

            Ex:
                [PyDV]: listannot
                [PyDV]: delannot 1
                [PyDV]: delannot 1:2
                [PyDV]: delannot 3 4
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:  # check for list notation
                self.do_delannot(pdvutil.getnumberargs(line, self.filelist))
                return 0
            else:
                print(line)
                line = line.split()
                rmlist = []
                for i in range(len(line)):
                    rmlist.append(self.usertexts[int(line[i]) - 1])
                for text in rmlist:
                    self.usertexts.remove(text)
        except:
            pdvutil.print_own_docstring(self)

    def do_span(self, line):
        """
        Generates straight line of slope 1 and y intercept 0 in the specified domain with an optional number of points.

        .. code::

            [PyDV]: span <xmin> <xmax> [points]

            Ex:
                [PyDV]: span 1 10
                [PyDV]: span 1 10 200
        """
        if not line:
            return 0
        try:
            line = line.split()
            numpts = 100
            if len(line) == 3:
                numpts = int(line.pop(-1))
            xmin = float(line[0])
            xmax = float(line[1])
            c = pydvpy.span(xmin, xmax, numpts)
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_line(self, line):
        """
        Generate a line with y = mx + b and an optional number of points.

        .. code::

            [PyDV]: line <m> <b> <xmin> <xmax> [# pts]

            Ex:
                [PyDV]: line 3 7 -1 20
                [PyDV]: line 3 7 -1 20 200
        """

        if not line:
            return 0
        try:
            line = line.split()
            numpts = 100
            if len(line) == 5:
                numpts = int(line.pop(-1))
            slope = float(line[0])
            yint = float(line[1])
            xmin = float(line[2])
            xmax = float(line[3])

            c = pydvpy.line(slope, yint, xmin, xmax, numpts)
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_makecurve(self, line):
        """
        Generate a curve from two tuples of numbers.

        .. code::

            [PyDV]: makecurve (<list of x-values>) (<list of y-values>)

            Ex:
                [PyDV]: makecurve (1 2 3) (20 30 40)
        """

        if not line:
            return 0
        try:
            line = line.strip().split(")")
            x = numpy.fromstring(line[0].strip().strip("("), dtype=float, sep=" ")
            y = numpy.fromstring(line[1].strip().strip("("), dtype=float, sep=" ")

            if len(x) != len(y):
                raise RuntimeError("Must have same number of x and y values")

            c = pydvpy.makecurve(x=x, y=y, name="Curve")
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_ymin(self, line):
        """
        Filter out points in curves whose y-values less than limit

        .. code::

            [PyDV]: ymin <curve-list> <limit>

            Ex:
                [PyDV]: ymin a 3
                [PyDV]: ymin a:b 3
                [PyDV]: ymin c d 3
        """

        try:
            self.__mod_curve(line, "ymin")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_ymax(self, line):
        """
        Filter out points in curves whose y-values greater than limit

        .. code::

            [PyDV]: ymax <curve-list> <limit>

            Ex:
                [PyDV]: ymax a 3
                [PyDV]: ymax a:b 3
                [PyDV]: ymax c d 3
        """

        try:
            self.__mod_curve(line, "ymax")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_xmin(self, line):
        """
        Filter out points in curves whose x-values less than limit

        .. code::

            [PyDV]: xmin <curve-list> <limit>

            Ex:
                [PyDV]: xmin a 3
                [PyDV]: xmin a:b 3
                [PyDV]: xmin c d 3
        """

        try:
            self.__mod_curve(line, "xmin")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_xmax(self, line):
        """
        Filter out points in curves whose x-values greater than limit.

        .. code::

            [PyDV]: xmax <curve-list> <limit>

            Ex:
                [PyDV]: xmax a 3
                [PyDV]: xmax a:b 3
                [PyDV]: xmax c d 3
        """

        try:
            self.__mod_curve(line, "xmax")
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_xminmax(self, line):
        """
        Filter out points; this is the only filter points function that returns a new curve
        due to how ULTRA behaved.

        .. code::

            [PyDV]: <xminmax | xmm> <curve-list> <low-lim> <high-lim>

            Ex:
                [PyDV]: xminmax a 1 3
                [PyDV]: xminmax a:b 1 3
                [PyDV]: xminmax c d 1 3
        """

        if len(line.split(":")) > 1:
            self.do_xminmax(pdvutil.getletterargs(line))
            return
        else:
            try:
                line = line.split()
                xmax = line.pop(-1)
                xmin = line.pop(-1)
                curves = []
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                for cur in curves:
                    curve_new = cur.copy()  # new curve
                    curve_new.name = "Extract " + cur.name.upper()  # ULTRA naming
                    curve_new.plotname = self.getcurvename()
                    curve_new.color = ""  # PyDV will pick a color on its own
                    self.addtoplot(curve_new)
                    minline = " ".join(curve_new.plotname) + " " + xmin
                    maxline = " ".join(curve_new.plotname) + " " + xmax
                    self.do_xmin(minline)
                    self.do_xmax(maxline)
                    # don't mark the new curve as having been edited by min and max; user doesn't care how we did it.
                    curve_new.edited = False

                self.plotedit = True

            except:
                pdvutil.print_own_docstring(self)

    def do_yminmax(self, line):
        """
        Trim the selected curves.

        .. code::

            [PyDV]: <yminmax | ymm> <curve-list> <low-limit> <high-lim>

            Ex:
                [PyDV]: yminmax a 3 7
                [PyDV]: yminmax a:b 3 7
                [PyDV]: yminmax c d 3 7
        """

        if len(line.split(":")) > 1:
            self.do_yminmax(pdvutil.getletterargs(line))
            return
        else:
            try:
                line = line.split()
                ymax = line.pop(-1)
                ymin = line.pop(-1)
                good_lines = []
                for i in range(len(line)):
                    try:
                        pdvutil.getCurveIndex(line[i], self.plotlist)
                        good_lines.append(line[i])
                    except pdvutil.CurveIndexError:
                        pass

                for curve_letter in good_lines:
                    minline = " ".join(curve_letter) + " " + ymin
                    maxline = " ".join(curve_letter) + " " + ymax
                    self.do_ymin(minline)
                    self.do_ymax(maxline)

                self.plotedit = True

            except:
                pdvutil.print_own_docstring(self)

    def do_filter(self, line):
        """
        Filter out points in the x and y axis.

        .. code::

            [PyDV]: filter <curve-list> <x-low-lim> <x-high-lim> <y-low-lim> <y-high-lim>

            Ex:
                [PyDV]: filter a 1 2 3 4
                [PyDV]: filter a:b -3 0 -5 10
                [PyDV]: filter c d 0 13 -7 15
        """

        if len(line.split(":")) > 1:
            self.do_filter(pdvutil.getletterargs(line))
            return
        else:
            try:
                line = line.split()
                ymax = line.pop(-1)
                ymin = line.pop(-1)
                xmax = line.pop(-1)
                xmin = line.pop(-1)
                good_lines = []
                for i in range(len(line)):
                    try:
                        pdvutil.getCurveIndex(line[i], self.plotlist)
                        good_lines.append(line[i])
                    except pdvutil.CurveIndexError:
                        pass

                for curve_letter in good_lines:
                    x_minline = " ".join(curve_letter) + " " + xmin
                    x_maxline = " ".join(curve_letter) + " " + xmax
                    y_minline = " ".join(curve_letter) + " " + ymin
                    y_maxline = " ".join(curve_letter) + " " + ymax

                    self.do_xmin(x_minline)
                    self.do_xmax(x_maxline)
                    self.do_ymin(y_minline)
                    self.do_ymax(y_maxline)

                self.plotedit = True
            except:
                pdvutil.print_own_docstring(self)

    def do_derivative(self, line):
        """
        Take the derivative of curves.

        .. code::

            [PyDV]: <derivative | der> <curve-list>

            Ex:
                [PyDV]: derivative a
                [PyDV]: derivative a:b
                [PyDV]: derivative c d
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_derivative(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    cur = self.plotlist[idx]
                    nc = self.derivative(cur)
                    self.addtoplot(nc)

                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_integrate(self, line):
        """
        Compute the definite integral of each curve in the list over the specified domain.

        .. code::

            [PyDV]: <integrate | int> <curve-list> [low-limit high-limit]

            Ex:
                [PyDV]: integrate a
                [PyDV]: integrate a:b
                [PyDV]: integrate c d
                [PyDV]: integrate c d 3 7
        """

        if not line:
            return 0
        try:
            if len(line.split(":")) > 1:
                self.do_integrate(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                xlow = None
                xhi = None
                subtrahend = 0

                try:
                    xhi = float(line[-1])
                    subtrahend = -1
                except:
                    xhi = None

                try:
                    xlow = float(line[-2])
                    subtrahend = -2
                except:
                    xlow = None

                if (xlow is None and xhi is not None) or (xlow is not None and xhi is None):
                    raise RuntimeError("<low-limit> and <high-limit> must BOTH be specified")

                stop = len(line) + subtrahend
                for i in range(stop):
                    for j in range(len(self.plotlist)):
                        cur = self.plotlist[j]
                        if cur.plotname == line[i].upper():
                            nc = pydvpy.integrate(cur, xlow, xhi)[0]
                            self.addtoplot(nc)
                            break

                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_vs(self, line):
        """
        Plot the range of the first curve against the range of the second curve.

        .. code::

            [PyDV]: vs <curve1> <curve2>

            Ex:
                [PyDV]: vs a b
        """

        if not line:
            return 0
        try:
            line = line.split()
            if len(line) != 2:
                return 0

            stuff = "0123456789"
            fidx1 = stuff.find(line[0])
            fidx2 = stuff.find(line[1])

            if fidx1 >= 0 and fidx2 >= 0:
                self.__vs_variant(line[0], line[1])
                return

            idx = pdvutil.getCurveIndex(line[0], self.plotlist)
            c1 = self.plotlist[idx]

            idx = pdvutil.getCurveIndex(line[1], self.plotlist)
            c2 = self.plotlist[idx]

            nc = pydvpy.vs(c1, c2)

            self.addtoplot(nc)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def __vs_variant(self, arg0, arg1):
        """
        This variant support directly plotting curve numbers against each other
        """

        def _extract_curvelist_number(arg):
            if ord(arg[0].upper()) >= ord("A") and ord(arg[0].upper()) <= ord("Z"):  # Look for a.% type stuff
                ifile_target = ord(arg[0].upper()) - ord("A")
                icurve = 0
                ifile = 0
                lastfile = self.curvelist[0].filename
                while icurve < len(self.curvelist) and ifile < ifile_target:
                    icurve += 1
                    if self.curvelist[icurve].filename != lastfile:
                        ifile += 1
                        lastfile = self.curvelist[icurve].filename
                if icurve == len(self.curvelist):
                    print("error: curve index out of bounds: ", arg)
                    return 0
                icurve += int(arg.split(".")[-1]) - 1
                return icurve
            elif int(arg) > 0 and int(arg) <= len(self.curvelist):
                return int(arg) - 1
            else:
                print("error: curve index out of bounds: ", arg)

        icur1, icur2 = _extract_curvelist_number(arg0), _extract_curvelist_number(arg1)
        xc1, yc1 = numpy.array(self.curvelist[icur1].x), numpy.array(self.curvelist[icur1].y)
        xc2, yc2 = numpy.array(self.curvelist[icur2].x), numpy.array(self.curvelist[icur2].y)
        newfilename = ""
        newrecord_id = ""
        if self.curvelist[icur2].filename == self.curvelist[icur1].filename:
            newfilename = self.curvelist[icur2].filename
            if self.curvelist[icur2].record_id == self.curvelist[icur1].record_id:
                newrecord_id = self.curvelist[icur2].record_id
        nc = pydvpy.makecurve(
            x=yc2,
            y=numpy.interp(xc2, xc1, yc1),
            name="%s vs %s" % (arg0, arg1),
            filename=newfilename,
            record_id=newrecord_id,
            xlabel=self.curvelist[icur2].ylabel,
            ylabel=self.curvelist[icur1].ylabel,
        )
        self.addtoplot(nc)
        self.plotedit = True
        return

    def do_errorbar(self, line):
        """
        Plot error bars on the given curve.

        .. code::

            [PyDV]: errorbar <curve> <y-error-curve> <y+error-curve> [x-error-curve x+error-curve] [point-skip]

            Ex:
                [PyDV]: errorbar a 2 3
                [PyDV]: errorbar a 2 3 4 5
                [PyDV]: errorbar a 2 3 4 5 2
        """

        if not line:
            return 0
        line = line.split()

        try:
            idx = pdvutil.getCurveIndex(line[0], self.plotlist)
            scur = self.plotlist[idx]

            # y-error-curve, y+error-curve
            idx = pdvutil.getCurveIndex(line[1], self.plotlist)
            cury1 = self.plotlist[idx]

            idx = pdvutil.getCurveIndex(line[2], self.plotlist)
            cury2 = self.plotlist[idx]

            # x-error-curve, x+error-curve
            curx1 = None
            curx2 = None
            if len(line) >= 5:
                idx = pdvutil.getCurveIndex(line[3], self.plotlist)
                curx1 = self.plotlist[idx]

                idx = pdvutil.getCurveIndex(line[4], self.plotlist)
                curx2 = self.plotlist[idx]

            # point-skip
            mod = 1
            if len(line) == 6:
                mod = line[5]
            elif len(line) == 4:
                mod = line[3]

            pydvpy.errorbar(scur, cury1, cury2, curx1, curx2, mod)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_errorrange(self, line):
        """
        Plot shaded error region on given curve. Note: y-error-curve and y+error-curve are
        curves and not scalars

        .. code::

            [PyDV]: errorrange <curve> <y-error-curve> <y+error-curve>

            Ex:
                [PyDV]: errorrannge a b c
        """

        if not line:
            return 0
        try:
            idx = pdvutil.getCurveIndex(line.split()[0], self.plotlist)
            scur = self.plotlist[idx]

            self.do_errorbar(line)
            scur.erange = [scur.ebar[0], scur.ebar[1]]
            scur.ebar = None
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_marker(self, line):
        """
        Set the marker symbol and marker size (optionally) for scatter plots. You can also use any of the matplotlib
        supported marker types as well. See the matplotlib documentation on markers for further information.

        .. code::

            [PyDV]: marker <curve-list> <marker-style: + | . | circle | square | diamond> [marker-size]

            Ex:
                [PyDV]: marker a +
                [PyDV]: marker a:b .
                [PyDV]: marker c d circle
                [PyDV]: marker c d 10
        """
        self.do_linemarker(line)

    def do_linemarker(self, line):
        """
        Set the marker symbol and marker size for the curves

        .. note::
            When setting this value through the interface or the curve object directly,
            use ONLY matplotlib supported marker types. Matplotlib marker types are also
            supported here as well. See matplotlib documentation on markers for further
            information.

        .. code::

            [PyDV]: linemarker <curve-list> <marker-style: + | . | circle | square | diamond> [<marker-size>]

            Ex:
                [PyDV]: linemarker a +
                [PyDV]: linemarker a:b .
                [PyDV]: linemarker c d circle
                [PyDV]: linemarker c d square 5
        """

        if not line:
            return 0
        try:
            markersize = None

            if len(line.split(":")) > 1:
                self.do_linemarker(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                ultra_markers = {"circle": "o", "square": "s", "diamond": "d"}

                try:
                    markersize = float(line[-1])
                    marker = line[-2]
                except:
                    markersize = None
                    marker = line[-1]
                if marker in ultra_markers:
                    marker = ultra_markers[marker]

                for i in range(len(line)):
                    for j in range(len(self.plotlist)):
                        cur = self.plotlist[j]
                        if cur.plotname == line[i].upper():
                            cur.markerstyle = marker
                            if markersize:
                                cur.markersize = markersize
                            break
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_mathinterpparams(self, line):
        """
        Set `numpy.interp()` `left`, `right`, and `period` parameters for internal curve math methods for Curve such
        as `+ a b c`, `- a b c`, etc.... Defaults are `None` which align with `numpy.interp()` defaults. To reset pass
        in none to <left> <right> <period>.

        .. code::

            [PyDV]: mathinterpparams <curve-list> <left> <right> <period>

            Ex:
                [PyDV]: mathinterpparams a 0 0 none
                [PyDV]: mathinterpparams a:b 0 0 none
                [PyDV]: mathinterpparams c d none none none
        """

        if not line:
            return 0
        try:
            left = None
            right = None
            period = None

            if len(line.split(":")) > 1:
                self.do_mathinterpparams(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                left = line[-3]
                right = line[-2]
                period = line[-1]
                if left.lower() == "none":
                    left = None
                else:
                    left = float(left)
                if right.lower() == "none":
                    right = None
                else:
                    right = float(right)
                if period.lower() == "none":
                    period = None
                else:
                    period = float(period)

                for i in range(len(line)):
                    for j in range(len(self.plotlist)):
                        cur = self.plotlist[j]
                        if cur.plotname == line[i].upper():
                            cur.math_interp_left = left
                            cur.math_interp_right = right
                            cur.math_interp_period = period
                            break
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_smooth(self, line):
        """
        Smooth the curve to the given degree.

        .. code::

            [PyDV]: smooth <curve-list> [smooth-factor]

            Ex:
                [PyDV]: sin a
                [PyDV]: sin a:b
                [PyDV]: sin c d
                [PyDV]: sin c d 4
        """

        if not line:
            return 0
        try:
            line = line.split()

            try:
                factor = int(line[-1])
                line.pop(-1)
            except:
                factor = 1

            line = " ".join(line)

            if len(line.split(":")) > 1:
                self.do_smooth(pdvutil.getletterargs(line) + str(factor))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        pydvpy.smooth(cur, factor)
                        cur.edited = True
                    except pdvutil.CurveIndexError:
                        pass

            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_fft(self, line):
        """
        Compute the one-dimensional discrete Fourier Transform for the curves.

        .. code::

            [PyDV]: fft <curve-list>

            Ex:
                [PyDV]: fft a
                [PyDV]: fft a:b
                [PyDV]: fft c d
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_fft(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()
                for item in line:
                    idx = pdvutil.getCurveIndex(item, self.plotlist)
                    c1 = self.plotlist[idx]
                    nc1, nc2 = pydvpy.fft(c1, norm="ortho")
                    self.addtoplot(nc1)
                    self.addtoplot(nc2)

                self.plotedit = True
            except:
                pdvutil.print_own_docstring(self)

    def do_appendcurves(self, line):
        """
        Merge a list of curves over the union of their domains.
        Where the domains overlap, take the average of the curves' y-values.

        .. code::

            [PyDV]: appendcurves <curve-list>

            Ex:
                [PyDV]: appendcurves a:b
                [PyDV]: appendcurves c d
        """

        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.do_appendcurves(pdvutil.getletterargs(line))
            return 0
        else:
            try:
                line = line.split()

                if len(line) < 2:
                    return

                curves = list()
                for i in range(len(self.plotlist)):
                    for j in range(len(line)):
                        if self.plotlist[i].plotname == line[j].upper():
                            curves.append(self.plotlist[i])
                            break

                nc = pydvpy.appendcurves(curves)

                if nc is not None:
                    self.addtoplot(nc)
                    self.plotedit = True
            except:
                pdvutil.print_own_docstring(self)

    def do_alpha(self, line):
        """
        Find the alpha.

        .. code::

            [PyDV]: alpha <calculated-a> <calculated-i> <response> [# points]
        """

        if not line:
            return 0

        try:
            line = line.split()
            linelen = len(line)
            if linelen == 3 or linelen == 4:
                for i in range(len(self.plotlist)):
                    if self.plotlist[i].plotname == line[0].upper():
                        c1 = self.plotlist[i]
                        break
                for i in range(len(self.plotlist)):
                    if self.plotlist[i].plotname == line[1].upper():
                        c2 = self.plotlist[i]
                        break
                for i in range(len(self.plotlist)):
                    if self.plotlist[i].plotname == line[2].upper():
                        c3 = self.plotlist[i]
                        break

                if linelen == 4:
                    npts = int(line[3])
                    nc = pydvpy.alpha(c1, c2, c3, npts)
                else:
                    nc = pydvpy.alpha(c1, c2, c3)

                self.addtoplot(nc)
                self.plotedit = True
            else:
                raise RuntimeError("Wrong number of arguments, expecting 3 or 4 but received %d." % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_convolve(self, line):
        """
        Computes the convolution of the two given curves.

        **THIS IS DEPRECIATED**

        * Use `convolc` for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))
        * Use `convolb` for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))
        """
        print(f"convol {line}")
        print("Use `convolc` for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))")
        print("Use `convolb` for (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))")

    def do_convolveb(self, line):
        """
        Computes the convolution of the two given curves and normalizes by the area under the second curve.

        (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))

        .. code::

            [PyDV]: convolveb <curve1> <curve2> [points] [points_interp]

            Ex:
                [PyDV]: convolveb g h
                [PyDV]: convolveb g h 200
                [PyDV]: convolveb g h 200 200
        """

        if not line:
            return 0
        try:
            line = line.split()
            for i in range(len(self.plotlist)):
                if self.plotlist[i].plotname == line[0].upper():
                    c1 = self.plotlist[i]
                    break
            for i in range(len(self.plotlist)):
                if self.plotlist[i].plotname == line[1].upper():
                    c2 = self.plotlist[i]
                    break

            if len(line) == 2:
                nc = pydvpy.convolveb(c1, c2, debug=self.debug)
            elif len(line) == 3:
                npts = int(line[2])
                nc = pydvpy.convolveb(c1, c2, npts, debug=self.debug)
            elif len(line) == 4:
                npts = int(line[2])
                npts_interp = int(line[3])
                nc = pydvpy.convolveb(c1, c2, npts, npts_interp, debug=self.debug)
            else:
                raise RuntimeError("Wrong number of arguments, expecting 2 or 3 but received %d." % len(line))

            self.addtoplot(nc)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_convolvec(self, line):
        """
        Computes the convolution of the two given curves with no normalization.

        (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))

        .. code::

            [PyDV]: convolvec <curve1> <curve2> [points] [points_interp]

            Ex:
                [PyDV]: convolvec g h
                [PyDV]: convolvec g h 200
                [PyDV]: convolvec g h 200 200
        """

        if not line:
            return 0
        try:
            line = line.split()
            for i in range(len(self.plotlist)):
                if self.plotlist[i].plotname == line[0].upper():
                    c1 = self.plotlist[i]
                    break
            for i in range(len(self.plotlist)):
                if self.plotlist[i].plotname == line[1].upper():
                    c2 = self.plotlist[i]
                    break

            if len(line) == 2:
                nc = pydvpy.convolvec(c1, c2, debug=self.debug)
            elif len(line) == 3:
                npts = int(line[2])
                nc = pydvpy.convolvec(c1, c2, npts, debug=self.debug)
            elif len(line) == 4:
                npts = int(line[2])
                npts_interp = int(line[3])
                nc = pydvpy.convolvec(c1, c2, npts, npts_interp, debug=self.debug)
            else:
                raise RuntimeError("Wrong number of arguments, expecting 2 or 3 but received %d." % len(line))

            self.addtoplot(nc)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_diffMeasure(self, line):
        """
        Compare two curves. For the given curves a fractional difference measure and its average is computed

        .. code::

            [PyDV]: diffMeasure <curve1> <curve2> [tolerance]

            Ex:
                [PyDV]: diffMeasure a b
                [PyDV]: diffMeasure a b 0.1
        """

        if not line:
            return 0
        try:
            try:
                tolerance = float(line.split()[-1])
                line = line.split()
                line.pop(-1)
                line = " ".join(line)
            except:
                tolerance = 1e-8

            line = line.split()
            idx = pdvutil.getCurveIndex(line[0], self.plotlist)
            c1 = self.plotlist[idx]

            idx = pdvutil.getCurveIndex(line[1], self.plotlist)
            c2 = self.plotlist[idx]

            cdiff, cint = pydvpy.diffMeasure(c1, c2, tolerance)
            self.addtoplot(cdiff)
            self.addtoplot(cint)
            self.plotedit = True
            print("Difference measure for curves " + c1.plotname + " and " + c2.plotname + ": " + str(cint.y[-1]))
        except:
            pdvutil.print_own_docstring(self)

    def do_correl(self, line):
        """
        Computes the cross-correlation of two curves.

        .. code::

            [PyDV]: correl <curve1> <curve2>

            Ex:
                [PyDV]: correl a b
        """

        if not line:
            return 0

        try:
            line = line.split()

            if len(line) != 2:
                raise RuntimeError("Wrong number of arguments, expecting 2 but received %d." % len(line))

            idx = pdvutil.getCurveIndex(line[0], self.plotlist)
            c1 = self.plotlist[idx]

            idx = pdvutil.getCurveIndex(line[1], self.plotlist)
            c2 = self.plotlist[idx]

            nc = pydvpy.correlate(c1, c2, "same")
            self.addtoplot(nc)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_theta(self, line):
        """
        Generate a unit step distribution.

        .. code::

            [PyDV]: theta <xmin> <x0> <xmax> [# points]

            Ex:
                [PyDV]: theta -5 0 5
                [PyDV]: theta -3 3 5 200
        """

        try:
            line = line.split()
            xmin = float(line[0])
            x0 = float(line[1])
            xmax = float(line[2])
            if len(line) == 4:
                numpts = float(line[3])
            else:
                numpts = 100

            c = pydvpy.theta(xmin, x0, xmax, numpts)
            self.addtoplot(c)
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_normalize(self, line):
        """
        Normalize a curve.

        .. code::

            [PyDV]: normalize <curve>

            Ex:
                [PyDV]: normalize a
        """

        try:
            idx = pdvutil.getCurveIndex(line, self.plotlist)
            c1 = self.plotlist[idx]
            c = pydvpy.normalize(c1)
            self.addtoplot(c)
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_hypot(self, line):
        """
        Calculate harmonic average of two curves, sqrt(a^2+b^2).

        .. code::

            [PyDV]: hypot <curve1> <curve2>

            Ex:
                [PyDV]: hypot a b
        """

        try:
            line = line.split()
            idx = pdvutil.getCurveIndex(line[0], self.plotlist)
            c1 = self.plotlist[idx]
            idx = pdvutil.getCurveIndex(line[1], self.plotlist)
            c2 = self.plotlist[idx]
            c = pydvpy.hypot(c1, c2)
            self.addtoplot(c)
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_delta(self, line):
        """
        Procedure: Generate a Dirac delta distribution such that `Int(xmin, xmax, dt*delta(t - x0)) = 1`.

        .. code::

            [PyDV]: delta <xmin> <x0> <xmax> [<# points>]

            Ex:
                [PyDV]: delta -5 0 5
                [PyDV]: delta -3 3 5 200
        """

        try:
            line = line.split()
            xmn = float(line[0])
            x0 = float(line[1])
            xmx = float(line[2])
            if len(line) > 3:
                npts = float(line[3])
            else:
                npts = 100
            c = pydvpy.delta(xmn, x0, xmx, npts)
            self.addtoplot(c)
            self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    def do_bkgcolor(self, line):
        """
        Change the background color of the plot, window, or both.

        .. code::

            [PyDV]: bkgcolor <[plot | window] color | reset>

            Ex:
                [PyDV]: bkgcolor plot blue
                [PyDV]: bkgcolor window blue
                [PyDV]: bkgcolor reset
        """

        try:
            line = line.split()
            color = line[-1]

            if color.lower() == "reset":
                color = None
                component = "reset"
            else:
                if not mclr.is_color_like(color):
                    print("error: invalid color " + color)
                    self.redraw = False
                    return 0

                if len(line) > 1:
                    component = line[0].lower()
                    if component != "plot" and component != "window" and component != "reset":
                        raise ValueError("'%s' is an invalid component name" % component)
                else:
                    component = "all"

            if component == "reset":
                self.figcolor = self.plotter.figcolor
                self.plotcolor = "#dddddd"
            else:
                if component == "all" or component == "window":
                    self.figcolor = color

                if component == "all" or component == "plot":
                    self.plotcolor = color

            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_fontcolor(self, line):
        """
        Change the font color of given plot component.

        .. code::

            [PyDV]: fontcolor [<component: xlabel | ylabel | title | xaxis | yaxis>] <color>

            Ex:
                [PyDV]: fontcolor xlabel blue
                [PyDV]: fontcolor ylabel blue
                [PyDV]: fontcolor title blue
                [PyDV]: fontcolor xaxis blue
                [PyDV]: fontcolor yaxis blue
        """

        try:
            line = line.split()
            color = line[-1]
            if not mclr.is_color_like(color):
                print("error: invalid color " + color)
                self.redraw = False
                return 0

            if len(line) > 1:
                com = line[0]
                if (
                    com != "xlabel"
                    and com != "ylabel"
                    and com != "xaxis"
                    and com != "yaxis"
                    and com != "title"
                    and com != "legend"
                ):
                    raise ValueError("'%s' is an invalid component name" % com)
            else:
                com = "all"

            if com == "all" or com == "xlabel":
                self.xlabelcolor = color

            if com == "all" or com == "ylabel":
                self.ylabelcolor = color

            if com == "all" or com == "xaxis":
                self.xtickcolor = color

            if com == "all" or com == "yaxis":
                self.ytickcolor = color

            if com == "all" or com == "title":
                self.titlecolor = color

            if com == "all" or com == "legend":
                self.keycolor = color

            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_fontsize(self, line):
        """
        Change the font size of given component, or overall scaling factor.

        .. code::

            [PyDV]: fontsize [<component: title | xlabel | ylabel | key | tick | curve | annotation>] <numerical-size | small | medium | large | default>

            Ex:
                [PyDV]: fontsize title 12
                [PyDV]: fontsize xlabel small
                [PyDV]: fontsize ylabel medium
                [PyDV]: fontsize key large
                [PyDV]: fontsize tick default
                [PyDV]: fontsize curve 12
                [PyDV]: fontsize annotation small
        """  # noqa: E501

        try:
            line = line.split()
            size = line[-1]
            if (
                size != "default"
                and size != "de"
                and size != "x-small"
                and size != "small"
                and size != "medium"
                and size != "large"
                and size != "x-large"
            ):
                size = float(size)
                if size > 40:
                    size = 40
            if len(line) > 1:
                com = line[0]
            else:
                com = "all"
            if com == "all" or com == "title":
                if size == "default" or size == "de":
                    self.titlefont = "large"
                else:
                    self.titlefont = size
            if com == "all" or com == "xlabel":
                if size == "default" or size == "de":
                    self.xlabelfont = "medium"
                else:
                    self.xlabelfont = size
            if com == "all" or com == "ylabel":
                if size == "default" or size == "de":
                    self.ylabelfont = "medium"
                else:
                    self.ylabelfont = size
            if com == "all" or com == "legend":
                if size == "default" or size == "de":
                    self.keyfont = "small"
                else:
                    self.keyfont = size
            if com == "all" or com == "tick":
                if size == "default" or size == "de":
                    self.axistickfont = "medium"
                else:
                    self.axistickfont = size
            if com == "all" or com == "curve":
                if size == "default" or size == "de":
                    self.curvelabelfont = "medium"
                else:
                    self.curvelabelfont = size
            if com == "all" or com == "annotation":
                if size == "default" or size == "de":
                    self.annotationfont = "medium"
                else:
                    self.annotationfont = size
        except:
            pdvutil.print_own_docstring(self)

    def do_gaussian(self, line):
        """
        Generate a gaussian function.

        .. code::

            [PyDV]: gaussian <amplitude> <width> <center> [<# points> [<# half-widths>]]

            Ex:
                [PyDV]: gaussian 5 2 0
                [PyDV]: gaussian 5 2 0 100
                [PyDV]: gaussian 5 2 0 100 2
        """

        if not line:
            return 0
        try:
            num = 100  # num of points
            nsd = 3  # num of half-widths

            line = line.split()

            if len(line) < 3:
                raise RuntimeError("Wrong number of arguments")

            if len(line) == 4:
                num = int(line[-1])
            elif len(line) == 5:
                nsd = float(line[-1])
                num = int(line[-2])

            amp = float(line[0])
            wid = float(line[1])
            center = float(line[2])

            c = pydvpy.gaussian(amp, wid, center, num, nsd)
            self.addtoplot(c)
            self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_geometry(self, line):
        """
        Change the PyDV window size and location in pixels.

        .. code::

            [PyDV]: geometry <xsize> <ysize> <xlocation> <ylocation>

            Ex:
                [PyDV]: geometry 500 500 250 250
        """

        try:
            line = line.split()
            if len(line) != 4:
                raise RuntimeError("Wrong number of arguments, expecting 4 but received %d." % len(line))

            self.geometry = int(line[0]), int(line[1]), int(line[2]), int(line[3])
            self.plotter.updatePlotGeometry(self.geometry)
        except:
            self.redraw = False
            pdvutil.print_own_docstring(self)

    def do_plotlayout(self, line):
        """
        Adjust the plot layout parameters. Where `left` is the position of the left edge of the
        plot as a fraction of the figure width, `right` is the position of the right edge of the
        plot, as a fraction of the figure width, `top` is the position of the top edge of the plot,
        as a fraction of the figure height and `bottom` is the position of the bottom edge of the plot,
        as a fraction of the figure height. Alternatively, `de` will revert to the default plot layout values.

        If no arguments are given, the plot's current layout settings will be displayed.

        .. code::

            [PyDV]: plotlayout [<left> <right> <top> <bottom> || de]

            Ex:
                [PyDV]: plotlayout left
                [PyDV]: plotlayout right
                [PyDV]: plotlayout top
                [PyDV]: plotlayout bottom
                [PyDV]: plotlayout de
        """

        try:
            line = line.split()
            paramcnt = len(line)

            if paramcnt == 4:
                plt.subplots_adjust(
                    left=float(line[0]), bottom=float(line[3]), right=float(line[1]), top=float(line[2])
                )
            elif paramcnt == 1 and line[0].lower() == "de":
                defaultPlotLayout = self.plotter.defaultPlotLayout

                if defaultPlotLayout is not None:
                    plt.subplots_adjust(
                        left=defaultPlotLayout["left"],
                        bottom=defaultPlotLayout["bottom"],
                        right=defaultPlotLayout["right"],
                        top=defaultPlotLayout["top"],
                        wspace=defaultPlotLayout["wspace"],
                        hspace=defaultPlotLayout["hspace"],
                    )
            elif paramcnt == 0:
                paramlist = list()
                paramlist.append("left: {}".format(self.plotter.fig.subplotpars.left))
                paramlist.append("right: {}".format(self.plotter.fig.subplotpars.right))
                paramlist.append("top: {}".format(self.plotter.fig.subplotpars.top))
                paramlist.append("bottom: {}".format(self.plotter.fig.subplotpars.bottom))
                print("\n")
                self.print_topics("Plot Layout (Borders):", paramlist, 15, 40)
            else:
                raise ValueError("Unknown argument(s)")
        except:
            self.redraw = False
            pdvutil.print_own_docstring(self)

    def do_reid(self, line):
        """
        Relabel all the curves into continuous alphabetical order.

        .. code::

            [PyDV]: reid
        """

        try:
            for i in range(len(self.plotlist)):
                c = self.plotlist[i]  # get i'th curve object
                if i < 26:
                    c.plotname = chr(ord("A") + i)  # label by alphabet
                else:
                    c.plotname = "@" + str(i + 1)  # after first 26 curves, go to @N labels
        except:
            pdvutil.print_own_docstring(self)

    def do_label(self, line):
        """
        Change the key and list label for a curve. For multiple curves, each label must start with ` (this is the
        backtick character ` , not the single quote character ').

        .. code::

            [PyDV]: label <curve> <new-label>

            Ex:
                [PyDV]: label a my_new_label
                [PyDV]: label a:b `my_new_label `my other label
                [PyDV]: label a:c `mynewlabel `my other label `my thirdlabel
        """

        try:
            if len(line.split(":")) > 1 and not self.do_label_done:
                self.do_label_done = True
                if "`" in line:
                    self.do_label(pdvutil.getletterargs(line))
                else:  # extra logic specifically for single label w/ :
                    self.do_label(pdvutil.getletterargs("PYDV_LABEL" + line))
                return 0
            else:
                self.do_label_done = False
                line_labels = line.split("`")[1:]  # First entry will be curves

                if line_labels:  # Multiple curves and labels
                    curves = line.split("`")[0].split()
                else:  # single curve and label
                    curves = [line.split()[0]]
                    line_labels = [" ".join(line.split()[1:])]

                for i in range(len(curves)):
                    idx = pdvutil.getCurveIndex(curves[i], self.plotlist)
                    cur = self.plotlist[idx]
                    cur.name = line_labels[i]

                self.plotedit = True
        except:
            self.do_label_done = False
            pdvutil.print_own_docstring(self)

    def do_labelrecordids(self, line):
        """
        Add curve recordid to the legend label. Command will only work with curves from Sina files with valid
        record ids.

        .. code::

            [PyDV]: labelrecordids <on | off>

            Ex:
                [PyDV]: labelrecordids on
                [PyDV]: labelrecordids off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showrecordidinlegend = False
            elif line == "1" or line.upper() == "ON":
                self.showrecordidinlegend = True
            else:
                raise RuntimeError("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_labelfilenames(self, line):
        """
        Add curve filename to the legend label.

        .. code::

            [PyDV]: labelfilenames <on | off>

            Ex:
                [PyDV]: labelfilenames on
                [PyDV]: labelfilenames off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showfilenameinlegend = False
            elif line == "1" or line.upper() == "ON":
                self.showfilenameinlegend = True
            else:
                raise RuntimeError("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_labelcurve(self, line):
        """
        Add curve letter to the legend label.

        .. code::

            [PyDV]: labelcurve <on | off>

            Ex:
                [PyDV]: labelcurve on
                [PyDV]: labelcurve off
        """

        try:
            line = line.strip()
            if line == "0" or line.upper() == "OFF":
                self.showcurveinlegend = False
            elif line == "1" or line.upper() == "ON":
                self.showcurveinlegend = True
            else:
                raise RuntimeError("invalid input: requires on or off as argument")
        except:
            pdvutil.print_own_docstring(self)

    def do_run(self, line):
        """
        Execute a list of commands from a file.

        .. code::

            [PyDV]: run <filename>

            Ex:
                [PyDV]: run my_file
        """

        try:
            fname = line.strip()
            if fname[0] == "~":
                fname = os.getenv("HOME") + fname[1:]
            f = open(fname, "r")
            for fline in f:
                try:
                    if len(fline.strip()) == 0:
                        continue  # skip blank lines
                    if fline.strip()[0] == "#":
                        continue  # skip comment lines
                    fline = self.precmd(fline.strip())
                    args = fline.split()
                    cmd = args.pop(0)
                    if cmd == "image":
                        self.updateplot
                    args = " ".join(args)
                    send = "self.do_" + cmd + "('" + args.replace("\\", "\\\\") + "')"
                    result = eval(send)  # noqa: F841
                except SystemExit:
                    self.do_quit(line)
                except:
                    print("invalid command: " + fline.strip())
                    if self.debug:
                        traceback.print_exc(file=sys.stdout)
            self.plotedit = True
            self.updateplot
        except SystemExit:
            self.do_quit(line)
        except:
            pdvutil.print_own_docstring(self)

    def do_movefront(self, line):
        """
        Move given curves to the front of the plot

        .. code::

            [PyDV]: movefront <curve-list>

            Ex:
                [PyDV]: movefront a
                [PyDV]: movefront a:b
                [PyDV]: movefront c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_movefront(pdvutil.getletterargs(line))
                return 0
            else:
                highest = 0
                for c in self.plotlist:
                    if c.plotprecedence > highest:
                        highest = c.plotprecedence

                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        cur = self.plotlist[curvidx]
                        cur.plotprecedence = highest + 1
                    except pdvutil.CurveIndexError:
                        pass

                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_custom(self, line):
        """
        Load a Python file of custom functions to extend PyDV. Functions must be of the form
        `def do_commandname(self, line): ...`.

        This custom Python script is imported at the `pdv.py` level and thus you can use the methods within
        `class Command():` by calling `self.do_METHOD_NAME():`. These are the methods used in the [PyDV]
        command line prompt that are detailed in this documentation.

        The `pydvpy.py` module is imported as `pydvpy` which means you can also use the PyDV Python API functions
        by calling `pydvpy.FUNCTION_NAME():`.

        Below are some template functions that are used throughout PyDV. The parameter `line` is the text that is
        passed into the function after the function name in the PyDV Command Line Interface.
        These functions should have `try` statements so that PyDV doesn't crash if there is an error. Be sure to
        pass in the command `debug on` to PyDV to get more information about any errors.

        .. code::

            [PyDV]: custom <file-name>

            Ex:
                [PyDV]: debug on
                [PyDV]: custom my_custom_functions.py
                [PyDV]: mycustomfunction
                [PyDV]: myothercustomfunction
                [PyDV]: createcustomcurve a:b
                [PyDV]: customcurveinfo a:b

        my_custom_functions.py:

        .. code:: python

            import os


            def do_mycustomfunction(self, line):
                '''
                Create new curve and add it to the `self.curvelist()`.
                These are the curves shown with the `menu` command.
                '''

                try:
                    num_curves = int(line)
                    for i in range(num_curves):
                        x = [i, i + 1, i + 2]
                        y = x
                        name = f'TestCurve_{i}'
                        fname = f'TestFilename_{i}'
                        xlabel = f'TestXlabel_{i}'
                        ylabel = f'TestYlabel_{i}'
                        title = f'TestTitle_{i}'
                        record_id = f'TestRecordID_{i}'
                        c = pydvpy.makecurve(x=x,
                                             y=y,
                                             name=name,
                                             filename=fname,
                                             xlabel=xlabel,
                                             ylabel=ylabel,
                                             title=title,
                                             record_id=record_id)
                        self.curvelist.append(c)
                except:
                    pdvutil.print_own_docstring(self)


            def do_myothercustomfunction(self, line):
                '''
                Calling other functions within PyDV.
                '''

                try:
                    files = line.split()

                    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
                    self.do_read(os.path.join(TEST_DIR, '../tests', files[0]))
                    self.do_readsina(os.path.join(TEST_DIR, '../tests', files[1]))
                except:
                    pdvutil.print_own_docstring(self)


            def do_createcustomcurve(self, line):
                '''
                Create new curve and add it to the `self.plotlist()`.
                These are the curves shown with the `list` command.
                '''

                if not line:
                    return 0
                try:
                    if len(line.split(':')) > 1:
                        self.do_createcustomcurve(pdvutil.getletterargs(line))
                        return 0
                    else:
                        line = line.split()

                        for i in line:
                        idx = pdvutil.getCurveIndex(i, self.plotlist)
                        cur = self.plotlist[idx]
                        x = cur.x + 10
                        y = cur.y - 10
                        nc = pydvpy.makecurve(x=x,
                                                y=y,
                                                name=name,
                                                filename=fname,
                                                xlabel=xlabel,
                                                ylabel=ylabel,
                                                title=title,
                                                record_id=record_id)
                        self.addtoplot(nc)

                        self.plotedit = True
                except:
                    pdvutil.print_own_docstring(self)


            def do_customcurveinfo(self, line):
                '''
                Acquire information from the the curves in `self.plotlist()`.
                '''

                try:
                    if len(line.split(':')) > 1:
                        self.do_customcurveinfo(pdvutil.getletterargs(line))
                        return 0
                    else:
                        print('\\nCustom Curve Info:')
                        line = line.split()

                        for i in range(len(line)):
                        try:
                            idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                            cur = self.plotlist[idx]
                            info = numpy.sum(cur.x) + 10
                            print(f'\\nCurve {cur.plotname}: {cur.name}')
                            print(f'\\tInfo: {info:.6e}')
                        except pdvutil.CurveIndexError:
                            pass
                        print('')
                except:
                    pdvutil.print_own_docstring(self)t)
                finally:
                    self.redraw = False

        """

        try:
            fname = line.strip()
            try:
                if fname.startswith("~"):
                    fname = os.path.expanduser(fname)

                with open(fname, "r") as f:
                    funcfile = f.read()

                ns = {
                    "self": self,
                    "pydvpy": pydvpy,
                    "__file__": fname,
                }

                exec(funcfile, ns)

                funcs = re.findall(r"def (do_\w+)\s*\(", funcfile)

                for func_name in funcs:
                    func_obj = ns[func_name]
                    setattr(self, func_name, types.MethodType(func_obj, self))

            except:
                print("error - invalid file: {}".format(fname))
                if self.debug:
                    traceback.print_exc(file=sys.stdout)
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_alias(self, line):
        """
        Define a synonym for an existing command.

        .. code::

            [PyDV]: alias <command> <alias>

            Ex:
                [PyDV]: alias list l
        """

        try:
            cmd = line.split()[0]
            alias = line.split()[1]

            function = "def do_" + alias + "(self, line): self.do_" + cmd + "(line)"
            exec(function)
            exec("self.do_" + alias + " = types.MethodType(do_" + alias + ", self)")
        except:
            pdvutil.print_own_docstring(self)
        finally:
            self.redraw = False

    def do_copy(self, line):
        """
        Copy and plot the given curves.

        .. code::

            [PyDV]: copy <curve-list>

            Ex:
                [PyDV]: copy a
                [PyDV]: copy a:b
                [PyDV]: copy c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_copy(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()
                for i in range(len(line)):
                    plotidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    cur = self.plotlist[plotidx]
                    curout = cur.copy()
                    curout.plotname = ""
                    curout.color = ""
                    self.addtoplot(curout)

                self.plotedit = True
        except:
            pdvutil.print_own_docstring(self)

    def do_makeextensive(self, line):
        """
        Set the y-values such that y[i] = y[i] * (x[i+1] - x[i]).

        .. code::

            [PyDV]: <makeextensive | mkext> <curve-list>

            Ex:
                [PyDV]: makeextensive a
                [PyDV]: makeextensive a:b
                [PyDV]: makeextensive c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_makeextensive(pdvutil.getletterargs(line))
                return 0
            else:
                curves = list()
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                if len(curves) > 0:
                    pydvpy.makeextensive(curves)
                else:
                    raise RuntimeError("Need to specify a valid curve or curves")

        except:
            pdvutil.print_own_docstring(self)

    def do_makeintensive(self, line):
        """
        Set the y-values such that y[i] = y[i] / (x[i+1] - x[i]).

        .. code::

            [PyDV]: <makeintensive | mkint> <curve-list>

            Ex:
                [PyDV]: makeintensive a
                [PyDV]: makeintensive a:b
                [PyDV]: makeintensive c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_makeintensive(pdvutil.getletterargs(line))
                return 0
            else:
                curves = list()
                line = line.split()
                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                if len(curves) > 0:
                    pydvpy.makeintensive(curves)
                else:
                    raise RuntimeError("Need to specify a valid curve or curves")

        except:
            pdvutil.print_own_docstring(self)

    def do_dupx(self, line):
        """
        Duplicate x-values so that y=x for each of the specified curves.

        .. code::

            [PyDV]: dupx <curve-list>

            Ex:
                [PyDV]: dupx a
                [PyDV]: dupx a:b
                [PyDV]: dupx c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_dupx(pdvutil.getletterargs(line))
                return 0
            else:
                curves = list()
                line = line.split()

                for i in range(len(line)):
                    try:
                        plotidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[plotidx])
                    except pdvutil.CurveIndexError:
                        pass

                if len(curves) > 0:
                    pydvpy.dupx(curves)

        except:
            pdvutil.print_own_docstring(self)

    def do_xindex(self, line):
        """
        Create curves with y-values vs. integer index values.

        .. code::

            [PyDV]: xindex <curve-list>

            Ex:
                [PyDV]: xindex a
                [PyDV]: xindex a:b
                [PyDV]: xindex c d
        """

        try:
            if len(line.split(":")) > 1:
                self.do_xindex(pdvutil.getletterargs(line))
                return 0
            else:
                curves = list()
                line = line.split()

                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curves.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                if len(curves) > 0:
                    pydvpy.xindex(curves)
                else:
                    raise RuntimeError("Need to specify a valid curve or curves")

        except:
            pdvutil.print_own_docstring(self)

    def do_ticks(self, line):
        """
        Set the maximum number of major ticks on the axes.

        .. code::

            [PyDV]: ticks <quantity> | de

                Ex:
                    [PyDV]: ticks 3
                    [PyDV]: ticks de
        """

        try:
            if line.strip() == "de":
                self.xticks = "de"
                self.yticks = "de"
            else:
                numticks = int(line)

                if numticks > 50:
                    numticks = 50
                elif numticks < 2:
                    numticks = 2

                self.xticks = numticks
                self.yticks = numticks
        except:
            pdvutil.print_own_docstring(self)

    def do_yticks(self, line):
        """
        Set the locations of major ticks on the y axis.

        .. code::

            [PyDV]: yticks de | <number> | <list of locations> | <list of locations, list of labels>

            Ex:
                [PyDV]: yticks 3
                [PyDV]: yticks (1, 2, 3)
                [PyDV]: yticks (1, 2, 3), ('first label', 'second label', 'third label')
                [PyDV]: yticks de
        """

        try:
            if line.strip() == "de":
                self.yticks = "de"
            elif isinstance(eval(line.strip()), Number):
                self.yticks = eval(line.strip())
            elif isinstance(eval(line.strip()), tuple):
                if isinstance(eval(line.strip())[0], Number):
                    self.yticks = eval(line.strip())
                else:
                    locs, labels = eval(line)
                    self.yticks = (locs, labels)
        except:
            pdvutil.print_own_docstring(self)

    def do_xticks(self, line):
        """
        Set the locations of major ticks on the x-axis

        .. code::

            [PyDV]: xticks de | <number> | <list of locations> | <list of locations, list of labels>

            Ex:
                [PyDV]: xticks 3
                [PyDV]: xticks (1, 2, 3)
                [PyDV]: xticks (1, 2, 3), ('first label', 'second label', 'third label')
                [PyDV]: xticks de
        """

        try:
            if line.strip() == "de":
                self.xticks = "de"
            elif isinstance(eval(line.strip()), Number):
                self.xticks = eval(line.strip())
            elif isinstance(eval(line.strip()), tuple):
                if isinstance(eval(line.strip())[0], Number):
                    self.xticks = eval(line.strip())
                else:
                    locs, labels = eval(line)
                    self.xticks = (locs, labels)
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickcolor(self, line):
        """
        Set the color of the ticks on the x-axis. Default is to apply to major ticks only.

        .. code::

            [PyDV]: xtickcolor <de | color> [which: major | minor | both]

            Ex:
                [PyDV]: xtickcolor blue major
                [PyDV]: xtickcolor blue minor
                [PyDV]: xtickcolor blue both
                [PyDV]: xtickcolor de both
        """

        try:
            line = line.split()

            if len(line) == 1:  # which = 'major'
                if line[0] == "de":
                    self.xmajortickcolor = "black"
                else:
                    self.xmajortickcolor = line[0]
            elif len(line) == 2:  # which = 'major|minor|both'
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.xmajortickcolor = "black"
                    else:
                        self.xmajortickcolor = line[0]
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.xminortickcolor = "black"
                    else:
                        self.xminortickcolor = line[0]
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.xmajortickcolor = "black"
                        self.xminortickcolor = "black"
                    else:
                        self.xmajortickcolor = line[0]
                        self.xminortickcolor = line[0]
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickcolor(self, line):
        """
        Set the color of the ticks on the y-axis. Default is to apply to major ticks only.

        .. code::

            [PyDV]: ytickcolor <de | color> [which: major | minor | both]

            Ex:
                [PyDV]: ytickcolor blue major
                [PyDV]: ytickcolor blue minor
                [PyDV]: ytickcolor blue both
                [PyDV]: ytickcolor de both
        """

        try:
            line = line.split()

            if len(line) == 1:  # which = 'major'
                if line[0] == "de":
                    self.ymajortickcolor = "black"
                else:
                    self.ymajortickcolor = line[0]
            elif len(line) == 2:  # which = 'major|minor|both'
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.ymajortickcolor = "black"
                    else:
                        self.ymajortickcolor = line[0]
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.yminortickcolor = "black"
                    else:
                        self.yminortickcolor = line[0]
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.ymajortickcolor = "black"
                        self.yminortickcolor = "black"
                    else:
                        self.ymajortickcolor = line[0]
                        self.yminortickcolor = line[0]
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_xticklength(self, line):
        """
        Set the length (in points) of x ticks on the axis. Default is apply to major ticks only.

        .. code::

            [PyDV]: xticklength <number> [which: major | minor | both]

            Ex:
                [PyDV]: xticklength 2 major
                [PyDV]: xticklength 2 minor
                [PyDV]: xticklength 2 both
        """

        try:
            line = line.split()

            if len(line) == 1:  # which = 'major'
                if line[0] == "de":
                    self.xticklength = 4
                else:
                    self.xticklength = float(line[0])
            elif len(line) == 2:  # which = 'major|minor|both'
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.xticklength = 4
                    else:
                        self.xticklength = float(line[0])
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.xminorticklength = 2
                    else:
                        self.xminorticklength = float(line[0])
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.xticklength = 4
                        self.xminorticklength = 2
                    else:
                        self.xticklength = float(line[0])
                        self.xminorticklength = float(line[0])
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_yticklength(self, line):
        """
        Set the length (in points) of y ticks on the y axis. Default is to apply to major ticks only.

        .. code::

            [PyDV]: yticklength <number> [which: major | minor | both]

            Ex:
                [PyDV]: yticklength 2 major
                [PyDV]: yticklength 2 minor
                [PyDV]: yticklength 2 both
        """

        try:
            line = line.split()

            if len(line) == 1:
                if line[0] == "de":
                    self.yticklength = 4
                else:
                    self.yticklength = float(line[0])
            elif len(line) == 2:
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.yticklength = 4
                    else:
                        self.yticklength = float(line[0])
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.yminorticklength = 2
                    else:
                        self.yminorticklength = float(line[0])
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.yticklength = 4
                        self.yminorticklength = 2
                    else:
                        self.yticklength = float(line[0])
                        self.yminorticklength = float(line[0])
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickwidth(self, line):
        """
        Set the width (in points) of x ticks on the x axis. Default is to apply to major ticks only.

        .. code::

            [PyDV]: xtickwidth <number> [which: major | minor | both]

            Ex:
                [PyDV]: xtickwidth 2 major
                [PyDV]: xtickwidth 2 minor
                [PyDV]: xtickwidth 2 both
        """

        try:
            line = line.split()

            if len(line) == 1:
                if line[0] == "de":
                    self.xtickwidth = 1
                else:
                    self.xtickwidth = float(line[0])
            elif len(line) == 2:
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.xtickwidth = 1
                    else:
                        self.xtickwidth = float(line[0])
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.xminortickwidth = 0.5
                    else:
                        self.xminortickwidth = float(line[0])
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.xtickwidth = 1
                        self.xminortickwidth = 0.5
                    else:
                        self.xtickwidth = float(line[0])
                        self.xminortickwidth = float(line[0])
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickwidth(self, line):
        """
        Set the width (in points) of y ticks on the y axis. Default is to apply to major ticks only.

        .. code::

            [PyDV]: ytickwidth <number> [which: major | minor | both]

            Ex:
                [PyDV]: ytickwidth 2 major
                [PyDV]: ytickwidth 2 minor
                [PyDV]: ytickwidth 2 both
        """

        try:
            line = line.split()

            if len(line) == 1:
                if line[0] == "de":
                    self.ytickwidth = 1
                else:
                    self.ytickwidth = float(line[0])
            elif len(line) == 2:
                if line[1].upper() == "MAJOR":
                    if line[0] == "de":
                        self.ytickwidth = 1
                    else:
                        self.ytickwidth = float(line[0])
                elif line[1].upper() == "MINOR":
                    if line[0] == "de":
                        self.yminortickwidth = 0.5
                    else:
                        self.yminortickwidth = float(line[0])
                elif line[1].upper() == "BOTH":
                    if line[0] == "de":
                        self.ytickwidth = 1
                        self.yminortickwidth = 0.5
                    else:
                        self.ytickwidth = float(line[0])
                        self.yminortickwidth = float(line[0])
                else:
                    raise ValueError("Unknown type of axis: %s" % line[1])
            else:
                raise RuntimeError("Too many arguments, expecting 1 or 2 but received %d" % len(line))
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickformat(self, line):
        """
        Set the format of major ticks on the y axis. Default is plain.

        .. code::

            [PyDV]: ytickformat <plain | sci | exp | 10**>

            Ex:
                [PyDV]: ytickformat plain
                [PyDV]: ytickformat sci
                [PyDV]: ytickformat exp
                [PyDV]: ytickformat 10**
        """

        try:
            if line.strip() == "plain":
                self.ytickformat = "de"
            else:
                self.ytickformat = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickformat(self, line):
        """
        Set the format of major ticks on the x axis. Default is plain.

        .. code::

            [PyDV]: xtickformat <plain | sci | exp | 10**>

            Ex:
                [PyDV]: xtickformat plain
                [PyDV]: xtickformat sci
                [PyDV]: xtickformat exp
                [PyDV]: xtickformat 10**
        """

        try:
            if line.strip() == "plain":
                self.xtickformat = "de"
            else:
                self.xtickformat = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickrotation(self, line):
        """
        Set the rotation (in degrees) of the tick labels on the x axis.

        .. code::

            [PyDV]: xtickrotation <degree>

            Ex:
                [PyDV]: xtickrotation 45
        """

        try:
            self.xtickrotation = float(line.strip())
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickha(self, line):
        """
        Set the horizontal alignment of tick labels on the x axis. Default is center.

        .. code::

            [PyDV]: xtickha <center | right | left>

            Ex:
                [PyDV]: xtickha right
        """

        try:
            self.xtickha = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_xtickva(self, line):
        """
        Set the vertical alignment of tick labels on the x axis. Default is top.

        .. code::

            [PyDV]: xtickva <center | top | bottom>

            Ex:
                [PyDV]: xtickva center
        """

        try:
            self.xtickva = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickha(self, line):
        """
        Set the horizontal alignment of tick labels on the y axis. Default is right.

        .. code::

            [PyDV]: ytickha <center | right | left>

            Ex:
                [PyDV]: ytickha center
        """

        try:
            self.ytickha = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickva(self, line):
        """
        Set the vertical alignment of tick labels on the y axis. Default is center.

        .. code::

            [PyDV]: ytickva <center | top | bottom>

            Ex:
                [PyDV]: ytickva top
        """

        try:
            self.ytickva = line.strip()
        except:
            pdvutil.print_own_docstring(self)

    def do_ytickrotation(self, line):
        """
        Set the rotation (in degrees) of the tick labels on the y axis.

        .. code::

            [PyDV]: ytickrotation <degree>

            Ex:
                [PyDV]: ytickrotation 45
        """

        try:
            self.ytickrotation = float(line.strip())
        except:
            pdvutil.print_own_docstring(self)

    def do_fontstyle(self, line):
        """
        Set the fontstyle family.

        .. code::

            [PyDV]: fontstyle <serif | sans-serif | monospace>

            Ex:
                [PyDV]: fontstyle serif
                [PyDV]: fontstyle sans-serif
                [PyDV]: fontstyle monospace
        """

        try:
            matplotlib.rc("font", family=line.strip())
        except:
            pdvutil.print_own_docstring(self)

    def do_subsample(self, line):
        """
        Subsample the curves by the optional stride. Default value for stride is 2.

        .. code::

            [PyDV]: subsample <curve-list> [stride]

            Ex:
                [PyDV]: subsample a 3
                [PyDV]: subsample a:b 3
                [PyDV]: subsample c d 3
        """

        try:
            if not line:
                return 0
            if len(line.split(":")) > 1:
                self.do_subsample(pdvutil.getletterargs(line))
                return 0
            else:
                line = line.split()

                try:
                    stride = int(line[-1])
                    line.pop(-1)
                except:
                    stride = 2
                curvelist = list()

                for i in range(len(line)):
                    try:
                        curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                        curvelist.append(self.plotlist[curvidx])
                    except pdvutil.CurveIndexError:
                        pass

                if len(curvelist) > 0:
                    print("\nSubsampling the data by stride %i...\n" % stride)
                    pydvpy.subsample(curvelist, stride, True)

                self.plotedit = True

        except:
            pdvutil.print_own_docstring(self)

    ########################################################################################################
    # helper functions #
    ########################################################################################################

    def find_xrange(self):
        """
        Find the proper x-range
        """

        orderlist = sorted(self.plotlist, key=lambda x: x.plotprecedence)
        xmin, xmax = 1e300, -1e300
        for cur in orderlist:
            if not cur.hidden:
                xmin = min(xmin, min(cur.x))
                xmax = max(xmax, max(cur.x))
        if self.xlogscale:
            xmin = 1e-2
            for cur in orderlist:
                if not cur.hidden:
                    xdat = numpy.where(cur.x < 1e-300, 1e301, cur.x)
                    localmin = min(xdat)
                    if localmin and localmin < xmin:
                        xmin = localmin
            if xmax < xmin:
                xmax = xmin * 10000
        return xmin, xmax

    def find_yrange(self):
        """
        Find the proper y-range
        """

        orderlist = sorted(self.plotlist, key=lambda x: x.plotprecedence)
        ymin, ymax = 1e300, -1e300
        for cur in orderlist:
            if not cur.hidden:
                ymin = min(ymin, min(cur.y))
                ymax = max(ymax, max(cur.y))
        if self.ylogscale:
            ymin = 1e-2
            for cur in orderlist:
                if not cur.hidden:
                    localmin = min(numpy.ma.masked_where(numpy.ma.array(cur.y) < 1e-300, numpy.ma.array(cur.y)))
                    if localmin and localmin < ymin:
                        ymin = localmin
            if ymax < ymin:
                ymax = ymin * 10000
            ymin *= 0.95
            ymax *= 1.05
        else:
            bump = 0.05 * (ymax - ymin)
            ymin -= bump
            ymax += bump
        return ymin, ymax

    def curvefromlabel(self, label):
        """
        Get curve from its label/plot name
        """

        label = label.upper()
        for c in self.plotlist:
            if c.plotname == label:
                return c

        raise ValueError('label "%s" not found in the plot list' % label)

    def addtoplot(self, cur):
        """
        Ensure curve is valid and add it to the plotlist
        """

        if cur.plotname == "" or (len(cur.plotname) > 1 and cur.plotname[0] != "@"):
            cur.plotname = self.getcurvename()

        cur.x = numpy.array(cur.x)
        cur.y = numpy.array(cur.y)
        if len(cur.x) < 1 or len(cur.y) < 1:
            raise ValueError("curve must have one or more points")
            return
        if len(cur.x) != len(cur.y):
            raise ValueError("curve must have same number of x and y values")
            return
        if cur.plotname[:1] != "@" and ord(cur.plotname) >= ord("A") and ord(cur.plotname) <= ord("Z"):
            self.plotlist.insert((ord(cur.plotname) - ord("A")), cur)
        else:
            self.plotlist.insert(int(cur.plotname[1:]) - 1, cur)

        self.reset_xticks_labels()
        self.set_xlabel(cur.xlabel, from_curve=True)
        self.set_ylabel(cur.ylabel, from_curve=True)
        self.set_title(cur.title, from_curve=True)
        self.set_filename(cur.filename, from_curve=True)
        self.set_record_id(cur.record_id, from_curve=True)

    def reset_xticks_labels(self):
        """
        Reset xtick labels whenever there is a new curve added/hidden/deleted
        """

        # Create an overall dictionary for all the xtick labels
        reset = True
        for i, labeled_curve in enumerate(self.plotlist):
            if labeled_curve.xticks_labels and not labeled_curve.hidden:
                # Clear if previous dict exists
                if self.xtick_labels and reset:
                    self.xtick_labels = {}
                    reset = False
                for key, val in labeled_curve.xticks_labels.items():
                    self.xtick_labels[key] = val

        # Update overall dictionary with increasing integers
        if self.xtick_labels:
            for i, (key, val) in enumerate(self.xtick_labels.items()):
                self.xtick_labels[key] = i

        # Update each individual curve x tick label dictionary with overall dictionary values
        x_labels = []
        for i, labeled_curve in enumerate(self.plotlist):
            if labeled_curve.xticks_labels and not labeled_curve.hidden:
                x_labels = []

                for xval in labeled_curve.x:
                    for key, val in labeled_curve.xticks_labels.items():
                        if xval == val:
                            x_labels.append(key)
                            break

                # Convert x values to new values from overall dictionary
                x_new = [self.xtick_labels[label] for label in x_labels]
                y_new = labeled_curve.y
                (
                    x_labels,
                    x_new,
                    y_new,
                ) = zip(*sorted(zip(x_labels, x_new, y_new)))

                labeled_curve.x = numpy.array(x_new)
                labeled_curve.y = numpy.array(y_new)
                labeled_curve.xticks_labels = {label: self.xtick_labels[label] for label in list(x_labels)}
                labeled_curve.scatter = True

        # X tick label string for labeled data
        if x_labels:
            str1 = "("
            str2 = "("
            for key, val in self.xtick_labels.items():
                str1 += f"{val}, "
                str2 += f"'{key}', "
            str1 = str1[:-2]
            str1 += ")"
            str2 = str2[:-2]
            str2 += ")"
            xticks_str = str1 + ", " + str2

            self.do_xticks(xticks_str)

            if self.xtickrotation == 0:
                self.xtickrotation = 90

        # Leave custom xticks if there is no labeled data
        elif not self.xtick_labels:
            self.do_xticks(str(self.xticks))

        # Reset x tick labels if there is no labeled data
        else:
            self.xticks = "de"
            self.xtick_labels = {}

    def derivative(self, cur):
        """
        Return derivative of curve
        """

        nc = pydvpy.derivative(cur)
        nc.plotname = self.getcurvename()
        return nc

    def getcurvename(self):
        """
        Find the next available curve name for the plot
        """

        name = ""
        for i in range(len(self.plotlist)):
            if i < 26:
                if self.plotlist[i].plotname != chr(ord("A") + i):
                    return "" + chr(ord("A") + i)
            else:
                if self.plotlist[i].plotname != ("@" + str(i + 1)):
                    name = "@" + str(i + 1)
                    return name
        if len(self.plotlist) < 26:
            return "" + chr(ord("A") + len(self.plotlist))
        else:
            name = "@" + str(len(self.plotlist) + 1)
            return name

    def getclosest(self, array, value):
        """
        Find closest value in numpy array
        """

        i = (numpy.abs(array - value)).argmin()
        return i

    def modcurve(self, line, flag, arg):
        """
        Operate on given curves by constant value depending on given operation flag
        """

        if not line:
            return 0
        modvalue = arg
        if len(line.split(":")) > 1:
            self.modcurve(pdvutil.getletterargs(line), flag, arg)
            return 0
        else:
            line = line.split()
            for i in range(len(line)):
                try:
                    curidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    cur = self.plotlist[curidx]

                    if flag == "my":
                        cur.y *= float(modvalue)
                        cur.edited = True
                    elif flag == "mx":
                        cur.x *= float(modvalue)
                        cur.edited = True
                    elif flag == "divy":
                        if float(modvalue) == 0:
                            modvalue = "1e-10"
                        cur.y /= float(modvalue)
                        cur.edited = True
                    elif flag == "divx":
                        if float(modvalue) == 0:
                            modvalue = "1e-10"
                        cur.x /= float(modvalue)
                        cur.edited = True
                    elif flag == "dy":
                        cur.y += float(modvalue)
                        cur.edited = True
                    elif flag == "dx":
                        cur.x += float(modvalue)
                        cur.edited = True
                    elif flag == "scatter":
                        if modvalue == "0" or modvalue.upper() == "OFF":
                            cur.scatter = False
                        elif modvalue == "1" or modvalue.upper() == "ON":
                            cur.scatter = True
                    elif flag == "linespoints":
                        if modvalue == "0" or modvalue.upper() == "OFF":
                            cur.linespoints = False
                        elif modvalue == "1" or modvalue.upper() == "ON":
                            cur.linespoints = True
                    elif flag == "lnwidth":
                        cur.linewidth = float(modvalue)
                    elif flag == "lnstyle":
                        if modvalue == "solid":
                            cur.linestyle = "-"
                        elif modvalue == "dot":
                            cur.linestyle = ":"
                        elif modvalue == "dash":
                            cur.linestyle = "--"
                        elif modvalue == "dashdot":
                            cur.linestyle = "-."
                        elif modvalue == "loosely_dotted":
                            cur.linestyle = (0, (1, 10))
                        elif modvalue == "long_dash_with_offset":
                            cur.linestyle = (5, (10, 3))
                        elif modvalue == "loosely_dashed":
                            cur.linestyle = (0, (5, 10))
                        elif modvalue == "dashed":
                            cur.linestyle = (0, (5, 5))
                        elif modvalue == "loosely_dashdotted":
                            cur.linestyle = (0, (3, 10, 1, 10))
                        elif modvalue == "dashdotted":
                            cur.linestyle = (0, (3, 5, 1, 5))
                        elif modvalue == "densely_dashdotted":
                            cur.linestyle = (0, (3, 1, 1, 1))
                        elif modvalue == "dashdotdotted":
                            cur.linestyle = (0, (3, 5, 1, 5, 1, 5))
                        elif modvalue == "loosely_dashdotdotted":
                            cur.linestyle = (0, (3, 10, 1, 10, 1, 10))
                        elif modvalue == "densely_dashdotdotted":
                            cur.linestyle = (0, (3, 1, 1, 1, 1, 1))
                        cur.dashes = None  # Restore default dash behaviour
                    elif flag == "drawstyle":
                        # default, steps, steps-pre, steps-post
                        cur.drawstyle = modvalue
                    elif flag == "dashstyle":
                        if modvalue[:2].upper() == "DE":
                            cur.dashes = None
                        else:
                            val = eval(modvalue)
                            assert isinstance(val, list)
                            assert len(val) % 2 == 0
                            assert min(val) > 0
                            cur.dashes = val
                    elif flag == "hide":
                        if modvalue == "OFF":
                            cur.hidden = False
                        elif modvalue == "ON":
                            cur.hidden = True
                    elif flag == "getx":
                        try:
                            getxvalues = pydvpy.getx(cur, float(modvalue))

                            if getxvalues:
                                print("\nCurve " + cur.plotname)

                                for i in range(len(getxvalues)):
                                    x, y = getxvalues[i]
                                    print("    x: %.6e    y: %.6e\n" % (x, y))
                        except ValueError as detail:
                            print("Error: %s" % detail)

                    elif flag == "gety":
                        try:
                            getyvalues = pydvpy.gety(cur, float(modvalue))

                            if getyvalues:
                                print("\nCurve " + cur.plotname)

                                for i in range(len(getyvalues)):
                                    x, y = getyvalues[i]
                                    print("    x: %.6e    y: %.6e" % (x, y))
                        except ValueError as detail:
                            print("Error: %s" % detail)
                    elif flag == "xmin":
                        nx = []
                        ny = []
                        for dex in range(len(cur.x)):
                            if cur.x[dex] >= float(modvalue):
                                nx.append(cur.x[dex])
                                ny.append(cur.y[dex])
                        if len(nx) > 0:
                            cur.x = numpy.array(nx)
                            cur.y = numpy.array(ny)
                            cur.edited = True
                            if len(nx) == 1:
                                cur.marker = "o"
                                cur.markersize = 3
                        else:
                            j = pdvutil.getCurveIndex(cur.plotname, self.plotlist)
                            cur.plotname = ""
                            self.plotlist.pop(j)
                    elif flag == "xmax":
                        nx = []
                        ny = []
                        for dex in range(len(cur.x)):
                            if cur.x[dex] <= float(modvalue):
                                nx.append(cur.x[dex])
                                ny.append(cur.y[dex])
                        if len(nx) > 0:
                            cur.x = numpy.array(nx)
                            cur.y = numpy.array(ny)
                            cur.edited = True
                            if len(nx) == 1:
                                cur.marker = "o"
                                cur.markersize = 3
                        else:
                            j = pdvutil.getCurveIndex(cur.plotname, self.plotlist)
                            cur.plotname = ""
                            self.plotlist.pop(j)
                    elif flag == "ymin":
                        nx = []
                        ny = []
                        for dex in range(len(cur.y)):
                            if cur.y[dex] >= float(modvalue):
                                nx.append(cur.x[dex])
                                ny.append(cur.y[dex])
                        if len(nx) > 0:
                            cur.x = numpy.array(nx)
                            cur.y = numpy.array(ny)
                            cur.edited = True
                            if len(nx) == 1:
                                cur.marker = "o"
                                cur.markersize = 3
                        else:
                            j = pdvutil.getCurveIndex(cur.plotname, self.plotlist)
                            cur.plotname = ""
                            self.plotlist.pop(j)
                    elif flag == "ymax":
                        nx = []
                        ny = []
                        for dex in range(len(cur.y)):
                            if cur.y[dex] <= float(modvalue):
                                nx.append(cur.x[dex])
                                ny.append(cur.y[dex])
                        if len(nx) > 0:
                            cur.x = numpy.array(nx)
                            cur.y = numpy.array(ny)
                            cur.edited = True
                            if len(nx) == 1:
                                cur.marker = "o"
                                cur.markersize = 3
                        else:
                            j = pdvutil.getCurveIndex(cur.plotname, self.plotlist)
                            cur.plotname = ""
                            self.plotlist.pop(j)
                except:
                    if self.debug:
                        traceback.print_exc(file=sys.stdout)

    def func_curve(self, line, flag, do_x=0, arg=0):
        """
        Operate on given curves by a function
        """

        if not line:
            return 0
        if len(line.split(":")) > 1:
            self.func_curve(pdvutil.getletterargs(line), flag, do_x, arg)
            return 0
        else:
            line = line.split()
            for i in range(len(line)):
                try:
                    idx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    cur = self.plotlist[idx]

                    if flag == "abs":
                        if do_x == 0:
                            cur.y = numpy.abs(cur.y)
                            cur.name = "abs(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.abs(cur.x)
                            cur.name = "absx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "exp":
                        if do_x == 0:
                            cur.y = numpy.exp(cur.y)
                            if cur.name[:3] == "log":
                                # Pop off the log( from the front and the ) from the back
                                cur.name = cur.name[4:-1]
                            else:
                                cur.name = "exp(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.exp(cur.x)
                            if cur.name[:4] == "logx":
                                # Pop off the logx( from the front and the ) from the back
                                cur.name = cur.name[5:-1]
                            else:
                                cur.name = "expx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "sin":
                        if do_x == 0:
                            cur.y = numpy.sin(cur.y)
                            cur.name = "sin(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.sin(cur.x)
                            cur.name = "sinx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "cos":
                        if do_x == 0:
                            cur.y = numpy.cos(cur.y)
                            cur.name = "cos(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.cos(cur.x)
                            cur.name = "cosx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "tan":
                        if do_x == 0:
                            cur.y = numpy.tan(cur.y)
                            cur.name = "tan(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.tan(cur.x)
                            cur.name = "tanx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "asin":
                        if do_x == 0:
                            cur.y = numpy.arcsin(cur.y)
                            cur.name = "asin(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arcsin(cur.x)
                            cur.name = "asinx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "acos":
                        if do_x == 0:
                            cur.y = numpy.arccos(cur.y)
                            cur.name = "acos(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arccos(cur.x)
                            cur.name = "acosx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "atan":
                        if do_x == 0:
                            cur.y = numpy.arctan(cur.y)
                            cur.name = "atan(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arctan(cur.x)
                            cur.name = "atanx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "sinh":
                        if do_x == 0:
                            cur.y = numpy.sinh(cur.y)
                            cur.name = "sinh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.sinh(cur.x)
                            cur.name = "sinhx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "cosh":
                        if do_x == 0:
                            cur.y = numpy.cosh(cur.y)
                            cur.name = "cosh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.cosh(cur.x)
                            cur.name = "coshx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "tanh":
                        if do_x == 0:
                            cur.y = numpy.tanh(cur.y)
                            cur.name = "tanh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.tanh(cur.x)
                            cur.name = "tanhx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "asinh":
                        if do_x == 0:
                            cur.y = numpy.arcsinh(cur.y)
                            cur.name = "asinh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arcsinh(cur.x)
                            cur.name = "asinhx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "acosh":
                        if do_x == 0:
                            cur.y = numpy.arccosh(cur.y)
                            cur.name = "acosh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arccosh(cur.x)
                            cur.name = "acoshx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "atanh":
                        if do_x == 0:
                            cur.y = numpy.arctanh(cur.y)
                            cur.name = "atanh(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.arctanh(cur.x)
                            cur.name = "atanhx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "j0":
                        if do_x == 0:
                            cur.y = scipy.special.j0(cur.y)
                            cur.name = "j0(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.j0(cur.x)
                            cur.name = "j0x(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "j1":
                        if do_x == 0:
                            cur.y = scipy.special.j1(cur.y)
                            cur.name = "j1(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.j1(cur.x)
                            cur.name = "j1x(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "jn":
                        if do_x == 0:
                            cur.y = scipy.special.jn(float(arg), cur.y)
                            cur.name = "jn(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.jn(float(arg), cur.x)
                            cur.name = "jnx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "y0":
                        if do_x == 0:
                            cur.y = scipy.special.y0(cur.y)
                            cur.name = "y0(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.y0(cur.x)
                            cur.name = "y0x(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "y1":
                        if do_x == 0:
                            cur.y = scipy.special.y1(cur.y)
                            cur.name = "y1(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.y1(cur.x)
                            cur.name = "y1x(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "yn":
                        if do_x == 0:
                            cur.y = scipy.special.yn(int(arg), cur.y)
                            cur.name = "yn(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = scipy.special.yn(int(arg), cur.x)
                            cur.name = "ynx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "powa":
                        if do_x == 0:
                            cur.y = numpy.power(float(arg), cur.y)
                            cur.name = "powa(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.power(float(arg), cur.x)
                            cur.name = "powax(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "powr":
                        if do_x == 0:
                            cur.y = numpy.power(cur.y, float(arg))
                            cur.name = "powr(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.power(cur.x, float(arg))
                            cur.name = "powrx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "recip":
                        if do_x == 0:
                            cur.y = numpy.reciprocal(cur.y)
                            cur.name = "recip(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.reciprocal(cur.x)
                            cur.name = "recipx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "sqr":
                        if do_x == 0:
                            cur.y = numpy.square(cur.y)
                            cur.name = "sqr(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.square(cur.x)
                            cur.name = "sqrx(" + cur.name + ")"
                            cur.edited = True
                    elif flag == "sqrt":
                        if do_x == 0:
                            cur.y = numpy.sqrt(cur.y)
                            cur.name = "sqrt(" + cur.name + ")"
                            cur.edited = True
                        else:
                            cur.x = numpy.sqrt(cur.x)
                            cur.name = "sqrtx(" + cur.name + ")"
                            cur.edited = True
                except:
                    if self.debug:
                        traceback.print_exc(file=sys.stdout)

    def apply_uichanges(self):
        """
        Applies the changes made by the user from the GUI.
        """

        # this attribute value never gets updated... apply_uichanges() never gets called
        self.plotter.plotChanged = False
        cur_axes = plt.gca()  # Get current axes

        # Save Logscale
        if cur_axes.get_xscale() == "linear":
            self.xlogscale = False
        else:
            self.xlogscale = True

        if cur_axes.get_yscale() == "linear":
            self.ylogscale = False
        else:
            self.ylogscale = True

        # Save plot title
        self.title = cur_axes.get_title()

        # Save x and y limits
        if self.guilims:
            self.xlim = cur_axes.get_xlim()
            self.ylim = cur_axes.get_ylim()

        # Save x and y labels
        self.xlabel = cur_axes.get_xlabel()
        self.ylabel = cur_axes.get_ylabel()

        # Update Curves
        orderlist = sorted(self.plotlist, key=lambda x: x.plotprecedence)
        plotcurvelist = cur_axes.get_lines()

        for i in range(len(plotcurvelist)):
            if not orderlist[i].hidden:
                c = orderlist[i]
                c.name = plotcurvelist[i].get_label()
                c.linestyle = plotcurvelist[i].get_linestyle()
                c.drawstyle = plotcurvelist[i].get_drawstyle()
                c.linewidth = plotcurvelist[i].get_linewidth()
                c.color = plotcurvelist[i].get_color()
                # Marker properties
                c.markerstyle = plotcurvelist[i].get_marker()
                c.markersize = plotcurvelist[i].get_markersize()
                c.markerfacecolor = plotcurvelist[i].get_markerfacecolor()
                c.markeredgecolor = plotcurvelist[i].get_markeredgecolor()

    @property
    def updateplot(self):
        """
        Iterates through plotlist and displays curves on graph
        """
        if self.group == 1:
            self.do_group("")

        try:
            if stylesLoaded:
                if self.updatestyle:
                    styles = pydvpy.get_styles()

                    try:
                        idx = styles.index(self.plotter.style)
                        style.use(styles[idx])
                    except:
                        if len(styles) > 0:
                            print(
                                "\nStyle Error: %s doesn't exist, defaulting to %s\n" % (self.plotter.style, styles[0])
                            )
                            self.plotter.style = styles[0]
                            style.use(styles[0])
                        else:
                            print("\nStyle Error: no styles available\n")

                    self.updatestyle = False

            plt.clf()
            # cur_axes = self.plotter.current_axes
            cur_axes = plt.gca()
            cur_axes.cla()

            # Border
            cur_axes.spines["bottom"].set_color(self.bordercolor)
            cur_axes.spines["top"].set_color(self.bordercolor)
            # cur_axes.spines['bottom'].set_smart_bounds(True)
            # cur_axes.spines['top'].set_smart_bounds(True)
            cur_axes.spines["right"].set_color(self.bordercolor)
            cur_axes.spines["left"].set_color(self.bordercolor)

            if self.plotcolor is not None:
                cur_axes.patch.set_facecolor(self.plotcolor)

            if self.figcolor is not None:
                self.plotter.fig.set_facecolor(self.figcolor)

            # Setup Plot Attributes
            xlabeltext = plt.xlabel(
                self.xlabel, fontsize=self.xlabelfont, weight=self.xlabelweight, style=self.xlabelstyle
            )
            if self.xlabelcolor is not None:
                xlabeltext.set_color(self.xlabelcolor)

            ylabeltext = plt.ylabel(
                self.ylabel, fontsize=self.ylabelfont, weight=self.ylabelweight, style=self.ylabelstyle
            )
            if self.ylabelcolor is not None:
                ylabeltext.set_color(self.ylabelcolor)

            title = plt.title(self.title, fontsize=self.titlefont)
            if self.titlecolor is not None:
                title.set_color(self.titlecolor)

            if self.xtickcolor is not None:
                for label in cur_axes.get_xticklabels():
                    label.set_color(self.xtickcolor)

            if self.ytickcolor is not None:
                for label in cur_axes.get_yticklabels():
                    label.set_color(self.ytickcolor)

            plt.xticks(size=self.axistickfont)
            plt.yticks(size=self.axistickfont)

            for tlabel in cur_axes.get_xticklabels(minor=True):
                plt.setp(tlabel, size=self.axistickfont)
            for tlabel in cur_axes.get_yticklabels(minor=True):
                plt.setp(tlabel, size=self.axistickfont)

            if len(self.plotlist) < 1:
                plt.draw()
                self.plotter.canvas.update()
                self.plotter.canvas.draw()
                return 0

            # Show in legend if enabled
            for cur in self.plotlist:
                # Show curve letter in legend if enabled
                addstr = str("[" + cur.plotname + "]")
                if cur.name.find(addstr) != -1:
                    strarr = cur.name.split(addstr)
                    cur.name = "".join(strarr).strip()
                if self.showcurveinlegend:
                    cur.name = addstr + " " + cur.name

                # only for sina files
                if cur.filename.endswith(".json"):
                    # Show curve recordid in legend if enabled
                    addrstr = str("- " + cur.record_id)
                    if cur.name.find(addrstr) != -1:
                        rstrarr = cur.name.split(addrstr)
                        cur.name = "".join(rstrarr).strip()
                    if self.showrecordidinlegend:
                        cur.name = cur.name + " " + addrstr

                # Show curve filename in legend if enabled
                addfstr = str("- " + cur.filename)
                if cur.name.find(addfstr) != -1 and not self.group:
                    fstrarr = cur.name.split(addfstr)
                    cur.name = "".join(fstrarr).strip()
                if self.showfilenameinlegend:
                    cur.name = cur.name + " " + addfstr

            # set scaling and tick locations
            #
            # Notes on matplotlib that I found very helpful:
            #
            # plt.gca() is "get current axes instance"
            # ScalarFormatter works with linear scales, MaxNLocator
            # LogFormatter is needed to work with LogLocator, produces 1,10,100,...
            # LogFormatterExponent produces 0,1,2,...
            # LogFormatterMathtext produces 10**0,10**1,10**2,...
            xls = self.xlogscale
            yls = self.ylogscale

            if xls:
                cur_axes.set_xscale("log")
            if yls:
                cur_axes.set_yscale("log")

            # thinking about what we want here
            #              xticks de
            #                     or a number
            #                     or a list of locations
            #                     or a tuple of (locations, labels)
            #              xls on or off
            #              xtickformat = 'sci', 'plain', 'exp', '10**'
            if self.showminorticks:
                plt.minorticks_on()
                cur_axes.tick_params(
                    axis="x",
                    which="minor",
                    length=self.xminorticklength,
                    width=self.xminortickwidth,
                    color=self.xminortickcolor,
                )
                cur_axes.tick_params(
                    axis="y",
                    which="minor",
                    length=self.yminorticklength,
                    width=self.yminortickwidth,
                    color=self.yminortickcolor,
                )

            # set x,y tick sizes and tick label format
            cur_axes.tick_params(
                axis="x",
                length=self.xticklength,
                width=self.xtickwidth,
                color=self.xmajortickcolor,
                labelrotation=self.xtickrotation,
            )
            cur_axes.tick_params(
                axis="y",
                length=self.yticklength,
                width=self.ytickwidth,
                color=self.ymajortickcolor,
                labelrotation=self.ytickrotation,
            )
            yaxis = cur_axes.yaxis
            xaxis = cur_axes.xaxis
            self.tickFormat(yaxis, self.ylogscale, self.yticks, self.ytickformat)
            self.tickFormat(xaxis, self.xlogscale, self.xticks, self.xtickformat)
            plt.setp(cur_axes.get_xticklabels(), horizontalalignment=self.xtickha, verticalalignment=self.xtickva)
            plt.setp(cur_axes.get_yticklabels(), horizontalalignment=self.ytickha, verticalalignment=self.ytickva)

            # plot the grid, if grid turned on
            if self.showgrid:
                if plt.xlim is not None and plt.ylim is not None:
                    if (plt.xlim()[0] * 100 > plt.xlim()[1] and xls) or (plt.ylim()[0] * 100 > plt.ylim()[1] and yls):
                        plt.grid(
                            True, which="both", color=self.gridcolor, linestyle=self.gridstyle, linewidth=self.gridwidth
                        )
                    else:
                        plt.grid(True, color=self.gridcolor, linestyle=self.gridstyle, linewidth=self.gridwidth)
                else:
                    plt.grid(True, color=self.gridcolor, linestyle=self.gridstyle, linewidth=self.gridwidth)
            else:
                plt.grid(False)

            # order list in which curves should be plotted
            orderlist = sorted(self.plotlist, key=lambda x: x.plotprecedence)

            # plot the curves
            for cur in orderlist:
                if not cur.hidden:
                    xdat = numpy.array(cur.x)
                    ydat = numpy.array(cur.y)
                    if yls:
                        ydat = numpy.where(ydat < 0, 1e-301, ydat)  # custom ydata clipping
                    if xls:
                        xdat = numpy.where(xdat < 0, 1e-301, xdat)  # custom ydata clipping

                    if cur.ebar is not None:
                        plt.errorbar(
                            xdat, ydat, yerr=[cur.ebar[0], cur.ebar[1]], xerr=[cur.ebar[2], cur.ebar[3]], fmt="-"
                        )
                        c = plt.plot(xdat, ydat)
                    elif cur.erange is not None:
                        c = plt.plot(xdat, ydat)
                        plt.fill_between(
                            xdat, ydat - cur.erange[0], ydat + cur.erange[1], alpha=0.4, color=c[0].get_color()
                        )
                        c = plt.plot(xdat, ydat)
                    else:
                        c = plt.plot(xdat, ydat)

                    if cur.color != "":
                        plt.setp(c, color=cur.color)
                    else:
                        cur.color = c[0].get_color()

                    if cur.linespoints:
                        plt.setp(c, marker=cur.marker, markersize=cur.markersize, linestyle=cur.linestyle)
                    elif cur.scatter:
                        plt.setp(c, marker=cur.marker, markersize=cur.markersize, linestyle=" ")
                    else:
                        if cur.markeredgecolor is None:
                            cur.markeredgecolor = cur.color
                        if cur.markerfacecolor is None:
                            cur.markerfacecolor = cur.color
                        if cur.markerstyle is None:
                            cur.markerstyle = "None"

                        # plt.setp(c, marker=cur.markerstyle, markeredgecolor=cur.markeredgecolor,
                        # markerfacecolor=cur.markerfacecolor, linestyle=cur.linestyle)
                        if self.showplot == "off":
                            linestyle = "None"
                            markerstyle = "None"
                        else:
                            linestyle = cur.linestyle
                            markerstyle = cur.markerstyle
                        plt.setp(
                            c,
                            marker=markerstyle,
                            markersize=cur.markersize,
                            markeredgecolor=cur.markeredgecolor,
                            markerfacecolor=cur.markerfacecolor,
                            linestyle=linestyle,
                        )

                        c[0].set_drawstyle(cur.drawstyle)
                        # Work-around for set_drawstyle bug (https://github.com/matplotlib/matplotlib/issues/10338)
                        c[0]._invalidx = True

                    if cur.linewidth:
                        plt.setp(c, lw=cur.linewidth)
                        plt.setp(c, mew=cur.linewidth)
                    elif self.linewidth:
                        plt.setp(c, lw=self.linewidth)
                        plt.setp(c, mew=self.linewidth)

                    if cur.legend_show:
                        plt.setp(c, label=cur.name)

                    if cur.dashes is not None:
                        c[0].set_dashes(cur.dashes)

            # ensure proper view limits
            # plt.axis('tight')

            if self.xlim is not None:
                plt.xlim(self.xlim[0], self.xlim[1])

            if self.ylim is not None:
                plt.ylim(self.ylim[0], self.ylim[1])

            # plot the curve labels
            if self.showletters and self.showplot == "on":
                # get range and domain of plot
                xmin = plt.axis()[0]
                xmax = plt.axis()[1]
                ymin = plt.axis()[2]
                ymax = plt.axis()[3]
                spacing = (xmax - xmin) / 6
                offset = 0
                for cur in orderlist:
                    if not cur.hidden:
                        plt.text(cur.x[0], cur.y[0], cur.plotname, color=cur.color, fontsize=self.curvelabelfont)
                        curxmax = max(cur.x)
                        curxmin = min(cur.x)
                        if self.xlim is not None:
                            if self.xlim[1] < curxmax:
                                curxmax = self.xlim[1]
                            if self.xlim[0] > curxmin:
                                curxmin = self.xlim[0]
                        spacing = (curxmax - curxmin) / 6
                        labelx = curxmin + offset * spacing / len(self.plotlist)
                        while labelx < curxmax:  # print letter labels along curves
                            close = self.getclosest(cur.x, labelx)
                            if cur.y[close] <= ymax and cur.y[close] >= ymin:
                                plt.text(
                                    cur.x[close],
                                    cur.y[close],
                                    cur.plotname,
                                    color=cur.color,
                                    fontsize=self.curvelabelfont,
                                )
                            labelx += spacing
                        plt.text(cur.x[-1], cur.y[-1], cur.plotname, color=cur.color, fontsize=self.curvelabelfont)
                        offset += 1

            # fonts/labels/legend
            if self.showkey:
                leg = plt.legend(
                    fancybox=True, numpoints=1, loc=self.key_loc, ncol=self.key_ncol, handlelength=self.handlelength
                )
                if leg is not None:
                    leg.get_frame().set_alpha(0.9)
                    leg.set_draggable(state=True)
                    ltext = leg.get_texts()
                    plt.setp(ltext, fontsize=self.keyfont)
                    plt.setp(ltext, color=self.keycolor)

            for text in self.usertexts:
                plt.text(text[0], text[1], text[2], fontsize=self.annotationfont)

            if self.showaxis == "off":
                plt.axis("off")
            else:
                plt.axis("on")

            if self.tightlayout:
                plt.tight_layout()
            else:
                bbox = matplotlib.transforms.Bbox(numpy.array([[0.125, 0.11], [0.9, 0.88]]))
                cur_axes.set_position(bbox)

            plt.draw()
            self.plotter.canvas.update()
            self.plotter.canvas.draw()

        except RuntimeError as detail:
            if detail[-1].split()[0] == "LaTeX":
                print("error: invalid LaTeX syntax")
            else:
                print("error: draw may not have completed properly: %s" % detail)
            if self.debug:
                traceback.print_exc(file=sys.stdout)
        except OverflowError:
            print('Caught overflow error attempting to plot.  Try using "subsample" to reduce the data.')
        except:
            print("error: draw may not have completed properly")
            if self.debug:
                traceback.print_exc(file=sys.stdout)
        finally:
            self.plotter.updateDialogs()

    def load(self, fname, gnu=False, pattern=None, matches=None):
        """
        Load an ultra file and add parsed curves to the curvelist
        """

        curves = pydvpy.read(fname, gnu, self.xCol, self.debug, pattern, matches)
        if len(curves) > 0:
            self.curvelist += curves
            self.filelist.append((fname, len(curves)))

    def load_csv(self, fname, col):
        """
        Load a csv (commas separated values) text data file, add parsed curves to the curvelist
        """
        curves = pydvpy.readcsv(fname, col, self.debug)
        if len(curves) > 0:
            self.curvelist += curves
            self.filelist.append((fname, len(curves)))

    def load_sina(self, fname):
        """
        Load a Sina JSON data file, add parsed curves to the curvelist
        """

        curves = pydvpy.readsina(fname, self.debug)
        if len(curves) > 0:
            self.curvelist += curves
            self.filelist.append((fname, len(curves)))

    def load_sinahdf5(self, fname):
        """
        Load a Sina HDF5 data file, add parsed curves to the curvelist
        """

        curves = pydvpy.readsinahdf5(fname, self.debug)
        if len(curves) > 0:
            self.curvelist += curves
            self.filelist.append((fname, len(curves)))

    def loadrc(self):
        """
        Read in a resource definition file
        """

        try:
            f = open(os.getenv("HOME") + "/.pdvrc", "r")

            for line in f:
                try:
                    line = line.split("=")
                    var = line[0].strip().lower()
                    val = line[1].strip()
                    if var == "xlabel":
                        self.xlabel = val
                    elif var == "ylabel":
                        self.ylabel = val
                    elif var == "title":
                        self.title = val
                    elif var == "menulength":
                        self.menulength = int(val)
                    elif var == "namewidth":
                        self.namewidth = int(val)
                    elif var == "xlabelwidth":
                        self.xlabelwidth = int(val)
                    elif var == "ylabelwidth":
                        self.ylabelwidth = int(val)
                    elif var == "filenamewidth":
                        self.filenamewidth = int(val)
                    elif var == "recordidwidth":
                        self.recordidwidth = int(val)
                    elif var == "key":
                        if val.upper() == "ON" or val == str(1):
                            self.showkey = True
                        else:
                            self.showkey = False
                    elif var == "grid":
                        if val.upper() == "ON" or val == str(1):
                            self.showgrid = True
                        else:
                            self.showgrid = False
                    elif var == "letters":
                        if val.upper() == "ON" or val == str(1):
                            self.showletters = True
                        else:
                            self.showletters = False
                    elif var == "geometry":
                        vals = val.split()
                        self.geometry = vals[0], vals[1], vals[2], vals[3]
                    elif var == "initcommands":
                        self.initrun = "".join(val)
                    elif var == "fontsize":
                        self.titlefont = val
                        self.xlabelfont = val
                        self.ylabelfont = val
                        self.keyfont = val
                        self.axistickfont = val
                        self.curvelabelfont = val
                        self.annotationfont = val
                    elif var == "lnwidth":
                        self.linewidth = val
                    elif var == "group":
                        if val.upper() == "ON" or val == str(1):
                            self.group = 1
                        else:
                            self.group = 0

                except:
                    continue
            f.close()
        except:
            return 0

    # set tick format and locations
    def tickFormat(self, axis, logscale, ticks, tickformat):
        if logscale:
            if tickformat == "de" or tickformat == "sci":
                axis.set_major_formatter(matplotlib.ticker.LogFormatter())
            elif tickformat == "exp":
                axis.set_major_formatter(matplotlib.ticker.LogFormatterExponent())
            elif tickformat == "10**":
                axis.set_major_formatter(matplotlib.ticker.LogFormatterMathtext())
            else:
                if tickformat[0] == "%":
                    print("\nWarning: C-style formating can not be applied when logscale is on")
                else:
                    print("\nError: Unknown xtick format (%s)" % tickformat)

                axis.set_major_formatter(matplotlib.ticker.LogFormatter())
        else:
            if tickformat == "de" or tickformat == "exp" or tickformat == "10**":
                if tickformat == "exp" or tickformat == "10**":
                    print("\nWarning: logscale is off. exp and 10** only apply when logscale is on")

                axis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
            elif tickformat == "sci":
                axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%5.2e"))
            else:
                if tickformat[0] == "%":
                    if tickformat[-1] in ("d", "e", "E", "f", "F"):
                        axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter(tickformat))
                    else:
                        print("\nError: %s is an unsupported xtickformat type" % tickformat[-1])
                        axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))
                else:
                    print("\nError: Unknown xtick format. Try adding '%' to the beginning of your format string")
                    axis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%d"))

        # if ticks is set, figure out what user wants for ticks
        if ticks != "de":
            if isinstance(ticks, int):
                # print 'setting ticks to number ', ticks
                axis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=ticks))
            elif isinstance(ticks, tuple):  # could be locations, could be (locations, labels)
                if isinstance(ticks[0], Number):  # it's a tuple of locations
                    # print 'setting ticks to tuple ', ticks
                    axis.set_major_locator(matplotlib.ticker.FixedLocator(ticks))
                    axis.set_major_formatter(matplotlib.ticker.FixedFormatter(ticks))
                if isinstance(ticks[0], tuple) and len(ticks) == 2:  # it's (locations, labels)
                    # print 'setting ticks to loc,label ', ticks
                    axis.set_major_locator(matplotlib.ticker.FixedLocator(ticks[0]))
                    axis.set_major_formatter(matplotlib.ticker.FixedFormatter(ticks[1]))
            else:  # I can't figure this out, throw an exception
                print("CAN'T SET TICKS!!!")
                raise RuntimeError("ticks set to bad value")

    def console_run(self):
        while True:
            self.cmdloop(
                f"\n\tPython Data Visualizer {pydv_version}  -  {pydv_date}\n"
                f'\tType "help" for more information.\n'
                f"\tDocumentation can be found here:\n"
                f"\t\tLLNL:   https://lc.llnl.gov/weave/pydv/html/index.html\n"
                f"\t\tGitHub: https://pydv.readthedocs.io/en/latest/\n"
                f"\tRunning from {os.path.abspath(__file__)}\n\n"
            )
            print("\n   Starting Python Console...\n   Ctrl-D to return to PyDV\n")
            console = code.InteractiveConsole(locals())
            console.interact()

    ################################################################################################
    # private functions #
    ################################################################################################

    def __log(self, line, log_type=LogEnum.LOG):
        if not line:
            return 0

        if len(line.split(":")) > 1:
            self.__log(pdvutil.getletterargs(line))
            return 0
        else:
            line = line.split()
            keepnegs = False

            if line[-1].upper() == "TRUE":
                keepnegs = True
                line.pop(-1)
            elif line[-1].upper() == "FALSE":
                keepnegs = False
                line.pop(-1)

            curves = list()
            for i in range(len(line)):
                try:
                    curvidx = pdvutil.getCurveIndex(line[i], self.plotlist)
                    curves.append(self.plotlist[curvidx])
                except pdvutil.CurveIndexError:
                    pass
                except:
                    print("error - usage: log <curve-list> [keep-neg-vals: True | False]")
                    if self.debug:
                        traceback.print_exc(file=sys.stdout)

            if log_type == LogEnum.LOG:
                pydvpy.log(curves, keepnegs)
            elif log_type == LogEnum.LOGX:
                pydvpy.logx(curves, keepnegs)
            elif log_type == LogEnum.LOG10:
                pydvpy.log10(curves, keepnegs)
            elif log_type == LogEnum.LOG10X:
                pydvpy.log10x(curves, keepnegs)
            else:
                raise RuntimeError("Unknown log type: {}".format(log_type))

    def __mod_curve(self, line, func, idx=-1):
        if not line:
            return

        line = line.split()
        value = line.pop(idx)

        if len(line) > 0:
            line = " ".join(line)
        else:
            raise RuntimeError("Unexpected empty line")

        self.modcurve(line, func, value)

    def __func_curve(self, line, func, do_x=0, idx=None):
        if not line:
            return

        value = 0
        line = line.split()

        if idx is not None:
            value = line.pop(idx)

        if len(line) > 0:
            line = " ".join(line)
        else:
            raise RuntimeError("Unexpected empty line")

        self.func_curve(line, func, do_x, value)

    def __qtMsgHandler(self, msgtype, context, msg):
        if self.debug:
            if msgtype == QtMsgType.QtDebugMsg:
                print("\nQt Debug: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            elif msgtype == QtMsgType.QtWarningMsg:
                print("\nQt Warning: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            elif msgtype == QtMsgType.QtCriticalMsg:
                print("\nQt Critical: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            elif msgtype == QtMsgType.QtFatalMsg:
                print("\nQt Fatal: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            elif msgtype == QtMsgType.QtSystemMsg:
                print("\nQt System: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            elif msgtype == QtMsgType.QtInfoMsg:
                print("\nQt Info: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))
            else:
                print("\nUnknown Message Type: %s (%s:%u, %s)\n" % (msg, context.file, context.line, context.function))

    ################################################################################################
    # main function #
    ################################################################################################

    def main(self):

        matplotlib.rc("text", usetex=False)
        matplotlib.rc("font", family="sans-serif")
        self.loadrc()

        qInstallMessageHandler(self.__qtMsgHandler)

        self.app = QApplication(sys.argv)
        self.plotter = pdvplot.Plotter(self)
        self.plotter.updatePlotGeometry(self.geometry)
        self.quit_helper = QuitHelper(self.app)

        try:
            readline.read_history_file(os.getenv("HOME") + "/.pdvhistory")
        except:
            f = open(os.getenv("HOME") + "/.pdvhistory", "w")
            f.close()

        # throw into column format mode if there is a -gnu or -csv arg
        gnu = False
        csv = False
        json = False  # throw into JSON mode if there's a -sina
        for i in range(len(sys.argv[1:])):
            if sys.argv[i] == "-gnu":
                gnu = True
                try:
                    self.xCol = int(sys.argv[i + 1])
                    sys.argv.pop(i + 1)
                except ValueError:
                    self.xCol = 0
                sys.argv.remove("-gnu")
                break
            if sys.argv[i] == "-csv":
                csv = True
                try:
                    self.xCol = int(sys.argv[i + 1])
                    sys.argv.pop(i + 1)
                except ValueError:
                    self.xCol = 0
                sys.argv.remove("-csv")
                break
            if sys.argv[i] == "-sina":
                json = True
                sys.argv.remove("-sina")
                break
        if gnu or csv:
            print("Going to column format, using ", self.xCol, " for x-axis data")
        elif json:
            print("Going to JSON format, loading all curves from curve_sets.")

        initarg = False
        other_args = [
            "-s",
        ]
        for i in range(len(sys.argv)):  # look for command line args:
            not_in_other_args = sys.argv[i] not in other_args
            if i != 0:  # '-i commandfile', and/or 'datafile1 datafile2 ...'
                if sys.argv[i] == "-i" or sys.argv[i] == "--init":
                    initarg = True
                if not_in_other_args:
                    if initarg:
                        initarg = sys.argv[i]
                    elif json:
                        self.load_sina(sys.argv[i])
                    else:
                        if not csv:
                            self.load(sys.argv[i], gnu)
                        else:
                            self.load_csv(sys.argv[i])

                if sys.argv[i] == "-s":
                    self.showplot = "off"
                    self.showkey = False

        if self.initrun is not None:  # does the .pdvrc specify a file to run of initial commands?
            self.do_run(self.initrun)  # yes? then run the file.

        if isinstance(initarg, str):  # If there was a '-i file' specified, run that file
            self.do_run(initarg)

        self.postcmd(0, "run")

        try:
            # Start interactive console in separate thread
            thread = Thread(target=self.console_run)
            thread.start()

            # Start PyDV Application
            self.plotter.show()
            self.app.exec()
        except SystemExit:
            self.app.quit()
            sys.exit()
        except KeyboardInterrupt:
            self.app.quit()
            sys.exit()
        except:
            if self.debug:
                traceback.print_exc(file=sys.stdout)
            else:
                pass


class QuitHelper(QObject):
    """
    PySide6 QuitHelper
    """

    quit_signal = Signal()

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.quit_signal.connect(self.handle_quit)

    def handle_quit(self):
        for widget in QApplication.topLevelWidgets():
            widget.close()
        self.app.quit()


def main():
    Command().main()


if __name__ == "__main__":
    main()
