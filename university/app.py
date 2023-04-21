from flask import Flask, request, make_response
from flask_restful import Api, Resource
from models import Student, Group, Course, StudentCourse, engine
from sqlalchemy.orm import Session
from sqlalchemy import func


app = Flask(__name__)
api = Api(app, "/api/v1")
session = Session(bind=engine)


class StudentsApi(Resource):
    def post(self):
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            group_id = request.form.get('group_id')
            session.add(Student(first_name=first_name,
                                last_name=last_name,
                                group_id=group_id))
            session.commit()
            return make_response(
                {'message': f"Student {first_name} {last_name} was created"})
        except Exception as ex:
            session.rollback()
            return make_response({'message': f"{ex}"})


class StudentApi(Resource):
    def delete(self, student_id):
        try:

            student = session.query(Student).get(student_id)
            if not student:
                raise Exception(f"Student id '{student_id}' was not found")
            session.delete(student)
            session.commit()
            return make_response(
                {"message": f'Student with {student_id} was deleted'})

        except Exception as ex:
            session.rollback()
            return make_response({'error': f"{ex}"})


class GroupsApi(Resource):
    def get(self, stud_count):
        groups = (session.query(Group)
                  .outerjoin(Student)
                  .group_by(Group.id)
                  .having(func.count(Student.first_name) <= stud_count)
                  .all())

        return make_response(Group.create_dict_for_api(groups))


class CourseStudentsApi(Resource):
    def get(self, course_id):
        students = (session
                    .query(Student)
                    .select_from(Student)
                    .join(StudentCourse)
                    .join(Course)
                    .filter(Course.id == course_id)
                    .order_by(Student.first_name)
                    )

        return make_response(Student.create_dict_for_api(students))

    def put(self, course_id, student_id):
        try:
            course = session.get(Course, course_id)
            student = session.get(Student, student_id)
            if not course:
                raise Exception(f"Course id '{course_id}' does not exist")

            if not student:
                raise Exception(f"Student id '{student_id}' does not exist")

            session.add(StudentCourse(student_id=student.id,
                                      course_id=course.id))
            session.commit()
            return make_response(
                {"message": f"Student {student.first_name} was added to course {course.name}"})
        except Exception as ex:
            session.rollback()
            return make_response({"error": f"{ex}"}, 400)

    def delete(self, course_id, student_id):
        try:
            course = session.get(Course, course_id)
            student = session.get(Student, student_id)
            if not course:
                raise Exception(f"Course id '{course_id}' does not exist")

            if not student:
                raise Exception(f"Student id '{student_id}' does not exist")
            student_course = (session
                              .query(StudentCourse)
                              .filter(StudentCourse.student_id == student.id,
                                      StudentCourse.course_id == course.id)
                              .one())
            session.delete(student_course)
            session.commit()
            return make_response(
                {"message": f"Student {student.first_name} was deleted from course {course.name}"})
        except Exception as ex:
            session.rollback()
            return make_response({"error": f"{ex}"}, 400)


api.add_resource(GroupsApi,
                 '/groups/<int:stud_count>',
                 endpoint='groups_api')
api.add_resource(CourseStudentsApi,
                 '/courses/<int:course_id>/students',
                 endpoint='get_students_from_course')
api.add_resource(CourseStudentsApi,
                 '/courses/<int:course_id>/<int:student_id>',
                 endpoint='add_delete_course_for_student')
api.add_resource(StudentsApi,
                 "/students",
                 endpoint='students_api')
api.add_resource(StudentApi,
                 "/students/<int:student_id>",
                 endpoint='student_api')


if __name__ == "__main__":
    app.run(debug=True)
