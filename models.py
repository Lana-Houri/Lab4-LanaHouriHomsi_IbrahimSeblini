from typing import Dict
import json
import re

class Person():
    '''
    Functionality: this class stores a persons name, age and email and it will check if the age is negative or not and will check if the email is in the correct format.
    it will also provide an introduction message of the person. 
    
    this class has 3 attributes:
    - name attribute needs to be a string and we write the name of the person.
    - the age attribute needs to be an integer and we write the age of the person and checks that its not negative
    - the email attribute needs to be a string and we write the email of the person and check that the format of the email is valid 
    
    Methods: The class has 2 methods
    -  __init__(name, age, email): this method initialze the name age and the email and makes sure that the age and the email are valid
    - introduce: this method return a string where it is introducing a person. 
    '''
    def __init__(self, name: str, age: int, email: str):
        '''
        Functionality: it will initilaze a new person instance.

        Parameter: this method has 3 parameters
        1. the name where we write the full name of the person and need to be a string 
        2. the age where we write the age of the person and it needs to be an positive integer. 
        3. the email where we write the email of the person and  has a string type and needs to be in the valid format.

        Return Value: it will return None

        Raises: it will send a value error if the age is negative or the email is invalid. 
        '''
        if age < 0:
            raise ValueError(" The age can't be negative")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("The email entered is not valid")
        self.name = name
        self.age = age
        self._email = email
    
    def introduce(self):
        '''
        Functionality: this function will send an introduction message about the person

        Parameter: it doesn't have any parameter 

        Return Value: the function will return a string.  
        '''
        return f"My name is {self.name} and I am {self.age} years old."
    
class Student(Person):
    '''
    Functionality: this class inherits from the Person class, the functionalities of this class is that it stores student-specific data that has been inhereted from the person class
    and it keeps track of the registered courses and allow the registration of new classes. 

    Attributes:
    1. name of type string: We have the name of the student that is inherited from the Person class.
    2. age of type integer: we have the age of the student but the age must be positive and its also inherited from the Person Class.
    3. _email of type string: we have the email address of the student but the email must be in a valid format and is also inherited from the Person Class.
    4. student_id of type string: the student_id is the unique identifier for the student.
    5. registered_courses  has a list type: it is a list of courses the student has registered for.

    Methods: this class has 2 functions
    - __init__(name, age, email, student_id): we initialize a student instance with student and personal data
    - register_course(course): this method register courses to student and return a confirmation message.  

    '''
    def __init__(self, name: str, age: int, email: str, student_id: str):
        '''
        Functionality: it will initilaze a new student instance. 

        Parameter: this function has 4 parameters
        1. name of type string: it takes the name of the student.
        2. age of type integer: it takes the age of the student and checks that the age entered is positive.
        3. email of type string: it takes the email address of the student but before adding it, it checks that email enter is in a valid format.
        4. student_id of type string: Unique identifier assigned to the student.

        Return Value: it returns None.
        '''
         super().__init__(name, age, email)
        self.student_id= student_id
        self.registered_courses = []
        return f"My name is {self.name} and I am {self.age} years old."
   
    def register_course(self, course: str):
        '''
        Functionality: this method register the student to a new course.

        Parameter: only takes one parameter which is course of type string

        Return Value: it returns a confirmation message that the student has been added to the certain course
        '''
        self.registered_courses.append(course)
        return f"{self.name} registeres in the {course} course."

class Instructor(Person):

    '''
    Functionality: this class inherite from the person class, the functionalities of this class is that it stores instructor-specific data and personal data inherited from person class.
    Additionally, it keeps track of courses assigned to the instructor and allows assigning new courses to the instructor.

    Attributes:
    1. name of type string: the  name of the instructor that is inherited from Person.
    2. age of type integer: the age of the instructor that needs to be positive and its also inherited from Person.
    3. email of type string:the email address of the instructor that needs to be in valid format and its inherited from Person.
    4. instructor_id of type string: is a unique identifier for the instructor.
    5. assigned_courses of type list: List of courses the instructor has been assigned to.

    Methods: we have for this class 2 methods.
    - __init__(name, age, email, instructor_id): it initializes the instructor instance with personal and instructor specific data
    - assign_course(course): it assigns the instructor to a new course and returns a confirmation message.
    '''
    def __init__(self, name: str, age: int, email: str, instructor_id: str):
        '''
        Functionality: it will initilaze a new instructor instance. 

        Parameter: this function has 4 parameters
        1. name of type string: it takes the name of the instructor.
        2. age of type integer: it takes the age of the instructor and checks that the age entered is positive.
        3. email of type string: it takes the email address of the instructor but before adding it, it checks that email enter is in a valid format.
        4. instructor_id of type string: Unique identifier assigned to the student.

        Return Value: it returns None.
        '''
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
