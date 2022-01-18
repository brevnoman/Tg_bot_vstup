import json

from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy import TypeDecorator
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine('postgresql+psycopg2://admin:admin@localhost/telegram_bot_db')
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
    """
    Model used to calculate average grade
    set_default: Method that resets all values to 0
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

    def set_default(self):
        self.sub1 = 0
        self.sub2 = 0
        self.sub3 = 0
        self.sub4 = 0
        self.sub5 = 0
        self.sub6 = 0


Base.metadata.create_all(engine)
