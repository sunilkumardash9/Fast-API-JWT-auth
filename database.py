from sqlalchemy import create_engine, Column, Integer, String, TEXT
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///user_database.db")

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class user_details(Base):
    __tablename__ = 'user_details_table'
    email = Column(String(30), primary_key = True)
    name = Column(String(256))
    password_hashed = Column(String(40))

class user_blogs(Base):
    __tablename__ = 'User_blogs'
    id = Column(Integer, primary_key = True)
    user_email = Column(String, )
    title = Column(TEXT)
    body = Column(TEXT)

