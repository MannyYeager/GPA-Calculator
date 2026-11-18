import unittest
from copy import deepcopy
from web import GradeServer, ensure_engine


class SubjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.engine=ensure_engine()

    def setUp(self):
        self.server=GradeServer(('127.0.0.1',0),self.engine)
        self.addCleanup(self.server.server_close)
        self.data={'records':[]}
        self.server.action('/api/student',dict(id='1',name='Fictional Learner',group='Blue'),self.data)
        self.definition=dict(name='Mathematics',code='MATH',components=[dict(id='test',name='Test',maximum='50',weight='20'),dict(id='exam',name='Exam',maximum='100',weight='80')])
        self.server.action('/api/subject',self.definition,self.data)
        self.subject=self.data['subjects'][-1]

    def test_weighted_marks_use_raw_maximum_and_cpp_thresholds(self):
        self.server.action('/api/marks',dict(subject_id=self.subject['id'],student_id='1',scores={'test':'40','exam':'80'}),self.data)
        snapshot=self.server.snapshot(self.data)
        result=snapshot['subject_results'][self.subject['id']]['records'][0]
        self.assertEqual(result['total'],80)
        self.assertEqual(result['grade'],'A')
        self.assertEqual(snapshot['subject_results']['general']['ungraded'],1)
        self.assertEqual(snapshot['subject_results']['general']['failed'],0)
        self.assertIn('Mathematics',self.server.export(self.data)[0])

    def test_fractional_weights_do_not_drop_an_exact_grade_boundary(self):
        definition=dict(name='Boundary check',code='EDGE',components=[dict(id=str(i),name=f'Part {i}',maximum=3,weight=weight) for i,weight in enumerate(['33.33','33.33','33.34'])])
        self.server.action('/api/subject',definition,self.data)
        subject=self.data['subjects'][-1]
        self.server.action('/api/marks',dict(subject_id=subject['id'],student_id=1,scores={str(i):'2.4' for i in range(3)}),self.data)
        result=self.server.snapshot(self.data)['subject_results'][subject['id']]['records'][0]
        self.assertEqual((result['total'],result['grade']),(80,'A'))

    def test_bad_weight_totals_and_marks_do_not_mutate(self):
        before=deepcopy(self.data)
        for weight in ['0','79','NaN','Infinity']:
            bad=deepcopy(self.definition);bad['components'][1]['weight']=weight
            with self.assertRaises(ValueError):self.server.action('/api/subject',bad,self.data)
            self.assertEqual(self.data,before)
        for scores in [{'test':'51','exam':'80'},{'test':'40'},{'test':'nan','exam':'80'}]:
            with self.assertRaises(ValueError):self.server.action('/api/marks',dict(subject_id=self.subject['id'],student_id='1',scores=scores),self.data)
            self.assertEqual(self.data,before)

    def test_subject_weight_edit_recalculates_and_protects_existing_scores(self):
        self.server.action('/api/marks',dict(subject_id=self.subject['id'],student_id=1,scores={'test':'50','exam':'50'}),self.data)
        edit=deepcopy(self.definition);edit['id']=self.subject['id'];edit['components'][0]['weight']=50;edit['components'][1]['weight']=50
        self.server.action('/api/subject',edit,self.data)
        self.assertEqual(self.server.snapshot(self.data)['subject_results'][self.subject['id']]['records'][0]['total'],75)
        edit['components'][0]['maximum']=40
        with self.assertRaises(ValueError):self.server.action('/api/subject',edit,self.data)

    def test_student_edit_preserves_subject_marks_and_subject_removal_is_explicit(self):
        self.server.action('/api/marks',dict(subject_id=self.subject['id'],student_id=1,scores={'test':'40','exam':'80'}),self.data)
        self.server.action('/api/student',dict(original_id='1',id='2',name='Updated Learner',group='Gold'),self.data)
        self.assertEqual(self.server.snapshot(self.data)['subject_results'][self.subject['id']]['records'][0]['id'],2)
        with self.assertRaises(ValueError):self.server.action('/api/subject/delete',dict(id=self.subject['id']),self.data)
        self.server.action('/api/subject/delete',dict(id=self.subject['id'],confirm=True),self.data)
        with self.assertRaises(ValueError):self.server.action('/api/subject/delete',dict(id='general',confirm=True),self.data)

    def test_default_attendance_is_required_but_teacher_can_reallocate_it(self):
        general=self.data['subjects'][0]
        self.assertEqual([(p['id'],p['maximum'],p['weight']) for p in general['components']],
                         [('quiz',10,10),('mid',30,30),('exam',50,50),('attendance',10,10)])
        before=deepcopy(self.data)
        with self.assertRaises(ValueError):
            self.server.action('/api/marks',dict(subject_id='general',student_id=1,scores={'quiz':10,'mid':30,'exam':29.5}),self.data)
        self.assertEqual(self.data,before)
        self.assertEqual(self.server.snapshot(self.data)['subject_results']['general']['ungraded'],1)
        self.server.action('/api/marks',dict(subject_id='general',student_id=1,scores={'quiz':10,'mid':30,'exam':29.5,'attendance':10}),self.data)
        result=self.server.snapshot(self.data)['subject_results']['general']['records'][0]
        self.assertEqual((result['total'],result['grade']),(79.5,'A-'))
        edit=deepcopy(general);edit['components']=edit['components'][:3];edit['components'][0]['weight']=20
        self.server.action('/api/subject',edit,self.data)
        self.assertNotIn('attendance',self.data['records'][0]['scores']['general'])
        self.assertEqual(self.server.snapshot(self.data)['subject_results']['general']['records'][0]['grade'],'A-')

    def test_weighted_grade_boundaries_and_decimal_gaps(self):
        self.server.action('/api/subject',dict(name='Boundaries',code='BANDS',components=[dict(id='work',name='Work',maximum=100,weight=100)]),self.data)
        subject=self.data['subjects'][-1]
        cases=[(39.9999,'F'),(40,'D'),(44.9999,'D'),(45,'C-'),(49.9999,'C-'),(50,'C'),(54.9999,'C'),(55,'C+'),
               (59.9999,'C+'),(60,'B-'),(64.9999,'B-'),(65,'B'),(69.9999,'B'),(70,'B+'),(74.9999,'B+'),(75,'A-'),(79.9999,'A-'),(80,'A')]
        for total,grade in cases:
            with self.subTest(total=total):
                self.server.action('/api/marks',dict(subject_id=subject['id'],student_id=1,scores={'work':total}),self.data)
                result=self.server.snapshot(self.data)['subject_results'][subject['id']]
                self.assertEqual((result['records'][0]['total'],result['records'][0]['grade']),(total,grade))
                self.assertEqual(result['passed'],int(grade!='F'))

    def test_unrepresentable_numbers_do_not_mutate(self):
        before=deepcopy(self.data)
        bad=deepcopy(self.definition);bad['components'][0]['maximum']='1e-400'
        with self.assertRaises(ValueError):self.server.action('/api/subject',bad,self.data)
        with self.assertRaises(ValueError):
            self.server.action('/api/marks',dict(subject_id=self.subject['id'],student_id=1,scores={'test':10**400,'exam':80}),self.data)
        self.assertEqual(self.data,before)
