import os
from celery import Celery
celery_app=Celery('hireiq',broker=os.getenv('REDIS_URL','redis://localhost:6379/0'),backend=os.getenv('REDIS_URL','redis://localhost:6379/0'))
@celery_app.task(bind=True,max_retries=2)
def process_response(self, session_id:int, response_id:int):
    # Hook for Whisper + LLM processing in a production worker.
    return {'session_id':session_id,'response_id':response_id,'status':'processed'}
