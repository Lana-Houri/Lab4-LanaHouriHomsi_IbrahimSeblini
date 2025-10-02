from typing import Dict
import json
import re

class Person():
    def __init__(self, name: str, age: int, email: str):
        if age < 0:
            raise ValueError(" The age can't be negative")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("The email entered is not valid")
        self.name = name
        self.age = age
        self._email = email
    
    def introduce(self):
        return f"My name is {self.name} and I am {self.age} years old."
    
class Student(Person):
    def __init__(self, name: str, age: int, email: str, student_id: str):
        super().__init__(name, age, email)
        self.student_id= student_id
        self.registered_courses = []

    def register_course(self, course: str):
        self.registered_courses.append(course)
        return f"{self.name} registeres in the {course} course."

class Instructor(Person):
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses= []
    
    def assign_course(self, course: str):
        self.assigned_courses.append(course)
        return f"Professor {self.name} was assigned to the {course} course."

class Course:
    """
    Represents a course with an ID, name, instructor, and enrolled students.

    Attributes:
        course_id (str): Unique course ID.
        course_name (str): Human-readable name of the course.
        instructor (Instructor | None): Instructor teaching the course.
        enrolled_students (list[Student]): Students enrolled in this course.
    """

    def __init__(self, course_id: str, course_name: str, instructor: Instructor):
        """
        Initialize a Course.

        Args:
            course_id (str): Unique course identifier.
            course_name (str): The name of the course.
            instructor (Instructor): Instructor assigned to the course.
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students: list[Student] = []

    def add_student(self, student: Student) -> str:
        """
        Enroll a student in the course.

        Args:
            student (Student): Student object to be added.

        Returns:
            str: Confirmation message.
        """
        self.enrolled_students.append(student)
        return f"{student.name} is enrolled in the {self.course_name} course"


class SchoolDB:
    """
    Represents a school database that stores students, instructors, and courses.

    Attributes:
        students (dict[str, Student]): Dictionary of students by student ID.
        instructors (dict[str, Instructor]): Dictionary of instructors by ID.
        courses (dict[str, Course]): Dictionary of courses by course ID.
    """

    def __init__(self):
        """Initialize an empty SchoolDB."""
        self.students: Dict[str, Student] = {}
        self.instructors: Dict[str, Instructor] = {}
        self.courses: Dict[str, Course] = {}

    def to_dictionary(self) -> dict:
        """
        Convert the database into a serializable dictionary.

        Returns:
            dict: JSON-serializable dictionary containing all data.
        """
        return {
            "students": [
                {
                    "name": s.name,
                    "age": s.age,
                    "email": s._email,
                    "student_id": s.student_id,
                    "registered_courses": list(s.registered_courses),
                }
                for s in self.students.values()
            ],
            "instructors": [
                {
                    "name": i.name,
                    "age": i.age,
                    "email": i._email,
                    "instructor_id": i.instructor_id,
                    "assigned_courses": i.assigned_courses,
                }
                for i in self.instructors.values()
            ],
            "courses": [
                {
                    "course_id": c.course_id,
                    "course_name": c.course_name,
                    "instructor": (
                        {
                            "id": c.instructor.instructor_id,
                            "name": c.instructor.name,
                        }
                        if c.instructor else None
                    ),
                    "enrolled_students": [
                        {"id": s.student_id, "name": s.name}
                        for s in c.enrolled_students
                    ],
                }
                for c in self.courses.values()
            ],
        }


    @classmethod
    def from_dictionary(cls, payload: Dict):
        db = cls()
        
        for s in payload.get("students",[]):
            st= Student(
                name=s["name"],
                age=s["age"],
                email= s["email"],
                student_id=s["student_id"],
            )
            st.registered_courses = list(s.get("registered_courses", []))
            db.students[st.student_id]= st

        for i in payload.get("instructors", []):
            ins = Instructor(
                name=i["name"],
                age=i["age"],
                email=i["email"],
                instructor_id=i["instructor_id"],
            )
            ins.assigned_courses = list(i.get("assigned_courses", []))
            db.instructors[ins.instructor_id] = ins
        
        for c in payload.get("courses", []):
            instr_info = c.get("instructor")
            instructor = None
            if instr_info:
                instructor = db.instructors.get(instr_info.get("id"))  
            co = Course(
                course_id=c["course_id"],
                course_name=c["course_name"],
                instructor=instructor,  
            )
            for s in c.get("enrolled_students", []):
                student = db.students.get(s["id"])
                if student:
                    co.enrolled_students.append(student)
            db.courses[co.course_id] = co
        return db
    
    def save_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dictionary(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return cls.from_dictionary(payload)
    
if __name__ == "__main__":
    person= Person("Lana", 20, "lana.houri@gmail.com")
    print(Person.introduce(person))

    student = Student("Lilas", 18, "lilas@gmail.com", "lth05")
    print(student.register_course("economy"))
    print(Student.introduce(student))

    instructor= Instructor("Mohamad", 35, "mohamad@gmail.com", "mh87")
    print(Instructor.introduce(instructor))
    print(instructor.assign_course("economy"))

    course= Course("ECON212", "economy", instructor)
    print(course.add_student(student))

    db= SchoolDB()
    inst = Instructor(name="Dr. Lina", age=40, email="lina@uni.edu", instructor_id="I-001")
    stu = Student(name="Omar", age=20, email="omar@student.edu", student_id="S-100")
    c = Course(course_id="CSE101", course_name="Intro to CS", instructor=inst)

    inst.assign_course(c.course_name)
    c.add_student(stu)

    db.instructors[inst.instructor_id] = inst
    db.students[stu.student_id] = stu
    db.courses[c.course_id] = c

    db.save_json("uni_data.json")
    db2 = SchoolDB.load_json("uni_data.json")
    print(db2.students["S-100"].introduce())
