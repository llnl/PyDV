import os
import shutil
import subprocess

import imageio
import pytest
from skimage import color, io
from skimage.metrics import structural_similarity

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PYDV_DIR = os.path.dirname(TEST_DIR)
BASELINE_DIR = os.path.join(TEST_DIR, "baseline")

# ------------------------ #
# --- Prepare the data --- #
# ------------------------ #

# The output directory will store the generated images to compare against the baseline
output_dir = os.path.join(TEST_DIR, "output")
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.makedirs(output_dir)

diff_dir = os.path.join(TEST_DIR, "diff")
if os.path.exists(diff_dir):
    shutil.rmtree(diff_dir)
os.makedirs(diff_dir)

# Generate a list of commands for PyDV to process. Between each command, we will
# place an "image" statement, which will cause PyDV to save the current state of
# the plot.
commands = [
    # 1
    f"""
    debug on
    rd {os.path.join(TEST_DIR, "testData.txt")}
    cur 1 2
    """,
    # 2
    """
    legend off
    """,
    # 3
    """
    erase
    """,
    # 4
    """
    cur 1 2
    L1 a b
    """,
    # 5
    """
    L2 a b  3.0 5.5
    """,
    # 6
    """
    del c d
    """,
    # 7
    """
    color a blue
    """,
    # 8
    """
    color a red
    """,
    # 9
    """
    add a b
    """,
    # 10
    """
    annot FOO 3 7
    """,
    # 11
    """
    convolc a b
    """,
    # 12
    """
    del d
    copy a
    """,
    # 13
    """
    cos a
    """,
    # 14
    """
    del d
    dashstyle b [2, 2, 4, 2]
    """,
    # 15
    """
    dataid off
    """,
    # 16
    """
    dataid on
    delannot 1
    """,
    # 17
    """
    derivative a
    """,
    # 18
    """
    del d
    dy b 2.5
    dx b 3
    """,
    # 19
    """
    dx b -3
    divide c a
    """,
    # 20
    """
    del d
    divx c 2
    divy c 2
    """,
    # 21
    """
    dom 0 10
    """,
    # 22
    """
    dom de
    """,
    # 23
    """
    exp a
    """,
    # 24
    """
    log a
    """,
    # 25
    """
    grid off
    """,
    # 26
    """
    grid on
    integrate a
    """,
    # 27
    """
    del d
    linespoints a on
    marker a . 20
    """,
    # 28
    """
    lnwidth b 10
    """,
    # 29
    """
    lnwidth b 3
    makecurve (1 2 3) (5 2 3)
    """,
    # 30
    """
    del d
    mx c 2
    """,
    # 31
    """
    my a 3
    """,
    # 32
    """
    recip a
    """,
    # 33
    """
    scatter b on
    """,
    # 34
    """
    scatter b off
    cos b
    """,
    # 35
    """
    acos b
    """,
    # 36
    """
    cosh b
    """,
    # 37
    """
    acosh b
    """,
    # 38
    """
    sin c
    """,
    # 39
    """
    asin c
    """,
    # 40
    """
    sinh c
    """,
    # 41
    """
    asinh c
    """,
    # 42
    """
    sqr b
    """,
    # 43
    """
    sqrt b
    """,
    # 44
    """
    sqrx b
    """,
    # 45
    """
    sqrtx b
    """,
    # 46
    """
    tan a
    """,
    # 47
    """
    atan a
    """,
    # 48
    """
    tanh a
    """,
    # 49
    """
    atanh a
    """,
    # 50
    """
    a - b
    """,
    # 51
    """
    del d
    b ** 2
    """,
    # 52
    """
    c / b
    """,
    # 53
    """
    smooth d
    """,
    # 54
    """
    dy d -3
    abs d
    """,
    # 55
    """
    erase
    legend on
    gaussian 1 1 5
    """,
    # 56
    """
    exp A
    """,
    # 57
    """
    log A
    """,
    # 58
    """
    expx A
    """,
    # 59
    """
    logx A
    """,
    # 60
    """
    exp A
    sin A
    log A
    """,
    # 61
    f"""
    readsina {os.path.join(TEST_DIR, "testSinaData.json")}
    readsina {os.path.join(TEST_DIR, "testSinaData2.json")}
    cur 3 4 5 6
    labelcurve on
    """,
    # 62
    """
    labelcurve off
    labelrecordids on
    """,
    # 63
    f"""
    labelrecordids off
    read {os.path.join(TEST_DIR, "testData.ult")}
    cur 7 8
    group slashes 0
    """,
    # 64
    """
    group off
    labelfilenames on
    """,
    # 65
    """
    labelfilenames off
    """,
    # 66
    f"""
    erase
    read {os.path.join(TEST_DIR, "testDataLog.ult")}
    cur 8 9 10
    """,
    # 67
    """
    yls on
    xls on
    """,
    # 68
    f"""
    erase
    kill all
    xls off
    yls off
    read {os.path.join(TEST_DIR, "step.ult")}
    cur 1 2
    + a a
    - a a
    * a a
    / a a

    + a b
    + b a
    - a b
    - b a
    * a b
    * b a
    / a b
    / b a
    """,
    # 69
    f"""
    erase
    kill all
    readsina {os.path.join(TEST_DIR, "sina_with_library_data.json")}
    cur 1 2 3
    """,
    # 70
    f"""
    erase
    kill all
    custom {os.path.join(TEST_DIR, "my_custom_functions.py")}
    mycustomfunction
    myothercustomfunction
    cur 1 2 3 4 5 6 7 8
    + a a
    + a b
    + a e
    + a g
    """,
    # 71
    f"""
    erase
    kill all
    read {os.path.join(TEST_DIR, "single_point.ult")}
    read {os.path.join(TEST_DIR, "step.ult")}
    cur 1 2 3
    """,
    # 72
    """
    xlabel testingx
    xlabel bold
    ylabel testingy italic
    """,
    # 73
    """
    xlabel testingxnew bold italic
    ylabel italic bold
    """,
    # 74
    """
    theta -3 4 6
    """,
    # 75
    """
    axis off
    """,
    # 76
    """
    axis on
    """,
    # 77
    """
    erase
    kill all
    span 1 20
    cos a
    normalize a
    """,
    # 78
    """
    erase
    kill all
    span 1 20
    span 1 20
    sin a
    cos b
    hypot a b
    """,
    # 79
    """
    legend hide a:c
    """,
    # 80
    """
    legend show a:c
    """,
    # 81
    """
    legend showid a:c
    """,
    # 82
    """
    legend hideid a:b
    """,
    # 83
    f"""
    erase
    kill all
    read {os.path.join(TEST_DIR, "curve.ult")}
    read {os.path.join(TEST_DIR, "curve_x_tick_data.ult")}
    read {os.path.join(TEST_DIR, "curve_x_tick_data2.ult")}
    cur 1:7
    marker b:g circle 10
    legend on ul
    """,
    # 84
    """
    hide a
    """,
    # 85
    """
    hide c d
    """,
    # 86
    """
    show c d
    """,
    # 87
    """
    del c d
    """,
    # 88
    """
    show a
    """,
    # 89
    """
    hide b e
    """,
    # 90
    """
    del f g
    """,
    # 91
    f"""
    erase
    kill all
    read {os.path.join(TEST_DIR, "diff_formats.txt")}
    cur 1:17
    xmax a:z 1
    """,
]

commands_file = os.path.join(output_dir, "pydv_commands")

with open(commands_file, "w") as fp:
    for i, command in enumerate(commands):
        image_file = os.path.join(output_dir, f"test_image_{i + 1:02d}")
        fp.write(command)
        fp.write(f"\nimage {image_file} png\n\n")
    fp.write("\nquit")

# Execute PyDv
exec_command = f"python {os.path.join(PYDV_DIR, 'pydv', 'pdv_launcher.py')} -i {commands_file}"
process = subprocess.Popen(exec_command.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print("Output:\n", output.decode())
print("Error:\n", error)


@pytest.mark.parametrize("i", list(range(1, len(commands) + 1)))
def test_image(i):
    test_image = f"test_image_{i:02d}.png"
    # Load images and convert to grayscale
    baseline = color.rgb2gray(imageio.v2.imread(os.path.join(BASELINE_DIR, test_image))[:, :, :3])
    output = color.rgb2gray(imageio.v2.imread(os.path.join(output_dir, test_image))[:, :, :3])

    # Image 64 contains file paths
    if i == 64:
        score_to_beat = 0.85
    else:
        score_to_beat = 0.90
    (score, diff) = structural_similarity(baseline, output, full=True, data_range=1.0)
    print("Image Similarity {}: {:.4f}%".format(i, score * 100))

    io.imsave(os.path.join(diff_dir, test_image), (diff * 255).astype("uint8"))

    assert score > score_to_beat
