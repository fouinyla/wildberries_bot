from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(30), nullable=False)
    tg_id = Column(BigInteger, nullable=False)
    tg_nickname = Column(String(50), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)


class Query(Base):
    __tablename__ = "queries"
    id = Column(Integer, primary_key=True)
    search_query = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class SEOquery(Base):
    __tablename__ = "SEO_queries"
    id = Column(Integer, primary_key=True)
    query_for_SEO = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class SearchPosition(Base):
    __tablename__ = "search_position"
    id = Column(Integer, primary_key=True)
    search_position_query = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)


class PriceSegmentation(Base):
    __tablename__ = "price_segmentations"
    id = Column(Integer, primary_key=True)
    query_for_price = Column(String(200))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    
class MonthSales(Base):
    __tablename__ = "month_sales"
    id = Column(Integer, primary_key=True)
    article = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    
class CardQueries(Base):
    __tablename__ = "card_queries"
    id = Column(Integer, primary_key=True)
    article = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
