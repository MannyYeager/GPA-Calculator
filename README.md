# Student Grade Management System

A student grade manager with a working web interface and the original C++ terminal program. Record assessment scores, assign letter grades, and review class performance. Both interfaces share the C++ rules in `grade_rules.h`; the web app calls a compiled C++ engine for totals, grades, and statistics.

The repository retains its original name, **GPA-Calculator**, but the current program calculates **assessment totals and letter grades**, not credit-weighted GPA. There are no course credits or grade-point scales.

## Open the web app

Requires **Python 3.11+** and a C++11 compiler (`g++` or `clang++`) available on PATH. No Python packages, frontend build, API keys, or database are needed.

```sh
git clone https://github.com/MannyYeager/GPA-Calculator.git
cd GPA-Calculator
python web.py
```

Open **http://127.0.0.1:8767/**. The launcher builds `grade_engine` (`grade_engine.exe` on Windows) if it is missing or its source changed. Use `--port 8772` if the default port is occupied.

Choose **Load sample class** to explore three fictional students. Add or edit scores through **Add student** and the row's **Edit** button. Totals, grade distribution, class average, highest/lowest scores, and pass rate update from the C++ engine after each change. Search by name/ID, filter Pass or Fail, and use **Export CSV** for a class report. Removal and replacement of the current class require confirmation.

Each browser session has its own class of up to 30 students. Refreshes retain the cookie session for up to eight hours; restarting the server discards all classes. The server is bound to loopback only. It does not share records with an independently running terminal process and is intended for local demonstrations.

## Build and run the original terminal app

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
python -m unittest -v
```

The terminal executable does not need Python. Python supplies the optional web server and tests; grading remains in C++. Tests exercise full terminal reports/search/statistics, grade boundaries, invalid input, duplicates, capacity, record replacement, EOF, the C++ web protocol, web CRUD, per-browser session isolation, and CSV export.

| File | Purpose |
| --- | --- |
| `main.cpp` | Original pointer/parallel-array terminal program |
| `grade_rules.h` | Shared assessment total and letter-grade rules |
| `grade_engine.cpp` | Numeric stdin/JSON stdout bridge for the browser app |
| `web.py`, `local_web.py` | Python web adapter and loopback server |
| `static/` | Interactive classroom dashboard and student forms |
| `test_cli.py`, `test_web.py` | Terminal, C++ engine, and HTTP tests |

Records are discarded when the application exits. There is no file storage, course management, or GPA calculation. Long names are shortened in the class table to preserve alignment; the search view shows the full name.
