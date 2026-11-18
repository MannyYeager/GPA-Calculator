// Numeric stdin/stdout bridge for the local web app. Names stay in Python.
#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>
#include <set>
#include <cmath>
#include "grade_rules.h"

struct ScoreRow { int id; double quiz, mid, exam, att, total; char grade; };

int main() {
    std::vector<ScoreRow> rows;
    std::set<int> ids;
    std::string line;
    while (std::getline(std::cin, line)) {
        std::istringstream input(line);
        ScoreRow row;
        char extra;
        bool weighted = !line.empty() && line[0] == 'W';
        if (weighted) {
            char marker; int count;
            double weights = 0, total = 0;
            if (!(input >> marker >> row.id >> count) || count < 1 || count > 8) return 1;
            for (int i = 0; i < count; ++i) {
                double score, maximum, weight;
                if (!(input >> score >> maximum >> weight) || !std::isfinite(score)
                    || !std::isfinite(maximum) || !std::isfinite(weight) || maximum <= 0
                    || maximum > 1000000 || score < 0 || score > maximum || weight <= 0 || weight > 100) return 1;
                weights += weight;
                total += score / maximum * weight;
            }
            if (std::abs(weights - 100) > 0.000001) return 1;
            // Remove arithmetic noise at grade boundaries, without rounding to display precision.
            row.total = std::round(total * 100000000.0) / 100000000.0;
        } else if (!(input >> row.id >> row.quiz >> row.mid >> row.exam)) return 1;
        if (rows.size() >= 30
            || (input >> extra) || row.id <= 0 || !ids.insert(row.id).second
            || (!weighted && (!std::isfinite(row.quiz) || !std::isfinite(row.mid) || !std::isfinite(row.exam)
            || row.quiz < 0 || row.quiz > 20 || row.mid < 0 || row.mid > 30
            || row.exam < 0 || row.exam > 50))) {
            std::cerr << "Invalid assessment record.\n";
            return 1;
        }
        if (!weighted) row.total = assessmentTotal(row.quiz, row.mid, row.exam, row.att);
        row.grade = assignGrade(row.total);
        rows.push_back(row);
    }
    double sum = 0;
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
