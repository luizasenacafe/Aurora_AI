"""Python process supervisor for the local API and optional HTTPS tunnel."""
import argparse
import ctypes
import hashlib
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
import time
import urllib.request
from storage import data_dir, read_config

ROOT=Path(__file__).resolve().parent
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0

def download_tunnel():
    target=data_dir()/'cloudflared.exe'
    if target.exists(): return target
    req=urllib.request.Request('https://api.github.com/repos/cloudflare/cloudflared/releases/latest',headers={'User-Agent':'Aurora-Server'})
    with urllib.request.urlopen(req,timeout=30) as response: release=json.load(response)
    asset=next(a for a in release['assets'] if a['name']=='cloudflared-windows-amd64.exe')
    digest=asset.get('digest','')
    if not digest.startswith('sha256:'): raise RuntimeError('A versão publicada não tem checksum SHA-256 verificável.')
    temp=target.with_suffix('.download')
    urllib.request.urlretrieve(asset['browser_download_url'],temp)
    if hashlib.sha256(temp.read_bytes()).hexdigest()!=digest.split(':',1)[1]:
        temp.unlink(); raise RuntimeError('A verificação do download falhou.')
    temp.replace(target)
    (data_dir()/'tunnel-version.txt').write_text(release['tag_name'],encoding='utf-8')
    return target

def startup_path():
    return Path(os.environ['APPDATA'])/'Microsoft/Windows/Start Menu/Programs/Startup/Aurora Server.vbs'

def set_startup(enabled):
    path=startup_path()
    if not enabled:
        path.unlink(missing_ok=True); return
    pythonw=Path(sys.executable).with_name('pythonw.exe')
    command=f'"{pythonw}" "{ROOT / "manage.py"}" run --https'
    path.write_text('Set sh = CreateObject("WScript.Shell")\nsh.Run "'+command.replace('"','""')+'", 0, False\n',encoding='utf-8')

def start(https=True):
    # Cross-process mutex inside run() prevents duplicate supervisors.
    (data_dir()/'stop').unlink(missing_ok=True)
    args=[str(Path(sys.executable).with_name('pythonw.exe')),str(ROOT/'manage.py'),'run']
    if https: args.append('--https')
    subprocess.Popen(args,creationflags=FLAGS,close_fds=True)

def stop(): (data_dir()/'stop').touch()

def status():
    try:
        value=json.loads((data_dir()/'status.json').read_text(encoding='utf-8'))
        if time.time()-value.get('heartbeat',0)>15: return {'running':False,'message':'Servidor parado.'}
        return value
    except (OSError,ValueError): return {'running':False,'message':'Servidor parado.'}

def ensure_lm(settings,log):
    """Recover LM Studio's local API through its installed official CLI."""
    headers={}
    if os.environ.get('AURORA_LM_TOKEN'): headers['Authorization']='Bearer '+os.environ['AURORA_LM_TOKEN']
    try:
        req=urllib.request.Request(settings['upstream'].rstrip('/')+'/models',headers=headers)
        with urllib.request.urlopen(req,timeout=3): return
    except urllib.error.HTTPError:
        return  # Reachable, but credentials or another LM configuration need attention.
    except (OSError,ValueError): pass
    cli=Path(os.environ['USERPROFILE'])/'.lmstudio/bin/lms.exe'
    if cli.exists() and settings['upstream']=='http://127.0.0.1:1234/v1':
        try:
            result=subprocess.run([str(cli),'server','start','--port','1234','--bind','127.0.0.1'],capture_output=True,creationflags=FLAGS,timeout=25)
            log.info('Tentativa de iniciar API do LM Studio: codigo %s',result.returncode)
        except (OSError,subprocess.TimeoutExpired): log.warning('LM Studio precisa ser iniciado manualmente.')

def run(https):
    mutex=None
    if os.name=='nt':
        # Keep the handle type correct on 64-bit Windows.
        ctypes.windll.kernel32.CreateMutexW.restype=ctypes.c_void_p
        mutex=ctypes.windll.kernel32.CreateMutexW(None,False,'Local\\AuroraServerSupervisor')
        if ctypes.windll.kernel32.GetLastError()==183: return
    folder=data_dir(); log=logging.getLogger('aurora-supervisor'); log.setLevel(logging.INFO)
    handler=RotatingFileHandler(folder/'server.log',maxBytes=1_000_000,backupCount=3,encoding='utf-8'); log.addHandler(handler)
    settings=read_config(); state={'running':True,'api':False,'https_url':'','message':'Iniciando…'}; processes={}; retries={'api':0.,'tunnel':0.}; lock=threading.Lock(); next_lm_check=0.

    def output(name,proc):
        for line in iter(proc.stdout.readline,''):
            # The API does not log prompts, tokens, or request bodies.
            log.info('%s: %s',name,line.rstrip())
            found=re.search(r'https://[a-z0-9-]+\.trycloudflare\.com',line)
            if found:
                with lock: state['https_url']=found.group(0)
        proc.stdout.close()

    def launch(name,args):
        proc=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8',errors='replace',creationflags=FLAGS)
        processes[name]=proc; threading.Thread(target=output,args=(name,proc),daemon=True).start()

    try:
        tunnel=download_tunnel() if https else None
        while not (folder/'stop').exists():
            now=time.monotonic()
            if now>=next_lm_check:
                next_lm_check=now+60
                threading.Thread(target=ensure_lm,args=(settings,log),daemon=True).start()
            for name in ('api','tunnel') if https else ('api',):
                proc=processes.get(name)
                if (proc is None or proc.poll() is not None) and now>=retries[name]:
                    retries[name]=now+15
                    if name=='api': launch(name,[sys.executable,str(ROOT/'api.py')])
                    else:
                        with lock: state['https_url']=''
                        launch(name,[str(tunnel),'tunnel','--no-autoupdate','--url',f'http://127.0.0.1:{settings["port"]}','--protocol','http2'])
            try:
                with urllib.request.urlopen(f'http://127.0.0.1:{settings["port"]}/health',timeout=2) as response:
                    ready=json.load(response).get('service')=='aurora-api'
            except Exception: ready=False
            with lock:
                state.update(api=ready,heartbeat=time.time(),pid=os.getpid(),message='API em execução.' if ready else 'Aguardando a API iniciar.')
                temp=folder/'status.tmp'; temp.write_text(json.dumps(state),encoding='utf-8'); temp.replace(folder/'status.json')
            if os.name=='nt':
                # Keep the PC awake only while this supervisor is alive; screen may turn off.
                ctypes.windll.kernel32.SetThreadExecutionState(0x80000001)
            time.sleep(2)
    except Exception as exc:
        log.error('Falha ao iniciar: %s',exc)
        state.update(running=False,message=str(exc),heartbeat=time.time()); (folder/'status.json').write_text(json.dumps(state),encoding='utf-8')
    finally:
        for proc in processes.values():
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        state.update(running=False,api=False,https_url='',heartbeat=time.time())
        (folder/'status.json').write_text(json.dumps(state),encoding='utf-8')
        if os.name=='nt':
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000)
            if mutex:
                ctypes.windll.kernel32.CloseHandle.argtypes=[ctypes.c_void_p]; ctypes.windll.kernel32.CloseHandle(mutex)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=['run','start','stop','status','download']); parser.add_argument('--https',action='store_true'); args=parser.parse_args()
    if args.action=='run': run(args.https)
    elif args.action=='start': start(args.https)
    elif args.action=='stop': stop()
    elif args.action=='status': print(json.dumps(status(),ensure_ascii=False))
    elif args.action=='download': print(download_tunnel())
