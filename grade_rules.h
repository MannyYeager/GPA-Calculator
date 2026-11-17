#ifndef GRADE_RULES_H
#define GRADE_RULES_H

// Shared by the original terminal app and the browser interface's C++ engine.
inline char assignGrade(double total) {
    if (total >= 80) return 'A';
    if (total >= 70) return 'B';
    if (total >= 60) return 'C';
    if (total >= 50) return 'D';
    return 'F';
}

inline float assessmentTotal(float quiz, float midSem, float exam) {
    return quiz + midSem + exam;
}

#endif
