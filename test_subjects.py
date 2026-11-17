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
