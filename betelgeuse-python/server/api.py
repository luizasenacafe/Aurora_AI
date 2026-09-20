"""Authenticated LM Studio gateway. Bind to loopback; HTTPS arrives via a tunnel."""
import asyncio
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from collections import deque
from typing import Literal

import httpx
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict, model_validator
from storage import Keys, read_config

class Message(BaseModel):
    model_config=ConfigDict(extra='forbid')
    role: Literal['system','user','assistant']
    content: str=Field(min_length=1,max_length=24000)

class Chat(BaseModel):
    model_config=ConfigDict(extra='forbid')
    model: str=Field(min_length=1,max_length=300)
    messages: list[Message]=Field(min_length=1,max_length=42)
    temperature: float=Field(default=.7,ge=0,le=2)
    max_tokens: int=Field(default=1200,ge=1,le=2048)
    stream: Literal[False]=False
    @model_validator(mode='after')
    def limit_context(self):
        if sum(len(m.content) for m in self.messages)>32000: raise ValueError('Contexto muito longo.')
        return self

def create_app(config=None, keys=None, transport=None):
    config=config or read_config(); keys=keys or Keys()
    jobs={}; rates={}; tasks=set(); semaphore=asyncio.Semaphore(config.get('concurrency',1))

    @asynccontextmanager
    async def lifespan(app):
        headers={}
        if os.environ.get('AURORA_LM_TOKEN'): headers['Authorization']='Bearer '+os.environ['AURORA_LM_TOKEN']
        async with httpx.AsyncClient(base_url=config['upstream'].rstrip('/')+'/',headers=headers,trust_env=False,follow_redirects=False,transport=transport,timeout=httpx.Timeout(config.get('timeout',480),connect=8)) as client:
            app.state.client=client
            async def cleanup():
                while True:
                    await asyncio.sleep(30); prune()
            cleaner=asyncio.create_task(cleanup()); tasks.add(cleaner)
            yield
            for task in list(tasks): task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)

    app=FastAPI(title='Betelgeuse A.I. Server',docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.jobs=jobs

    async def auth(request:Request):
        value=request.headers.get('authorization','')
        kid=keys.identify(value[7:]) if value.startswith('Bearer ') else None
        if not kid: raise HTTPException(401,'Chave de acesso ausente, inválida ou revogada.',headers={'WWW-Authenticate':'Bearer'})
        return kid

    def rate(kid):
        now=time.monotonic(); history=rates.setdefault(kid,deque())
        while history and history[0]<now-60: history.popleft()
        if len(history)>=30: raise HTTPException(429,'Muitas solicitações. Aguarde um minuto.',headers={'Retry-After':'60'})
        history.append(now)
        # Bound retained entries even as keys are repeatedly issued and revoked.
        for old in list(rates):
            if rates[old] and rates[old][-1]<now-60: rates.pop(old,None)

    @app.middleware('http')
    async def boundaries(request,call_next):
        if request.method=='POST':
            value=request.headers.get('content-length','')
            try: size=int(value)
            except ValueError: return JSONResponse({'detail':'Content-Length é obrigatório.'},status_code=411)
            if size<0 or size>160000: return JSONResponse({'detail':'Mensagem muito grande.'},status_code=413)
            if request.headers.get('content-type','').split(';')[0]!='application/json': return JSONResponse({'detail':'Use JSON.'},status_code=415)
            # Enforce the actual body size as well as the advertised length.
            body=bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body)>160000: return JSONResponse({'detail':'Mensagem muito grande.'},status_code=413)
            request._body=bytes(body)
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'; response.headers['X-Content-Type-Options']='nosniff'
        return response

    @app.exception_handler(RequestValidationError)
    async def invalid(request,exc):
        return JSONResponse({'detail':'Solicitação inválida. Confira o modelo, as mensagens e os limites de contexto.'},status_code=422)

    async def upstream(method,path,payload=None):
        try:
            response=await app.state.client.request(method,path,json=payload)
        except httpx.TimeoutException: raise HTTPException(504,'O modelo demorou demais. Tente uma mensagem menor.')
        except httpx.HTTPError: raise HTTPException(503,'LM Studio indisponível. Verifique se o servidor local está iniciado.')
        if response.status_code in (401,403): raise HTTPException(503,'O servidor precisa configurar a autenticação do LM Studio.')
        if response.status_code>=400: raise HTTPException(502,'O LM Studio não conseguiu atender. Confira o modelo carregado no servidor.')
        try: return response.json()
        except ValueError: raise HTTPException(502,'Resposta inválida do LM Studio.')

    async def available():
        data=await upstream('GET','models')
        if not isinstance(data,dict) or not isinstance(data.get('data'),list): raise HTTPException(502,'Lista de modelos inválida.')
        models=[m for m in data['data'] if isinstance(m,dict) and isinstance(m.get('id'),str) and not any(word in m['id'].lower() for word in ('embedding','embed-text','embed-'))]
        if config.get('model'): models=[m for m in models if m['id']==config['model']]
        return {'object':'list','data':[{'id':m['id'],'object':'model','owned_by':'aurora'} for m in models]}

    async def generate(payload):
        if config.get('model') and payload.model!=config['model']: raise HTTPException(400,'Este modelo não está habilitado pelo dono do servidor.')
        if payload.model not in [m['id'] for m in (await available())['data']]: raise HTTPException(400,'Selecione um modelo de conversa disponível no servidor.')
        data=await upstream('POST','chat/completions',payload.model_dump())
        try: content=data['choices'][0]['message']['content']
        except (KeyError,IndexError,TypeError): raise HTTPException(502,'Resposta de conversa inválida.')
        if not isinstance(content,str) or not content.strip(): raise HTTPException(502,'O modelo retornou uma resposta vazia.')
        # Return only the contract the client needs; do not relay arbitrary upstream fields.
        return {'id':'aurora-'+secrets.token_hex(8),'object':'chat.completion','model':payload.model,'choices':[{'index':0,'message':{'role':'assistant','content':content},'finish_reason':'stop'}]}

    def prune():
        now=time.monotonic()
        for jid in list(jobs):
            j=jobs[jid]
            if j['state'] in ('done','error') and now-j['updated']>600: jobs.pop(jid,None)
        if len(jobs)>=64:
            finished=sorted((jid for jid in jobs if jobs[jid]['state'] in ('done','error')),key=lambda jid:jobs[jid]['updated'])
            for jid in finished[:max(1,len(jobs)-63)]: jobs.pop(jid,None)

    def admit(kid):
        prune()
        pending=[j for j in jobs.values() if j['state'] in ('queued','running')]
        if any(j['owner']==kid for j in pending): raise HTTPException(429,'Você já tem uma resposta em andamento.')
        if len(pending)>=config.get('max_pending',8): raise HTTPException(429,'A fila está cheia. Tente novamente em instantes.')

    async def run_job(jid,payload):
        job=jobs[jid]
        try:
            # Bound both waiting time and inference, so abandoned requests cannot live forever.
            async with asyncio.timeout(config.get('timeout',480)+30):
                async with semaphore:
                    job['state']='running'; result=await generate(payload)
            job.update(state='done',result=result,updated=time.monotonic())
        except (HTTPException,TimeoutError) as exc:
            job.update(state='error',error=getattr(exc,'detail','O tempo de espera terminou. Tente novamente.'),code=getattr(exc,'status_code',504),updated=time.monotonic())
        except asyncio.CancelledError: raise
        except Exception:
            job.update(state='error',error='Falha ao gerar a resposta.',code=502,updated=time.monotonic())

    @app.get('/health')
    async def health(): return {'status':'ok','service':'aurora-api'}

    @app.get('/v1/aurora/info')
    async def info(kid=Depends(auth)): return {'protocol':'aurora-jobs-v1','poll_seconds':2}

    @app.get('/v1/models')
    async def models(kid=Depends(auth)):
        rate(kid); return await available()

    @app.post('/v1/aurora/jobs',status_code=202)
    async def submit(payload:Chat,kid=Depends(auth)):
        rate(kid); admit(kid)
        jid=secrets.token_urlsafe(24); jobs[jid]={'owner':kid,'state':'queued','updated':time.monotonic()}
        task=asyncio.create_task(run_job(jid,payload)); tasks.add(task); task.add_done_callback(tasks.discard)
        return {'id':jid,'state':'queued'}

    @app.get('/v1/aurora/jobs/{jid}')
    async def poll(jid:str,kid=Depends(auth)):
        prune(); job=jobs.get(jid)
        if not job or job['owner']!=kid: raise HTTPException(404,'Resposta não encontrada. O servidor pode ter reiniciado; tente novamente.')
        return {k:v for k,v in job.items() if k not in ('owner','updated')}

    @app.post('/v1/chat/completions')
    async def chat(payload:Chat,kid=Depends(auth)):
        # Same queue and limits as the Aurora protocol; supports standard API clients.
        queued=await submit(payload,kid); jid=queued['id']
        while jobs[jid]['state'] in ('queued','running'): await asyncio.sleep(.1)
        job=jobs.pop(jid)
        if job['state']=='error': raise HTTPException(job['code'],job['error'])
        return job['result']

    return app

if __name__=='__main__':
    import uvicorn
    settings=read_config()
    uvicorn.run(create_app(settings),host=settings['host'],port=settings['port'],workers=1,access_log=False,proxy_headers=False,limit_concurrency=64,timeout_keep_alive=5)
