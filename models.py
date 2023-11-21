from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Time,
    Numeric,
    Text,
    LargeBinary,
    delete,
    select,
    func,
)
from sqlalchemy.orm import sessionmaker, declarative_base, aliased

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    given_name = Column(String(255))
    surname = Column(String(255))
    city = Column(String(255))
    phone_number = Column(String(15), unique=True)
    profile_description = Column(Text)
    password = Column(String(255))


class Caregiver(Base):
    __tablename__ = "caregiver"
    caregiver_user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    photo = Column(LargeBinary)
    gender = Column(String(1))
    caregiving_type = Column(String(255))
    hourly_rate = Column(Numeric(5, 2))


class Member(Base):
    __tablename__ = "member"
    member_user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    house_rules = Column(Text)


class Address(Base):
    __tablename__ = "address"
    member_user_id = Column(
        Integer, ForeignKey("member.member_user_id"), primary_key=True
    )
    house_number = Column(String(255))
    street = Column(String(255))
    town = Column(String(255))


class Job(Base):
    __tablename__ = "job"
    job_id = Column(Integer, primary_key=True)
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    required_caregiving_type = Column(String(255))
    other_requirements = Column(Text)
    date_posted = Column(Date)


class JobApplication(Base):
    __tablename__ = "job_application"
    job_application_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"))
    job_id = Column(Integer, ForeignKey("job.job_id"))
    date_applied = Column(Date)


class Appointment(Base):
    __tablename__ = "appointment"
    appointment_id = Column(Integer, primary_key=True)
    caregiver_user_id = Column(Integer, ForeignKey("caregiver.caregiver_user_id"))
    member_user_id = Column(Integer, ForeignKey("member.member_user_id"))
    appointment_date = Column(Date)
    appointment_time = Column(Time)
    work_hours = Column(Integer)
    status = Column(String(255))
