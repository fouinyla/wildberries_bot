from numpy import unsignedinteger
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Boolean, BigInteger
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    tg_id = Column(BigInteger, nullable=False)
    tg_nickname = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    search_query = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class SEOquery(Base):
    __tablename__ = "SEO_queries"
    id = Column(Integer, primary_key=True)
    query_for_SEO = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
