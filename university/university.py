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


api.add_resource(GroupsApi, '/groups/<int:stud_count>', endpoint='groups_api')
api.add_resource(CourseStudentsApi,
                 '/courses/<int:course_id>/students',
                 endpoint='course_students_api')
api.add_resource(StudentsApi, "/students", endpoint='students_api')


if __name__ == "__main__":
    app.run(debug=True)
