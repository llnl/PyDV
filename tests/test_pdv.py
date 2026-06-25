import os
import sys
from contextlib import redirect_stdout

import numpy as np

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PYDV_DIR = os.path.dirname(TEST_DIR)

sys.path.append(os.path.join(PYDV_DIR, "pydv"))
import pdv  # noqa: E402


def test_read():
    main = pdv.Command()
    main.app = pdv.QApplication([])
    main.plotter = pdv.pdvplot.Plotter(main)
    main.do_readsina(os.path.join(TEST_DIR, "testSinaData.json"))
    assert len(main.curvelist) == 2

    curve_1 = main.curvelist[0]
    curve_2 = main.curvelist[1]
    assert curve_1.name == "darkness vs cycle (lux_cycle_series)"
    assert curve_2.name == "lightness vs cycle (lux_cycle_series)"

    # darkness
    np.testing.assert_allclose(curve_1.y, np.array([0, 1, 4, 9, 16]))
    # lightness
    np.testing.assert_allclose(curve_2.y, np.array([5, 4, 2.5, 2.1, 2.0]))

    # do_xlabelwidth
    main.do_xlabelwidth("")
    assert main.xlabelwidth == 10

    main.do_xlabelwidth("15")
    assert main.xlabelwidth == 15

    # do_ylabelwidth
    main.do_ylabelwidth("")
    assert main.ylabelwidth == 10

    main.do_ylabelwidth("15")
    assert main.ylabelwidth == 15

    # do_filenamewidth
    main.do_filenamewidth("")
    assert main.filenamewidth == 30

    main.do_filenamewidth("35")
    assert main.filenamewidth == 35

    # do_recordidwidth
    main.do_recordidwidth("")
    assert main.recordidwidth == 10

    main.do_recordidwidth("15")
    assert main.recordidwidth == 15

    # read space-delimited txt
    main.do_read(os.path.join(TEST_DIR, "testData.txt"))
    assert len(main.curvelist) == 4

    curve_3 = main.curvelist[2]
    curve_4 = main.curvelist[3]
    assert curve_3.name == "darkness"
    assert curve_4.name == "lightness"

    # darkness
    np.testing.assert_allclose(curve_3.y, np.array([0, 1, 4, 9, 16]))
    # lightness
    np.testing.assert_allclose(curve_4.y, np.array([5, 4, 2.5, 2.1, 2.0]))

    # read tab-delimited ult
    main.do_read(os.path.join(TEST_DIR, "testData.ult"))
    assert len(main.curvelist) == 6

    curve_5 = main.curvelist[4]
    curve_6 = main.curvelist[5]
    assert curve_5.name == "darkness"
    assert curve_6.name == "lightness"

    # darkness
    np.testing.assert_allclose(curve_5.y, np.array([0, 1, 4, 9, 16]))
    # lightness
    np.testing.assert_allclose(curve_6.y, np.array([5, 4, 2.5, 2.1, 2.0]))

    # create and save gaussian curves
    main.do_gaussian("1 1 5")
    main.do_gaussian("1 1 1")
    main.do_save(os.path.join(TEST_DIR, "testSave.txt") + " a:b")

    # read saved gaussian curves
    main.do_read(os.path.join(TEST_DIR, "testSave.txt"))
    assert len(main.curvelist) == 8

    curve_7 = main.curvelist[6]
    curve_8 = main.curvelist[7]
    assert curve_7.name == "Gaussian (a: 1.0 w: 1.0 c: 5.0)"
    assert curve_8.name == "Gaussian (a: 1.0 w: 1.0 c: 1.0)"


def test_getx_getymax_getymin():

    main = pdv.Command()
    if not pdv.QApplication.instance():
        main.app = pdv.QApplication([])
    else:
        main.app = pdv.QApplication.instance()

    main.plotter = pdv.pdvplot.Plotter(main)

    main.curvelist = []
    main.plotlist = []

    main.do_read(os.path.join(TEST_DIR, "curve.ult"))
    main.do_menu("")
    main.do_curve("1")
    assert len(main.curvelist) == 1

    curve_1 = main.curvelist[0]

    assert curve_1.name == "y vs x"

    # ########## getx ##########
    # 17.5
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getx("a 17.5")

    pydv_output = ["\n", "Curve A\n", "    x: 5.078947e+01    y: 1.750000e+01\n", "\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # 296.35
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getx("a 296.35")

    pydv_output = [
        "\n",
        "Curve A\n",
        "    x: 2.719865e+02    y: 2.963500e+02\n",
        "\n",
        "    x: 3.296143e+02    y: 2.963500e+02\n",
        "\n",
        "    x: 4.703857e+02    y: 2.963500e+02\n",
        "\n",
        "    x: 5.296143e+02    y: 2.963500e+02\n",
        "\n",
        "\n",
    ]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # out of range low
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getx("a 1")

    pydv_output = ["Error: y-value out of range\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # out of range high
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getx("a 10000")

    pydv_output = ["Error: y-value out of range\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # ########## getymax ##########
    # no points in between
    # c.x, 62.3, 65.2, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymax("a 62.3 65.2")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 6.520000e+01    y: 1.544000e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # one point in between uneven
    # c.x, 62.3, c.x, 104.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymax("a 62.3 104.23")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 7.000000e+01    y: 2.000000e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # c.x, 104.23, c.x, 251.56, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymax("a 104.23 251.56")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 2.515600e+02    y: 2.207720e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # one point in between even
    # c.x, 350.23, c.x, 450.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymax("a 350.23 449.77")

    pydv_output = [
        " \n",
        "A Curve y vs x\n",
        "    x: 3.502300e+02    y: 2.241950e+02\n",
        "\n",
        "    x: 4.497700e+02    y: 2.241950e+02\n",
        "\n",
    ]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # multiple points in between
    # c.x, 62.3, c.x, ..., c.x, 375.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymax("a 62.3 375.23")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 3.000000e+02    y: 4.000000e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # ########## getymin ##########
    # no points in between
    # c.x, 62.3, 65.2, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymin("a 62.3 65.2")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 6.230000e+01    y: 1.268500e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # one point in between uneven
    # c.x, 62.3, c.x, 104.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymin("a 62.3 104.23")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 6.230000e+01    y: 1.268500e+02\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # c.x, 104.23, c.x, 251.56, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymin("a 104.23 251.56")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 2.000000e+02    y: 3.000000e+01\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # one point in between even
    # c.x, 450.23, c.x, 550.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymin("a 450.23 549.77")

    pydv_output = [
        " \n",
        "A Curve y vs x\n",
        "    x: 4.502300e+02    y: 2.258050e+02\n",
        "\n",
        "    x: 5.497700e+02    y: 2.258050e+02\n",
        "\n",
    ]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output

    # multiple points in between
    # c.x, 62.3, c.x, ..., c.x, 375.23, c.x
    with open("out.txt", "w") as f:
        with redirect_stdout(f):
            main.do_getymin("a 62.3 375.23")

    pydv_output = [" \n", "A Curve y vs x\n", "    x: 2.000000e+02    y: 3.000000e+01\n", "\n"]

    with open("out.txt", "r") as f:
        contents = f.readlines()
        assert contents == pydv_output
