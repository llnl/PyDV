"""Some example custom functions."""

from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent


def do_mycustomfunction(self, line):  # noqa: ARG001
    """Create different curves."""
    for i in range(4):
        x = [i, i + 1, i + 2]
        y = x
        name = f"TestCurve_{i}"
        fname = f"TestFilename_{i}"
        xlabel = f"TestXlabel_{i}"
        ylabel = f"TestYlabel_{i}"
        title = f"TestTitle_{i}"
        record_id = f"TestRecordID_{i}"
        c = pydvpy.makecurve(  # noqa: F821
            x=x,
            y=y,
            name=name,
            filename=fname,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            record_id=record_id,
        )
        self.curvelist.append(c)


def do_myothercustomfunction(self, line):  # noqa: ARG001
    """Automatically read different files."""
    self.do_read(str(TEST_DIR / "../tests" / "step.ult"))
    self.do_readsina(str(TEST_DIR / "../tests" / "testSinaData2.json"))
