import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
import tempfile
import threading
import json
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from core import Store, normalize_url, request_api
from aurora import Aurora, STYLE, icon
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

class API(BaseHTTPRequestHandler):
    payload = None
    def log_message(self, *args): pass
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b'{"data":[{"id":"test-model"}]}')
    def do_POST(self):
        API.payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.send_response(200); self.end_headers()
        self.wfile.write(json.dumps({'choices':[{'message':{'content':'Resposta de teste recebida.'}}]}).encode())

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([]); cls.app.setStyleSheet(STYLE)
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), API)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True); cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.http.server_port}/v1'
    @classmethod
    def tearDownClass(cls): cls.http.shutdown(); cls.http.server_close()
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name)/'test.db'; self.store = Store(self.path)
    def tearDown(self): self.store.db.close(); self.temp.cleanup()
    def test_storage_and_profile_isolation(self):
        a = self.store.save_profile('Ana', 'Estuda', 'Seja didática')
        b = self.store.save_profile('Bruno', 'Cozinha', 'Seja direta')
        self.store.add_message(a, 'user', 'Mensagem privada de Ana')
        self.assertEqual(self.store.history(b), [])
        msgs = self.store.messages_for(self.store.profiles()[1], 'Oi')
        self.assertNotIn('Ana', str(msgs)); self.assertIn('Bruno', msgs[0]['content'])
        self.store.set('persona', 'Use frases curtas')
        self.assertIn('Use frases curtas', self.store.messages_for(self.store.profiles()[0], 'Oi')[0]['content'])
        self.store.save_profile('Ana', 'Trabalha', 'Seja breve', a)
        reopened = Store(self.path)
        self.assertEqual(reopened.profiles()[0]['details'], 'Trabalha'); reopened.db.close()
    def test_url_and_transport(self):
        self.assertEqual(normalize_url('http://localhost:1234/'), 'http://localhost:1234/v1')
        for bad in ['file:///abc', 'localhost:1234', 'https://user:pass@example.com']:
            with self.assertRaises(ValueError): normalize_url(bad)
        self.assertEqual(request_api(self.base, '', '/models')['data'][0]['id'], 'test-model')
    def test_ui_roundtrip_and_organizer(self):
        pid = self.store.save_profile('Teste', 'Rotina da casa', 'Gentil')
        self.store.set('server', self.base); self.store.set('model', 'test-model')
        window = Aurora(self.store); window.show()
        window.composer.setPlainText('Olá, Aurora'); window.send()
        for _ in range(100):
            QTest.qWait(30)
            if not window.jobs: break
        self.assertFalse(window.jobs); self.assertEqual(len(self.store.history(pid)), 2)
        self.assertEqual(API.payload['model'], 'test-model')
        window.item_title.setText('Café'); window.add_item(); self.assertEqual(window.items.count(), 1)
        window.kind.setCurrentIndex(1); window.item_title.setText('Regar plantas'); window.add_item(); self.assertEqual(window.items.count(), 1)
        window.server.setText('http://192.168.1.20:1234'); window.personality.setPlainText('Personalidade editada'); window.save_settings()
        self.assertEqual(self.store.get('server'), 'http://192.168.1.20:1234/v1')
        window.close()
    def test_ui_failed_connection_preserves_draft(self):
        pid = self.store.save_profile('Teste', '', '')
        self.store.set('server', 'http://127.0.0.1:1/v1'); self.store.set('model', 'test-model')
        window = Aurora(self.store); window.composer.setPlainText('Não perca meu texto'); window.send()
        for _ in range(150):
            QTest.qWait(30)
            if not window.jobs: break
        self.assertFalse(window.jobs); self.assertEqual(self.store.history(pid), [])
        self.assertEqual(window.composer.toPlainText(), 'Não perca meu texto'); window.close()

if __name__ == '__main__': unittest.main()
