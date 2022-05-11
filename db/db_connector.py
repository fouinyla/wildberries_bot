import sqlalchemy as database
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy import func, inspect, text
from .models import *
from os import getenv
import xlsxwriter 
from datetime import date


class Database:
    def __init__(self):
        self.engine = database.create_engine(getenv("DATABASE"))
        self.session = scoped_session(sessionmaker(bind=self.engine))

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
                    .scalar()  # scalar?

                if query:
                    return dict(id=query.id, tg_nickname=query.tg_nickname, is_admin=query.is_admin)
                else:
                    return False

    def add_search_query(self, search_query, user_id):
        with self.session() as session:
            with session.begin():
                query = Query(
                    search_query=search_query,
                    user_id=user_id
                )
                session.add(query)

    def add_SEO_query(self, query_for_SEO, tg_id):
        with self.session() as session:
            with session.begin():
                user_id = session\
                    .query(User.id)\
                    .filter(User.tg_id.__eq__(tg_id))\
                    .scalar()

                query = SEOquery(
                    query_for_SEO=query_for_SEO,
                    user_id=user_id
                )
                session.add(query)

    def get_number_of_users(self):
        with self.session() as session:
            with session.begin():
                number_of_users = session\
                                .query(func.count(User.id))\
                                .scalar()
                return number_of_users

    def get_data_from_db(self):
        today_date = date.today()
        file_name = f'db_damp_{today_date}.xlsx'
        try:
            workbook = xlsxwriter.Workbook(file_name)
            inspector = inspect(self.engine)
            with self.engine.connect() as connection:
                for table_name in inspector.get_table_names()[-1::-1]:
                    worksheet = workbook.add_worksheet(name=table_name)
                    for column_index, column in enumerate(inspector.get_columns(table_name)):
                        worksheet.write(0, column_index, column['name'])
                    result = connection.execute(text(f'select * from {table_name}'))
                    for row_index, data in enumerate(result, start=1):
                        worksheet.write_row(row_index, 0, data)
        finally:
            workbook.close()
        return file_name
