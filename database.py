import sqlite3
import os
from datetime import datetime


def create_table():

    ''' 
    Functionality: 
    For the create_table function, we are creating 4 different tables in the database and it defines the primary key, foreign key and constraints of the attributes in each table:
    1. students table which has 4 columns: student id which is unique to each student, name, age(the check means that its only accepted if the age is positive ) and the email
    2. instructors table has also 4 columns: instructor id that is unique, name, age with the condition and email 
    3. courses table has 3 columns: course_id that is unique, course_name, instructor id which links the course to an id.
    4. registration table has 3 columns: registration_id which is unique, student id and course_id

    Parameter: this function doesn't has any parameter
    return values: the function doesn't return anything. 
    '''

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK (age >= 0),
        email TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS instructors (
        instructor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER CHECK (age >= 0),
        email TEXT NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        course_id TEXT PRIMARY KEY,
        course_name TEXT NOT NULL,
        instructor_id TEXT,
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        course_id TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
    )
    """)
    db.commit()
    db.close()


def create_student(student_id, name, age, email):

    '''
    Functionality: the crear_student function inserts new students into the students table in database.db
    Parameters: this function has 4 parameters 
        1.student_id which is the unique identifier of a student
        2.name is the name of the student that we want to enter
        3.age: the age of the student with a constraint
        4.Email: the email of the sudent 
    Return value: this function doesn't have a return value it only adds the student to the database table.
    '''

    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)",(student_id, name, age, email))
    db.commit()
    db.close()


def read_student(student_id):
    '''
    Functionality: This function retrieve the records of a student based on the provided student_id
    Parameters: the only parameter that this function take is the student_id to identify the student
    Return value: in this function there is 2 case of return value, if the student id provided exist in the table then the function will return a tupple with the information of the student
    if the student_id provided does not exist then the function will return None
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_student(student_id, name=None, age=None, email=None):
    '''
    Functionality: this function update an existing studend record in the students table in the database
    Parameter: this function has 4 parameters
    1. student_id which is the unique identifier of a student 
    2. name: this parameter is optional, either we can add a new name or the default value will be None 
    3. age: also optional, either we can add a new age or the default value will be None
    4. email: also optional, either we can add a new name or the default would be optional
    Return value: the function doesn't return any value. 
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if name:
        cursor.execute("UPDATE students SET name = ? WHERE student_id = ?", (name, student_id))
    if age is not None:
        cursor.execute("UPDATE students SET age = ? WHERE student_id = ?", (age, student_id))
    if email:
        cursor.execute("UPDATE students SET email = ? WHERE student_id = ?", (email, student_id))
    db.commit()
    db.close()

def delete_student(student_id):
    ''' 
    Functionality: This function delete a student and the registrations related to this student based on his student_id.
    This function first start by deleting any record in the registration table where the student_id that we want to delete is present and then it will delete the student from the students table.
    Parameter: this function has only one parameter which is the student_id, we enter the student_id of the student that we want to delete
    Return value: this function doesn't return anything, it returns None
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    db.close()

def create_instructor(instructor_id, name, age, email):
    '''
    Functionality: this function inserts new instructors into the instructors table in database.db
    Parameters: this function has 4 parameters 
        1.instructor_id which is the unique identifier of an instructor
        2.name is the name of the instructor that we want to insert
        3.age: the age of the instructor with a constraint
        4.Email: the email of the instructor  
    Return value: it return None, it only adds the instructor to the database table.
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",(instructor_id, name, age, email))
    db.commit()
    db.close()

def read_instructor(instructor_id):
    '''
    Functionality: This function retrieve the records of an instructor based on the provided instructor_id
    Parameters: the only parameter that this function takes is the instructor_id to identify the instructor
    Return value: in this function there is 2 case of return value, if the instructor_id provided exist in the table then the function will return a tupple with the information of the instructor
    if the instructor_id provided does not exist then the function will return None
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_instructor(instructor_id, name=None, age=None, email=None):
    '''
    Functionality: this function update an existing instructor record in the instructors table in the database
    Parameter: this function has 4 parameters
    1. instructor_id which is the unique identifier of an instructor
    2. name: this parameter is optional, either we can add a new name or the default value will be None 
    3. age: also optional, either we can add a new age or the default value will be None
    4. email: also optional, either we can add a new name or the default would be optional
    Return value: the function will return None. 
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if name:
        cursor.execute("UPDATE instructors SET name = ? WHERE instructor_id = ?", (name, instructor_id))
    if age is not None:
        cursor.execute("UPDATE instructors SET age = ? WHERE instructor_id = ?", (age, instructor_id))
    if email:
        cursor.execute("UPDATE instructors SET email = ? WHERE instructor_id = ?", (email, instructor_id))
    db.commit()
    db.close()

def delete_instructor(instructor_id):
    '''
    Functionality: this function deletes an instructor and unassigns them from the courses based on the instructor_id of the instructor that we want to delete
    this function first start by unassigning the instructor to do that it will go to the courses table and replace the instructor_id of the instructor that we want to delete by NULL
    and then it will go in the instructor table and delete the instructor based on the provided id. 
    Parameters: it only has one parameter which is the instructor_id of the instructor that we want to delete.
    Return value: it will return None.
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("UPDATE courses SET instructor_id = NULL WHERE instructor_id = ?", (instructor_id,))
    cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
    db.commit()
    db.close()

def create_course(course_id, course_name, instructor_id=None):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",(course_id, course_name, instructor_id))
    db.commit()
    db.close()

def read_course(course_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_course(course_id, course_name=None, instructor_id=None):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if course_name:
        cursor.execute("UPDATE courses SET course_name = ? WHERE course_id = ?", (course_name, course_id))
    if instructor_id is not None:
        cursor.execute("UPDATE courses SET instructor_id = ? WHERE course_id = ?", (instructor_id, course_id))
    db.commit()
    db.close()

def delete_course(course_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM registrations WHERE course_id = ?", (course_id,))
    cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))
    db.commit()
    db.close()

def create_registration(student_id, course_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO registrations (student_id, course_id) VALUES (?, ?)",(student_id, course_id))
    db.commit()
    db.close()

def read_registration(registration_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM registrations WHERE registration_id = ?", (registration_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_registration(registration_id, student_id=None, course_id=None):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    if student_id:
        cursor.execute("UPDATE registrations SET student_id = ? WHERE registration_id = ?", (student_id, registration_id))
    if course_id:
        cursor.execute("UPDATE registrations SET course_id = ? WHERE registration_id = ?", (course_id, registration_id))
    db.commit()
    db.close()

def delete_registration(registration_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM registrations WHERE registration_id = ?", (registration_id,))
    db.commit()
    db.close()

def list_students():
    '''
    Functionality: this function will print all of the students present in the student table in an alphabetical order based on the name of the student
    parameters: None
    Return Value: this function will return a list of tupples of the students and there information present in the table 
    and if the students table is empty it will return an empty list
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT student_id, name, age, email FROM students ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return rows

def list_instructors():
    '''
    Functionality: this function will print all of the instructors present in the instructors table in an alphabetical order based on the name of the instructor
    parameters: None
    Return Value: this function will return a list of tupples of the instructors and there information present in the table 
    and if the instructor table is empty it will return an empty list.
    '''
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT instructor_id, name, age, email FROM instructors ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return rows

def list_courses(): 
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("""
        SELECT c.course_id, c.course_name, COALESCE(i.name,'')
        FROM courses c
        LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
        ORDER BY c.course_name
    """)
    rows = cursor.fetchall()
    db.close()
    return rows

def backup_database(backup_path=None):
    if backup_path is None or os.path.isdir(backup_path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"database_backup_{ts}.db"
        dirpath = backup_path if backup_path and os.path.isdir(backup_path) else "."
        backup_path = os.path.join(dirpath, fname)
    src = sqlite3.connect('database.db')
    dst = sqlite3.connect(backup_path)
    with dst:
        src.backup(dst)
    src.close()
    dst.close()
    return backup_path

create_table()
