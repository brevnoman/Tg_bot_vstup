# import sqlalchemy.exc
# import psycopg2
# from psycopg2.extensions import  ISOLATION_LEVEL_AUTOCOMMIT
import json

from sqlalchemy import create_engine, Column, Integer, String, Float, ARRAY, Text
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import sessionmaker, Session, declarative_base


engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/telegram_bot_db')
engine.connect()

session = sessionmaker()
session.configure(bind=engine)
Base = declarative_base()


class TextPickleType(TypeDecorator):

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class Vstup(Base):
    __tablename__ = 'vstup_info'

    id = Column(Integer, primary_key=True)
    depends_on = Column(String(254), nullable=True)
    study_degree = Column(String(254), nullable=True)
    area = Column(String(254), nullable=True)
    area_url = Column(String(254), nullable=True)
    university = Column(String(254), nullable=True)
    university_url = Column(String(254), nullable=True)
    department = Column(String(254), nullable=True)
    speciality = Column(String(254), nullable=True)
    subjects = Column(TextPickleType())
    avg_grade_for_budget = Column(Float(2), nullable=True)
    avg_grade_for_contract = Column(Float(2), nullable=True)


Base.metadata.create_all(engine)

session = Session(bind=engine)

# session.add(department)
# session.commit()
# deps: Vstup = session.query(Vstup).all()
# print(len(deps))
# for dep in deps:
#     if dep.subjects:
#         print(dep.area,
#             dep.area_url,
#             dep.university,
#             dep.university_url,
#             dep.department,
#             dep.study_degree,
#             dep.depends_on,
#             dep.speciality,
#             dep.subjects,
#             dep.avg_grade_for_contract,
#             dep.avg_grade_for_budget)
# area_list = []
# data = session.query(Vstup).distinct()
# for i in data:
#     if i.area not in area_list:
#         area_list.append(i.area)
# print(area_list)