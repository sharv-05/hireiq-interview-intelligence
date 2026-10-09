import os, re, math, json

from pathlib import Path
from .models import Question, Rubric

DEFAULT_TRANSCRIPTS=[
"I would start by clarifying the success metric, then build a small baseline and evaluate it with a held-out dataset. I would monitor latency, cost, drift, and fairness across relevant groups before shipping.",
"For a production ML service I would version data and models, add observability, use canary deployment, and define a rollback path. I would also document assumptions and failure modes for the team.",
"I communicate tradeoffs early, invite review from domain experts, and separate evidence from opinion. When an experiment fails, I write down what changed and use the result to narrow the next hypothesis."]

def transcribe_audio(filename:str|None=None)->str:
    # Production boundary: wire this function to faster-whisper/OpenAI Whisper.
    return DEFAULT_TRANSCRIPTS[hash(filename or 'demo') % len(DEFAULT_TRANSCRIPTS)]

def nlp_enrich(text:str):
    words=re.findall(r"[a-zA-Z]{4,}", text.lower())
    stop={'would','then','with','that','this','from','have','what','when','before','after','into','also','about'}
    keywords=[]
    for w in words:
        if w not in stop and w not in keywords: keywords.append(w)
    positive={'success','baseline','monitor','fairness','production','observability','review','evidence','document','rollback'}
    negative={'fail','failure','risk','drift','latency','cost'}
    score=(sum(w in positive for w in words)-0.4*sum(w in negative for w in words))/max(1,len(words)/10)
    sentiment=max(-1,min(1,score))
    confidence=max(0.35,min(0.96,0.45+0.03*len(words)+0.08*text.count('.')))
    return {'keywords':keywords[:8], 'sentiment':round(sentiment,3), 'confidence':round(confidence,3)}

def _llm_score(question:Question, transcript:str, rubric:Rubric|None):
    """Optional server-side OpenAI-compatible structured evaluator; failures fall back safely."""
    key=os.getenv('OPENAI_API_KEY')
    if os.getenv('AI_PROVIDER','mock').lower()!='openai' or not key:
        return None
    try:
        import httpx
        criteria=rubric.criteria if rubric else []
        prompt={'question':question.prompt,'rubric':criteria,'transcript':transcript}
        response=httpx.post('https://api.openai.com/v1/chat/completions',headers={'Authorization':f'Bearer {key}'},json={'model':os.getenv('OPENAI_MODEL','gpt-4o-mini'),'temperature':0,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':'You are a structured interview evaluator. Score only job-related evidence. Ignore names, accent, age, gender, ethnicity, disability, and all protected or proxy attributes. Return JSON with score (0-10) and rationale.'},{'role':'user','content':json.dumps(prompt)}]},timeout=30)
        response.raise_for_status()
        data=response.json(); return json.loads(data['choices'][0]['message']['content'])
    except Exception:
        return None

def evaluate(question:Question, transcript:str, rubric:Rubric|None):
    enrichment=nlp_enrich(transcript)
    criteria=rubric.criteria if rubric and rubric.criteria else [{'name':'Clarity','weight':1},{'name':'Technical depth','weight':1},{'name':'Evidence','weight':1}]
    signals={'clarity':min(10,4+len(transcript.split())/25),'technical':min(10,4+sum(k in transcript.lower() for k in ['model','data','api','metric','deploy','latency','test'])*0.8),'evidence':min(10,4+sum(k in transcript.lower() for k in ['baseline','monitor','measure','experiment','rollback'])*0.9)}
    scores=[]
    for c in criteria:
        key=c['name'].lower()
        base=next((v for k,v in signals.items() if k in key), 6.0)
        scores.append(base*float(c.get('weight',1)))
    score=round(max(0,min(10,sum(scores)/max(1,sum(float(c.get('weight',1)) for c in criteria)))),2)
    llm=_llm_score(question,transcript,rubric)
    if llm and isinstance(llm.get('score'),(int,float)):
        score=round(max(0,min(10,float(llm['score']))),2)
    rationale=f"Response shows {len(enrichment['keywords'])} relevant signals, a {enrichment['sentiment']:+.2f} sentiment polarity, and {enrichment['confidence']:.0%} confidence heuristic. Rubric alignment: {score}/10."
    if llm and llm.get('rationale'): rationale=str(llm['rationale'])
    return score, enrichment, rationale
