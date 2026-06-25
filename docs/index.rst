.. PyDV documentation master file, created by
   sphinx-quickstart on Fri Dec 18 11:38:25 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyDV Documentation!
************************************
The Python Data Visualizer (PyDV) is a replacement for ULTRA writtern in python. PyDV allows the presentation, manipulation, and analysis of 1D data sets, i.e. (x,y) pairs. Presentation refers to the capability to display, and make hard copies of data plots. Manipulation refers to the capability to excerpt, shift, and scale data sets. Analysis refers to the capability to combine data sets in various ways to create new data sets.

The principal object with which PyDV works is the curve. A curve is an object which consists of an array of x values, an array of y values, a number of points (the length of the x and y arrays), and an ASCII label. PyDV operates on curves.


Users
=====

.. toctree::
   :maxdepth: 1

   release_notes
   pdvrc
   getting_started
   io_commands
   math_operations
   env_inquiry_cmds
   curve_inquiry_cmds
   env_control_cmds
   plot_control_cmds
   curve_control_cmds
   ui_features

Developers
==========

.. toctree::
   :maxdepth: 1

   pydv

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
