# import sqlalchemy.exc
# import psycopg2
# from psycopg2.extensions import  ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, Column, Integer, String, Float, ARRAY
from sqlalchemy.orm import sessionmaker, Session, declarative_base


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
    area = Column(String(254), nullable=True)
    area_url = Column(String(254), nullable=True)
    university = Column(String(254), nullable=True)
    university_url = Column(String(254), nullable=True)
    department = Column(String(254), nullable=True)
    speciality = Column(String(254), nullable=True)
    first_main_subject = Column(String(254), nullable=True)
    first_main_subject_grade_coefficient = Column(Float(2), nullable=True)
    second_main_subject = Column(String(254), nullable=True)
    second_main_subject_grade_coefficient = Column(Float(2), nullable=True)
    third_subject = Column(ARRAY(item_type=String, as_tuple=False), nullable=True)
    third_subject_grade_coefficient = Column(Float(2), nullable=True)
    school_certificate_coefficient = Column(Float(2), nullable=True)
    course_certificate_grade_coefficient = Column(Float(2), nullable=True)
    avg_grade_for_budget = Column(Float(2), nullable=True)
    avg_grade_for_contract = Column(Float(2), nullable=True)


# class User_Grades(Base):
#     __tablename__ = "user_grade"
#
#     id = Column(Integer, primary_key=True)
#     user_session = Column(Integer, unique=True)
#     ukrainian = Column(Float)
#     ukrainian_and_literature = Column(Float)
#     biology = Column(Float)
#     foreign_language = Column(Float)
#     ukrainian_history = Column(Float)
#     math = Column(Float)
#     geography = Column(Float)
#     physics = Column(Float)
#     chemistry = Column(Float)

Base.metadata.create_all(engine)

department = Vstup(area="Запорізька область",
                   area_url="https://vstup.osvita.ua/r9/",
                   university='Національний університет "Запорізька політехніка"',
                   university_url="https://vstup.osvita.ua/r9/91/",
                   department='Механічна інженерія',
                   speciality='134 Авіаційна та ракетно-космічна техніка',
                    first_main_subject='Українська мова ',
                    first_main_subject_grade_coefficient=0.20,
                    second_main_subject='Математика ',
                    second_main_subject_grade_coefficient=0.30,
                    course_certificate_grade_coefficient=0.05,
                    third_subject=['Іноземна мова* ', 'Історія України* ', 'Біологія* '],
                    third_subject_grade_coefficient=0.35,
                    school_certificate_coefficient=0.10,
                    avg_grade_for_budget=142.20,
                    avg_grade_for_contract=151.67
                   )

session = Session(bind=engine)
# session.add(department)
# session.commit()
# dep = session.query(Vstup).first()
# session.delete(dep)
# session.commit()