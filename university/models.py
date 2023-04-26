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
                Column('group_id', ForeignKey('group.id', ondelete="SET NULL")),
                Column('first_name', String(100), nullable=False),
                Column('last_name', String(100), nullable=False)
                )

course = Table('course', mapper_registry.metadata,
               Column('id', Integer(), primary_key=True),
               Column('name', String(100), nullable=False, unique=True),
               Column('description', Text))

student_course = Table('student_course', mapper_registry.metadata,
                       Column('id', Integer(), primary_key=True),
                       Column('student_id', ForeignKey('student.id',
                                                       ondelete="CASCADE")),
                       Column('course_id', ForeignKey('course.id',
                                                      ondelete="CASCADE")),
                       UniqueConstraint('student_id', 'course_id',
                                        name='unique_student_course')
                       )


class Base:
    def as_dict(self):
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns}

    @classmethod
    def create_dict_for_api(cls, query) -> dict:
        try:
            data = []
            for obj in query:
                data.append(obj.as_dict())
            return {f"{cls.__table__}": data}
        except AttributeError as ex:
            print(ex)
            return {
                "message": f"query can't contains {type(obj)} type, only {type(cls)}"}


class Group(Base):
    pass


class Student(Base):
    pass


class Course(Base):
    pass


class StudentCourse(Base):
    pass


mapper_registry.map_imperatively(Group, group)
mapper_registry.map_imperatively(Student, student)
mapper_registry.map_imperatively(Course, course)
mapper_registry.map_imperatively(StudentCourse, student_course)
