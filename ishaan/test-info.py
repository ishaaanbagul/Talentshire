"""
1. Service for Storing Test Information -> ishaan
Table                         Key Columns
tests                    test_id, test_name, created_by (FK→users), duration_minutes, status (enum)
test_questions     id, test_id (FK), question_id (FK), question_type (enum), order_index
"""


from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, Session
from pydantic import BaseModel
from typing import List
import enum

# Initialize FastAPI app
app = FastAPI()

# Database URL and Engine
DATABASE_URL = "sqlite:///./test.db"  # Adjust for your DB
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enum definitions
class TestStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    completed = "completed"

class QuestionTypeEnum(str, enum.Enum):
    multiple_choice = "multiple_choice"
    true_false = "true_false"
    short_answer = "short_answer"

# SQLAlchemy Models

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)

class Test(Base):
    __tablename__ = "tests"
    test_id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String, index=True)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    duration_minutes = Column(Integer)
    status = Column(Enum(TestStatusEnum))

    created_by_user = relationship("User", back_populates="tests")

class TestQuestion(Base):
    __tablename__ = "test_questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("tests.test_id"))
    question_id = Column(Integer)
    question_type = Column(Enum(QuestionTypeEnum))
    order_index = Column(Integer)

    test = relationship("Test", back_populates="questions")

# Relationships
User.tests = relationship("Test", back_populates="created_by_user")
Test.questions = relationship("TestQuestion", back_populates="test")

# Pydantic Schemas for Validation

class TestBase(BaseModel):
    test_name: str
    duration_minutes: int
    status: TestStatusEnum

class TestCreate(TestBase):
    pass

class Test(TestBase):
    test_id: int
    created_by: int

    class Config:
        orm_mode = True

class TestQuestionBase(BaseModel):
    question_id: int
    question_type: QuestionTypeEnum
    order_index: int

class TestQuestionCreate(TestQuestionBase):
    pass

class TestQuestion(TestQuestionBase):
    id: int
    test_id: int

    class Config:
        orm_mode = True

# CRUD Operations

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_test(db: Session, test: TestCreate, created_by: int):
    db_test = Test(test_name=test.test_name, 
                   duration_minutes=test.duration_minutes, 
                   status=test.status, 
                   created_by=created_by)
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def create_test_question(db: Session, test_question: TestQuestionCreate, test_id: int):
    db_test_question = TestQuestion(test_id=test_id, 
                                    question_id=test_question.question_id, 
                                    question_type=test_question.question_type, 
                                    order_index=test_question.order_index)
    db.add(db_test_question)
    db.commit()
    db.refresh(db_test_question)
    return db_test_question

def get_tests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Test).offset(skip).limit(limit).all()

def get_test_questions(db: Session, test_id: int):
    return db.query(TestQuestion).filter(TestQuestion.test_id == test_id).all()

# FastAPI Endpoints

@app.post("/tests/", response_model=Test)
def create_test_endpoint(test: TestCreate, db: Session = Depends(get_db)):
    user_id = 1  # Placeholder for user_id; In real-world, this would come from authentication
    return create_test(db=db, test=test, created_by=user_id)

@app.post("/tests/{test_id}/questions/", response_model=TestQuestion)
def create_test_question_endpoint(test_id: int, test_question: TestQuestionCreate, db: Session = Depends(get_db)):
    return create_test_question(db=db, test_question=test_question, test_id=test_id)

@app.get("/tests/", response_model=List[Test])
def get_tests_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_tests(db=db, skip=skip, limit=limit)

@app.get("/tests/{test_id}/questions/", response_model=List[TestQuestion])
def get_test_questions_endpoint(test_id: int, db: Session = Depends(get_db)):
    return get_test_questions(db=db, test_id=test_id)

# Database Setup (without creating tables, assuming they already exist)
Base.metadata.create_all(bind=engine)