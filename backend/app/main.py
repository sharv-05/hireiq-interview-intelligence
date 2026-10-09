import os
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession, joinedload
from sqlalchemy import select
from .db import Base,engine,get_db
from .models import Question,Rubric,Session,Response
from .schemas import *
from .services import transcribe_audio,evaluate
from .report import build_report

app=FastAPI(title='HireIQ API',version='1.0.0',description='Multimodal AI interview intelligence API')
origins=os.getenv('CORS_ORIGINS','http://localhost:5173,http://localhost:4173').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    Base.metadata.create_all(engine)
    with next(get_db()) as db:
        if not db.scalar(select(Rubric)):
            rubric=Rubric(name='AI Engineer Core',description='Balanced technical and behavioral interview rubric',criteria=[{'name':'Clarity','weight':1,'description':'Structured, direct communication'},{'name':'Technical depth','weight':2,'description':'Correct engineering reasoning'},{'name':'Evidence','weight':1,'description':'Metrics, experiments, and tradeoffs'}]); db.add(rubric); db.flush()
            for p,c in [('Design an ML system for a high-volume support assistant.','Technical'),('Tell us about a time an experiment failed and what you learned.','Behavioral'),('How do you make an AI system reliable and fair in production?','AI Safety')]: db.add(Question(prompt=p,category=c,difficulty='Intermediate',rubric_id=rubric.id))
            db.commit()
@app.get('/api/health')
def health(): return {'status':'ok','service':'hireiq-api','ai_provider':os.getenv('AI_PROVIDER','mock')}
@app.get('/api/questions',response_model=list[QuestionOut])
def questions(db:DBSession=Depends(get_db)): return db.scalars(select(Question).order_by(Question.id)).all()
@app.post('/api/questions',response_model=QuestionOut)
def create_question(payload:QuestionIn,db:DBSession=Depends(get_db)):
    q=Question(**payload.model_dump()); db.add(q); db.commit(); db.refresh(q); return q
@app.get('/api/rubrics',response_model=list[RubricOut])
def rubrics(db:DBSession=Depends(get_db)): return db.scalars(select(Rubric).order_by(Rubric.id)).all()
@app.post('/api/rubrics',response_model=RubricOut)
def create_rubric(payload:RubricIn,db:DBSession=Depends(get_db)):
    r=Rubric(name=payload.name,description=payload.description,criteria=[c.model_dump() for c in payload.criteria]); db.add(r); db.commit(); db.refresh(r); return r
@app.post('/api/sessions',response_model=SessionOut)
def create_session(payload:SessionIn,db:DBSession=Depends(get_db)):
    s=Session(**payload.model_dump()); db.add(s); db.commit(); db.refresh(s); return s
@app.get('/api/sessions',response_model=list[SessionOut])
def sessions(db:DBSession=Depends(get_db)): return db.scalars(select(Session).order_by(Session.created_at.desc())).all()
@app.get('/api/sessions/{session_id}',response_model=SessionDetail)
def session_detail(session_id:int,db:DBSession=Depends(get_db)):
    s=db.scalar(select(Session).options(joinedload(Session.responses).joinedload(Response.question)).where(Session.id==session_id))
    if not s: raise HTTPException(404,'Session not found')
    return s
@app.post('/api/sessions/{session_id}/responses',response_model=ResponseOut)
def add_response(session_id:int,question_id:int,transcript:str='',audio:UploadFile|None=File(default=None),db:DBSession=Depends(get_db)):
    s=db.get(Session,session_id); q=db.get(Question,question_id)
    if not s or not q: raise HTTPException(404,'Session or question not found')
    text=transcript.strip() or transcribe_audio(audio.filename if audio else None)
    rubric=db.get(Rubric,q.rubric_id) if q.rubric_id else None
    score, enrichment, rationale=evaluate(q,text,rubric)
    r=Response(session_id=session_id,question_id=question_id,transcript=text,score=score,sentiment=enrichment['sentiment'],confidence=enrichment['confidence'],keywords=enrichment['keywords'],rationale=rationale)
    db.add(r); s.status='in_progress'; db.commit(); db.refresh(r); return r
@app.post('/api/sessions/{session_id}/complete',response_model=SessionOut)
def complete(session_id:int,db:DBSession=Depends(get_db)):
    s=db.scalar(select(Session).options(joinedload(Session.responses)).where(Session.id==session_id))
    if not s: raise HTTPException(404,'Session not found')
    scores=[r.score for r in s.responses]; s.overall_score=round(sum(scores)/len(scores),2) if scores else 0; s.recommendation='Proceed' if s.overall_score>=7.2 else ('Hold' if s.overall_score>=5.5 else 'Reject'); s.status='completed'; db.commit(); db.refresh(s); return s
@app.get('/api/sessions/{session_id}/report')
def report(session_id:int,db:DBSession=Depends(get_db)):
    s=db.scalar(select(Session).options(joinedload(Session.responses).joinedload(Response.question)).where(Session.id==session_id))
    if not s: raise HTTPException(404,'Session not found')
    return StreamingResponse(build_report(s),media_type='application/pdf',headers={'Content-Disposition':f'attachment; filename=hireiq-{session_id}.pdf'})
