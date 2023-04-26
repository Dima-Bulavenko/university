import psycopg2
import pytest
from random import choice
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from university.models import mapper_registry
from university.app import app as my_app, Session
from university.models import Student, Group, Course, StudentCourse


DATABASE_NAME = "postgres"
DIALECT = 'postgresql'
USER = "postgres"
PASSWORD = "1111"
HOST = "localhost"
TEST_DB_NAME = 'test_db'
DRIVER = 'psycopg2'
POSTGRES_ENGINE = f"{DIALECT}+{DRIVER}://{USER}:{PASSWORD}@{HOST}/"

STUDENT_COUNT = 30
GROUP_COUNT = 3
COURSE_COUNT = 3


@pytest.fixture(scope='session', autouse=True)
def data_base():
    conn = psycopg2.connect(dbname=DATABASE_NAME,
                            user=USER,
                            password=PASSWORD,
                            host=HOST)
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
    cursor.close()
    conn.close()

    yield

    conn = psycopg2.connect(dbname=DATABASE_NAME,
                            user=USER,
                            password=PASSWORD,
                            host=HOST)
    cursor = conn.cursor()
    conn.autocommit = True
    cursor.execute(f"DROP DATABASE {TEST_DB_NAME}")
    cursor.close()
    conn.close()


@pytest.fixture(scope='session')
def engine():
    engine = create_engine(
        f"{DIALECT}+{DRIVER}://{USER}:{PASSWORD}@{HOST}/{TEST_DB_NAME}")
    print('create engine')
    yield engine

    engine.dispose()


@pytest.fixture
def tables(engine):
    mapper_registry.metadata.create_all(bind=engine)

    yield

    mapper_registry.metadata.drop_all(bind=engine)


@pytest.fixture
def session(engine):
    session = Session(bind=engine)

    yield session

    session.close()


@pytest.fixture(autouse=True)
def fill_database(tables, session):
    try:
        groups = [Group(name=f"AA-{i}{i}")
                  for i in range(1, GROUP_COUNT + 1)]
        session.add_all(groups)

        courses = [Course(name=f"course_{i}")
                   for i in range(COURSE_COUNT)]
        session.add_all(courses)
        session.commit()

        students = [Student(first_name=f"student_{i}",
                            last_name=f'student_{i}_{i}',
                            group_id=choice(groups).id)
                    for i in range(STUDENT_COUNT)]
        session.add_all(students)
        session.commit()

        student_course = [StudentCourse(student_id=s.id,
                                        course_id=choice(courses).id)
                          for s in students]
        session.add_all(student_course)
        session.commit()
    except Exception as ex:
        session.rollback()
        raise ex


@pytest.fixture
def app():
    my_app.config.update({
        "TESTING": True,
    })

    yield my_app


@pytest.fixture
def client(app):
    with app.test_request_context():
        yield app.test_client()


@pytest.fixture
def mock_session(session, monkeypatch):
    monkeypatch.setattr("university.app.session", session)



