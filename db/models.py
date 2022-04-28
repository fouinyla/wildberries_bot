from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    tg_id = Column(Integer, nullable=False)
    tg_nickname = Column(String, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    search_query = Column(String)
    user_id = Column(Integer, nullable=False)

# this class (table) will be changed
class Subquery(Base):
    __tablename__ = "subqueries"
    id = Column(Integer, primary_key=True)
    subquery = Column(String)
    query_id = Column(Integer, nullable=False)
