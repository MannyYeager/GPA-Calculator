"""Local web interface using the project's shared C++ grading rules."""
import argparse
import csv
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
from copy import deepcopy

from local_web import LocalServer
from gradebook import ensure_data, subject_snapshot, book_action, default_subject

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / ("grade_engine.exe" if os.name == "nt" else "grade_engine")


def ensure_engine():
    sources = [ROOT / "grade_engine.cpp", ROOT / "grade_rules.h"]
    if ENGINE.exists() and ENGINE.stat().st_mtime >= max(p.stat().st_mtime for p in sources):
        return ENGINE
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        raise RuntimeError("Install a C++11 compiler (g++ or clang++) before starting the web app.")
    result = subprocess.run([compiler, "-std=c++11", "-Wall", "-Wextra", "-pedantic", str(sources[0]), "-o", str(ENGINE)],
                            capture_output=True, text=True, timeout=45)
    if result.returncode:
        raise RuntimeError("Could not compile the grading engine:\n" + result.stderr)
    return ENGINE


def compute(records, engine):
    text = ''.join(('W ' + str(r['id']) + ' ' + str(len(r['marks'])) + ' ' + ' '.join(str(v) for triple in r['marks'] for v in triple) + '\n')
                   if 'marks' in r else f"{r['id']} {r['quiz']} {r['mid']} {r['exam']}" + (f" {r['attendance']}" if 'attendance' in r else '') + '\n' for r in records)
    try:
        result = subprocess.run([str(engine)], input=text, text=True, capture_output=True, timeout=5)
    except subprocess.TimeoutExpired:
        raise RuntimeError("The local C++ grading engine timed out.") from None
    if result.returncode:
        raise ValueError("The C++ engine rejected these assessment scores.")
    return json.loads(result.stdout)


def positive_id(value):
    if isinstance(value, bool) or not isinstance(value, (str, int)) or not str(value).isascii() or not str(value).isdigit():
        raise ValueError("Student ID must be a positive whole number.")
    value = int(value)
    if not 1 <= value <= 2147483647:
        raise ValueError("Student ID must be between 1 and 2147483647.")
    return value


def format_total(value):
    text = f'{value:.8f}'.rstrip('0')
    return text + '0' if text.endswith('.') else text


def parse_record(payload):
    name = payload.get('name', '')
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 80:
        raise ValueError("Enter a student name of 1 to 80 characters.")
    record = {"id": positive_id(payload.get('id')), "name": name.strip()}
    group = payload.get('group', '')
    if not isinstance(group, str) or len(group) > 40:
        raise ValueError('Class/group must be at most 40 characters.')
    record['group'] = group.strip()
    if not any(field in payload for field in ['quiz', 'mid', 'exam', 'attendance']):
        return record
    for field, maximum in [('quiz', 10), ('mid', 30), ('exam', 50), ('attendance', 10)]:
        raw = payload.get(field)
        if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
            raise ValueError(f"Enter a numeric {field} score.")
        try:
            score = float(raw)
        except (ValueError, OverflowError):
            raise ValueError(f"Enter a numeric {field} score.") from None
        if not math.isfinite(score) or not 0 <= score <= maximum:
            raise ValueError(f"{field.capitalize()} score must be from 0 to {maximum}.")
        record[field] = score
    return record


class GradeServer(LocalServer):
    def __init__(self, address, engine):
        super().__init__(address, ROOT / "static", "grade_room_session", lambda: {"records": []})
        self.engine = engine

    def snapshot(self, data):
        return subject_snapshot(data, self.engine, compute)

    def action(self, path, payload, data):
        ensure_data(data)
        if path in {'/api/subject', '/api/subject/delete', '/api/marks'}:
            return book_action(path, payload, data, positive_id, self.engine, compute)
        records = deepcopy(data['records'])
        if path == '/api/student':
            record = parse_record(payload)
            original = payload.get('original_id', '')
            if original != '':
                original = positive_id(original)
                index = next((i for i, item in enumerate(records) if item['id'] == original), None)
                if index is None:
                    raise ValueError("Student no longer exists. Refresh the class list.")
                others = [r for i, r in enumerate(records) if i != index]
            else:
                if len(records) >= 30:
                    raise ValueError("This class is full. The limit is 30 students.")
                index, others = len(records), records
            if any(item['id'] == record['id'] for item in others):
                raise ValueError("That student ID already exists. Use a unique ID.")
            if index == len(records):
                records.append(record)
            else:
                record = {**records[index], **record}
                records[index] = record
            record.setdefault('scores', {})
            if all(key in payload for key in ['quiz', 'mid', 'exam', 'attendance']):
                record['scores']['general'] = {key: record[key] for key in ['quiz', 'mid', 'exam', 'attendance']}
            message = f"{record['name']}'s record is saved. Grades have been updated."
        elif path == '/api/delete':
            target = positive_id(payload.get('id'))
            records = [r for r in records if r['id'] != target]
            if len(records) == len(data['records']):
                raise ValueError("Student not found.")
            message = "Student removed from this session's class."
        elif path == '/api/sample':
            if records and payload.get('replace') is not True:
                raise ValueError("Confirm replacement before loading the sample class.")
            records = [dict(id=101, name='Ama Mensah', quiz=8, mid=25, exam=42, attendance=10),
                       dict(id=102, name='Kojo Owusu', quiz=4, mid=10, exam=20, attendance=5),
                       dict(id=103, name='Esi Adjei', quiz=8, mid=22, exam=36, attendance=8)]
            message = "Sample class loaded. These are fictional demonstration records."
        else:
            raise ValueError("Unknown class action.")
        candidate = {**data, 'records': records}
        if path == '/api/sample':
            candidate['subjects'] = [default_subject()]
        subject_snapshot(candidate, self.engine, compute)
        data.update(candidate)
        return message

    def export(self, data):
        buffer = io.StringIO(newline='')
        writer = csv.writer(buffer)
        writer.writerow(['ID', 'Name', 'Subject', 'Assessments (raw/max; weight)', 'Total /100', 'Grade', 'Remark'])
        snapshot = self.snapshot(data)
        safe = lambda text: "'" + text if text.startswith(('=', '+', '-', '@')) else text
        for subject in snapshot['subjects']:
            results = {r['id']: r for r in snapshot['subject_results'][subject['id']]['records']}
            for record in snapshot['students']:
                result = results.get(record['id'])
                marks = record['scores'].get(subject['id'], {})
                breakdown = '; '.join(f"{p['name']}: {marks.get(p['id'], 'ungraded')}/{p['maximum']:g} ({p['weight']:g}%)" for p in subject['components'])
                writer.writerow([record['id'], safe(record['name']), safe(subject['name']), safe(breakdown),
                                 format_total(result['total']) if result else '', result['grade'] if result else '', result['remark'] if result else 'Ungraded'])
        return buffer.getvalue(), 'class-report.csv'


def main():
    parser = argparse.ArgumentParser(description="Student Grade Management local web app")
    parser.add_argument('--port', type=int, default=8767)
    args = parser.parse_args()
    try:
        engine = ensure_engine()
    except (RuntimeError, OSError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"{error}\n")
    with GradeServer(('127.0.0.1', args.port), engine) as server:
        print(f"Grade manager preview: http://127.0.0.1:{server.server_port}/", flush=True)
        print('Each browser has its own in-memory class. Grading is calculated by C++.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nClassroom closed.')


if __name__ == '__main__':
    main()
