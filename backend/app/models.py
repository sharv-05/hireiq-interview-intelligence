from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base
class Question(Base):
    __tablename__='questions'
    id:Mapped[int]=mapped_column(primary_key=True)
    prompt:Mapped[str]=mapped_column(Text)
    category:Mapped[str]=mapped_column(String(80), default='Technical')
    difficulty:Mapped[str]=mapped_column(String(30), default='Intermediate')
    rubric_id:Mapped[int|None]=mapped_column(ForeignKey('rubrics.id'), nullable=True)
    rubric=relationship('Rubric', back_populates='questions')
class Rubric(Base):
    __tablename__='rubrics'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120), unique=True)
    description:Mapped[str]=mapped_column(Text, default='')
    criteria:Mapped[list]=mapped_column(JSON, default=list)
    questions=relationship('Question', back_populates='rubric')
class Session(Base):
    __tablename__='sessions'
    id:Mapped[int]=mapped_column(primary_key=True)
    candidate_name:Mapped[str]=mapped_column(String(120))
    candidate_email:Mapped[str]=mapped_column(String(180), default='')
    role:Mapped[str]=mapped_column(String(120))
    status:Mapped[str]=mapped_column(String(30), default='in_progress')
    overall_score:Mapped[float|None]=mapped_column(Float, nullable=True)
    recommendation:Mapped[str|None]=mapped_column(String(30), nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    responses=relationship('Response', back_populates='session', cascade='all, delete-orphan')
class Response(Base):
    __tablename__='responses'
    id:Mapped[int]=mapped_column(primary_key=True)
    session_id:Mapped[int]=mapped_column(ForeignKey('sessions.id'))
    question_id:Mapped[int]=mapped_column(ForeignKey('questions.id'))
    transcript:Mapped[str]=mapped_column(Text, default='')
    score:Mapped[float]=mapped_column(Float, default=0)
    sentiment:Mapped[float]=mapped_column(Float, default=0)
    confidence:Mapped[float]=mapped_column(Float, default=0)
    keywords:Mapped[list]=mapped_column(JSON, default=list)
    rationale:Mapped[str]=mapped_column(Text, default='')
    created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    session=relationship('Session', back_populates='responses')
    question=relationship('Question')
