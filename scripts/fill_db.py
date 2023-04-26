from faker import Faker
from university.models import Group, StudentCourse, Student, Course, engine, mapper_registry
from sqlalchemy import func
from sqlalchemy.orm import Session

session = Session(bind=engine)

fake = Faker()

GROUP_COUNT = 10
STUDENT_COUNT = 200
COURSE_COUNT = 10
MIN_STUDENTS_PER_GROUP = 10
MAX_STUDENTS_PER_GROUP = 30
MIN_COURSES_PER_STUDENT = 1
MAX_COURSES_PER_STUDENT = 3


def fill_group():
    for _ in range(GROUP_COUNT):
        group_name = fake.bothify(text='??-%#', letters='ASDFGH')
        session.add(Group(name=group_name))


def fill_course():
    for subj in range(COURSE_COUNT):
        course_name = fake.word()
        description = fake.text()
        session.add(Course(name=course_name,
                           description=description))


def fill_student():
    for _ in range(STUDENT_COUNT):
        name = fake.first_name()
        surname = fake.last_name()
        session.add(Student(first_name=name,
                            last_name=surname))


def add_group_for_student():
    students = iter(session.query(Student))
    for group in fake.random_sample(
            elements=tuple(
                session.query(Group)),
            length=7):
        try:
            for _ in range(fake.random_int(min=MIN_STUDENTS_PER_GROUP,
                                           max=MAX_STUDENTS_PER_GROUP)):
                student = next(students)
                student.group_id = group.id
                session.add(student)
        except StopIteration:
            break


def add_courses_for_students():
    for stud in session.query(Student):
        stud_courses = (session
                        .query(Course)
                        .order_by(func.random())
                        .limit(fake.random_int(min=MIN_COURSES_PER_STUDENT,
                                               max=MAX_COURSES_PER_STUDENT))
                        .all())
        for course in stud_courses:
            session.add(StudentCourse(student_id=stud.id,
                                      course_id=course.id))


if __name__ == "__main__":
    try:
        mapper_registry.metadata.drop_all(bind=engine)
        mapper_registry.metadata.create_all(bind=engine)
        fill_group()
        fill_student()
        fill_course()
        add_group_for_student()
        add_courses_for_students()
        session.commit()
    except Exception as ex:
        print(f"Exception: {ex}")
        session.rollback()
