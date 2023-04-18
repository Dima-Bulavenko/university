# Project's plan



## Steps

### Database
1. Create database with tables "Group, Student, Course" using SQLalchemy ORM
#### Tables' structure
group: 
    id Integer primary key
    name Varchar(100) NOT NULL UNIQUE
    CheckConstraint("name ~ '^[A-Z][A-Z]-[1-9][0-9]$'")

student:
    id Integer primary key
    group_id Integer foreign key
    first_name Varchar(100) NOT NULL
    last_name Varchar(100) NOT NULL

course:
    id Integer primary key
    name Varchar(100) NOT NULL UNIQUE
    description Text

student_course:
    id Integer primary key
    student_id ForeignKey('student.id')
    course_id ForeignKey('course.id')
    UniqueConstraint('student_id', 'course_id')

2. Fill the database with test data
   Write a script witch will be fill database:
    2.1 determine func witch crates 10 group with randomly names
   (The names should contain 2 characters, hyphen, 2 numbers)
    2.2 Func for creating 10 courses (math, biology)
    2.3 Func for create 200 students
    2.4 Func for randomly assign students to groups. Each group could 
        contain from 10 to 30 students
    2.5 Func for creating relation many-to-many between tables students and courses.
        Randomly assign from 1 to 3 courses for each student
### Application
3. Create application views

#### Views
3.1 Find all groups with less or equals student count.
3.2 Find all students related to the course with a given name.
3.3 Add new student
3.4 Delete student by STUDENT_ID
3.5 Add a student to the course (from a list)
3.6 Remove the student from one of his or her courses

### Tests for app
4. Write tests for each view

### Api
5. Add api to previous app

### Tests for api
6. Write tests for api