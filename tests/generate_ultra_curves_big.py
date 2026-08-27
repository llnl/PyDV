"""Generate large ultra curves for new multiprocessing reading function update."""

import time
from multiprocessing import Pool, cpu_count
from pathlib import Path

import numpy as np
import scipy.special

from pydv import pydvpy

TEST_DIR = Path(__file__).resolve().parent

_list_of_funcs_with_domain = [
    ("sin", np.sin, 0, 2 * np.pi),
    ("cos", np.cos, 0, 2 * np.pi),
    ("tan", np.tan, -0.9999 * np.pi / 2, 0.9999 * np.pi / 2),
    ("arcsin", np.arcsin, -0.9999, 0.9999),
    ("arccos", np.arccos, -0.9999, 0.9999),
    ("arctan", np.arctan, -10_000, 10_000),
    ("sinh", np.sinh, -100.0, 100.0),
    ("cosh", np.cosh, -100.0, 100.0),
    ("tanh", np.tanh, -10.0, 10.0),
    ("arcsinh", np.arcsinh, -10_000, 10_000),
    ("arccosh", np.arccosh, 1.0, 10_000),
    ("arctanh", np.arctanh, -0.9999, 0.9999),
    ("erf", scipy.special.erf, -3.0, 3.0),
    ("erfc", scipy.special.erfc, 0.0, 5.0),
    ("gamma", scipy.special.gamma, 0.1, 6.0),
    ("fresnel", scipy.special.fresnel, 0.0, 6.0),
    ("dawsn", scipy.special.dawsn, 0.0, 100.0),
    ("j0", scipy.special.j0, 0.0, 5.0),
    ("j1", scipy.special.j1, 0.0, 5.0),
    ("y0", scipy.special.y0, 0.0, 5.0),
    ("y1", scipy.special.y1, 0.0, 5.0),
]

_ufile = TEST_DIR / "BIG_ULTRA_FILE.ult"


def create_curve_perproc(input_tuple):
    """Create a large curve."""
    num_points = 2_000_000
    name, func, xmin, xmax = input_tuple
    print(f"Creating {name}")
    yvals = np.linspace(xmin, xmax, num_points)
    xvals = func(yvals)
    if isinstance(xvals, tuple):
        xvals = xvals[0]
    print(f"Done creating {name}")

    return pydvpy.curve.Curve(x=xvals, y=yvals, name=name, filename=_ufile, xlabel="time", ylabel=name)


if __name__ == "__main__":
    time0 = time.perf_counter()
    print(f"CPU COUNT {cpu_count()}")

    with Pool(processes=cpu_count()) as pool:
        curvelist = list(pool.map(create_curve_perproc, _list_of_funcs_with_domain))
        pydvpy.save(_ufile, curvelist, save_labels=True)
        print(
            f"took {time.perf_counter() - time0:0.3f} seconds to save {len(curvelist)} ULTRA curves ",
            f"to an ULTRA file = {_ufile}.",
        )
