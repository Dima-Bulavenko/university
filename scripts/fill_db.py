from faker import Faker
from university.models import Group, StudentCourse, Student, Course, engine, mapper_registry
from sqlalchemy.orm import Session

session = Session(bind=engine)

fake = Faker()


def fill_group():
    for _ in range(10):
        group_name = fake.bothify(text='??-%#', letters='ASDFGH')
        session.add(Group(name=group_name))


def fill_course():
    subjects = [
        'math',
        'biology',
        'history',
        'physics',
        'literature',
        'chemistry',
        'psychology',
        'computer science',
        'economics',
        'music']

    for subj in subjects:
        course_name = subj
        description = fake.text()
        session.add(Course(name=course_name,
                           description=description))


def fill_student():
    for _ in range(200):
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
            for _ in range(fake.random_int(min=10, max=30)):
                student = next(students)
                student.group_id = group.id
                session.add(student)
        except StopIteration:
            break


def add_courses_for_students():
    for stud in session.query(Student):
        stud_courses = (session
                        .query(Course)
                        .limit(fake.random_int(min=1, max=3))
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