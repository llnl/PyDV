import os


def do_mycustomfunction(self, line):

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


def do_myothercustomfunction(self, line):

    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    self.do_read(os.path.join(TEST_DIR, "../tests", "step.ult"))
    self.do_readsina(os.path.join(TEST_DIR, "../tests", "testSinaData2.json"))
