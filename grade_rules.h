#ifndef GRADE_RULES_H
#define GRADE_RULES_H

// Shared by the original terminal app and the browser interface's C++ engine.
inline char assignGrade(double total) {
    if (total >= 80) return 'A';
    if (total >= 75 && total <= 79) return 'A-';
    if (total >= 70 && total <= 74) return 'B+';
    if (total >= 65 && total <= 69) return 'B';
    if (total >= 60 && total <= 64) return 'B-';
    if (total >= 55 && total <= 59) return 'C+';
    if (total >= 50 && total <= 54) return 'C';
    if (total >= 45 && total <= 49) return 'C-';
    if (total >= 40 && total <= 44) return 'D';
    return 'F';
}

inline float assessmentTotal(float quiz, float midSem, float exam) {
    return quiz + midSem + exam;
}

#endif
