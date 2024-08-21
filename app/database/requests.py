from datetime import datetime, timedelta

from sqlalchemy import desc, select, update

from app.database.models import (Document, Employee, Meet, Product, User, generate_uuid,
                                 UserDocument, employee_skills, product_documents, MeetStatusEnum)
from app.database.session import db_session


def get_user_by_id(user_id):
    with db_session() as session:
        user = session.scalar(select(User).where(User.id == user_id))

        return user


def get_user_by_jwt(jwt):
    with db_session() as session:
        user = session.scalar(select(User).where(User.jwt_id == jwt))

        return user


def get_user_by_phone(phone):
    with db_session() as session:
        user = session.scalar(select(User).where(User.phone == phone))

        return user


def get_user_meets(user_id, status: list):
    """
    @user_id: id of user
    @offset: offset for pagination
    @limit: max meets count
    @status: list of available statuses
    example: [MeetStatusEnum.CREATED, MeetStatusEnum.ARRIVED]
    """

    with db_session() as session:
        meets = session.scalars(
            select(Meet).where(Meet.user_id == user_id, Meet.status.in_([i.value for i in status])).order_by(
                desc(Meet.date)))

        return list(meets)


def get_employee(employee_id):
    with db_session() as session:
        employee = session.scalar(select(Employee).where(Employee.id == employee_id))

        return employee


def get_document_by_id(document_id):
    with db_session() as session:
        document = session.scalar(select(Document).where(Document.id == document_id))

        return document


def get_product_by_id(product_id):
    with db_session() as session:
        product = session.scalar(select(Product).where(Product.id == product_id))

        return product


def get_user_documents(user_id):
    with db_session() as session:
        documents = session.scalars(
            select(UserDocument).where(UserDocument.user_id == user_id, UserDocument.expire > datetime.now().date()))
        return list(documents)


def get_last_user_locations(user_id, limit=5):
    with db_session() as session:
        addresses = session.scalars(
            select(Meet.address).where(Meet.user_id == user_id).order_by(desc(Meet.date)).limit(limit))

        return list(addresses)


def get_employees_busy_time(employees: list):
    with db_session() as session:
        data = session.query(Meet.id, Meet.date).where(Meet.employee_id.in_(employees),
                                                       Meet.status.in_([MeetStatusEnum.CREATED,
                                                                        MeetStatusEnum.IN_PROGRESS,
                                                                        MeetStatusEnum.ARRIVED])).all()
        dates = {}
        for a, b in data:
            if b in dates:
                dates[b].append(a)
            else:
                dates[b] = [a]
        buff = {}
        for a, b in dates.items():
            if len(b) < len(employees):
                continue
            key = a.strftime("%Y-%m-%d")
            if key not in buff:
                buff[key] = [f"{a.strftime('%H:00')} - {(a + timedelta(hours=1)).strftime('%H:00')}"]
            else:
                buff[key].append(f"{a.strftime('%H:00')} - {(a + timedelta(hours=1)).strftime('%H:00')}")

        return buff


def get_busy_employees(date):
    with db_session() as session:
        employees = session.scalars(
            select(Employee.id).join(Meet, Meet.employee_id == Employee.id).where(Meet.date == date))
        return set(employees)


def get_city_employees(city, product_id):
    with db_session() as session:
        employees = session.scalars(
            select(Employee.id).join(employee_skills, employee_skills.c.employee_id == Employee.id).where(
                Employee.work_location == city,
                employee_skills.c.product_id == product_id))

        return list(employees)


def create_meet(user_id, product_id, lat, lon, address, date: datetime, agent, employee_id):
    with db_session() as session:
        meet = Meet(user_id=user_id, product_id=product_id, date=date, agent=agent,
                    address=dict(lat=lat, lon=lon, name=address), employee_id=employee_id)
        session.add(meet)
        session.commit()

        session.refresh(meet)
        return meet


def set_rate_meet(meet_id, rate):
    with db_session() as session:
        session.execute(update(Meet).where(Meet.id == meet_id).values(rate=rate))
        session.commit()


def get_employee_rate(employee_id):
    with db_session() as session:
        rates = session.scalars(select(Meet.rate).where(Meet.employee_id == employee_id, Meet.rate is not None))

        return sum(rates) / len(rates)


def create_user(first_name, last_name, phone, password):
    with db_session() as session:
        user = User(first_name=first_name, last_name=last_name, phone=phone, password=password)
        session.add(user)
        session.commit()

        session.refresh(user)
        return user


def get_all_products():
    with db_session() as session:
        products = session.scalars(select(Product))
        return list(products)


def get_all_documents():
    with db_session() as session:
        documents = session.scalars(select(Document))

        return list(documents)


def change_meet_status(meet_id, status):
    with db_session() as session:
        session.execute(update(Meet).where(Meet.id == meet_id).values(status=status))
        session.commit()


def change_meet_date(meet_id, date):
    with db_session() as session:
        session.execute(update(Meet).where(Meet.id == meet_id).values(date=date))
        session.commit()


def get_meet_by_id(meet_id):
    with db_session() as session:
        meet = session.scalar(select(Meet).where(Meet.id == meet_id))

        return meet


def get_product_documents(product_id):
    with db_session() as session:
        documents = session.scalars(
            select(product_documents.c.document_id).where(product_documents.c.product_id == product_id))

        return list(documents)


def set_user_documents(user_id, documents: list):
    with db_session() as session:
        for document_id in documents:
            life_time = get_document_by_id(document_id=document_id).life_time
            expire = datetime.now() + timedelta(days=life_time)

            user_doc = UserDocument(user_id=user_id, document_id=document_id, expire=expire)
            session.add(user_doc)

        session.commit()


def revoke_user_jwt(user_id):
    with db_session() as session:
        session.execute(update(User).where(User.id == user_id).values(jwt_id=generate_uuid()))
        session.commit()
