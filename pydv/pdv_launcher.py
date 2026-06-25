import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# HPC Import
try:
    import pdv

    pdv.Command().main()

# Package Import
except ImportError:
    import pydv.pdv

    pydv.pdv.Command().main()
