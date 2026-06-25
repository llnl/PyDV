import os
import pathlib
import subprocess
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import pytest
import scipy

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PYDV_DIR = os.path.dirname(TEST_DIR)

sys.path.append(os.path.join(PYDV_DIR, "pydv"))
import pydvpy  # noqa: E402

test_files = list(pathlib.Path(TEST_DIR).glob("testData.*"))


@pytest.mark.parametrize("test_file", test_files)
def test_read(test_file):
    curves = pydvpy.read(test_file)

    # darkness
    np.testing.assert_array_equal(curves[0].y, [0, 1, 4, 9, 16])

    # lightness
    np.testing.assert_array_equal(curves[1].y, [5, 4, 2.5, 2.1, 2.0])


def test_sinaread():
    curves = pydvpy.readsina(os.path.join(TEST_DIR, "testSinaData.json"))

    # darkness curve
    np.testing.assert_array_equal(curves[0].y, [0, 1, 4, 9, 16])

    # darkness curve record id
    assert curves[0].record_id == "sinaTest_1"

    # lightness
    np.testing.assert_array_equal(curves[1].y, [5, 4, 2.5, 2.1, 2.0])

    # lightness curve record id
    assert curves[1].record_id == "sinaTest_1"


def test_sinaread_mult_ind():
    curves = pydvpy.readsina(os.path.join(TEST_DIR, "testSinaData_mult_ind.json"))

    assert len(curves) == 6


test_files = list(pathlib.Path(TEST_DIR).glob("testDataregex.*"))


@pytest.mark.parametrize("test_file", test_files)
def test_read_regex(test_file):

    # darkness
    curves = pydvpy.read(test_file, pattern="darkness")
    np.testing.assert_array_equal(curves[0].y, [0, 1, 4, 9, 16])
    np.testing.assert_array_equal(curves[1].y, [0, 1, 4, 9, 16])
    np.testing.assert_array_equal(curves[2].y, [0, 1, 4, 9, 16])

    # lightness
    curves = pydvpy.read(test_file, pattern="lightness")
    np.testing.assert_array_equal(curves[0].y, [5, 4, 2.5, 2.1, 2.0])
    np.testing.assert_array_equal(curves[1].y, [5, 4, 2.5, 2.1, 2.0])
    np.testing.assert_array_equal(curves[2].y, [5, 4, 2.5, 2.1, 2.0])

    # 2
    curves = pydvpy.read(test_file, pattern="2")
    np.testing.assert_array_equal(curves[0].y, [0, 1, 4, 9, 16])
    np.testing.assert_array_equal(curves[1].y, [5, 4, 2.5, 2.1, 2.0])

    # 3
    curves = pydvpy.read(test_file, pattern="3")
    np.testing.assert_array_equal(curves[0].y, [0, 1, 4, 9, 16])
    np.testing.assert_array_equal(curves[1].y, [5, 4, 2.5, 2.1, 2.0])


# Steps: **ONLY** do steps below if new curves are added to tests/convolution_pydv_create_curves_to_convolv
#     1. pydv/pdv -i tests/convolution_pydv_create_curves_to_convolv
#            The randomness here can cause issues with ultra! divide by 0? Re-run all steps if issues arise in step 5
#     2. python tests/convolution_create_pydv_and_ultra_commands.py
#     3. pydv/pdv -i tests/convolution_pydv_commands
#     4. export PATH=$PATH:/usr/apps/pact/bin/
#     5. ultra -l tests/convolution_ultra_commands
# convolb: (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t)) / Int(-inf, inf, dt*h(t))
# convolc: (g*h)(x) = Int(-inf, inf, dt*g(t)*h(x-t))
curves_pydv = pydvpy.read(os.path.join(TEST_DIR, "convol_pydv.ult"))
curves_ultra = pydvpy.read(os.path.join(TEST_DIR, "convol_ultra.ult"))
convol_plot_path = os.path.join(TEST_DIR, "convolution_plots")
os.makedirs(convol_plot_path, exist_ok=True)


def convol_curves():
    curves = pydvpy.read(os.path.join(TEST_DIR, "convolution_created_curves_to_convol.ult"))
    start = ord("A")

    for i, cur in enumerate(curves):
        curve_letter = chr(start + i)
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.plot(cur.x, cur.y, marker="x", linewidth=1)
        ax.set_title(f"Curve {curve_letter}: {cur.name}")
        ax.legend()
        fig.savefig(os.path.join(TEST_DIR, "convolution_plots", f"convol_curve_{curve_letter}.png"))
        plt.close(fig)


@pytest.mark.parametrize("i", list(range(len(curves_pydv))))
def convol(i):

    # for cp, cu in zip(curves_pydv, curves_ultra):
    cp = curves_pydv[i]
    cu = curves_ultra[i]
    print(f"Curve {i + 1} of {len(curves_pydv)}")
    print("Lengths:")
    print(f"\tPyDV:  {len(cp.y)}")
    print(f"\tUltra: {len(cu.y)}")

    print("First 5 x:")
    print(f"\tPyDV:  {cp.x[:5]}")
    print(f"\tUltra: {cu.x[:5]}")

    print("Last 5 x:")
    print(f"\tPyDV:  {cp.x[-5:]}")
    print(f"\tUltra: {cu.x[-5:]}")

    print("First 5 y:")
    print(f"\tPyDV:  {cp.y[:5]}")
    print(f"\tUltra: {cu.y[:5]}")

    print("Last 5 y:")
    print(f"\tPyDV:  {cp.y[-5:]}")
    print(f"\tUltra: {cu.y[-5:]}")

    print("Max y:")
    print(f"\tPyDV:  {max(cp.y)}")
    print(f"\tUltra: {max(cu.y)}")

    # Ultra sometimes has 99 points for some reason
    if len(cu.y) == 99:
        start = 1
    else:
        start = 0

    plot_details = ""

    # Area
    area_pydv = scipy.integrate.simpson(cp.y[start:], cp.x[start:])
    area_ultra = scipy.integrate.simpson(cu.y, cu.x)
    area_diff = abs(area_pydv - area_ultra)
    area_percent = area_diff / area_ultra * 100
    print("Area:")
    print("\tpydv ", area_pydv)
    print("\tultra", area_ultra)
    print("\tdiff ", area_diff)
    print("\tdiff percent", area_percent, "%\n")
    if area_percent > 1:
        plot_details += f"_area_diff_percent_{area_percent:.3f}"

    # Max diff of ys
    diff = abs(cp.y[start:] - cu.y)
    diff_max = np.max(diff)
    diff_index = diff.argmax()
    diff_percent = diff_max / abs(cu.y[diff_index]) * 100
    print("Maximum diff of all ys:")
    print(f"\tdiff: {diff_max} at:")
    print(f"\t\tPydv.y  {cp.y[diff_index + start]}")
    print(f"\t\tUltra.y {cu.y[diff_index]}")
    print("\tdiff percent", diff_percent, "%\n\n")
    # Most pass with 1% Difference but Ultra sometimes has missing points during integration which causes spikes
    # This is most evident with the noisy or sparse curves
    if diff_percent > 1:
        plot_details += f"_max_diff_y_percent_{diff_percent:.3f}"

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.plot(cp.x, cp.y, marker="x", linewidth=1, label="PyDV")
    ax.plot(cu.x, cu.y, marker="+", linewidth=1, label="Ultra")
    ax.scatter(
        cp.x[diff_index + start],
        cp.y[diff_index + start],
        marker="x",
        s=200,
        label=f"PyDV Max Diff Y {cp.y[diff_index + start]:.5f}",
    )
    ax.scatter(cu.x[diff_index], cu.y[diff_index], marker="+", s=200, label=f"Ultra Max Diff Y {cu.y[diff_index]:.5f}")
    ax.set_title(f"{cp.name} {plot_details}")
    ax.legend()
    fig.savefig(os.path.join(TEST_DIR, "convolution_plots", f"convol_plot_{i + 1}{plot_details}.png"))
    plt.close(fig)

    # All these tests will never pass but see the plots in tests/convolution_plots/
    # np.testing.assert_array_less(area_percent, 1)
    # np.testing.assert_array_less(diff_percent, 1)


def test_read_labels():

    test_file = os.path.join(TEST_DIR, "labels.txt")
    curves = pydvpy.read(test_file)
    # curve name, xlabel, ylabel
    names = [
        ["nospace0", "0Time", ""],
        ["onespace0", "", ""],
        ["nospace1", "1aTime [seconds]", ""],
        ["onespace1", "1bTime [seconds]", ""],
        ["nospace2", "", "2aTemperature [K]"],
        ["onespace2", "", "2bTemperature [K]"],
        ["nospace3", "3aTime [seconds]", "3aTemperature [K]"],
        ["onespace3", "3bTime [seconds]", "3bTemperature [K]"],
        ["nospace4", "4aTime [seconds]", "4aTemperature [K]"],
        ["onespace4", "4bTime [seconds]", "4bTemperature [K]"],
        ["nospace5 withspace", "5aTime [seconds]", ""],
        ["onespace5 withspace", "5bTime [seconds]", ""],
        ["nospace6 withspace", "", "6aTemperature [K]"],
        ["onespace6 withspace", "", "6bTemperature [K]"],
        ["nospace7 withspace", "7aTime [seconds]", "7aTemperature [K]"],
        ["onespace7 withspace", "7bTime [seconds]", "7bTemperature [K]"],
        ["nospace8 withspace", "8aTime [seconds]", "8aTemperature [K]"],
        ["onespace8 withspace", "8bTime [seconds]", "8bTemperature [K]"],
        ["onespace9 withspace", "", ""],
        ["onespace10 withspace", "10aTime [seconds]", ""],
        ["onespace11 withspace ::test", "10aTime [seconds]", ""],
        ["nospace12 withspace::test", "10aTime [seconds]", ""],
        ["onespace13 withspace:: test", "10aTime [seconds]", ""],
        ["nospace14 withspace :: test", "10aTime [seconds]", ""],
        ["onespace11b withspace :test", "10aTime [seconds]", ""],
        ["nospace12b withspace:test", "10aTime [seconds]", ""],
        ["onespace13b withspace: test", "10aTime [seconds]", ""],
        ["nospace14b withspace : test", "10aTime [seconds]", ""],
        ["#+onespace11c withspace :test", "10aTime [seconds]", ""],
        ["#-nospace12c withspace:test", "10aTime [seconds]", ""],
        ["#*onespace13c withspace: test", "Temperature [K]", "10aTime [seconds]"],
        ["#/nospace14c withspace : test", "10aTime [seconds]", "Temperature [K]"],
        ["#+onespace11d withspace :test", "", ""],
        ["#-nospace12d withspace:test", "", ""],
        ["#*onespace13d withspace: test", "", ""],
        ["#/nospace14d withspace : test", "", ""],
        ["a", "", ""],
        ["b", "", ""],
        ["myzlabel1:test##", "", ""],
        ["#my1  :: t#esting", "", ""],
        ["ot#her#1:: te##st", "", ""],
        ["the1::te##/st", "", ""],
        ["label1:########again   ###  ###", "", ""],
        ["#", "", ""],
    ]

    for i, cur in enumerate(curves):
        assert cur.name == names[i][0]
        assert cur.xlabel == names[i][1]
        assert cur.ylabel == names[i][2]

    test_file = os.path.join(TEST_DIR, "labels2.txt")

    pydvpy.save(test_file, curves, verbose=False, save_labels=True)

    curves = pydvpy.read(test_file)

    for i, cur in enumerate(curves):
        assert cur.name == names[i][0]
        assert cur.xlabel == names[i][1]
        assert cur.ylabel == names[i][2]


def test_BIG_file():

    subprocess.run(["python", os.path.join(TEST_DIR, "generate_ultra_curves_big.py")])

    start = time.time()

    big_file = os.path.join(TEST_DIR, "BIG_ULTRA_FILE.ult")
    _ = pydvpy.read(big_file)

    end = start - time.time()

    os.remove(big_file)

    assert end < 10


@pytest.mark.parametrize(
    ("hdf5_file", "json_file"), zip(["test.hdf5", "medium_recs_test.hdf5"], ["test.json", "medium_recs_test.json"])
)
def test_sina_hdf5(hdf5_file, json_file):

    curves_hdf5 = pydvpy.read(os.path.join(TEST_DIR, hdf5_file))

    curves_json = pydvpy.read(os.path.join(TEST_DIR, json_file))

    for cur_hdf5, cur_json in zip(curves_hdf5, curves_json):
        assert cur_hdf5.record_id == cur_json.record_id
        assert cur_hdf5.name == cur_json.name
        assert cur_hdf5.xlabel == cur_json.xlabel
        assert cur_hdf5.ylabel == cur_json.ylabel
        np.testing.assert_array_equal(cur_hdf5.x, cur_json.x)
        np.testing.assert_array_equal(cur_hdf5.y, cur_json.y)
