#ifndef GRADE_RULES_H
#define GRADE_RULES_H

#include <array>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <string>

// One scale drives the terminal, engine results and browser distribution labels.
struct GradeBand { double minimum; const char* grade; };
inline const std::array<GradeBand, 10>& gradeScale() {
    static const std::array<GradeBand, 10> scale = {{{80,"A"}, {75,"A-"},
        {70,"B+"}, {65,"B"}, {60,"B-"}, {55,"C+"}, {50,"C"},
        {45,"C-"}, {40,"D"}, {0,"F"}}};
    return scale;
}

inline std::string assignGrade(double total) {
    for (const GradeBand& band : gradeScale())
        if (total >= band.minimum) return band.grade;
    return "F";
}

inline double normalizeTotal(double total) {
    return std::round(total * 100000000.0) / 100000000.0;
}

inline double assessmentTotal(double quiz, double midSem, double exam, double attendance) {
    return normalizeTotal(quiz + midSem + exam + attendance);
}

inline std::string formatScore(double score) {
    std::ostringstream text;
    text << std::fixed << std::setprecision(8) << score;
    std::string value = text.str();
    while (value.back() == '0') value.pop_back();
    if (value.back() == '.') value += '0';
    return value;
}

#endif
