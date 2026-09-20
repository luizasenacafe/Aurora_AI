"""Local server configuration and revocable, individually issued access keys."""
import hashlib
import json
import os
import secrets
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from contextlib import contextmanager

def data_dir():
    path = Path(os.environ.get('AURORA_SERVER_DATA') or Path(os.environ['LOCALAPPDATA']) / 'AuroraServer')
    path.mkdir(parents=True, exist_ok=True)
    return path

def read_config():
    path=data_dir()/'config.json'
    if not path.exists():
        config={'host':'127.0.0.1','port':8787,'upstream':'http://127.0.0.1:1234/v1','model':'','concurrency':1,'max_pending':8,'timeout':480}
        path.write_text(json.dumps(config,indent=2),encoding='utf-8')
    return json.loads(path.read_text(encoding='utf-8'))

class Keys:
    def __init__(self, path=None):
        self.path=Path(path) if path else data_dir()/'keys.db'
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS keys (id TEXT PRIMARY KEY, name TEXT NOT NULL, digest TEXT NOT NULL UNIQUE, created TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1)')
    @contextmanager
    def connect(self):
        db=sqlite3.connect(self.path)
        try:
            with db: yield db
        finally: db.close()
    def issue(self,name):
        name=name.strip()
        if not name or len(name)>80: raise ValueError('Use um nome entre 1 e 80 caracteres.')
        key='aurora_'+secrets.token_urlsafe(32); kid=secrets.token_hex(8)
        with self.connect() as db:
            if db.execute('SELECT count(*) FROM keys WHERE active=1').fetchone()[0]>=64: raise ValueError('Limite de 64 acessos ativos. Revogue um acesso antes de criar outro.')
            db.execute('INSERT INTO keys VALUES (?,?,?,?,1)',(kid,name,hashlib.sha256(key.encode()).hexdigest(),datetime.now(timezone.utc).isoformat()))
        return kid,key
    def identify(self,key):
        if not key or len(key)>256: return None
        with self.connect() as db:
            row=db.execute('SELECT id FROM keys WHERE digest=? AND active=1',(hashlib.sha256(key.encode()).hexdigest(),)).fetchone()
        return row[0] if row else None
    def revoke(self,kid):
        with self.connect() as db: db.execute('UPDATE keys SET active=0 WHERE id=?',(kid,))
    def list(self):
        with self.connect() as db: return db.execute('SELECT id,name,created,active FROM keys ORDER BY created').fetchall()
