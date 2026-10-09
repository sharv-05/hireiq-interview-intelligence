from fastapi.testclient import TestClient
from app.main import app

def test_health():
    with TestClient(app) as client:
        assert client.get('/api/health').status_code == 200

def test_questions_seeded():
    with TestClient(app) as client:
        assert len(client.get('/api/questions').json()) >= 3

def test_session_flow():
    with TestClient(app) as client:
        s=client.post('/api/sessions',json={'candidate_name':'Test Candidate','candidate_email':'test@example.com','role':'AI Engineer'}).json()
        q=client.get('/api/questions').json()[0]
        r=client.post(f"/api/sessions/{s['id']}/responses",params={'question_id':q['id'],'transcript':'I would measure latency, test a baseline, and monitor fairness.'})
        assert r.status_code==200 and r.json()['score']>0
        done=client.post(f"/api/sessions/{s['id']}/complete").json(); assert done['status']=='completed'
