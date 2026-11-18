"""Compile main.cpp first, then run: python test_cli.py."""
from pathlib import Path
import subprocess
import os
import unittest

ROOT = Path(__file__).parent
APP = Path(os.environ.get('GRADE_APP', str(ROOT / ("grades.exe" if os.name == 'nt' else "grades"))))


def run_program(text):
    result = subprocess.run([str(APP.resolve())], input=text, text=True, capture_output=True, timeout=5)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout


def enter_total(total):
    marks = []
    for maximum in (10, 30, 50, 10):
        mark = min(maximum, total)
        marks.append(str(mark))
        total -= mark
    return '1\nReader\n1\n' + '\n'.join(marks) + '\nn\n'


class GradeCliTests(unittest.TestCase):
    def test_report_statistics_and_search(self):
        output = run_program('1\nAma Mensah\n101\n8\n25\n42\n10\ny\nKojo Owusu\n102\n4\n10\n20\n5\nn\n3\n4\n5\n101\n6\n')
        for expected in ('85.0', '39.0', '62.0', 'Students Passed: 1', 'Failed: 1', 'Grade    : A', 'Ama Mensah'):
            self.assertIn(expected, output)

    def test_nonnumeric_ranges_trailing_junk_and_duplicate_ids(self):
        output = run_program('oops\n1x\n1\n\nAma\n1.5\nabc\n101\nwords\n11\n8x\n8\nnan\n31\n25\ninf\n51\n42\nnan\n11\n-1\n10\ny\nKojo\n101\n102\n0\n0\n0\n0\nn\n5\nabc\n101\n6\n')
        self.assertGreaterEqual(output.count('Invalid input'), 12)
        self.assertIn('already exists', output)
        self.assertIn('Grade    : A', output)

    def test_all_grade_boundaries_and_fractional_scores(self):
        cases = [(0,'F'), (39.9999,'F'), (40,'D'), (44.9999,'D'), (45,'C-'),
                 (49.9999,'C-'), (50,'C'), (54.9999,'C'), (55,'C+'), (59.9999,'C+'),
                 (60,'B-'), (64.9999,'B-'), (65,'B'), (69.9999,'B'), (70,'B+'),
                 (74.9999,'B+'), (75,'A-'), (79.5,'A-'), (79.9999,'A-'), (80,'A'), (100,'A')]
        for total, grade in cases:
            with self.subTest(total=total):
                output = run_program(enter_total(total) + '5\n1\n6\n')
                self.assertIn(f'Grade    : {grade}\n', output)
                self.assertIn('Remark   : ' + ('Fail' if grade == 'F' else 'Pass'), output)
        self.assertIn('Total    : 79.9999 / 100', run_program(enter_total(79.9999)+'5\n1\n6\n'))

    def test_explicit_and_automatic_computation_preserve_attendance(self):
        for prefix in ('', '2\n', '2\n2\n'):
            with self.subTest(prefix=prefix):
                output = run_program(enter_total(100)+prefix+'3\n4\n5\n1\n6\n')
                self.assertIn('Attendance  : 10.0 / 10', output)
                self.assertIn('Total    : 100.0 / 100', output)
                self.assertIn('Grade    : A\n', output)
                self.assertIn('Students Passed: 1', output)

    def test_record_replacement_can_be_cancelled(self):
        output = run_program('1\nAma\n1\n10\n30\n50\n10\nn\n1\nn\n5\n1\n6\n')
        self.assertIn('Name     : Ama', output)

    def test_capacity_limit(self):
        records = '1\n' + ''.join(f'Reader {i}\n{i}\n10\n30\n50\n10\n' + ('y\n' if i < 30 else '') for i in range(1, 31))
        output = run_program(records+'2\n4\n6\n')
        self.assertIn('30 student record(s)', output)
        self.assertIn('Students Passed: 30', output)

    def test_eof_exits_instead_of_looping(self):
        self.assertIn('Input ended. Goodbye!', run_program('1\nAma\n'))


if __name__ == '__main__':
    unittest.main()
