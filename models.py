import json

from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import sessionmaker, Session, declarative_base


engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/telegram_bot_db')
engine.connect()
print(engine)

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


class UserSubjects(Base):
    __tablename__ = 'user_subjects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True, unique=True)
    sub1 = Column(Integer, nullable=True)
    sub2 = Column(Integer, nullable=True)
    sub3 = Column(Integer, nullable=True)
    sub4 = Column(Integer, nullable=True)
    sub5 = Column(Integer, nullable=True)
    sub6 = Column(Integer, nullable=True)

Base.metadata.create_all(engine)
# Base.metadata.drop_all(bind=engine, tables=[UserSubjects.__table__])


session = Session(bind=engine)

# session.add(department)
# session.commit()
# deps: list = session.query(Vstup).distinct(Vstup.subjects).all()

# pprint(subjects)
#     if dep.avg_grade_for_contract != None and dep.avg_grade_for_budget != None:
#         print(dep.area, "\n",
#               dep.area_url, "\n",
#               dep.university, "\n",
#               dep.university_url, "\n",
#               dep.department, "\n",
#               dep.study_degree, "\n",
#               dep.depends_on, "\n",
#               dep.speciality, "\n",
#               dep.subjects, "\n",
#               dep.avg_grade_for_contract, "\n",
#               dep.avg_grade_for_budget)
#
# print(len(deps))