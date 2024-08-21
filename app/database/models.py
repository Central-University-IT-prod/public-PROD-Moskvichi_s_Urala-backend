import uuid
from enum import Enum
from typing import List

from sqlalchemy import (JSON, Column, Date, DateTime, ForeignKey, Integer,
                        String, Table)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship
from werkzeug.security import check_password_hash, generate_password_hash


class MeetStatusEnum(Enum):
    CREATED = 'CREATED'
    IN_PROGRESS = 'IN_PROGRESS'
    ARRIVED = 'ARRIVED'
    DONE = 'DONE'
    CANCELED = 'CANCELED'


def generate_uuid():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    ...


employee_skills = Table(
    "employee_skills",
    Base.metadata,
    Column("employee_id", ForeignKey("employees.id", ondelete='CASCADE'), primary_key=True),
    Column("product_id", ForeignKey("products.id", ondelete='CASCADE'), primary_key=True),
)
product_documents = Table(
    "product_documents",
    Base.metadata,
    Column("document_id", ForeignKey("documents.id", ondelete='CASCADE'), primary_key=True),
    Column("product_id", ForeignKey("products.id", ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    phone = Column(String(20), nullable=False)

    jwt_id = Column(String, default=generate_uuid, unique=True)
    _password = Column("password", String, nullable=False)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str):
        if self._password != value:
            self._password = generate_password_hash(password=value)

    @property
    def rate(self):
        from app.database.requests import get_employee_rate
        return get_employee_rate(employee_id=self.id)

    def check_password(self, password: str):
        return check_password_hash(pwhash=self.password, password=password)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    phone = Column(String(20), nullable=False)

    work_location = Column(String)
    skills: Mapped[List['Product']] = relationship(secondary=employee_skills, back_populates='employees')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    description = Column(String(200), nullable=False)

    employees: Mapped[List['Employee']] = relationship(secondary=employee_skills, back_populates='skills')
    documents: Mapped[List['Document']] = relationship(secondary=product_documents, back_populates='products')

    def __str__(self) -> str:
        return self.name


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    life_time = Column(Integer, nullable=False)
    ref_url = Column(String, nullable=True)

    products: Mapped[List['Product']] = relationship(secondary=product_documents, back_populates='documents')

    def __str__(self) -> str:
        return self.name


class Meet(Base):
    __tablename__ = 'meets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(ForeignKey('users.id'))
    employee_id = Column(ForeignKey('employees.id'))
    product_id = Column(ForeignKey('products.id'))
    status = Column(PgEnum(MeetStatusEnum, name='meet_status_enum', create_type=True), nullable=False,
                    default=MeetStatusEnum.CREATED)

    date = Column(DateTime, nullable=False, index=True)
    address = Column(JSON)

    agent = Column(String(100))
    rate = Column(Integer)

    user: Mapped["User"] = relationship()
    employee: Mapped["Employee"] = relationship()
    product: Mapped["Product"] = relationship()


class UserDocument(Base):
    __tablename__ = 'userdocuments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('users.id'))
    document_id = Column(ForeignKey('documents.id'))
    expire = Column(Date, nullable=False)
