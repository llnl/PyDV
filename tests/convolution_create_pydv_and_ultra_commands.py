"""Generate convolution command file for PyDV and Ultra."""

from itertools import combinations
from pathlib import Path

from pydv import pydvpy

TEST_DIR = Path(__file__).resolve().parent

curves_to_convol = pydvpy.read(TEST_DIR / "convolution_created_curves_to_convol.ult")

total_curves = len(curves_to_convol)

start = ord("a")
print(total_curves)

curve_letters = [chr(start + i) for i in range(total_curves)]
print(curve_letters)
new_letter = chr(start + total_curves)
print(new_letter)  # if more than 26 curves will need to start @27
total_combos = len(list(combinations(curve_letters, 2)))
print(total_combos)
total_convols = total_combos * 4
print(total_convols)

for sw in ["pydv", "ultra"]:
    conv_cmds = TEST_DIR / f"convolution_{sw}_commands"
    with conv_cmds.open("w") as file1:
        file1.write("rd tests/convolution_created_curves_to_convol.ult\n")
        file1.write(f"cur 1:{total_curves}\n")

        for i in list(combinations(curve_letters, 2)):
            file1.write(f"convolc {i[0]} {i[1]}\n")
            file1.write(f"convolc {i[1]} {i[0]}\n")
            file1.write(f"convolb {i[0]} {i[1]}\n")
            file1.write(f"convolb {i[1]} {i[0]}\n")

        if sw == "pydv":
            file1.write(f"save tests/convol_pydv.ult {new_letter}:@{total_curves + total_convols}\n")
        elif sw == "ultra":
            file1.write('system "rm tests/convol_ultra.ult"\n')
            file1.write(f"save ascii tests/convol_ultra.ult {new_letter}:@{total_curves + total_convols}\n")
