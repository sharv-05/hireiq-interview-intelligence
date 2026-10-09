from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
class Criterion(BaseModel): name:str; weight:float=1; description:str=''
class RubricIn(BaseModel): name:str; description:str=''; criteria:list[Criterion]
class RubricOut(RubricIn): model_config=ConfigDict(from_attributes=True); id:int
class QuestionIn(BaseModel): prompt:str; category:str='Technical'; difficulty:str='Intermediate'; rubric_id:int|None=None
class QuestionOut(QuestionIn): model_config=ConfigDict(from_attributes=True); id:int
class SessionIn(BaseModel): candidate_name:str=Field(min_length=2); candidate_email:str=''; role:str='AI Engineer'
class ResponseOut(BaseModel): id:int; question_id:int; transcript:str; score:float; sentiment:float; confidence:float; keywords:list; rationale:str
class SessionOut(BaseModel): model_config=ConfigDict(from_attributes=True); id:int; candidate_name:str; candidate_email:str; role:str; status:str; overall_score:float|None; recommendation:str|None; created_at:datetime
class SessionDetail(SessionOut): responses:list[ResponseOut]=[]
