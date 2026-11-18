#include <iostream>
#include <iomanip>
#include <string>
#include <sstream>
#include <limits>
#include <cmath>
#include <stdexcept>
#include "grade_rules.h"
using namespace std;

const int MAX_STUDENTS = 30;

string readText(const string& prompt) {
    string line;
    while (true) {
        cout << prompt;
        if (!getline(cin, line)) throw runtime_error("Input ended. Goodbye!");
        const size_t first = line.find_first_not_of(" \t\r");
        if (first != string::npos)
            return line.substr(first, line.find_last_not_of(" \t\r") - first + 1);
        cout << "Please enter a nonempty value.\n";
    }
}

template <typename T>
T readNumber(const string& prompt, T minimum, T maximum) {
    while (true) {
        string line = readText(prompt);
        istringstream input(line);
        T value;
        char extra;
        if ((input >> value) && !(input >> extra) && isfinite(static_cast<double>(value))
            && value >= minimum && value <= maximum) return value;
        cout << "Invalid input. Enter a number from " << minimum << " to " << maximum << ".\n";
    }
}

void inputStudents(string* names, int* ids, float* quiz,
                   float* midSem, float* exam, float* attendance, int* count) {
    char addMore;
    *count = 0;

    cout << "\n==========================================\n";
    cout << "         ENTER STUDENT RECORDS\n";
    cout << "==========================================\n";

    do {
        if (*count >= MAX_STUDENTS) {
            cout << "\nMaximum capacity of " << MAX_STUDENTS
                 << " students reached.\n";
            break;
        }

        int idx = *count;
        cout << "\n--- Student " << (idx + 1) << " ---\n";

        names[idx] = readText("Enter Name: ");
        while (true) {
            ids[idx] = readNumber<int>("Enter Student ID: ", 1, numeric_limits<int>::max());
            bool duplicate = false;
            for (int i = 0; i < idx; ++i) {
                if (ids[i] == ids[idx]) duplicate = true;
            }
            if (!duplicate) break;
            cout << "That student ID already exists. Use a unique ID.\n";
        }
        quiz[idx] = readNumber<float>("Enter Quiz Score (0 - 10): ", 0, 10);
        midSem[idx] = readNumber<float>("Enter Mid-Sem Score (0 - 30): ", 0, 30);
        exam[idx] = readNumber<float>("Enter Exam Score (0 - 50): ", 0, 50);
        attendance[idx] = readNumber<float>("Enter Attendance Score (0 - 10): ", 0, 10); 

        (*count)++;

        if (*count < MAX_STUDENTS) {
            string answer;
            do {
                answer = readText("Add another student? (y/n): ");
                if (answer != "y" && answer != "Y" && answer != "n" && answer != "N")
                    cout << "Choose y or n.\n";
            } while (answer != "y" && answer != "Y" && answer != "n" && answer != "N");
            addMore = answer[0];
        }

    } while ((addMore == 'y' || addMore == 'Y') && *count < MAX_STUDENTS);

    cout << "\n" << *count << " student record(s) entered successfully.\n";
}

void computeGrades(float* quiz, float* midSem, float* exam, float* attendance,
                   float* totals, char* grades, string* remarks,
                   int count) {
    // Use pointer arithmetic to traverse all arrays
    for (int i = 0; i < count; i++) {
        *(totals + i) = assessmentTotal(*(quiz + i), *(midSem + i), *(exam + i), *(attendance + i));
        *(grades + i) = assignGrade(*(totals + i));
        *(remarks + i) = (*(grades + i) == 'F') ? "Fail" : "Pass";
    }
    cout << "\nGrades computed and assigned successfully!\n";
}

void displayReport(string* names, int* ids, float* totals,
                   char* grades, string* remarks, int count) {
    if (count == 0) {
        cout << "\nNo student records found. "
             << "Please enter records first.\n";
        return;
    }

    cout << "\n==========================================\n";
    cout << "           FULL CLASS REPORT\n";
    cout << "==========================================\n";
    cout << left
         << setw(10) << "ID"
         << setw(22) << "NAME"
         << setw(8)  << "TOTAL"
         << setw(7)  << "GRADE"
         << setw(7)  << "REMARK"
         << "\n";
    cout << "------------------------------------------\n";

    // Traverse using pointer arithmetic (pointer use #2)
    for (int i = 0; i < count; i++) {
        cout << left
             << setw(10) << *(ids     + i)
             << setw(22) << (names[i].size() > 20 ? names[i].substr(0, 17) + "..." : names[i])
             << setw(8)  << fixed << setprecision(1) << *(totals + i)
             << setw(7)  << *(grades  + i)
             << setw(7)  << *(remarks + i)
             << "\n";
    }
    cout << "==========================================\n";
}

void findHighestLowest(float* totals, int count,
                       int* highIdx, int* lowIdx) {
    *highIdx = 0;
    *lowIdx  = 0;
    for (int i = 1; i < count; i++) {
        if (totals[i] > totals[*highIdx]) *highIdx = i;
        if (totals[i] < totals[*lowIdx])  *lowIdx  = i;
    }
}

void displayStatistics(string* names, float* totals,
                       char* grades, int count) {
    if (count == 0) {
        cout << "\nNo records available. "
             << "Please enter student records first.\n";
        return;
    }

    // Use pass-by-pointer to retrieve highest and lowest indices
    int highIdx, lowIdx;
    findHighestLowest(totals, count, &highIdx, &lowIdx);

    float sum      = 0;
    int   passCount = 0;
    int   failCount = 0;

    for (int i = 0; i < count; i++) {
        sum += totals[i];
        if (grades[i] != 'F') passCount++;
        else                   failCount++;
    }
    float average = sum / count;

    cout << "\n==========================================\n";
    cout << "           CLASS STATISTICS\n";
    cout << "------------------------------------------\n";
    cout << "  Highest Score  : " << fixed << setprecision(1)
         << totals[highIdx] << "  (" << names[highIdx] << ")\n";
    cout << "  Lowest Score   : " << fixed << setprecision(1)
         << totals[lowIdx]  << "  (" << names[lowIdx]  << ")\n";
    cout << "  Class Average  : " << fixed << setprecision(1)
         << average << "\n";
    cout << "  Students Passed: " << passCount
         << "    Failed: " << failCount << "\n";
    cout << "==========================================\n";
}

int searchByID(int* ids, int count, int id) {
    // Traverse using pointer arithmetic
    for (int i = 0; i < count; i++) {
        if (*(ids + i) == id) return i;
    }
    return -1;
}

void displayMenu() {
    cout << "\n==========================================\n";
    cout << "   STUDENT GRADE MANAGEMENT SYSTEM\n";
    cout << "==========================================\n";
    cout << "  1. Enter Student Records\n";
    cout << "  2. Compute and Assign Grades\n";
    cout << "  3. Display Full Class Report\n";
    cout << "  4. Display Class Statistics\n";
    cout << "  5. Search Student by ID\n";
    cout << "  6. Exit\n";
    cout << "------------------------------------------\n";
    cout << "Enter your choice: ";
}

int run() {
    // --- Parallel arrays for student data ---
    string names[MAX_STUDENTS];
    int    ids[MAX_STUDENTS];
    float  quiz[MAX_STUDENTS];
    float  attendance[MAX_STUDENTS];
    float  midSem[MAX_STUDENTS];
    float  exam[MAX_STUDENTS];
    float  totals[MAX_STUDENTS];
    char   grades[MAX_STUDENTS];
    string remarks[MAX_STUDENTS];

    int  studentCount   = 0;   // Initialised before the input loop
    bool gradesComputed = false;
    int  choice;

    do {
        displayMenu();

        choice = readNumber<int>("", 1, 6);

        switch (choice) {

            case 1:
                if (studentCount > 0) {
                    string confirm = readText("Replace all current records? (y/n): ");
                    if (confirm != "y" && confirm != "Y") break;
                }
                inputStudents(names, ids, quiz, midSem, exam, attendance,
                              &studentCount);
                gradesComputed = false;   // Reset flag on new input
                break;

            case 2:
                if (studentCount == 0) {
                    cout << "\nNo records found. "
                         << "Please enter student records first.\n";
                } else {
                    computeGrades(quiz, midSem, exam, totals, attendance,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                break;

            case 3:
                // Auto-compute if needed before displaying
                if (studentCount > 0 && !gradesComputed) {
                    cout << "\nGrades not yet computed. "
                         << "Computing automatically...\n";
                    computeGrades(quiz, midSem, exam, attendance, totals,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                displayReport(names, ids, totals, grades,
                              remarks, studentCount);
                break;

            case 4:
                if (studentCount > 0 && !gradesComputed) {
                    cout << "\nGrades not yet computed. "
                         << "Computing automatically...\n";
                    computeGrades(quiz, midSem, exam, attendance, totals,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                displayStatistics(names, totals, grades, studentCount);
                break;

            case 5: {
                if (studentCount == 0) {
                    cout << "\nNo records found. "
                         << "Please enter student records first.\n";
                    break;
                }
                if (!gradesComputed) {
                    cout << "\nGrades not yet computed. "
                         << "Computing automatically...\n";
                    computeGrades(quiz, midSem, exam, attendance, totals,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                int searchID;
                searchID = readNumber<int>("Enter Student ID to search: ", 1, numeric_limits<int>::max());

                int idx = searchByID(ids, studentCount, searchID);

                if (idx == -1) {
                    cout << "\nStudent with ID " << searchID
                         << " was not found.\n";
                } else {
                    cout << "\n--- Student Record ---\n";
                    cout << "Name     : " << names[idx]  << "\n";
                    cout << "ID       : " << ids[idx]    << "\n";
                    cout << fixed << setprecision(1);
                    cout << "Quiz     : " << quiz[idx]   << " / 10\n";
                    cout << "Attendance  : " << attendance[idx] << " / 10\n";
                    cout << "Mid-Sem  : " << midSem[idx] << " / 30\n";
                    cout << "Exam     : " << exam[idx]   << " / 50\n";
                    cout << "Total    : " << totals[idx] << " / 100\n";
                    cout << "Grade    : " << grades[idx] << "\n";
                    cout << "Remark   : " << remarks[idx] << "\n";
                }
                break;
            }

            case 6:
                cout << "\nThank you for using the Student Grade "
                     << "Management System.\nGoodbye!\n\n";
                break;
        }

    } while (choice != 6);

    return 0;
}

int main() {
    try {
        return run();
    } catch (const runtime_error& error) {
        cout << "\n" << error.what() << "\n";
        return 0;
    }
}
