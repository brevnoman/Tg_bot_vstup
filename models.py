import json

from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker, declarative_base, Session

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/telegram_bot_db')
engine.connect()
session = sessionmaker()
session.configure(bind=engine)
Base = declarative_base()


class TextPickleType(TypeDecorator):
    """
    Custom Column type to store json in db
    """
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
    """
    Main model that store all information about specialities
    """
    __tablename__ = 'vstup_info'

    id = Column(Integer, primary_key=True)
    knowledge_area = Column(String, nullable=True)
    program = Column(String, nullable=True)
    depends_on = Column(String(254), nullable=True)
    study_degree = Column(String(254), nullable=True)
    area = Column(String(254), nullable=True)
    area_url = Column(String(254), nullable=True)
    university = Column(String(254), nullable=True)
    university_url = Column(String(254), nullable=True)
    department = Column(String(254), nullable=True)
    speciality = Column(String(254), nullable=True)
    subjects = Column(JSONB)
    avg_grade_for_budget = Column(Float(2), nullable=True)
    avg_grade_for_contract = Column(Float(2), nullable=True)


class UserSubjects(Base):
    """
    Model used to calculate average grade
    """
    __tablename__ = 'user_subjects'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True, unique=True)
    sub1 = Column(Integer, nullable=True)
    sub2 = Column(Integer, nullable=True)
    sub3 = Column(Integer, nullable=True)
    sub4 = Column(Integer, nullable=True)
    sub5 = Column(Integer, nullable=True)
    sub6 = Column(Integer, nullable=True)
    sub7 = Column(Integer, nullable=True)
    sub8 = Column(Integer, nullable=True)
    sub9 = Column(Integer, nullable=True)
    sub10 = Column(Integer, nullable=True)

    def set_subject_by_counter(self, counter, value):
        """
        Method that sets subject by counter
        """
        if counter == 1:
            self.sub1 = value
        if counter == 2:
            self.sub2 = value
        if counter == 3:
            self.sub3 = value
        if counter == 4:
            self.sub4 = value
        if counter == 5:
            self.sub5 = value
        if counter == 6:
            self.sub6 = value
        if counter == 7:
            self.sub7 = value
        if counter == 8:
            self.sub8 = value
        if counter == 9:
            self.sub9 = value
        if counter == 10:
            self.sub10 = value

    def get_subject_by_counter(self, counter):
        """
        Method that gets subject by counter
        """
        if counter == 1:
            return self.sub1
        if counter == 2:
            return self.sub2
        if counter == 3:
            return self.sub3
        if counter == 4:
            return self.sub4
        if counter == 5:
            return self.sub5
        if counter == 6:
            return self.sub6

    def set_default(self):
        """
        Method that resets all values to 0
        """
        self.sub1 = 0
        self.sub2 = 0
        self.sub3 = 0
        self.sub4 = 0
        self.sub5 = 0
        self.sub6 = 0
        self.sub7 = 0
        self.sub8 = 0
        self.sub9 = 0
        self.sub10 = 0


# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(engine)
#
# session = Session(bind=engine)
#
# all_objects = session.query(Vstup).count()
# print(all_objects)
# for one in all_objects:
#     print(
#         one.knowledge_area, "\n",
#         one.program, "\n",
#         one.area, "\n",
#         one.area_url, "\n",
#         one.university, "\n",
#         one.university_url, "\n",
#         one.department, "\n",
#         one.speciality, "\n",
#         one.subjects, "\n",
#         one.avg_grade_for_budget, "\n",
#         one.avg_grade_for_contract, "\n",
#     )