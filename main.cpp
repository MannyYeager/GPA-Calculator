#include <iostream>
#include <iomanip>
#include <string>
using namespace std;

const int MAX_STUDENTS = 30;

char assignGrade(float total) {
    if (total >= 80) return 'A';
    else if (total >= 70) return 'B';
    else if (total >= 60) return 'C';
    else if (total >= 50) return 'D';
    else return 'F';
}

void inputStudents(string* names, int* ids, float* quiz,
                   float* midSem, float* exam, int* count) {
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

        cout << "Enter Name     : ";
        cin.ignore();
        getline(cin, names[idx]);

        // Validate student ID (must be a positive integer)
        cout << "Enter Student ID : ";
        while (!(cin >> ids[idx]) || ids[idx] <= 0) {
            cin.clear();
            cin.ignore(1000, '\n');
            cout << "Invalid ID. Please enter a positive integer: ";
        }

        // Validate quiz score (0 – 20)
        do {
            cout << "Enter Quiz Score    (0 - 20) : ";
            cin >> quiz[idx];
            if (quiz[idx] < 0 || quiz[idx] > 20)
                cout << "  Invalid! Score must be between 0 and 20.\n";
        } while (quiz[idx] < 0 || quiz[idx] > 20);

        // Validate mid-semester score (0 – 30)
        do {
            cout << "Enter Mid-Sem Score (0–30) : ";
            cin >> midSem[idx];
            if (midSem[idx] < 0 || midSem[idx] > 30)
                cout << "  Invalid! Score must be between 0 and 30.\n";
        } while (midSem[idx] < 0 || midSem[idx] > 30);

        // Validate exam score (0 – 50)
        do {
            cout << "Enter Exam Score    (0–50) : ";
            cin >> exam[idx];
            if (exam[idx] < 0 || exam[idx] > 50)
                cout << "  Invalid! Score must be between 0 and 50.\n";
        } while (exam[idx] < 0 || exam[idx] > 50);

        (*count)++;

        if (*count < MAX_STUDENTS) {
            cout << "\nAdd another student? (y/n) : ";
            cin >> addMore;
        }

    } while ((addMore == 'y' || addMore == 'Y') && *count < MAX_STUDENTS);

    cout << "\n" << *count << " student record(s) entered successfully.\n";
}

void computeGrades(float* quiz, float* midSem, float* exam,
                   float* totals, char* grades, string* remarks,
                   int count) {
    // Use pointer arithmetic to traverse all arrays
    for (int i = 0; i < count; i++) {
        *(totals + i) = *(quiz + i) + *(midSem + i) + *(exam + i);
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
             << setw(22) << *(names   + i)
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

int main() {
    // --- Parallel arrays for student data ---
    string names[MAX_STUDENTS];
    int    ids[MAX_STUDENTS];
    float  quiz[MAX_STUDENTS];
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

        // Validate menu choice
        while (!(cin >> choice) || choice < 1 || choice > 6) {
            cin.clear();
            cin.ignore(1000, '\n');
            cout << "Invalid input. Please enter a number (1-6): ";
        }

        switch (choice) {

            case 1:
                inputStudents(names, ids, quiz, midSem, exam,
                              &studentCount);
                gradesComputed = false;   // Reset flag on new input
                break;

            case 2:
                if (studentCount == 0) {
                    cout << "\nNo records found. "
                         << "Please enter student records first.\n";
                } else {
                    computeGrades(quiz, midSem, exam, totals,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                break;

            case 3:
                // Auto-compute if needed before displaying
                if (studentCount > 0 && !gradesComputed) {
                    cout << "\nGrades not yet computed. "
                         << "Computing automatically...\n";
                    computeGrades(quiz, midSem, exam, totals,
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
                    computeGrades(quiz, midSem, exam, totals,
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
                    computeGrades(quiz, midSem, exam, totals,
                                  grades, remarks, studentCount);
                    gradesComputed = true;
                }
                int searchID;
                cout << "\nEnter Student ID to search: ";
                cin >> searchID;

                int idx = searchByID(ids, studentCount, searchID);

                if (idx == -1) {
                    cout << "\nStudent with ID " << searchID
                         << " was not found.\n";
                } else {
                    cout << "\n--- Student Record ---\n";
                    cout << "Name     : " << names[idx]  << "\n";
                    cout << "ID       : " << ids[idx]    << "\n";
                    cout << fixed << setprecision(1);
                    cout << "Quiz     : " << quiz[idx]   << " / 20\n";
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
