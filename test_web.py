import http.client
import json
import subprocess
import threading
import unittest
from web import GradeServer, ensure_engine


class GradeWebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = ensure_engine()

    def setUp(self):
        self.server = GradeServer(('127.0.0.1', 0), self.engine)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.cleanup)

    def cleanup(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path='/api/state', data=None, cookie=None, origin=True):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=5)
        headers = {'Content-Type': 'application/json'}
        if origin:
            headers['Origin'] = f'http://127.0.0.1:{self.server.server_port}'
        if cookie:
            headers['Cookie'] = cookie
        connection.request('POST' if data is not None else 'GET', path, json.dumps(data) if data is not None else None, headers)
        response = connection.getresponse()
        text = response.read().decode()
        result = response.status, dict(response.getheaders()), json.loads(text) if 'application/json' in response.getheader('Content-Type') else text
        connection.close()
        return result

    def session(self):
        return self.request()[1]['Set-Cookie'].split(';')[0]

    def test_offline_interface_assets_and_boundaries(self):
        for path in ['/', '/app.js', '/ui.js', '/ui.css', '/theme.css', '/vendor/anime.umd.min.js']:
            status, headers, body = self.request(path)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 100)
            self.assertIn("script-src 'self'", headers['Content-Security-Policy'])
        self.assertEqual(self.request('/vendor/../../web.py')[0], 404)

    def test_sample_class_is_calculated_by_cpp_and_exported(self):
        cookie = self.session()
        status, _, result = self.request('/api/sample', {}, cookie)
        self.assertEqual(status, 200)
        state = result['state']
        self.assertEqual([r['grade'] for r in state['records']], ['A', 'F', 'B'])
        self.assertAlmostEqual(state['average'], 199/3, places=4)
        self.assertEqual((state['passed'], state['failed']), (2, 1))
        self.assertEqual((state['highest_id'], state['lowest_id']), (101, 102))
        status, headers, text = self.request('/api/export', cookie=cookie)
        self.assertEqual(status, 200)
        self.assertIn('attachment', headers['Content-Disposition'])
        self.assertIn('Ama Mensah', text)
        self.assertIn('85.0,A,Pass', text)

    def test_add_edit_delete_and_invalid_input(self):
        cookie = self.session()
        record = dict(id='42', name='Test Student', quiz='20', mid='30', exam='50')
        self.assertEqual(self.request('/api/student', record, cookie)[2]['state']['records'][0]['grade'], 'A')
        self.assertEqual(self.request('/api/student', record, cookie)[0], 400)
        for field, value in [('quiz','nan'), ('mid','31'), ('exam','words'), ('id','1.5'), ('name','')]:
            self.assertEqual(self.request('/api/student', {**record, field:value}, cookie)[0], 400)
        edited = {**record, 'original_id':'42', 'exam':'0'}
        self.assertEqual(self.request('/api/student', edited, cookie)[2]['state']['records'][0]['grade'], 'D')
        self.assertEqual(self.request('/api/delete', {'id':'42'}, cookie)[2]['state']['records'], [])

    def test_sessions_and_replacement_confirmation(self):
        first, second = self.session(), self.session()
        self.request('/api/sample', {}, first)
        self.assertEqual(self.request(cookie=second)[2]['records'], [])
        self.assertEqual(self.request('/api/sample', {}, first)[0], 400)
        self.assertEqual(self.request('/api/sample', {'replace':True}, first)[0], 200)
        self.assertEqual(self.request('/api/sample', {}, first, origin=False)[0], 403)

    def test_capacity_is_enforced_before_mutation(self):
        data = {'records': []}
        for index in range(1,31):
            self.server.action('/api/student', dict(id=str(index),name=f'Student {index}',quiz='0',mid='0',exam='0'), data)
        with self.assertRaises(ValueError):
            self.server.action('/api/student',dict(id='31',name='Extra',quiz='0',mid='0',exam='0'),data)
        self.assertEqual(len(data['records']),30)

    def test_engine_rejects_invalid_protocol_and_uses_grade_boundaries(self):
        result = subprocess.run([str(self.engine)], input='1 20 30 30\n2 20 30 0\n3 0 0 49\n',text=True,capture_output=True,timeout=5)
        self.assertEqual(result.returncode,0)
        self.assertEqual([r['grade'] for r in json.loads(result.stdout)['records']],['A','D','F'])
        for text in ['1 21 0 0\n','1 nan 0 0\n','1 0 0 0\n1 0 0 0\n','1 0 0 0 trailing\n']:
            self.assertNotEqual(subprocess.run([str(self.engine)],input=text,text=True,capture_output=True,timeout=5).returncode,0)


if __name__ == '__main__':
    unittest.main()
