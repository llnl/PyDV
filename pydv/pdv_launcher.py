"""Launcher for PyDV CLI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# HPC Import
try:
    import pdv

    pdv.Command().main()

# Package Import
except ImportError:
    import pydv.pdv

    pydv.pdv.Command().main()
