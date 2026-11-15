"""Compile main.cpp first, then run: python test_cli.py"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).parent
APP = ROOT / ("grades.exe" if (ROOT / "grades.exe").exists() else "grades")


def run_program(text):
    result = subprocess.run([str(APP.resolve())], input=text, text=True, capture_output=True, timeout=5)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout


class GradeCliTests(unittest.TestCase):
    def test_report_statistics_and_search(self):
        output = run_program("1\nAma Mensah\n101\n18\n25\n42\ny\nKojo Owusu\n102\n10\n10\n20\nn\n3\n4\n5\n101\n6\n")
        for expected in ("85.0", "40.0", "62.5", "Students Passed: 1", "Failed: 1", "Grade    : A", "Ama Mensah"):
            self.assertIn(expected, output)

    def test_nonnumeric_ranges_trailing_junk_and_duplicate_ids(self):
        output = run_program("oops\n1x\n1\n\nAma\n1.5\nabc\n101\nwords\n21\n18x\n18\nnan\n31\n25\ninf\n51\n42\ny\nKojo\n101\n102\n0\n0\n0\nn\n5\nabc\n101\n6\n")
        self.assertGreaterEqual(output.count("Invalid input"), 10)
        self.assertIn("already exists", output)
        self.assertIn("Grade    : A", output)

    def test_grade_boundaries(self):
        for total, grade in [(0,'F'),(49,'F'),(50,'D'),(60,'C'),(70,'B'),(80,'A'),(100,'A')]:
            quiz = min(20, total)
            mid = min(30, total - quiz)
            exam = total - quiz - mid
            with self.subTest(total=total):
                output = run_program(f"1\nReader\n1\n{quiz}\n{mid}\n{exam}\nn\n5\n1\n6\n")
                self.assertIn(f"Grade    : {grade}", output)

    def test_record_replacement_can_be_cancelled(self):
        output = run_program("1\nAma\n1\n20\n30\n50\nn\n1\nn\n5\n1\n6\n")
        self.assertIn("Name     : Ama", output)

    def test_capacity_limit(self):
        records = "1\n" + "".join(f"Reader {i}\n{i}\n20\n30\n50\n" + ("y\n" if i < 30 else "") for i in range(1, 31))
        output = run_program(records + "4\n6\n")
        self.assertIn("30 student record(s)", output)
        self.assertIn("Students Passed: 30", output)

    def test_eof_exits_instead_of_looping(self):
        self.assertIn("Input ended. Goodbye!", run_program("1\nAma\n"))


if __name__ == "__main__":
    unittest.main()
