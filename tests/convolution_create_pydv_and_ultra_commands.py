import os
import sys
from itertools import combinations

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PYDV_DIR = os.path.dirname(TEST_DIR)

sys.path.append(os.path.join(PYDV_DIR, "pydv"))
import pydvpy  # noqa: E402

curves_to_convol = pydvpy.read(os.path.join(TEST_DIR, "convolution_created_curves_to_convol.ult"))

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
    with open(f"tests/convolution_{sw}_commands", "w") as file1:
        file1.write("rd tests/convolution_created_curves_to_convol.ult\n")
        file1.write(f"cur 1:{total_curves}\n")

        for i in list(combinations(curve_letters, 2)):
            # print (i)
            file1.write(f"convolc {i[0]} {i[1]}\n")
            file1.write(f"convolc {i[1]} {i[0]}\n")
            file1.write(f"convolb {i[0]} {i[1]}\n")
            file1.write(f"convolb {i[1]} {i[0]}\n")

        if sw == "pydv":
            file1.write(f"save tests/convol_pydv.ult {new_letter}:@{total_curves + total_convols}\n")
        elif sw == "ultra":
            file1.write('system "rm tests/convol_ultra.ult"\n')
            file1.write(f"save ascii tests/convol_ultra.ult {new_letter}:@{total_curves + total_convols}\n")
