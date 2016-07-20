import os
from lib.perfBaseTest import PerfBaseTest


class TestSikuli(PerfBaseTest):
    def test_chrome_pilot_run(self):
        self.sikuli_script_path = os.getenv("SIKULI_SCRIPT_PATH")
        if self.sikuli_script_path.endswith(os.sep):
            self.env.test_method_name = self.sikuli_script_path.split(os.sep)[-2].split(".")[0]
        else:
            self.env.test_method_name = self.sikuli_script_path.split(os.sep)[-1].split(".")[0]
        self.sikuli_status = self.sikuli.run_sikulix_cmd(self.sikuli_script_path)
