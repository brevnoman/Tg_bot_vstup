# import sqlalchemy.exc
# import psycopg2
# from psycopg2.extensions import  ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base


# try:
engine = create_engine('postgresql+psycopg2://admin:admin@localhost/telegram_bot_db')
engine.connect()
print(engine)
# except sqlalchemy.exc.OperationalError:
#     connection = psycopg2.connect(user="postgres", password="postgres")
#     connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#
#     cursor = connection.cursor()
#     create_user = cursor.execute("CREATUSER admin WITH PASSWORD admin ALTER ROLE admin SAT client_encoding TO 'utf-8'")
#     sql_create_database = cursor.execute("create database telegram_bot_db with owner admin")
#     cursor.close()
#     connection.close()
#     engine = create_engine("postgresql+psycopg2://admin:admin@localhost/telegram_bot_db")
#     engine.connect()

session = sessionmaker()
session.configure(bind=engine)
Base = declarative_base()


class Vstup(Base):
    __tablename__ = 'vstup_info'

    id = Column(Integer, primary_key=True)
    aria = Column(String)
    aria_url = Column(String)
    university = Column(String)
    university_url = Column(String)
    faculty = Column(String)
    speciality = Column(String)
    first_main_subject = Column(String)
    first_main_subject_grade_coefficient = Column(Float)
    second_main_subject = Column(String)
    second_main_subject_grade_coefficient = Column(Float)
    third_subject = Column(String)
    third_subject_grade_coefficient = Column(Float)
    school_certificate_coefficient = Column(Float)
    license_places = Column(Integer)
    contract_places = Column(Integer)
    avg_grade_for_budget = Column(Float)
    avg_grade_for_contract = Column(Float)


# class User_Grades(Base):
#     __tablename__ = "user_grade"
#
#     id = Column(Integer, primary_key=True)
    # here i will add all subjects as separated column

# Base.metadata.create_all(engine)