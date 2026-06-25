.. _getting_started:

Getting started
===============

This section gives a tutorial introduction to PyDV. A sample session is run which highlights the basic PyDV commands.

.. note::
   In PyDV commands, spaces are used to delimit items on the input line. More precisely items on a command line are
   either space delimited, are preceded by a left parenthesis if the first item in a list, or terminated by a right
   parenthesis if the last item in a list. In interactive mode, ranges of curve numbers or data-id’s may be indicated using colon notation.
   For example, a:f or 5:9

Run PyDV (LLNL)
---------------

.. code::

   /usr/gapps/pydv/pdv     # Current version

   /usr/gapps/pydv/3.0/pdv # Version specific

Run PyDV With a Command File
----------------------------

.. code::

   /usr/gapps/pydv/pdv -i <command-file>

Run PyDV In Column Format Mode
------------------------------

.. code::

   /usr/gapps/pydv/pdv -gnu <file.gnu>


Create a curve consisting of a straight line y=x over the interval (0,6.28).
----------------------------------------------------------------------------

.. code::

   [PyDV]: span 0 6.28

Print a list of curves on the display.
--------------------------------------

.. code::

   [PyDV]: lst

Take the sine of curve A
------------------------

.. code::

   [PyDV]: sin a

Take the product of curves A and B
----------------------------------

.. code::

   [PyDV]: * A B

Write all of the curves to an ASCII file
----------------------------------------

.. code::

   [PyDV]: save foo.txt a:c

Read file foo.txt
-----------------

.. code::

   [PyDV]: rd foo.txt

Display curves in all open files
--------------------------------

.. code::

   [PyDV]: menu

Display curves from the menu on
-------------------------------

.. code::

   [PyDV]: cur 1 3

Shift curve A by one unit to the right
--------------------------------------

.. code::

   [PyDV]: dx A 1

Delete curve A from the display
-------------------------------

.. code::

   [PyDV]: del A

Exit PyDV
---------

.. code::

   [PyDV]: quit
