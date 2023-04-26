from university.models import Student, Group, Course, StudentCourse
from flask import url_for
from university.tests.conftest import STUDENT_COUNT


def test_students_api_post(client, session, mock_session):
    data = {'first_name': 'student_test',
            'last_name': 'student_test'}

    response = client.post(url_for("students_api"), data=data)
    new_count_student = session.query(Student).count()

    assert new_count_student == STUDENT_COUNT + 1
    assert response.status_code == 200
    assert response.json.get('message') == f"Student {data['first_name']}" \
                                           f" {data['last_name']} was created"
    assert response.content_type == 'application/json'


def test_students_api_post_not_valid_form(client, session, mock_session):
    data = {'last_name': 'student_test'}

    response = client.post(url_for("students_api"), data=data)
    new_count_student = session.query(Student).count()

    assert new_count_student == STUDENT_COUNT
    assert response.status_code == 400
    assert response.json.get('message') == '400 Bad Request: The browser' \
                                           ' (or proxy) sent a request that' \
                                           ' this server could not understand.'
    assert response.content_type == 'application/json'


def test_student_api_delete(client, session, mock_session):
    student_id = 3
    url = url_for("student_api", student_id=student_id)

    response = client.delete(url)
    new_count_student = session.query(Student).count()

    assert session.get(Student, student_id) is None
    assert new_count_student == STUDENT_COUNT - 1
    assert response.status_code == 200
    assert response.json.get(
        'message') == f'Student with {student_id} was deleted'
    assert response.content_type == 'application/json'


def test_student_api_delete_not_valid_id(client, session, mock_session):
    student_id = 0
    url = url_for("student_api", student_id=student_id)
    response = client.delete(url)
    new_count_student = session.query(Student).count()

    assert new_count_student == STUDENT_COUNT
    assert response.status_code == 400
    assert response.json.get(
        'message') == f"Student id '{student_id}' was not found"
    assert response.content_type == 'application/json'


def test_groups_api_get(client, session, mock_session):
    student_count = 8
    url = url_for("groups_api", stud_count=student_count)
    response = client.get(url)

    assert response.status_code == 200
    assert 'group' in response.json
    assert response.content_type == 'application/json'

    for group in response.json["group"]:
        group_id = group['id']
        students_in_group = (session
                             .query(Student)
                             .filter(Student.group_id == group_id)
                             .count())
        assert students_in_group <= student_count


def test_course_students_get(client, session, mock_session):
    course_id = 1
    url = url_for("get_students_from_course", course_id=course_id)
    response = client.get(url)

    assert response.status_code == 200
    assert 'student' in response.json
    assert response.content_type == 'application/json'


def test_course_students_post(client, session, mock_session):
    course_id = 1
    new_student = Student(first_name='student_test',
                          last_name='student_test')
    session.add(new_student)
    session.commit()
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=new_student.id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.post(url)
    new_count_student_course = session.query(StudentCourse).count()
    course_name = session.get(Course, course_id).name

    assert response.status_code == 200
    assert 'message' in response.json
    assert response.json['message'] == f"Student {new_student.first_name} " \
                                       f"was added to course {course_name}"
    assert new_count_student_course == old_count_student_course + 1
    assert response.content_type == 'application/json'


def test_course_students_post_invalid_course_id(client, session, mock_session):
    course_id = 0
    new_student = Student(first_name='student_test',
                          last_name='student_test')
    session.add(new_student)
    session.commit()
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=new_student.id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.post(url)
    new_count_student_course = session.query(StudentCourse).count()

    assert response.status_code == 400
    assert 'message' in response.json
    assert response.content_type == 'application/json'
    assert new_count_student_course == old_count_student_course
    assert response.json['message'] == f"Course id '{course_id}' does not exist"


def test_course_students_post_invalid_student_id(
        client, session, mock_session):
    course_id = 1
    student_id = 0
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=student_id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.post(url)
    new_count_student_course = session.query(StudentCourse).count()

    assert response.status_code == 400
    assert 'message' in response.json
    assert response.content_type == 'application/json'
    assert new_count_student_course == old_count_student_course
    assert response.json['message'] == f"Student id '{student_id}' does not exist"


def test_course_students_delete(client, session, mock_session):
    student_course = session.get(StudentCourse, 1)
    student_id = student_course.student_id
    course_id = student_course.course_id
    student_name = session.get(Student, student_id).first_name
    course_name = session.get(Course, course_id).name
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=student_id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.delete(url)
    new_count_student_course = session.query(StudentCourse).count()

    assert response.status_code == 200
    assert 'message' in response.json
    assert response.content_type == 'application/json'
    assert new_count_student_course == old_count_student_course - 1
    assert response.json['message'] == f"Student {student_name}" \
                                       f" was deleted from course {course_name}"


def test_course_students_delete_invalid_course_id(
        client, session, mock_session):
    course_id = 0
    student_id = 1
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=student_id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.delete(url)
    new_count_student_course = session.query(StudentCourse).count()

    assert response.status_code == 400
    assert 'message' in response.json
    assert response.content_type == 'application/json'
    assert new_count_student_course == old_count_student_course
    assert response.json['message'] == f"Course id '{course_id}' does not exist"


def test_course_students_delete_invalid_student_id(
        client, session, mock_session):
    course_id = 1
    student_id = 0
    url = url_for("add_delete_course_for_student",
                  course_id=course_id,
                  student_id=student_id)
    old_count_student_course = session.query(StudentCourse).count()
    response = client.delete(url)
    new_count_student_course = session.query(StudentCourse).count()

    assert response.status_code == 400
    assert 'message' in response.json
    assert response.content_type == 'application/json'
    assert new_count_student_course == old_count_student_course
    assert response.json['message'] == f"Student id '{student_id}' does not exist"
