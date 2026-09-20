"""Local persistence and OpenAI-compatible transport for Aurora."""
import json
import sqlite3
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError

DEFAULT_PERSONA = 'Você é Betelgeuse, uma assistente doméstica acolhedora, prática e atenciosa. Responda em português brasileiro, com clareza e sem exageros.'

def normalize_url(value):
    value = value.strip().rstrip('/')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Informe um endereço como http://localhost:1234/v1, sem senha ou parâmetros na URL.')
    return value if value.endswith('/v1') else value + '/v1'

def _request(base, token, path, payload=None, optional=False):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    req = Request(normalize_url(base) + path, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
    try:
        with urlopen(req, timeout=180 if payload else 12) as response:
            return json.load(response)
    except HTTPError as exc:
        if optional and exc.code==404: return None
        if exc.code in (401, 403):
            raise ValueError('Acesso recusado. Confira o token nas configurações.') from exc
        try:
            detail=json.loads(exc.read(4096)).get('detail')
            if isinstance(detail,str): raise ValueError(detail[:500]) from exc
        except (json.JSONDecodeError,UnicodeDecodeError,AttributeError): pass
        raise ValueError(f'O servidor respondeu com erro {exc.code}. Confira o modelo e o painel do LM Studio.') from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError('Não consegui conversar com o servidor. Confira o endereço, o LM Studio e a conexão de rede. Se o modelo estiver lento, tente uma mensagem menor.') from exc

def request_api(base, token, path, payload=None):
    if path=='/chat/completions' and payload is not None:
        info=_request(base,token,'/aurora/info',optional=True)
        if isinstance(info,dict) and info.get('protocol')=='aurora-jobs-v1':
            job=_request(base,token,'/aurora/jobs',payload)
            jid=job.get('id','')
            if not jid or not all(c.isalnum() or c in '_-' for c in jid): raise ValueError('O servidor retornou um identificador inválido.')
            deadline=time.monotonic()+540
            while time.monotonic()<deadline:
                result=_request(base,token,'/aurora/jobs/'+jid)
                if result.get('state')=='done': return result['result']
                if result.get('state')=='error': raise ValueError(result.get('error','Falha no servidor.'))
                time.sleep(2)
            raise ValueError('O servidor não terminou a resposta dentro do prazo. Tente novamente em instantes.')
    return _request(base,token,path,payload)

class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS profiles (id INTEGER PRIMARY KEY, name TEXT NOT NULL, details TEXT NOT NULL, persona TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, profile INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, profile INTEGER NOT NULL, kind TEXT NOT NULL, title TEXT NOT NULL, due TEXT, done INTEGER NOT NULL DEFAULT 0);
        ''')
    def get(self, key, default=''):
        row = self.db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        return row[0] if row else default
    def set(self, key, value):
        self.db.execute('INSERT OR REPLACE INTO settings VALUES (?,?)', (key, value))
        self.db.commit()
    def profiles(self):
        return self.db.execute('SELECT * FROM profiles ORDER BY id').fetchall()
    def save_profile(self, name, details, persona, pid=None):
        if not name.strip():
            raise ValueError('Escreva o nome da pessoa.')
        if pid is None:
            pid = self.db.execute('INSERT INTO profiles(name,details,persona) VALUES (?,?,?)', (name.strip(), details, persona)).lastrowid
        else:
            self.db.execute('UPDATE profiles SET name=?,details=?,persona=? WHERE id=?', (name.strip(), details, persona, pid))
        self.db.commit()
        return pid
    def history(self, pid):
        return [dict(r) for r in self.db.execute('SELECT role,content FROM messages WHERE profile=? ORDER BY id', (pid,))]
    def add_message(self, pid, role, content):
        self.db.execute('INSERT INTO messages(profile,role,content) VALUES (?,?,?)', (pid, role, content))
        self.db.commit()
    def messages_for(self, profile, user_text):
        instructions = self.get('persona', DEFAULT_PERSONA)
        instructions += '\nPessoa atendida: ' + profile['name'] + '\nSobre ela: ' + profile['details'] + '\nPreferências de atendimento: ' + profile['persona']
        instructions += '\nVocê pode sugerir listas e lembretes no chat, mas NÃO pode salvar itens, agendar notificações nem executar ações. Oriente a pessoa a usar a aba Organização para salvar. Não diga que fez uma ação que não fez.'
        history = self.history(profile['id'])[-20:]
        # Bound context for small local models, retaining the most recent turns.
        selected, size = [], len(user_text)
        for msg in reversed(history):
            if size + len(msg['content']) > 12000:
                break
            selected.insert(0, msg)
            size += len(msg['content'])
        return [{'role': 'system', 'content': instructions}] + selected + [{'role': 'user', 'content': user_text}]
