"""Plotter class interface for Matplotlib and Qt."""

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

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas

# Package Import
if __package__:
    from pydv import pdvutil
    from pydv.pdvnavbar import PyDVToolbar

# HPC Import
else:
    import pdvutil
    from pdvnavbar import PyDVToolbar

try:
    from matplotlib import style

    styles_loaded = True
except:
    styles_loaded = False

from importlib.metadata import version

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

# Package Import
if __package__:
    pydv_version = version("LLNL-PyDV")

# HPC Import
else:
    import tomllib

    PYDV_DIR = Path(__file__).resolve().parent
    toml_file = PYDV_DIR / "pyproject.toml"
    with toml_file.open("rb") as fp:
        pydv_version = tomllib.load(fp)["project"]["version"]


class Plotter(QMainWindow):
    """Plotter with Matplotlib and Qt."""

    # PyDV
    _pydvcmd = None
    # Dialogs
    _list_dialog = None
    _menu_dialog = None
    # Tables
    _table_widget = None
    _menu_table_widget = None
    # Actions
    _list_action = None
    _menu_action = None
    _geom_action = None

    _geometry = "de"

    canvas = None
    style = "ggplot"
    plot_changed = False
    fig = None
    figcolor = "white"
    default_plot_layout = None

    def __init__(self, pydvcmd):
        """Initialize the plotter."""
        QMainWindow.__init__(self)

        here = Path(__file__).resolve().parent

        # Setup Application
        self.setWindowTitle(f"Python Data Visualizer {pydv_version}")
        self.setWindowIcon(QIcon(str(here / "img/app_icon3.png")))
        self._pydvcmd = pydvcmd

        # Window geometry action
        self._geom_action = QAction(self)
        self._geom_action.triggered.connect(self.__setgeometry)

        # View Menu
        view_menu = self.menuBar().addMenu("View")

        self._list_action = QAction("List...", self)
        self._list_action.triggered.connect(self.show_curvelist_dialog)
        view_menu.addAction(self._list_action)

        self._menu_action = QAction("Menu...", self)
        self._menu_action.triggered.connect(self.show_menu_dialog)
        view_menu.addAction(self._menu_action)

        # Help Menu
        help_menu = self.menuBar().addMenu("Help")

        # Copyright
        copyright_action = QAction("Copyright...", self)
        copyright_action.triggered.connect(self.__view_copyright)
        help_menu.addAction(copyright_action)
        # About PyDV
        about_action = QAction("&About PyDV", self)
        about_action.setShortcut("ctrl+a")
        about_action.triggered.connect(self.__about_pydv)
        help_menu.addAction(about_action)
        # About QT
        about_qt_action = QAction("About &Qt", self)
        about_qt_action.triggered.connect(self.__about_qt)
        help_menu.addAction(about_qt_action)

        # Styles
        if styles_loaded:
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

        self.default_plot_layout = dict(vars(self.fig.subplotpars))

        self.canvas = FigureCanvas(self.fig)
        self.setCentralWidget(self.canvas)

        toolbar = PyDVToolbar(self.canvas, self, True)  # Add False as third parameter to turn off coordinates
        self.addToolBar(toolbar)

    def update_plot_geometry(self, geometry="de"):
        """Update the size and location of the window.

        Using an action to trigger the update to ensure that the resizing is happening on the main GUI thread.
        """
        self._geometry = geometry
        self._geom_action.trigger()

    def update_dialogs(self):
        """Update the list and menu dialogs if visible."""
        if self._list_dialog is not None and self._list_dialog.isVisible():
            self._list_action.trigger()

        if self._menu_dialog is not None and self._menu_dialog.isVisible():
            self._menu_action.trigger()

    ########################################################################################################
    # SLOTS
    ########################################################################################################

    @Slot()
    def show_curvelist_dialog(self):
        """Show a dialog with the output of the list command in a table."""
        refresh = True

        if self._list_dialog is None:
            refresh = False
            self._list_dialog = QDialog(self)
            self._list_dialog.setWindowTitle("Curve List")
            self._list_dialog.setModal(False)

        # Curves List
        header_labels = [
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
        cols = len(header_labels)

        # Create or clear table
        if self._table_widget is None:
            self._table_widget = QTableWidget(rows, cols, self)
            self._table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._table_widget.setHorizontalHeaderLabels(header_labels)
            self._table_widget.setAlternatingRowColors(True)
            self._table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

            # Setup Right-click menu
            self._table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            delete_curve_action = QAction("Delete selected curve(s)", self._table_widget)
            delete_curve_action.triggered.connect(self.__delete_curve)
            self._table_widget.addAction(delete_curve_action)
        else:
            self._table_widget.clearContents()
            self._table_widget.setRowCount(rows)

        # Populate table with curves
        for row, c in enumerate(self._pydvcmd.plotlist):
            col = 0

            # Plot Name
            prefix = ""
            if c.edited:
                prefix = "*"
            plot_name_item = QTableWidgetItem(self.tr(f"{prefix}{c.plotname}"))
            plot_name_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            self._table_widget.setItem(row, col, plot_name_item)
            col += 1

            # Label
            label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.name, self._pydvcmd.namewidth)))
            self._table_widget.setItem(row, col, label_item)
            col += 1

            # X Label
            x_label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.xlabel, self._pydvcmd.namewidth)))
            self._table_widget.setItem(row, col, x_label_item)
            col += 1

            # Y Label
            y_label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.ylabel, self._pydvcmd.namewidth)))
            self._table_widget.setItem(row, col, y_label_item)
            col += 1

            # xmin
            xmin_item = QTableWidgetItem(self.tr(f"{min(c.x):.2e}"))
            self._table_widget.setItem(row, col, xmin_item)
            col += 1

            # xmax
            xmax_item = QTableWidgetItem(self.tr(f"{max(c.x):.2e}"))
            self._table_widget.setItem(row, col, xmax_item)
            col += 1

            # ymin
            ymin_item = QTableWidgetItem(self.tr(f"{min(c.y):.2e}"))
            self._table_widget.setItem(row, col, ymin_item)
            col += 1

            # ymax
            ymax_item = QTableWidgetItem(self.tr(f"{max(c.y):.2e}"))
            self._table_widget.setItem(row, col, ymax_item)
            col += 1

            # File Name
            fname_item = QTableWidgetItem(self.tr(c.filename))
            self._table_widget.setItem(row, col, fname_item)
            col += 1

            # Sina Record ID
            rec_id_item = QTableWidgetItem(self.tr(c.record_id))
            self._table_widget.setItem(row, col, rec_id_item)

        maxrows = rows
        if rows > 10:
            maxrows = 10

        if not refresh:
            # Layout
            vbox = QVBoxLayout(self._list_dialog)

            # Scroll Bar
            scroll = QScrollArea(self._list_dialog)
            scroll.setGeometry(QRect(10, 20, cols * 115, maxrows * 50))
            scroll.setMinimumSize(150, 150)
            scroll.setWidget(self._table_widget)
            scroll.setWidgetResizable(True)
            vbox.addWidget(scroll)

            hbox = QHBoxLayout(self._list_dialog)
            hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Dismiss Button
            ok_button = QPushButton(self._list_dialog)
            ok_button.clicked.connect(self._list_dialog.close)
            ok_button.setMinimumSize(100, 20)
            ok_button.setMaximumSize(100, 20)
            ok_button.setText("Dismiss")
            hbox.addWidget(ok_button)

            vbox.addLayout(hbox)

        self._list_dialog.resize(cols * 115, maxrows * 50)
        if not self._list_dialog.isVisible():
            self._list_dialog.show()

    @Slot()
    def show_menu_dialog(self):
        """Show a dialog with the output of the menu command in a table."""
        refresh = True

        if self._menu_dialog is None:
            refresh = False
            self._menu_dialog = QDialog(self)
            self._menu_dialog.setWindowTitle("Menu")
            self._menu_dialog.setModal(False)

        # Available Curves
        header_labels = ["Label", "X Label", "Y Label", "XMIN", "XMAX", "YMIN", "YMAX", "File Name", "Sina Record ID"]
        rows = len(self._pydvcmd.curvelist)
        cols = len(header_labels)

        # Create or clear table
        if self._menu_table_widget is None:
            self._menu_table_widget = QTableWidget(rows, cols, self)
            self._menu_table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self._menu_table_widget.setHorizontalHeaderLabels(header_labels)
            self._menu_table_widget.setAlternatingRowColors(True)
            self._menu_table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

            # Setup Right-click menu
            self._menu_table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
            plot_curve_action = QAction("Plot selected curve(s)", self._menu_table_widget)
            plot_curve_action.triggered.connect(self.__plot_menu_curve)
            self._menu_table_widget.addAction(plot_curve_action)

            delete_curve_action = QAction("Delete selected curve(s)", self._menu_table_widget)
            delete_curve_action.triggered.connect(self.__delete_menu_curve)
            self._menu_table_widget.addAction(delete_curve_action)
        else:
            self._menu_table_widget.clearContents()
            self._menu_table_widget.setRowCount(rows)

        # Populate table with curves
        for row, c in enumerate(self._pydvcmd.curvelist):
            col = 0

            # Label
            label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.name, self._pydvcmd.namewidth)))
            self._menu_table_widget.setItem(row, col, label_item)
            col += 1

            # X Label
            x_label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.xlabel, self._pydvcmd.namewidth)))
            self._menu_table_widget.setItem(row, col, x_label_item)
            col += 1

            # Y Label
            y_label_item = QTableWidgetItem(self.tr(pdvutil.truncate(c.ylabel, self._pydvcmd.namewidth)))
            self._menu_table_widget.setItem(row, col, y_label_item)
            col += 1

            # xmin
            xmin_item = QTableWidgetItem(self.tr(f"{min(c.x):.2e}"))
            self._menu_table_widget.setItem(row, col, xmin_item)
            col += 1

            # xmax
            xmax_item = QTableWidgetItem(self.tr(f"{max(c.x):.2e}"))
            self._menu_table_widget.setItem(row, col, xmax_item)
            col += 1

            # ymin
            ymin_item = QTableWidgetItem(self.tr(f"{min(c.y):.2e}"))
            self._menu_table_widget.setItem(row, col, ymin_item)
            col += 1

            # ymax
            ymax_item = QTableWidgetItem(self.tr(f"{max(c.y):.2e}"))
            self._menu_table_widget.setItem(row, col, ymax_item)
            col += 1

            # File Name
            fname_item = QTableWidgetItem(self.tr(c.filename))
            self._menu_table_widget.setItem(row, col, fname_item)
            col += 1

            # Sina Record ID
            rec_id_item = QTableWidgetItem(self.tr(c.record_id))
            self._menu_table_widget.setItem(row, col, rec_id_item)

        maxrows = rows
        if rows > 10:
            maxrows = 10

        if not refresh:
            # Layout
            vbox = QVBoxLayout(self._menu_dialog)

            # Scroll Bar
            scroll = QScrollArea(self._menu_dialog)
            scroll.setGeometry(QRect(10, 20, cols * 115, maxrows * 50))
            scroll.setMinimumSize(150, 150)
            scroll.setWidget(self._menu_table_widget)
            scroll.setWidgetResizable(True)
            vbox.addWidget(scroll)

            hbox = QHBoxLayout(self._menu_dialog)
            hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Dismiss Button
            ok_button = QPushButton(self._menu_dialog)
            ok_button.clicked.connect(self._menu_dialog.close)
            ok_button.setMinimumSize(100, 20)
            ok_button.setMaximumSize(100, 20)
            ok_button.setText("Dismiss")
            hbox.addWidget(ok_button)

            vbox.addLayout(hbox)

        self._menu_dialog.resize(cols * 115, maxrows * 50)
        if not self._menu_dialog.isVisible():
            self._menu_dialog.show()

    def __view_copyright(self):
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
        ok_button = QPushButton(copy_dialog)
        ok_button.clicked.connect(copy_dialog.close)
        ok_button.setMinimumSize(100, 20)
        ok_button.setMaximumSize(100, 20)
        ok_button.setText("OK")
        hbox.addWidget(ok_button, Qt.AlignmentFlag.AlignCenter)
        vbox.addLayout(hbox)

        copy_dialog.resize(300, 500)
        copy_dialog.show()

    def __about_qt(self):
        QMessageBox.aboutQt(self)

    def __about_pydv(self):
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

    def __delete_curve(self):
        rowcnt = len(self._table_widget.selectionModel().selectedRows())

        if rowcnt > 0:
            if rowcnt == len(self._pydvcmd.plotlist):
                print("erase")
                self._pydvcmd.do_erase("erase")
            else:
                plotnames = ""
                for index in self._table_widget.selectionModel().selectedRows():
                    row = index.row()
                    plotnames += f"{self._pydvcmd.plotlist[row].plotname} "

                print(f"delete {plotnames}")
                self._pydvcmd.do_delete(f"{plotnames}")

            self._pydvcmd.updateplot()

    def __delete_menu_curve(self):
        rowcnt = len(self._menu_table_widget.selectionModel().selectedRows())

        if rowcnt > 0:
            if rowcnt == len(self._pydvcmd.curvelist):
                print("kill all")
                self._pydvcmd.do_kill("all")
            else:
                menuindexes = ""
                for index in self._menu_table_widget.selectionModel().selectedRows():
                    row = index.row()
                    menuindexes += f"{row + 1} "

                print(f"kill {menuindexes}")
                self._pydvcmd.do_kill(f"{menuindexes}")

    def __plot_menu_curve(self):
        rowcnt = len(self._menu_table_widget.selectionModel().selectedRows())

        if rowcnt > 0:
            plotnames = ""

            for index in self._menu_table_widget.selectionModel().selectedRows():
                row = index.row()
                plotnames += f" {row + 1}"

            print(f"curve{plotnames}")
            self._pydvcmd.do_curve(f"{plotnames}")
            self._pydvcmd.updateplot()

    def __setgeometry(self):
        geometry = self._geometry
        if geometry != "de":
            self.setGeometry(int(geometry[2]), int(geometry[3]), int(geometry[0]), int(geometry[1]))
        else:
            self.setGeometry(50, 50, 600, 500)

    def close_event(self, event):
        """Close the plotter."""
        if hasattr(self, "plot_updater") and self.plot_updater.is_alive():
            self.plot_updater.stop()
            self.plot_updater.join()

        plt.close("all")

        event.accept()
