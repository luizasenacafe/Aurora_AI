import asyncio
import tempfile
import time
import unittest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from api import create_app
from storage import Keys

class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.keys=Keys(Path(self.temp.name)/'keys.db')
        self.kid,self.key=self.keys.issue('Ana'); self.other_id,self.other=self.keys.issue('Bruno')
        self.headers={'Authorization':'Bearer '+self.key}; self.other_headers={'Authorization':'Bearer '+self.other}
        self.payload={'model':'chat-model','messages':[{'role':'system','content':'Seja gentil com Ana.'},{'role':'user','content':'Oi'}]}
        self.received=[]; self.mode='ok'
        async def handler(request):
            if self.mode=='offline': raise httpx.ConnectError('offline')
            if request.url.path.endswith('models'): return httpx.Response(200,json={'data':[{'id':'chat-model'},{'id':'text-embedding-nomic-embed-text-v1.5'}]})
            import json
            self.received.append(json.loads(request.content)); await asyncio.sleep(.15)
            return httpx.Response(200,json={'choices':[{'message':{'content':'Olá, Ana!'}}]})
        config={'upstream':'http://127.0.0.1:1234/v1','concurrency':1,'max_pending':2,'timeout':2}
        self.app=create_app(config,self.keys,httpx.MockTransport(handler)); self.client=TestClient(self.app); self.client.__enter__()
    def tearDown(self):
        self.client.__exit__(None,None,None); self.temp.cleanup()
    def poll(self,jid):
        for _ in range(100):
            response=self.client.get('/v1/aurora/jobs/'+jid,headers=self.headers); data=response.json()
            if data.get('state') in ('done','error'): return data
            time.sleep(.02)
        self.fail('Job não terminou')
    def test_auth_revocation_and_minimal_health(self):
        self.assertEqual(self.client.get('/v1/models').status_code,401)
        self.assertEqual(self.client.get('/health').json(),{'status':'ok','service':'aurora-api'})
        self.assertEqual(self.client.get('/v1/models',headers=self.headers).status_code,200)
        self.keys.revoke(self.kid)
        self.assertEqual(self.client.get('/v1/models',headers=self.headers).status_code,401)
    def test_roundtrip_persona_and_job_ownership(self):
        models=self.client.get('/v1/models',headers=self.headers).json()['data']
        self.assertEqual([m['id'] for m in models],['chat-model'])
        response=self.client.post('/v1/aurora/jobs',json=self.payload,headers=self.headers); self.assertEqual(response.status_code,202)
        jid=response.json()['id']
        self.assertEqual(self.client.get('/v1/aurora/jobs/'+jid,headers=self.other_headers).status_code,404)
        result=self.poll(jid); self.assertEqual(result['result']['choices'][0]['message']['content'],'Olá, Ana!')
        self.assertEqual(self.received[0]['messages'],self.payload['messages'])
        self.assertNotIn('owner',result)
    def test_single_outstanding_request_and_queue_capacity(self):
        self.client.post('/v1/aurora/jobs',json=self.payload,headers=self.headers)
        self.assertEqual(self.client.post('/v1/aurora/jobs',json=self.payload,headers=self.headers).status_code,429)
        self.assertEqual(self.client.post('/v1/aurora/jobs',json=self.payload,headers=self.other_headers).status_code,202)
        _,third=self.keys.issue('Terceiro')
        self.assertEqual(self.client.post('/v1/aurora/jobs',json=self.payload,headers={'Authorization':'Bearer '+third}).status_code,429)
    def test_limits_and_no_arbitrary_proxy(self):
        body={**self.payload,'tools':[{'url':'http://example.org'}]}
        response=self.client.post('/v1/chat/completions',json=body,headers=self.headers)
        self.assertEqual(response.status_code,422); self.assertNotIn('Seja gentil',response.text)
        response=self.client.post('/v1/chat/completions',content=b'x'*160001,headers={**self.headers,'Content-Type':'application/json'})
        self.assertEqual(response.status_code,413)
        self.assertEqual(self.client.post('/v1/models/delete',json={},headers=self.headers).status_code,404)
    def test_standard_contract_and_upstream_failure(self):
        response=self.client.post('/v1/chat/completions',json=self.payload,headers=self.headers)
        self.assertEqual(response.status_code,200)
        self.mode='offline'
        response=self.client.post('/v1/aurora/jobs',json=self.payload,headers=self.headers)
        result=self.poll(response.json()['id']); self.assertEqual(result['state'],'error'); self.assertEqual(result['code'],503)
    def test_invalid_model_and_rate_limit(self):
        payload={**self.payload,'model':'text-embedding-nomic-embed-text-v1.5'}
        response=self.client.post('/v1/chat/completions',json=payload,headers=self.headers)
        self.assertEqual(response.status_code,400)
        for _ in range(29): self.client.get('/v1/models',headers=self.headers)
        self.assertEqual(self.client.get('/v1/models',headers=self.headers).status_code,429)

if __name__=='__main__': unittest.main()
