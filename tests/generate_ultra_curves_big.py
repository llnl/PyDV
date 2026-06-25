import os
import sys
import time
from multiprocessing import Pool, cpu_count

import numpy
import scipy.special

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PYDV_DIR = os.path.dirname(TEST_DIR)

sys.path.append(os.path.join(PYDV_DIR, "pydv"))
import pydvpy  # noqa: E402

_list_of_funcs_with_domain = [
    ("sin", numpy.sin, 0, 2 * numpy.pi),
    ("cos", numpy.cos, 0, 2 * numpy.pi),
    ("tan", numpy.tan, -0.9999 * numpy.pi / 2, 0.9999 * numpy.pi / 2),
    ("arcsin", numpy.arcsin, -0.9999, 0.9999),
    ("arccos", numpy.arccos, -0.9999, 0.9999),
    ("arctan", numpy.arctan, -10_000, 10_000),
    ("sinh", numpy.sinh, -100.0, 100.0),
    ("cosh", numpy.cosh, -100.0, 100.0),
    ("tanh", numpy.tanh, -10.0, 10.0),
    ("arcsinh", numpy.arcsinh, -10_000, 10_000),
    ("arccosh", numpy.arccosh, 1.0, 10_000),
    ("arctanh", numpy.arctanh, -0.9999, 0.9999),
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

_ufile = os.path.join(TEST_DIR, "BIG_ULTRA_FILE.ult")


def create_curve_perproc(input_tuple):
    num_points = 2_000_000
    name, func, xmin, xmax = input_tuple
    print(f"Creating {name}")
    yvals = numpy.linspace(xmin, xmax, num_points)
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
            "took %0.3f seconds to save %d ULTRA curves to an ULTRA file = %s."
            % (time.perf_counter() - time0, len(curvelist), _ufile)
        )
