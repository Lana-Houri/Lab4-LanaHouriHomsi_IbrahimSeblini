import sqlite3
import os
from datetime import datetime

def create_table():
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
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO students (student_id, name, age, email) VALUES (?, ?, ?, ?)",(student_id, name, age, email))
    db.commit()
    db.close()

def read_student(student_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_student(student_id, name=None, age=None, email=None):
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
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("DELETE FROM registrations WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    db.commit()
    db.close()

def create_instructor(instructor_id, name, age, email):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("INSERT INTO instructors (instructor_id, name, age, email) VALUES (?, ?, ?, ?)",(instructor_id, name, age, email))
    db.commit()
    db.close()

def read_instructor(instructor_id):
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (instructor_id,))
    result = cursor.fetchone()
    db.close()
    return result

def update_instructor(instructor_id, name=None, age=None, email=None):
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
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("UPDATE courses SET instructor_id = NULL WHERE instructor_id = ?", (instructor_id,))
    cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (instructor_id,))
    db.commit()
    db.close()

def create_course(course_id: str, course_name: str, instructor_id: str = None) -> None:
    """
    Create a new course record in the database.

    Parameters:
        course_id (str): Unique identifier for the course.
        course_name (str): The name/title of the course.
        instructor_id (str, optional): The ID of the instructor teaching the course. Defaults to None.

    Returns:
        None
    """
    # Connect to the database
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Insert a new course row into the "courses" table
    cursor.execute(
        "INSERT INTO courses (course_id, course_name, instructor_id) VALUES (?, ?, ?)",
        (course_id, course_name, instructor_id)
    )

    # Save changes and close connection
    db.commit()
    db.close()


def read_course(course_id: str):
    """
    Retrieve a single course record from the database.

    Parameters:
        course_id (str): The ID of the course to fetch.

    Returns:
        tuple | None: A tuple containing course details (course_id, course_name, instructor_id),
                      or None if no record is found.
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Query the course by ID
    cursor.execute("SELECT * FROM courses WHERE course_id = ?", (course_id,))
    result = cursor.fetchone()

    db.close()
    return result


def update_course(course_id: str, course_name: str = None, instructor_id: str = None) -> None:
    """
    Update details of an existing course in the database.

    Parameters:
        course_id (str): The ID of the course to update.
        course_name (str, optional): The new name of the course. If None, the name is not updated.
        instructor_id (str, optional): The new instructor ID. If None, the instructor is not updated.

    Returns:
        None
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Update course name if provided
    if course_name:
        cursor.execute(
            "UPDATE courses SET course_name = ? WHERE course_id = ?",
            (course_name, course_id)
        )

    # Update instructor if provided
    if instructor_id is not None:
        cursor.execute(
            "UPDATE courses SET instructor_id = ? WHERE course_id = ?",
            (instructor_id, course_id)
        )

    db.commit()
    db.close()


def delete_course(course_id: str) -> None:
    """
    Delete a course and any associated registrations from the database.

    Parameters:
        course_id (str): The ID of the course to delete.

    Returns:
        None
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Remove registrations tied to this course
    cursor.execute("DELETE FROM registrations WHERE course_id = ?", (course_id,))

    # Remove the course itself
    cursor.execute("DELETE FROM courses WHERE course_id = ?", (course_id,))

    db.commit()
    db.close()

def create_registration(student_id: str, course_id: str) -> None:
    """
    Create a new registration record (enroll a student in a course).

    Parameters:
        student_id (str): The ID of the student enrolling.
        course_id (str): The ID of the course being registered for.

    Returns:
        None
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Insert a new registration row
    cursor.execute(
        "INSERT INTO registrations (student_id, course_id) VALUES (?, ?)",
        (student_id, course_id)
    )

    db.commit()
    db.close()


def read_registration(registration_id: int):
    """
    Retrieve a registration record by its ID.

    Parameters:
        registration_id (int): The unique ID of the registration.

    Returns:
        tuple | None: A tuple containing registration details (registration_id, student_id, course_id),
                      or None if no record is found.
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM registrations WHERE registration_id = ?",
        (registration_id,)
    )
    result = cursor.fetchone()

    db.close()
    return result


def update_registration(registration_id: int, student_id: str = None, course_id: str = None) -> None:
    """
    Update details of an existing registration.

    Parameters:
        registration_id (int): The ID of the registration to update.
        student_id (str, optional): New student ID to assign. If None, not updated.
        course_id (str, optional): New course ID to assign. If None, not updated.

    Returns:
        None
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Update student if provided
    if student_id:
        cursor.execute(
            "UPDATE registrations SET student_id = ? WHERE registration_id = ?",
            (student_id, registration_id)
        )

    # Update course if provided
    if course_id:
        cursor.execute(
            "UPDATE registrations SET course_id = ? WHERE registration_id = ?",
            (course_id, registration_id)
        )

    db.commit()
    db.close()


def delete_registration(registration_id: int) -> None:
    """
    Delete a registration record from the database.

    Parameters:
        registration_id (int): The ID of the registration to delete.

    Returns:
        None
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    cursor.execute(
        "DELETE FROM registrations WHERE registration_id = ?",
        (registration_id,)
    )

    db.commit()
    db.close()

def list_students():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT student_id, name, age, email FROM students ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return rows

def list_instructors():
    db = sqlite3.connect('database.db')
    cursor = db.cursor()
    cursor.execute("SELECT instructor_id, name, age, email FROM instructors ORDER BY name")
    rows = cursor.fetchall()
    db.close()
    return rows

def list_courses():
    """
    List all courses in the database along with their instructor names.

    Parameters:
        None

    Returns:
        list[tuple]: A list of tuples in the format (course_id, course_name, instructor_name).
                     If an instructor is not assigned, the instructor_name will be an empty string.
    """
    db = sqlite3.connect('database.db')
    cursor = db.cursor()

    # Join courses with instructors to display instructor names
    cursor.execute("""
        SELECT c.course_id, c.course_name, COALESCE(i.name, '')
        FROM courses c
        LEFT JOIN instructors i ON i.instructor_id = c.instructor_id
        ORDER BY c.course_name
    """)

    rows = cursor.fetchall()

    db.close()
    return rows


def backup_database(backup_path: str = None) -> str:
    """
    Create a backup of the database file.

    Parameters:
        backup_path (str, optional): Directory where the backup should be saved.
                                     If None, the backup will be stored in the current directory.

    Returns:
        str: The full file path of the backup file created.
    """
    # If no path is given or the path is a directory, generate a timestamped filename
    if backup_path is None or os.path.isdir(backup_path):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"database_backup_{ts}.db"
        dirpath = backup_path if backup_path and os.path.isdir(backup_path) else "."
        backup_path = os.path.join(dirpath, fname)

    # Copy contents of main database into backup file
    src = sqlite3.connect('database.db')
    dst = sqlite3.connect(backup_path)
    with dst:
        src.backup(dst)

    src.close()
    dst.close()
    return backup_path

create_table()
