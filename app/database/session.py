from app.config import ECHO, ENGINE
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base

engine = create_engine(ENGINE, echo=ECHO)
db_session = sessionmaker(bind=engine)


def init_db():
    with engine.begin() as conn:
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
