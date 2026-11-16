// Numeric stdin/stdout bridge for the local web app. Names stay in Python.
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <set>
#include <cmath>
#include "grade_rules.h"

struct ScoreRow { int id; float quiz, mid, exam, total; char grade; };

int main() {
    std::vector<ScoreRow> rows;
    std::set<int> ids;
    std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream input(line);
        ScoreRow row;
        char extra;
        if (rows.size() >= 30 || !(input >> row.id >> row.quiz >> row.mid >> row.exam)
            || (input >> extra) || row.id <= 0 || !ids.insert(row.id).second
            || !std::isfinite(row.quiz) || !std::isfinite(row.mid) || !std::isfinite(row.exam)
            || row.quiz < 0 || row.quiz > 20 || row.mid < 0 || row.mid > 30
            || row.exam < 0 || row.exam > 50) {
            std::cerr << "Invalid assessment record.\n";
            return 1;
        }
        row.total = assessmentTotal(row.quiz, row.mid, row.exam);
        row.grade = assignGrade(row.total);
        rows.push_back(row);
    }
    float sum = 0;
    int passed = 0;
    std::size_t high = 0, low = 0;
    std::cout << std::setprecision(9) << "{\"records\":[";
    for (std::size_t i = 0; i < rows.size(); ++i) {
        const ScoreRow& row = rows[i];
        sum += row.total;
        if (row.grade != 'F') ++passed;
        if (row.total > rows[high].total) high = i;
        if (row.total < rows[low].total) low = i;
        if (i) std::cout << ',';
        std::cout << "{\"id\":" << row.id << ",\"total\":" << row.total
                  << ",\"grade\":\"" << row.grade << "\",\"remark\":\""
                  << (row.grade == 'F' ? "Fail" : "Pass") << "\"}";
    }
    std::cout << "],\"average\":" << (rows.empty() ? 0 : sum / rows.size())
              << ",\"passed\":" << passed << ",\"failed\":" << rows.size() - passed
              << ",\"highest_id\":" << (rows.empty() ? 0 : rows[high].id)
              << ",\"lowest_id\":" << (rows.empty() ? 0 : rows[low].id) << "}\n";
    return 0;
}
