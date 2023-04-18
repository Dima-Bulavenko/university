from sqlalchemy import (create_engine, Table,
                        Column, Integer, String,
                        ForeignKey, Text, UniqueConstraint,
                        CheckConstraint,)
from sqlalchemy.orm import registry

mapper_registry = registry()

engine = create_engine(
    "postgresql+psycopg2://postgres:1111@localhost/university")

group = Table('group', mapper_registry.metadata,
              Column('id', Integer(), primary_key=True),
              Column('name', String(100), nullable=False, unique=True),
              CheckConstraint("name ~ '^[A-Z][A-Z]-[1-9][0-9]$'",
                              name='name_check')
              )

student = Table('student', mapper_registry.metadata,
                Column('id', Integer(), primary_key=True),
                Column('group_id', ForeignKey('group.id')),
                Column('first_name', String(100), nullable=False),
                Column('last_name', String(100), nullable=False)
                )

course = Table('course', mapper_registry.metadata,
               Column('id', Integer(), primary_key=True),
               Column('name', String(100), nullable=False, unique=True),
               Column('description', Text))

student_course = Table('student_course', mapper_registry.metadata,
                       Column('id', Integer(), primary_key=True),
                       Column('student_id', ForeignKey('student.id')),
                       Column('course_id', ForeignKey('course.id')),
                       UniqueConstraint('student_id', 'course_id',
                                        name='unique_student_course')
                       )


class Group:
    pass


class Student:
    pass


class Course:
    pass


class StudentCourse:
    pass


mapper_registry.map_imperatively(Group, group)
mapper_registry.map_imperatively(Student, student)
mapper_registry.map_imperatively(Course, course)
mapper_registry.map_imperatively(StudentCourse, student_course)
