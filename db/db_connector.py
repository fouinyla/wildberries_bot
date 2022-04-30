import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.elements import and_, or_
from .models import *
from os import getenv


class Database:
    def __init__(self):
        engine = database.create_engine(getenv("DATABASE"))
        self.session = scoped_session(sessionmaker(bind=engine))

    def add_user(self, tg_id, tg_nickname, name, email, phone_number):
        with self.session() as session:
            with session.begin():
                user = User(
                    tg_id=tg_id,
                    tg_nickname=tg_nickname,
                    name=name,
                    email=email,
                    phone_number=phone_number
                )
                session.add(user)

    def get_user(self, tg_id):
        with self.session() as session:
            with session.begin():
                query = session\
                    .query(User)\
                    .filter(User.tg_id.__eq__(tg_id))\
                    .scalar()

                if query:
                    return dict(id=query.id, tg_nickname=query.tg_nickname, is_admin=query.is_admin)
                return False

    def add_search_query(self, search_query, user_id):
        with self.session() as session:
            with session.begin():
                query = Query(
                    search_query=search_query,
                    user_id=user_id
                )
                session.add(query)

    def add_SEO_query(self, query_for_SEO, user_id):
        with self.session() as session:
            with session.begin():
                query = SEOquery(
                    query_for_SEO=query_for_SEO,
                    user_id=user_id
                )
                session.add(query)