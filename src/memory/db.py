from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from src.config.settings import DB_FILE

Base = declarative_base()

class Interaction(Base):
    __tablename__ = 'interactions'
    id = Column(Integer, primary_key=True)
    channel = Column(String(50)) # telegram, discord, heartbeat
    user_id = Column(String(100))
    prompt = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

class MemoryChunk(Base):
    __tablename__ = 'memory_chunks'
    id = Column(Integer, primary_key=True)
    file_path = Column(String(255))
    content = Column(Text)
    embedding = Column(Text) # JSON string or binary representation if using vectors
    last_updated = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = 'user_profiles'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True)
    preferences = Column(Text) # JSON blob
    last_seen = Column(DateTime, default=datetime.utcnow)

engine = create_engine(f"sqlite:///{DB_FILE}")
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
