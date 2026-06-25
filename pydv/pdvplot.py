# Copyright (c) Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
# See top-level LICENSE AND COPYRIGHT files for dates and other details.
# LLNL-CODE-507071
# All rights reserved.

# This file is part of PyDV.  For details, see <URL describing code and
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

from os import path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas

# HPC Import
try:
    import pdvutil
    from pdvnavbar import PyDVToolbar

# Package Import
except ImportError:
    from pydv import pdvutil
    from pydv.pdvnavbar import PyDVToolbar

try:
    from matplotlib import style

    stylesLoaded = True
except:
    stylesLoaded = False

from PySide6.QtCore import QRect, Qt, Slot
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
)

PYDV_DIR = path.dirname(path.abspath(__file__))
try:
    version_file = path.join(PYDV_DIR, "../scripts/version.txt")
    with open(version_file, "r") as fp:
        pydv_version = fp.read()

except:
    version_file = path.join(PYDV_DIR, "scripts/version.txt")
    with open(version_file, "r") as fp:
        pydv_version = fp.read()


class Plotter(QMainWindow):
    # PyDV
    _pydvcmd = None
    # Dialogs
    _listDialog = None
    _menuDialog = None
    # Tables
    _tableWidget = None
    _menuTableWidget = None
    # Actions
    _listAction = None
    _menuAction = None
    _geomAction = None

    _geometry = "de"

    canvas = None
    style = "ggplot"
    plotChanged = False
    fig = None
    figcolor = "white"
    defaultPlotLayout = None

    def __init__(self, pydvcmd):
        QMainWindow.__init__(self)

        here = path.abspath(path.dirname(__file__))

        # Setup Application
        self.setWindowTitle(f"Python Data Visualizer {pydv_version}")
        self.setWindowIcon(QIcon(path.join(here, "img/app_icon3.png")))
        self._pydvcmd = pydvcmd

        # Window geometry action
        self._geomAction = QAction(self)
        self._geomAction.triggered.connect(self.__setgeometry)

        # View Menu
        viewMenu = self.menuBar().addMenu("View")

        self._listAction = QAction("List...", self)
        self._listAction.triggered.connect(self.showCurvelistDialog)
        viewMenu.addAction(self._listAction)

        self._menuAction = QAction("Menu...", self)
        self._menuAction.triggered.connect(self.showMenuDialog)
        viewMenu.addAction(self._menuAction)

        # Help Menu
        helpMenu = self.menuBar().addMenu("Help")

        # Copyright
        copyrightAction = QAction("Copyright...", self)
        copyrightAction.triggered.connect(self.__viewCopyright)
        helpMenu.addAction(copyrightAction)
        # About PyDV
        aboutAction = QAction("&About PyDV", self)
        aboutAction.setShortcut("ctrl+a")
        aboutAction.triggered.connect(self.__aboutPyDV)
        helpMenu.addAction(aboutAction)
        # About QT
        aboutQtAction = QAction("About &Qt", self)
        aboutQtAction.triggered.connect(self.__aboutQt)
        helpMenu.addAction(aboutQtAction)

        # Styles
        if stylesLoaded:
            styles = plt.style.available

            try:
                idx = styles.index(self.style)
                style.use(styles[idx])
            except:
                if len(styles) > 0:
                    self.style = styles[0]
                    style.use(self.style)

        # Figure Canvas
        self.fig = plt.figure(figsize=(1, 1))
        self.current_axes = self.fig.subplots()
        self.fig.set_facecolor(self.figcolor)

        self.defaultPlotLayout = dict(vars(self.fig.subplotpars))

        self.canvas = FigureCanvas(self.fig)
        self.setCentralWidget(self.canvas)

        toolbar = PyDVToolbar(self.canvas, self, True)  # Add False as third parameter to turn off coordinates
        self.addToolBar(toolbar)

    def updatePlotGeometry(self, geometry="de"):
        """
        Updates the size and location of the window. Using an action to trigger the update to
        ensure that the resizing is happening on the main GUI thread.
        """
        self._geometry = geometry
        self._geomAction.trigger()

    def updateDialogs(self):
        """
        Updates the list and menu dialogs if visible.
        """
        if self._listDialog is not None:
            if self._listDialog.isVisible():
                self._listAction.trigger()

        if self._menuDialog is not None:
            if self._menuDialog.isVisible():
                self._menuAction.trigger()

    ########################################################################################################
    # SLOTS
    ########################################################################################################

    @Slot()
    def showCurvelistDialog(self):
        """
        Shows a dialog with the output of the list command in a table.
        """
        refresh = True

        if self._listDialog is None:
            refresh = False
            self._listDialog = QDialog(self)
            self._listDialog.setWindowTitle("Curve List")
            self._listDialog.setModal(False)

        # Curves List
        headerLabels = [
            "Plot Name",
            "Label",
            "X Label",
            "Y Label",
            "XMIN",
            "XMAX",
            "YMIN",
            "YMAX",
            "File Name",
            "Sina Record ID",
        ]
        rows = len(self._pydvcmd.plotlist)
        cols = len(headerLabels)

        # Create or clear table
        if self._tableWidget is None:
            self._tableWidget = QTableWidget(rows, cols, self)
            self._tableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._tableWidget.setHorizontalHeaderLabels(headerLabels)
            self._tableWidget.setAlternatingRowColors(True)
            self._tableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

            # Setup Right-click menu
            self._tableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            deleteCurveAction = QAction("Delete selected curve(s)", self._tableWidget)
            deleteCurveAction.triggered.connect(self.__deleteCurve)
            self._tableWidget.addAction(deleteCurveAction)
        else:
            self._tableWidget.clearContents()
            self._tableWidget.setRowCount(rows)

        # Populate table with curves
        row = 0
        for c in self._pydvcmd.plotlist:
            col = 0

            # Plot Name
            prefix = ""
            if c.edited:
                prefix = "*"
            plotnameItem = QTableWidgetItem(self.tr("%s%s" % (prefix, c.plotname)))
            plotnameItem.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            self._tableWidget.setItem(row, col, plotnameItem)
            col += 1

            # Label
            labelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.name, self._pydvcmd.namewidth)))
            self._tableWidget.setItem(row, col, labelItem)
            col += 1

            # X Label
            xlabelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.xlabel, self._pydvcmd.namewidth)))
            self._tableWidget.setItem(row, col, xlabelItem)
            col += 1

            # Y Label
            ylabelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.ylabel, self._pydvcmd.namewidth)))
            self._tableWidget.setItem(row, col, ylabelItem)
            col += 1

            # xmin
            xminItem = QTableWidgetItem(self.tr("%.2e" % min(c.x)))
            self._tableWidget.setItem(row, col, xminItem)
            col += 1

            # xmax
            xmaxItem = QTableWidgetItem(self.tr("%.2e" % max(c.x)))
            self._tableWidget.setItem(row, col, xmaxItem)
            col += 1

            # ymin
            yminItem = QTableWidgetItem(self.tr("%.2e" % min(c.y)))
            self._tableWidget.setItem(row, col, yminItem)
            col += 1

            # ymax
            ymaxItem = QTableWidgetItem(self.tr("%.2e" % max(c.y)))
            self._tableWidget.setItem(row, col, ymaxItem)
            col += 1

            # File Name
            fnameItem = QTableWidgetItem(self.tr(c.filename))
            self._tableWidget.setItem(row, col, fnameItem)
            col += 1

            # Sina Record ID
            recidItem = QTableWidgetItem(self.tr(c.record_id))
            self._tableWidget.setItem(row, col, recidItem)

            row += 1

        maxrows = rows
        if rows > 10:
            maxrows = 10

        if not refresh:
            # Layout
            vbox = QVBoxLayout(self._listDialog)

            # Scroll Bar
            scroll = QScrollArea(self._listDialog)
            scroll.setGeometry(QRect(10, 20, cols * 115, maxrows * 50))
            scroll.setMinimumSize(150, 150)
            scroll.setWidget(self._tableWidget)
            scroll.setWidgetResizable(True)
            vbox.addWidget(scroll)

            hbox = QHBoxLayout(self._listDialog)
            hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Dismiss Button
            okButton = QPushButton(self._listDialog)
            okButton.clicked.connect(self._listDialog.close)
            okButton.setMinimumSize(100, 20)
            okButton.setMaximumSize(100, 20)
            okButton.setText("Dismiss")
            hbox.addWidget(okButton)

            vbox.addLayout(hbox)

        self._listDialog.resize(cols * 115, maxrows * 50)
        if not self._listDialog.isVisible():
            self._listDialog.show()

    @Slot()
    def showMenuDialog(self):
        """
        Shows a dialog with the output of the menu command in a table.
        """
        refresh = True

        if self._menuDialog is None:
            refresh = False
            self._menuDialog = QDialog(self)
            self._menuDialog.setWindowTitle("Menu")
            self._menuDialog.setModal(False)

        # Available Curves
        headerLabels = ["Label", "X Label", "Y Label", "XMIN", "XMAX", "YMIN", "YMAX", "File Name", "Sina Record ID"]
        rows = len(self._pydvcmd.curvelist)
        cols = len(headerLabels)

        # Create or clear table
        if self._menuTableWidget is None:
            self._menuTableWidget = QTableWidget(rows, cols, self)
            self._menuTableWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._menuTableWidget.setHorizontalHeaderLabels(headerLabels)
            self._menuTableWidget.setAlternatingRowColors(True)
            self._menuTableWidget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

            # Setup Right-click menu
            self._menuTableWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            plotCurveAction = QAction("Plot selected curve(s)", self._menuTableWidget)
            plotCurveAction.triggered.connect(self.__plotMenuCurve)
            self._menuTableWidget.addAction(plotCurveAction)

            deleteCurveAction = QAction("Delete selected curve(s)", self._menuTableWidget)
            deleteCurveAction.triggered.connect(self.__deleteMenuCurve)
            self._menuTableWidget.addAction(deleteCurveAction)
        else:
            self._menuTableWidget.clearContents()
            self._menuTableWidget.setRowCount(rows)

        # Populate table with curves
        row = 0
        for c in self._pydvcmd.curvelist:
            col = 0

            # Plot Name
            # prefix = ''
            # if c.edited:
            #     prefix = '*'
            # plotnameItem = QTableWidgetItem(self.tr("%s%s" % (prefix, c.plotname)))
            # plotnameItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            # self._menuTableWidget.setItem(row, col, plotnameItem)
            # col += 1

            # Label
            labelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.name, self._pydvcmd.namewidth)))
            self._menuTableWidget.setItem(row, col, labelItem)
            col += 1

            # X Label
            xlabelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.xlabel, self._pydvcmd.namewidth)))
            self._menuTableWidget.setItem(row, col, xlabelItem)
            col += 1

            # Y Label
            ylabelItem = QTableWidgetItem(self.tr(pdvutil.truncate(c.ylabel, self._pydvcmd.namewidth)))
            self._menuTableWidget.setItem(row, col, ylabelItem)
            col += 1

            # xmin
            xminItem = QTableWidgetItem(self.tr("%.2e" % min(c.x)))
            self._menuTableWidget.setItem(row, col, xminItem)
            col += 1

            # xmax
            xmaxItem = QTableWidgetItem(self.tr("%.2e" % max(c.x)))
            self._menuTableWidget.setItem(row, col, xmaxItem)
            col += 1

            # ymin
            yminItem = QTableWidgetItem(self.tr("%.2e" % min(c.y)))
            self._menuTableWidget.setItem(row, col, yminItem)
            col += 1

            # ymax
            ymaxItem = QTableWidgetItem(self.tr("%.2e" % max(c.y)))
            self._menuTableWidget.setItem(row, col, ymaxItem)
            col += 1

            # File Name
            fnameItem = QTableWidgetItem(self.tr(c.filename))
            self._menuTableWidget.setItem(row, col, fnameItem)
            col += 1

            # Sina Record ID
            recidItem = QTableWidgetItem(self.tr(c.record_id))
            self._menuTableWidget.setItem(row, col, recidItem)

            row += 1

        maxrows = rows
        if rows > 10:
            maxrows = 10

        if not refresh:
            # Layout
            vbox = QVBoxLayout(self._menuDialog)

            # Scroll Bar
            scroll = QScrollArea(self._menuDialog)
            scroll.setGeometry(QRect(10, 20, cols * 115, maxrows * 50))
            scroll.setMinimumSize(150, 150)
            scroll.setWidget(self._menuTableWidget)
            scroll.setWidgetResizable(True)
            vbox.addWidget(scroll)

            hbox = QHBoxLayout(self._menuDialog)
            hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Dismiss Button
            okButton = QPushButton(self._menuDialog)
            okButton.clicked.connect(self._menuDialog.close)
            okButton.setMinimumSize(100, 20)
            okButton.setMaximumSize(100, 20)
            okButton.setText("Dismiss")
            hbox.addWidget(okButton)

            vbox.addLayout(hbox)

        self._menuDialog.resize(cols * 115, maxrows * 50)
        if not self._menuDialog.isVisible():
            self._menuDialog.show()

    def __viewCopyright(self):
        msg = self.tr(
            '<b> \
                      <p style="font-family:verdana;">Copyright &copy; Lawrence Livermore National Security, LLC.</p> \
                      <p style="font-family:verdana;">Produced at the Lawrence Livermore National Laboratory.</p> \
                      <p style="font-family:verdana;">See top-level LICENSE AND COPYRIGHT files for dates and other \
                      details.</p> \
                      <p style="font-family:verdana;">LLNL-CODE-507071</p> \
                      <p style="font-family:verdana;">All rights reserved.</p></b> \
                      <p style="font-family:courier; font-size:80%;">This file is part of PyDV. \
                      For details, see <URL describing code and \
                      how to download source>. Please also read "Additional BSD Notice".</p> \
                      <p style="font-family:courier; font-size:80%;"> Redistribution and use in \
                      source and binary forms, with or without \
                      modification, are permitted provided that the following conditions are met:</p> \
                      <p style="font-family:courier; font-size:80%;"> Redistributions of source code \
                      must retain the above copyright \
                      notice, this list of conditions and the disclaimer below. \
                      Redistributions in binary form must reproduce the above copyright \
                      notice, this list of conditions and the disclaimer (as noted below) \
                      in the documentation and/or other materials provided with the \
                      distribution.  Neither the name of the LLNS/LLNL nor the names of \
                      its contributors may be used to endorse or promote products derived \
                      from this software without specific prior written permission.</p> \
                      <p style="font-family:courier; font-size:80%;"> THIS SOFTWARE IS PROVIDED \
                      BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS \
                      "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT \
                      LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS \
                      FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL LAWRENCE \
                      LIVERMORE NATIONAL SECURITY, LLC, THE U.S. DEPARTMENT OF ENERGY OR \
                      CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, \
                      SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT \
                      LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF \
                      USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND \
                      ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, \
                      OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT \
                      OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF \
                      SUCH DAMAGE.</p> \
                      <p style="font-family:courier; font-size:80%;">Additional BSD Notice</p> \
                      <p style="font-family:courier; font-size:80%;"> 1. This notice is required \
                      to be provided under our contract with \
                      the U.S.  Department of Energy (DOE).  This work was produced at \
                      Lawrence Livermore National Laboratory under Contract \
                      No. DE-AC52-07NA27344 with the DOE.</p> \
                      <p style="font-family:courier; font-size:80%;"> 2. Neither the United States \
                      Government nor Lawrence Livermore \
                      National Security, LLC nor any of their employees, makes any \
                      warranty, express or implied, or assumes any liability or \
                      responsibility for the accuracy, completeness, or usefulness of any \
                      information, apparatus, product, or process disclosed, or represents \
                      that its use would not infringe privately-owned rights.</p> \
                      <p style="font-family:courier; font-size:80%;"> 3.  Also, reference herein to \
                      any specific commercial products, \
                      process, or services by trade name, trademark, manufacturer or \
                      otherwise does not necessarily constitute or imply its endorsement, \
                      recommendation, or favoring by the United States Government or \
                      Lawrence Livermore National Security, LLC.  The views and opinions \
                      of authors expressed herein do not necessarily state or reflect \
                      those of the United States Government or Lawrence Livermore National \
                      Security, LLC, and shall not be used for advertising or product \
                      endorsement purposes.</p>'
        )

        # Copyright Dialog
        copy_dialog = QDialog(self)
        copy_dialog.setWindowTitle("PyDV Copyright")
        copy_dialog.setModal(True)

        # Layout
        vbox = QVBoxLayout(copy_dialog)

        # Copyright message
        html_view = QTextEdit(copy_dialog)
        html_view.setReadOnly(True)
        html_view.setText(msg)

        scroll = QScrollArea(copy_dialog)
        scroll.setGeometry(QRect(10, 20, 280, 400))
        scroll.setMinimumSize(150, 150)
        scroll.setWidget(html_view)
        scroll.setWidgetResizable(True)
        vbox.addWidget(scroll)

        # OK Button
        hbox = QHBoxLayout(copy_dialog)
        okButton = QPushButton(copy_dialog)
        okButton.clicked.connect(copy_dialog.close)
        okButton.setMinimumSize(100, 20)
        okButton.setMaximumSize(100, 20)
        okButton.setText("OK")
        hbox.addWidget(okButton, Qt.AlignmentFlag.AlignCenter)
        vbox.addLayout(hbox)

        copy_dialog.resize(300, 500)
        copy_dialog.show()

    def __aboutQt(self):
        QMessageBox.aboutQt(self)

    def __aboutPyDV(self):
        QMessageBox.about(
            self,
            self.tr("About PyDV"),
            self.tr(
                "<h2>About PyDV</h2>"
                f'<p style="font-family:courier; font-size:40%;">version {pydv_version}</p>'
                '<p style="font-family:verdana;"><a href="https://pydv.readthedocs.io/en/latest/"> \
                                   PyDV</a> is a 1D graphics tool, heavily based on the ULTRA plotting tool.</p> \
                                   <p style="font-family:verdana;">Produced at the Lawrence Livermore National \
                                   Laboratory.</p> \
                                   <p style="font-family:verdana;">See top-level LICENSE AND COPYRIGHT files for \
                                   dates and other details.</p> \
                                   <p style="font-family:verdana;">LLNL-CODE-507071</p> \
                                   <p style="font-family:verdana;">All rights reserved.</p>'
            ),
        )

    def __deleteCurve(self):
        rowcnt = len(self._tableWidget.selectionModel().selectedRows())

        if rowcnt > 0:
            if rowcnt == len(self._pydvcmd.plotlist):
                print("erase")
                self._pydvcmd.do_erase("erase")
            else:
                plotnames = str()
                for index in self._tableWidget.selectionModel().selectedRows():
                    row = index.row()
                    plotnames += "%s " % self._pydvcmd.plotlist[row].plotname

                print("delete %s" % plotnames)
                self._pydvcmd.do_delete("%s" % plotnames)

            self._pydvcmd.updateplot

    def __deleteMenuCurve(self):
        rowcnt = len(self._menuTableWidget.selectionModel().selectedRows())

        if rowcnt > 0:
            if rowcnt == len(self._pydvcmd.curvelist):
                print("kill all")
                self._pydvcmd.do_kill("all")
            else:
                menuindexes = str()
                for index in self._menuTableWidget.selectionModel().selectedRows():
                    row = index.row()
                    menuindexes += "%d " % (row + 1)

                print("kill %s" % menuindexes)
                self._pydvcmd.do_kill("%s" % menuindexes)

    def __plotMenuCurve(self):
        rowcnt = len(self._menuTableWidget.selectionModel().selectedRows())

        if rowcnt > 0:
            plotnames = str()

            for index in self._menuTableWidget.selectionModel().selectedRows():
                row = index.row()
                plotnames += " %d" % (row + 1)

            print("curve%s" % plotnames)
            self._pydvcmd.do_curve("%s" % plotnames)
            self._pydvcmd.updateplot

    def __setgeometry(self):
        geometry = self._geometry
        if geometry != "de":
            self.setGeometry(int(geometry[2]), int(geometry[3]), int(geometry[0]), int(geometry[1]))
        else:
            self.setGeometry(50, 50, 600, 500)

    def closeEvent(self, event):

        if hasattr(self, "plot_updater") and self.plot_updater.is_alive():
            self.plot_updater.stop()
            self.plot_updater.join()

        plt.close("all")

        event.accept()
