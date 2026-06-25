# PyDV

A 1D graphics and data analysis tool, heavily based on the ULTRA plotting tool.

## PyDV Importable Interface Module ###
You can now call most of PyDV's functionality from within a Python script. Below is an example of how to do this.

### Most Current

```
import sys
sys.path.append("/usr/gapps/pydv/current")
import pydvpy

curves = list()
curves.append(pydvpy.span(1,10,6))
pydvpy.save('myFile.txt', curves)
```

### PyPi or WEAVE Environment

```
from pydv import pydvpy

curves = list()
curves.append(pydvpy.span(1,10,6))
pydvpy.save('myFile.txt', curves)
```

# Documentation

[PyDV Users Manual](https://pydv.readthedocs.io/en/latest/) [![Documentation Status](https://readthedocs.org/projects/pydv/badge/?version=latest)](https://pydv.readthedocs.io/en/latest/?badge=latest)

# License

PyDV is distributed under the terms of the [BSD-3 License](LICENSE)

All new contributions must be made under the [BSD-3 License](LICENSE)

See [LICENSE](LICENSE) for details.

LLNL-CODE-507071
