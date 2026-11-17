# Grade Room — subject-based student assessment management

A local teacher workspace with separate **Overview**, **Students**, **Subjects**, **Gradebook** and **Class insights** sections. Teachers define the assessment structure for each subject. A shared C++ engine calculates the saved weighted totals and letter grades.

## Run

Requires Python 3.10+ and a C++11 compiler (`g++` or `clang++`) on PATH.

```sh
python web.py
```

Open http://127.0.0.1:8767/ . The launcher compiles `grade_engine` (`grade_engine.exe` on Windows) when missing or stale. Use `--port 8772` for another loopback port. No Python packages or frontend build are needed.

## A complete teaching workflow

1. Open **Subjects** and add a subject name/code. Add one to eight assessment components, each with a name, raw maximum mark and percentage weight. Weights must total exactly 100% for that subject.
2. Open **Students** and create a learner using name, unique positive ID and optional class/group. The next step opens subject assessment entry. The roster supports up to 30 students and the workspace up to 12 subjects.
3. Open **Gradebook**, choose a subject and enter marks. A test scored out of 50 can contribute 20%, independently of its raw maximum. Every learner has separate marks per subject.
4. Review weighted totals, letter grades, filters, subject averages/pass rates, assessment coverage and distributions in **Class insights**. Missing assessments remain ungraded and are excluded from averages and pass/fail counts.
5. Export all subjects and their raw marks, maxima, weights and final results to CSV.

Example: Quiz 40/50 at 20% + Mid-semester 80/100 at 30% + Exam 80/100 at 50% gives 16 + 24 + 40 = **80/100, A**.

The default General assessment starts with Quiz /20 at 20%, Mid-semester /30 at 30% and Exam /50 at 50%. It is editable like other subjects. Quick templates provide either three assessments or Coursework 40% / Exam 60%; teachers can change the allocations and add assessments such as projects or practical work.

Editing weights recalculates existing completed results. Lowering a maximum below an existing mark is rejected. Adding a component makes previous records ungraded until its mark is entered. Removing a subject requires confirmation, removes that subject's marks and leaves the roster intact. At least one subject is retained.

## Grade thresholds

| Total | Grade |
| --- | --- |
| 80–100 | A |
| 70–<80 | B |
| 60–<70 | C |
| 50–<60 | D |
| <50 | F |

A–D are passing. These thresholds stay consistent across subjects. The app calculates assessment grades, not credit-weighted GPA.

## Original terminal app

The pointer/parallel-array terminal program remains available with its original Quiz /20 + Mid-semester /30 + Exam /50 model.

```sh
g++ -std=c++11 -Wall -Wextra -pedantic main.cpp -o grades
./grades
```

On Windows, build with `-o grades.exe` and run `./grades.exe`. Both the terminal program and the weighted web engine share the letter-grade rules in `grade_rules.h`. The engine supports both legacy numeric rows and validated weighted assessment rows.

## Verify

```sh
g++ -std=c++11 -Wall -Wextra -pedantic main.cpp -o grades
python -m unittest -v
node --check static/app.js
node --check static/ui.js
node test_motion.cjs
```

`GRADE_APP` can select an alternate terminal executable for CLI tests. Tests cover existing terminal behavior, C++ protocol boundaries, subject weights, independent raw maxima, missing marks, edits/recalculation, validation before mutation, student edits preserving assessments, deletion, CSV, isolated sessions and local HTTP/file boundaries.

## Runtime and limits

Each browser has a separate in-memory class. Sessions expire after eight hours and restart resets the class. The server binds to loopback, validates Host/Origin and serves an explicit local asset whitelist. It is a portfolio teaching tool, without hosted accounts or durable class storage.

The UI includes custom SVG icons and a vendored Anime.js 4.5.0 runtime with its MIT license. Motion is optional and respects reduced-motion settings. Fonts, icons and animations load locally; no CDN is required.
