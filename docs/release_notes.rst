.. _release_notes:

Release Notes
=============
3.10.0
------
* Switched to `PySide6`
* Updated `pyproject.toml`
* Added `pre-commit` with `ruff` and other tools
* Removed `requirements.txt` and `flake8`

3.9.1
------
* Remove `distutils`

3.9.0
------
* Support for sina hdf5 files
* Bugfix for `fit`

3.8.2
------
* Bugfix for xminmax mask
* Added `stats()` to pydvpy which prints statistics of the curve

3.8.1
------
* Bugfix for PyQt6 GUI updates

3.8.0
------
* Upgraded to PyQt6
* Bugfix for marker with more than one curve
* Refactored docs
* PyDVpy common function

3.7.0
------
* Updated read function for faster read times

3.6.6
------
* Bugfix: Label confusion with curve maths for curves greater than 26
* Refactoring a lot of methods to use `numpy` instead of for loops

3.6.5
------
* Bugfix: Launcher update for HPCs read files from command line

3.6.4
------
* Launcher update for HPCs

3.6.3
------
* Updated default parameter values for curve comparison functions in PyDVpy API
* Added `getfl()` which returns the first and last value from a curve in PyDVpy API

3.6.2
------
* Curve file plotting (e.g. cur a.1 \*.1, \*.1:\*.3) now works for files above a-z (@27.1, @28.5, etc...)
* `group` goes back to default plotting if only one file is present in list command table
* `deltax` and `deltay` creates new curve that calculates difference between its own X or Y points. Delta X or Y vs # of points - 1.
* Curve names can now have `:` and `#`
* `label` curve name separator is now ` to allow for other characters

3.6.1
------
* Consolidate read functions

3.6.0
------
* Curve comparison functions for PyDVpy API

3.5.2
------
* `tightlayout`: Users can now turn on and off plot tight layout.
* `xtickha`, `xtickva`, `ytickha`, `ytickva`: Users can now horizontally and vertically align ticks.
* `group`: Users can now update title to curve name and labels to filenames if all curves have the same name.
* `cur`: Asterisks now work for all file curves (\*.1 plot curve 1 for all files, \*.1:\*.3 plot curve 1:3 for all files)
* Bugfix for image test
* Bugfix for backslash literal string
* Bugfix for `cur` asterisk file format plotting past file curves

3.5.1
------
* `mathinterpparams`: Users can now set `numpy.interp()` `left`, `right`, and `period` parameters for internal curve math methods for Curve such as `+ a b c`, `- a b c`, etc....

3.5.0
------
* Consolidated `pydvpy.makecurve()` and `curve.Curve()`. Now uses `pydvpy.makecurve()` throughout PyDV.
* Changed `from pydv import pydvpy as pydvif` to `from pydv import pydvpy`. Now uses `pydvpy` throughout PyDV.

3.4.5
------
* `image` now has width and height options
* `disp` now has format options
* Cleaning up docs

3.4.4
------
* Can now have multiple independent curves in a curve set in sina.json files

3.4.3
------
* Added original data to step data as curve.step_original_x and curve.step_original_y

3.4.2
------
* Added documentation links at startup
* Bug fix for `diffMeasure()` when both curves are all zeros
* `create_plot()` now returns plot, figure, and axis

3.4.1
------
* Bug fix for maths when curves are deleted

3.4.0
------
* Bug fix for convolution function
* Bug fix for normalize function
* WEAVE environment Python for Makefile
* Move scripts/ directory for installation
* Bug fix for blank labels
* Re-added underscores to curve names
* Menu now has `menulength` option
* Bugfix when files don't end in valid data
* Updated docs with examples
* Added `sum`` and `cumsum` functions
* Added `area` function
* Updated `stats` function
* Updated `savecsv` and `readcsv` to allow curves with different lengths
* Updated `read` to allow x-columns to be x-tick labels

3.3.0
------
* Curvelist support for multiple commands
* Ability to add Curve ID to plot
* Ability to read and save ultra files with x and y labels
* Ultra file curve name issues
* Consolidate linemarker and marker commands
* Filter command
* Dirac Delta command

3.2.0
------
* Bug fix for normalize
* Added bold and italic option for xlabel and ylabel
* Added theta command
* Added hypot command
* Added merge ultra files command
* Added axis on off command
* Added plot on off command
* Added recolor command
* Allow multiple labels to be deleted at once
* Added single point curves
* Bug fix for module imports

3.1.16
------
* Restore docs theme back to sphinx-rtd-theme
* Apply flake8
* Bug fix for getx, getymin, getymax
* Bug fix for addition, subtraction, multiplication, division
* Bug fix for saving images in command line

3.1.15
------
* Bug fix for save command

3.1.14
------
* Bug fix for custom functions
* Bug fix for step functions

3.1.13
------
* Sina curve sets in library data can now be read

3.1.12
------
* Fixed `parsemath()` not working with step functions for addition, subraction, multiplication, and division

3.1.11
------
* Axes log scale bug fixed

3.1.10
------
* Updated matplotlib from 3.2 to 3.7
* Fixed install bug and duplicate axes bug

3.1.9
-----
* Updated setup.py to pyproject.toml
* Changed docs sphinx theme to furo

3.1.8
-----
* Updated Python path for HPC Upgrades

3.1.7
-----
* Fixed file reading regex bug not reading data points correctly
* Updated `labelfilenames` command to append filename to curve legend
  with toggle on/off functionality


3.1.6
-----
* Updated `read` command to accommodate tab-delimited ultra files
* Added `labelrecordids` and `group` commands
  compatible with curves from Sina files
* Updated test baselines to cover new commands
* Added tests for pdv and pydypy to cover read functions for
  different curve file types and commands to set `menu` column widths:
  `xlabelwidth`, `ylabelwidth`, `filenamewidth`, and `recordidwidth`
* Updated CI to run without --system-site-packages; matplotlib version fixed to 3.2.0
  and numpy updated to 1.24.2


3.1.5
-----
* Updated CI to run on closed side.



3.1.4
-----
* Makefile change to do 'sed' on pdv to update the python path
  and chmod -R 750 develop


3.1.3
-----
* Added CI running in CZ and RZ
* Run RZ specific tests in CI (when running in RZ)
* Updated test baselines - due to python.3.8.2


3.1.2
-----
* Improved `pydvpy.read()` performance.



3.1.1
-----
``@`` notation in curve indexing fixed for mathematical operations.



3.1.0
-----
`getymin` and `getymax` will now return a list of x, y pairs for the min/max value.
If there is a domain specified, these functions will only return points in that
domain.



3.0.7
-----
* Fixed a bug in PyDV internal when using min and max over a range.



3.0.6
-----
* Fixed functions that did not work with curve lists, which were: dupx, del,
  markerfacecolor, markeredgecolor, random, rev, sort, subsample, xindex, xminmax,
  yminmax, log{,x,10,10x}, makeintensive, makeextensive, max, smooth, disp{,x},
  getdomain, getrange, stats, movefront
* All curve list functions support gaps in the list of curves. For example,
  if there are curves A, B, and E, then ``function A:E`` will still work on
  A, B, and E.



3.0.5
-----
* log{, x, 10, 10x} commands update the legend
* log{, x} and exp{, x} cancel each other in the legend



3.0.4
-----

* Changed "ultra" to "pydv" in error messages.
* Changed "majorminor" to "both" in grid argument.
* Force interp num to be integers.



3.0.3
-----

Enhancements
~~~~~~~~~~~~

* Ability to read Sina curve sets.
* Ability to specify which curves will appear in the legend.



3.0.2
-----

Bug Fixes
~~~~~~~~~

* Zoom settings from the User Interface are now persisted throughout the application.

Enhancements
~~~~~~~~~~~~

* Allow simple math operations on curves that have been read in but not yet plotted.
* Enhanced the **image** command to allow the user to define the image resolution and transparency.
* Added the **menur** command that works like the **menu** command with the addition of allowing *start* and *stop* indices.
* Added the **listr** command that works like the **list** command with the addition of allowing *start* and *stop* indices.
* Added the **plotlayout** command that allows the user to adjust the plot layout parameters.



3.0.1
-----

Bug Fixes
~~~~~~~~~

* Fixed the @ symbol range bug
* Fixed guilims command

Enhancements
~~~~~~~~~~~~

* Added **labelcurve** command that allows users to add curve letter to the legend label
* Enhanced the **divide**, **multiply**, **add**, and **subtract** commands to support dividing by a real number
* Suppressed user warnings
* Added **border** command that turns plot border on or off
* Updated the link in the **About** dialog popup

Changes for PyDV Developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Moved repository to the LLNL Github organization



3.0
---

Python 3 port with bug fixes and a lot of minor code refactoring.



2.4.3
-----

Bug Fixes
~~~~~~~~~

* Fixed the piece-wise constant integration bug
* Fit command bug fixed
* Added Doug Miller's fix for retrieving a curve by label

Enhancements
~~~~~~~~~~~~

* Added the minorticks command. Minor ticks can now be made visible.
* Added the xtickcolor command to change the color of major and minor ticks on the x~axis
* Added the ytickcolor command to change the color of major and minor ticks on the y~axis
* Updated the xticklength command to support minor ticks
* Updated the xtickwidth command to support minor ticks
* Updated the yticklength command to support minor ticks
* Updated the ytickwidth command to support minor ticks
* Added the gridcolor command
* Added the gridstyle command
* Added the gridwidth command
* Added the random command
* Added the rev command
* Added the sort command
* Added the alpha command
* Added the gaussian command



2.4.2
-----

Bug Fixes
~~~~~~~~~

* Fixed the FFT command to produce two curves for the complex and imaginary part like Ultra
* Corrected the 'off by one' index error for curves named with the '@' symbol
* The xtick commands now display the correct help information
* errorbar command works now

Enhancements
~~~~~~~~~~~~

* Implemented the convol, convolb, and convolc commands like their Ultra equivalent
* Added the intensize and extensive commands
* Added the correl command
* Added the system command to allow passing commands to the operating system
* Allow the user to optionally throw away zero and negative values when using the log commands
* Updated the integrate command to use a new color for the new curve it produces
* Added the getymax/getymin commands
* Enhanced the convol commands to add the number of points to the label



2.4
---

Bug Fixes
~~~~~~~~~

* Display updates correctly after running a batch file
* Draw style command can now draw all of the step options (pre, post, mid)
* Fixed the lableFileNames command from adding the filename more than once
* For certain commands that create a new curve, ensured that all attributes were copied to the new curve
* Fixed a bug in the integrate command that ignored the upper and lower limits
* Fixed a bug in the subsample command. Also, enhanced it so the user needs to specify a curve(s)

Enhancements
~~~~~~~~~~~~

* Added the dupx command
* Added the xindex command
* Added the append~curves command
* Added the average command
* Added the max command
* Added the min command
* Added the get~attributes command
* Added the stats command
* Removed unused 'Plot Name' column in the Menu dialog
* Piecewise constant plots are now supported
* The font size and font color can be changed only for the legend
* The getx and gety command now returns all the x~ and y~values for a given y~ or x~value respectively
* The .pdvrc file supports more default values (fontsize, lnwidth)
* Improved the syntax of the legend command
* Added the bkgcolor command that allows the use to change the background color of the plot, window, or both
* The menu and curve regex option is now done over the curve name and filename
* Both the x- and y-column can be specified when reading in an ULTRA text file



2.3
---

Bug Fixes
~~~~~~~~~

* Fixed the **getx** and **gety** commands to work with horizontal/vertical lines.
* Fixed the sign issue with subtracting curves.

Enhancements
~~~~~~~~~~~~

* Added window to display the contents of the **list** command. You can also delete curves from this window.
* Allow figure size specification in **create_plot**.
* Enhanced the **list** command to use a regex for filtering the list.
* Display the **menu** command contents in a popup window. Can also plot and delete curves from the popup window.
* Enhanced the read command to filter the curves as they are read in. Also, the user can specify the number of matched curves to read in.
* Added the **getlabel** command that prints the given curve's label.
* Added the **getnumpoints** command that prints the given curve's number of points.
* Added the **kill** command that deletes specified entries from the menu.



2.2
---

Bug Fixes
~~~~~~~~~

* Fixed the interpolation function for two curves
* Got alias command working again by adding back the removed import new line

Enhancements
~~~~~~~~~~~~

* Added convolvef math command that performs a convolution of two curves using the Fast Fourier transform method
* Added Fast Fourier Transform math command
* Added disp and dispx commands for displaying the curves y~ and x~values
* Enhanced the read command to optionally use a regular expression to filter the curves that are read in
* Created a method in the PyDV Python interface to filter curves using a regular expression
* Added handlelength command to control the length of lines in the legend
* Allow namewidth to be changed from the .pdvrc file
* Added documentation for the .pdrc file format



2.1
---

Bug Fixes
~~~~~~~~~

* Addition operator dropping down into the Python interpreter after execution
* Error when reading ULTRA files with an extra data item
* Geometry command not working

Enhancements
~~~~~~~~~~~~

* Changing plot properties from the GUI are now persistent
* Added fontcolor command
* Added guilims command
* Added linemarker command
* Added markeredgecolor command
* Added markerfacecolor command
* Added drawstyle command


Changes for PyDV Developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Created compile and test scripts
* Integrated compile and test scripts with Bamboo



2.0
---

Bug Fixes
~~~~~~~~~

* Plot limits auto adjust fixed
* Cleaned up a lot of typos and errors in the help documentation

Enhancements
~~~~~~~~~~~~

* Legend can be moved by clicking on it and dragging with the mouse
* Added style command that allows user to change the style of the plot
* Added showstyles command that lists all the available styles
* Added sinhx math command
* Added support for reading .csv files
* Created a Python interface (pydvpy) for PyDV functionality
* Turned Latex off by default
* Changed backend to Qt4Agg
* New 'About' dialogs with links to the PyDV confluence page, developer contact information and copyright details


Changes for PyDV Developers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Setup a documentation framework with SPHINX
* Added an application icon
