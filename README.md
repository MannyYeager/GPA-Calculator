# Student Grade Management System

A C++ terminal program for recording a class's assessment scores, assigning letter grades, and reviewing class performance. It keeps the original parallel-array and pointer-based design as a practical exercise in functions, input validation, and basic statistics.

The repository retains its original name, **GPA-Calculator**, but the current program calculates **assessment totals and letter grades**, not credit-weighted GPA. There are no course credits or grade-point scales.

## Build and run

Requires a C++11-compatible compiler, such as GCC/MinGW or Clang. No external libraries are needed.

### Windows with MinGW

```powershell
git clone https://github.com/MannyYeager/GPA-Calculator.git
cd GPA-Calculator
g++ -std=c++11 -Wall -Wextra -pedantic main.cpp -o grades.exe
.\grades.exe
```

### Linux or macOS

```sh
git clone https://github.com/MannyYeager/GPA-Calculator.git
cd GPA-Calculator
g++ -std=c++11 -Wall -Wextra -pedantic main.cpp -o grades
./grades
```

Use `clang++` in place of `g++` if that is your installed compiler.

## What it does

- Stores up to **30 student records** in memory.
- Accepts full names and unique positive integer student IDs.
- Validates numeric input, rejects trailing text and out-of-range scores, and handles EOF cleanly.
- Computes total marks, letter grades, and pass/fail remarks.
- Displays a class report, highest/lowest score, average, and pass/fail counts.
- Searches for a student by ID; computes grades automatically when required.
- Confirms before replacing an existing class's records.

### Assessment model

| Component | Allowed score |
| --- | ---: |
| Quiz | 0–20 |
| Mid-semester | 0–30 |
| Exam | 0–50 |
| Total | 0–100 |

| Total | Grade | Remark |
| --- | --- | --- |
| 80–100 | A | Pass |
| 70–less than 80 | B | Pass |
| 60–less than 70 | C | Pass |
| 50–less than 60 | D | Pass |
| Less than 50 | F | Fail |

These are the project's existing grading rules, not a claim about a particular institution's policy. Decimal assessment scores are supported.

## Demonstration

Choose `1` to enter records:

```text
Name: Ama Mensah    ID: 101    Quiz: 18    Mid-Sem: 25    Exam: 42
Name: Kojo Owusu    ID: 102    Quiz: 10    Mid-Sem: 10    Exam: 20
```

Answer `y` to add the second student, then `n`. Choose `3` for the report or `4` for statistics:

```text
Ama Mensah: 85.0 / 100, A, Pass
Kojo Owusu: 40.0 / 100, F, Fail
Highest Score: 85.0
Lowest Score: 40.0
Class Average: 62.5
Students Passed: 1    Failed: 1
```

Choose `5` and enter `101` to inspect Ama's full record. Choose `6` to exit.

## Verify

After compiling as above, run the terminal regression suite with **Python 3.11+**:

```sh
python test_cli.py -v
```

Python is used only for tests, not for the application. Tests exercise full reports/search/statistics, grade boundaries, invalid numeric input, duplicate IDs, capacity, record replacement, and EOF.

Records are discarded when the application exits. There is no file storage, course management, or GPA calculation. Long names are shortened in the class table to preserve alignment; the search view shows the full name.
