"""Subject configuration, roster and marks. All grade totals are computed by C++."""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import math
import secrets


def default_subject():
    return {'id': 'general', 'name': 'General assessment', 'code': 'GEN', 'components': [
        {'id': key, 'name': label, 'maximum': maximum, 'weight': maximum}
        for key, label, maximum in [('quiz', 'Quiz', 20), ('mid', 'Mid-semester', 30), ('exam', 'Exam', 50)]]}


def ensure_data(data):
    data.setdefault('subjects', [default_subject()])
    for record in data['records']:
        if 'scores' not in record:
            record['scores'] = {'general': {key: record[key] for key in ['quiz', 'mid', 'exam']}} if all(key in record for key in ['quiz', 'mid', 'exam']) else {}
        record.setdefault('group', '')


def validate_subject(payload, existing=None):
    name, code = payload.get('name'), payload.get('code')
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 60 or not isinstance(code, str) or not 1 <= len(code.strip()) <= 12:
        raise ValueError('Enter a subject name (up to 60 characters) and code (up to 12).')
    parts = payload.get('components')
    if not isinstance(parts, list) or not 1 <= len(parts) <= 8:
        raise ValueError('Add between one and eight assessment components.')
    components, ids, total = [], set(), Decimal(0)
    for index, part in enumerate(parts):
        if not isinstance(part, dict):
            raise ValueError('Each component needs a name, maximum and percentage.')
        label = part.get('name')
        if not isinstance(label, str) or not 1 <= len(label.strip()) <= 40:
            raise ValueError('Give every assessment a name of up to 40 characters.')
        try:
            maximum, weight = Decimal(str(part.get('maximum'))), Decimal(str(part.get('weight')))
        except InvalidOperation:
            raise ValueError('Maximum marks and weights must be numbers.') from None
        if not maximum.is_finite() or not weight.is_finite() or not 0 < maximum <= 1000000 or not 0 < weight <= 100:
            raise ValueError('Use positive maximum marks and percentages from 0 to 100.')
        key = part.get('id') or 'part-' + secrets.token_hex(3)
        if not isinstance(key, str) or len(key) > 40 or key in ids:
            raise ValueError('Each assessment component needs a unique ID.')
        ids.add(key)
        components.append({'id': key, 'name': label.strip(), 'maximum': float(maximum), 'weight': float(weight)})
        total += weight
    if total != 100:
        raise ValueError(f'Assessment percentages must total 100%. Current total: {total}%.')
    return {'id': existing['id'] if existing else 'subject-' + secrets.token_hex(4), 'name': name.strip(),
            'code': code.strip().upper(), 'components': components}


def subject_snapshot(data, engine, compute):
    ensure_data(data)
    results = {}
    for subject in data['subjects']:
        rows = []
        for record in data['records']:
            marks = record['scores'].get(subject['id'], {})
            if all(part['id'] in marks for part in subject['components']):
                rows.append({'id': record['id'], 'marks': [(marks[p['id']], p['maximum'], p['weight']) for p in subject['components']]})
        calculated = compute(rows, engine)
        lookup = {row['id']: row for row in calculated['records']}
        calculated['records'] = [{**record, **lookup[record['id']]} for record in data['records'] if record['id'] in lookup]
        calculated['ungraded'] = len(data['records']) - len(rows)
        results[subject['id']] = calculated
    first = results.get('general', next(iter(results.values())))
    lookup = {r['id']: r for r in first['records']}
    records = [{**record, **lookup.get(record['id'], {'total': None, 'grade': None, 'remark': 'Ungraded'})} for record in data['records']]
    return {**first, 'records': records, 'students': data['records'], 'subjects': data['subjects'],
            'subject_results': results, 'capacity': 30, 'engine': 'C++', 'session_only': True}


def book_action(path, payload, data, positive_id, engine, compute):
    ensure_data(data)
    candidate = deepcopy(data)
    subject = next((s for s in candidate['subjects'] if s['id'] == payload.get('id', payload.get('subject_id'))), None)
    if path == '/api/subject':
        if payload.get('id') and not subject:
            raise ValueError('Subject not found.')
        if not subject and len(candidate['subjects']) >= 12:
            raise ValueError('This workspace supports up to 12 subjects.')
        updated = validate_subject(payload, subject)
        if any(s['id'] != updated['id'] and s['code'].casefold() == updated['code'].casefold() for s in candidate['subjects']):
            raise ValueError('Use a unique subject code.')
        if subject:
            for record in candidate['records']:
                marks = record['scores'].get(subject['id'], {})
                for part in updated['components']:
                    if marks.get(part['id'], 0) > part['maximum']:
                        raise ValueError('An existing mark exceeds this new maximum. Adjust the marks first.')
                record['scores'][subject['id']] = {p['id']: marks[p['id']] for p in updated['components'] if p['id'] in marks}
            candidate['subjects'][candidate['subjects'].index(subject)] = updated
        else:
            candidate['subjects'].append(updated)
        message = 'Subject saved. Its assessment weights total 100%.'
    elif path == '/api/subject/delete':
        if not subject or len(candidate['subjects']) == 1:
            raise ValueError('Keep at least one subject in your workspace.')
        if payload.get('confirm') is not True:
            raise ValueError('Confirm subject removal and its marks.')
        candidate['subjects'].remove(subject)
        for record in candidate['records']:
            record['scores'].pop(subject['id'], None)
        message = 'Subject and its assessment marks removed.'
    elif path == '/api/marks':
        if not subject:
            raise ValueError('Choose an existing subject.')
        target = positive_id(payload.get('student_id'))
        record = next((r for r in candidate['records'] if r['id'] == target), None)
        if not record:
            raise ValueError('Student not found.')
        raw = payload.get('scores')
        if not isinstance(raw, dict) or set(raw) != {p['id'] for p in subject['components']}:
            raise ValueError('Enter one mark for every assessment component.')
        marks = {}
        for part in subject['components']:
            value = raw[part['id']]
            if isinstance(value, bool) or not isinstance(value, (str, int, float)):
                raise ValueError('Marks must be numeric.')
            try:
                value = float(value)
            except ValueError:
                raise ValueError('Marks must be numeric.') from None
            if not math.isfinite(value) or not 0 <= value <= part['maximum']:
                raise ValueError(f"{part['name']} must be from 0 to {part['maximum']:g}.")
            marks[part['id']] = value
        record['scores'][subject['id']] = marks
        message = 'Assessment marks saved and weighted grades recalculated.'
    else:
        raise ValueError('Unknown gradebook action.')
    subject_snapshot(candidate, engine, compute)
    data.update(candidate)
    return message
