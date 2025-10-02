from models import Student, Instructor, Course
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QWidget, QVBoxLayout,
    QFormLayout, QMessageBox, QComboBox, QInputDialog, QTableWidget,
    QTableWidgetItem, QHBoxLayout, QSizePolicy, QFileDialog
)
from PyQt5.QtCore import Qt
import database as dbapi

CONTENT_WIDTH = 520

class MainWindow(QMainWindow):
    '''
    Main application window for the School Management System.

    Functionality: this class is the main application window for the School Management System. the functionalities of this class are: 
    1. Provides forms for creating Students, Instructors, and Courses.
    2. Registers students to courses
    3. Assigns instructors to courses.
    3. Displays tables of the students, instructor and courses with search.
    4. Supports edit/delete actions on selected records.
    5. Exports current view to CSV; imports/exports full DB snapshot as JSON.

    Attributes:
        current_view of type string: Active table view ('students' | 'instructors' | 'courses').
        table (QTableWidget): Main table widget showing the current view.
        # Form inputs (selected examples below):
        student_name (QLineEdit)
        student_age (QLineEdit)
        student_email (QLineEdit)
        student_id (QLineEdit)
        instructor_name (QLineEdit)
        instructor_age (QLineEdit)
        instructor_email (QLineEdit)
        instructor_id (QLineEdit)
        course_id (QLineEdit)
        course_name (QLineEdit)
        course_instructor_id (QLineEdit)
        reg_student_id (QLineEdit)
        reg_course_dropdown (QComboBox)
        assign_instructor_dropdown (QComboBox)
        assign_course_dropdown (QComboBox)
        search_input (QLineEdit)

    Methods: we have 19 methods
        __init__(): Build and lay out the UI; initialize dropdowns and default view.
        update_course_dropdown(): Refresh registration course dropdown from DB.
        register_student_to_course(): Register a given student to the selected course.
        export_to_csv(): Export the current table view to a CSV file.
        save_data(): Serialize the entire DB to JSON via SchoolDB model.
        load_data(): Load JSON snapshot into the DB (upsert-like behavior).
        get_selected_row(): Return the currently selected row index or None.
        edit_selected_record(): Edit the selected record depending on current_view.
        delete_selected_record(): Delete the selected record depending on current_view.
        display_students(): Populate table with students (optionally a provided list).
        display_instructors(): Populate table with instructors (optionally a list).
        display_courses(): Populate table with courses (optionally a list).
        search_records(): Filter current view based on free-text query.
        update_instructor_dropdowns(): Refresh instructor pickers.
        update_assign_course_dropdown(): Refresh assignment course picker.
        assign_instructor_to_course(): Assign selected instructor to selected course.
        add_student(): Validate and create a new student.
        add_instructor(): Validate and create a new instructor.
        add_course(): Validate and create a new course.
    '''

    def update_course_dropdown(self):
        '''
        Functionality: it refreshes the courses dropdown that we are using for the student registration

        Parameter: it doesn't take any parameter

        Return Value: None but the function clear and repopulate self.reg_course_dropdown with the name and id of the course.
        '''
        self.reg_course_dropdown.clear()
        for cid, cname, _ in dbapi.list_courses():
            self.reg_course_dropdown.addItem(f"{cname} ({cid})", cid)

    def register_student_to_course(self):
        '''
        Functionality: this function register students using there ID to the selected course.
        this function first start by validating the present of the student_id and the course selection and it ensures that both exists.
        and it prevents duplicate registration so if a student is already registered in the course it won't let him register twice. 
        it the student isn't registered yet it performs the registration and refresh the displayed table for the student to appear on it. 

        Parameter: None

        Return Value: None 

        User feedback: when a student want to register a course he/she will get a pop up message box that will tell them whether it was succesfull or there is an error. 
        '''
        student_id = self.reg_student_id.text().strip()
        course_id = self.reg_course_dropdown.currentData()
        if not student_id or not course_id:
            QMessageBox.warning(self, "Error", "Student ID and Course are required.")
            return
        if not dbapi.read_student(student_id):
            QMessageBox.warning(self, "Error", "Student ID not found!")
            return
        if not dbapi.read_course(course_id):
            QMessageBox.warning(self, "Error", "Course not found!")
            return
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM registrations WHERE student_id=? AND course_id=?", (student_id, course_id))
            exists = cur.fetchone()
        if exists:
            QMessageBox.information(self, "Info", "Student already registered for this course.")
            return
        dbapi.create_registration(student_id, course_id)
        QMessageBox.information(self, "Success", "Student registered for course!")
        if self.current_view == 'students':
            self.display_students()
        elif self.current_view == 'courses':
            self.display_courses()

    def __init__(self):
        '''
        Functionality: It builds and initialize the main window UI and defualt state
        
        Layout:
        - Forms: Student, Instructor, Course, Student Registration, Instructor Assignment.
        - Table for the main view and controls for search/edit/delete/export.
        - File actions: export JSON snapshot, import JSON, export CSV.

        Parameter: None 
        
        Return value: None but the function initializes the dropdowns and renders the default students view.
        '''
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 900, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout()
        central_widget.setLayout(root_layout)

        container = QWidget()
        container.setFixedWidth(CONTENT_WIDTH)
        container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        layout = QVBoxLayout(container)
        root_layout.addWidget(container, alignment=Qt.AlignTop | Qt.AlignLeft)

        student_form = QFormLayout()
        self.student_name = QLineEdit()
        self.student_age = QLineEdit()
        self.student_email = QLineEdit()
        self.student_id = QLineEdit()
        student_form.addRow("Student Name:", self.student_name)
        student_form.addRow("Age:", self.student_age)
        student_form.addRow("Email:", self.student_email)
        student_form.addRow("Student ID:", self.student_id)
        student_btn = QPushButton("Add Student")
        student_btn.clicked.connect(self.add_student)
        student_form.addRow(student_btn)
        layout.addLayout(student_form)

        instructor_form = QFormLayout()
        self.instructor_name = QLineEdit()
        self.instructor_age = QLineEdit()
        self.instructor_email = QLineEdit()
        self.instructor_id = QLineEdit()
        instructor_form.addRow("Instructor Name:", self.instructor_name)
        instructor_form.addRow("Age:", self.instructor_age)
        instructor_form.addRow("Email:", self.instructor_email)
        instructor_form.addRow("Instructor ID:", self.instructor_id)
        instructor_btn = QPushButton("Add Instructor")
        instructor_btn.clicked.connect(self.add_instructor)
        instructor_form.addRow(instructor_btn)
        layout.addLayout(instructor_form)

        course_form = QFormLayout()
        self.course_id = QLineEdit()
        self.course_name = QLineEdit()
        self.course_instructor_id = QLineEdit()
        course_form.addRow("Course ID:", self.course_id)
        course_form.addRow("Course Name:", self.course_name)
        course_form.addRow("Instructor ID:", self.course_instructor_id)
        course_btn = QPushButton("Add Course")
        course_btn.clicked.connect(self.add_course)
        course_form.addRow(course_btn)
        layout.addLayout(course_form)

        register_form = QFormLayout()
        self.reg_student_id = QLineEdit()
        self.reg_course_dropdown = QComboBox()
        register_form.addRow("Student ID:", self.reg_student_id)
        register_form.addRow("Course:", self.reg_course_dropdown)
        reg_btn = QPushButton("Register Student to Course")
        reg_btn.clicked.connect(self.register_student_to_course)
        register_form.addRow(reg_btn)
        layout.addLayout(register_form)

        assign_form = QFormLayout()
        self.assign_instructor_dropdown = QComboBox()
        self.assign_course_dropdown = QComboBox()
        assign_form.addRow("Instructor:", self.assign_instructor_dropdown)
        assign_form.addRow("Course:", self.assign_course_dropdown)
        assign_btn = QPushButton("Assign Instructor to Course")
        assign_btn.clicked.connect(self.assign_instructor_to_course)
        assign_form.addRow(assign_btn)
        layout.addLayout(assign_form)

        table_layout = QHBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setRowCount(0)
        self.table.setFixedWidth(CONTENT_WIDTH)
        self.table.setFixedHeight(240)
        self.table.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        table_layout.addWidget(self.table)
        layout.addLayout(table_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or course...")
        search_layout.addWidget(self.search_input)
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.search_records)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        btn_layout = QHBoxLayout()
        self.show_students_btn = QPushButton("Show Students")
        self.show_students_btn.clicked.connect(lambda: self.display_students())
        btn_layout.addWidget(self.show_students_btn)
        self.show_instructors_btn = QPushButton("Show Instructors")
        self.show_instructors_btn.clicked.connect(lambda: self.display_instructors())
        btn_layout.addWidget(self.show_instructors_btn)
        self.show_courses_btn = QPushButton("Show Courses")
        self.show_courses_btn.clicked.connect(lambda: self.display_courses())
        btn_layout.addWidget(self.show_courses_btn)
        layout.addLayout(btn_layout)

        action_layout = QHBoxLayout()
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_record)
        action_layout.addWidget(self.edit_btn)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_record)
        action_layout.addWidget(self.delete_btn)
        layout.addLayout(action_layout)

        file_layout = QHBoxLayout()
        self.save_btn = QPushButton("Export JSON Snapshot")
        self.save_btn.clicked.connect(self.save_data)
        file_layout.addWidget(self.save_btn)
        self.load_btn = QPushButton("Import JSON Into DB")
        self.load_btn.clicked.connect(self.load_data)
        file_layout.addWidget(self.load_btn)
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.export_to_csv)
        file_layout.addWidget(self.export_btn)
        layout.addLayout(file_layout)

        self.current_view = 'students'
        self.update_instructor_dropdowns()
        self.update_assign_course_dropdown()
        self.update_course_dropdown()
        self.display_students()

    def export_to_csv(self):
        '''
        Functionality: it exports the current view to a csv file selected by the user. 
        if the view is students then the file will include the registeres courses per student.
        if the view is the instructors then the file will contain the information of the instructor
        and if the view is the courses then the file will containe the enrolled student names.

        Parameter: None

        Return Value: None but if an error occured then it will display a message box telling the user that the function failed.
        '''
        import csv
        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "records.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            if self.current_view == 'students':
                headers = ["Name", "Age", "Email", "Student ID", "Registered Courses"]
                rows = []
                with sqlite3.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("SELECT student_id, name, age, email FROM students ORDER BY name")
                    for sid, name, age, email in cur.fetchall():
                        cur.execute(
                            "SELECT c.course_name FROM registrations r JOIN courses c ON c.course_id=r.course_id WHERE r.student_id=? ORDER BY c.course_name",
                            (sid,),
                        )
                        courses = ", ".join([r[0] for r in cur.fetchall()])
                        rows.append([name, age, email, sid, courses])
            elif self.current_view == 'instructors':
                headers = ["Name", "Age", "Email", "Instructor ID"]
                rows = []
                for iid, name, age, email in dbapi.list_instructors():
                    rows.append([name, age, email, iid])
            elif self.current_view == 'courses':
                headers = ["Course ID", "Course Name", "Instructor", "Enrolled Students"]
                rows = []
                with sqlite3.connect("database.db") as con:
                    cur = con.cursor()
                    cur.execute("""
                        SELECT c.course_id, c.course_name, COALESCE(i.name,'')
                        FROM courses c LEFT JOIN instructors i ON i.instructor_id=c.instructor_id
                        ORDER BY c.course_name
                    """)
                    for cid, cname, iname in cur.fetchall():
                        cur.execute(
                            "SELECT s.name FROM registrations r JOIN students s ON s.student_id=r.student_id WHERE r.course_id=? ORDER BY s.name",
                            (cid,),
                        )
                        students = ", ".join([r[0] for r in cur.fetchall()])
                        rows.append([cid, cname, iname, students])
            else:
                QMessageBox.warning(self, "Error", "No data to export.")
                return
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(rows)
            QMessageBox.information(self, "Success", f"Data exported to {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to export: {e}")

    def save_data(self):
        '''
        Functionality: the function exports a JSON snapshot of the entire database.
        the function will first build a SchoolDB instance from the current sqlite content and then will serialize to a user chosen JSON file.

        Parameter: None

        Return Value: None but will show a message box on exceptions. 
        '''
        from models import SchoolDB
        path, _ = QFileDialog.getSaveFileName(self, "Export JSON Snapshot", "data.json", "JSON Files (*.json)")
        if not path:
            return
        try:
            sdb = SchoolDB()
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT student_id, name, age, email FROM students")
                for sid, name, age, email in cur.fetchall():
                    s = Student(name, age, email, sid)
                    cur.execute("SELECT c.course_name FROM registrations r JOIN courses c ON c.course_id=r.course_id WHERE r.student_id=?", (sid,))
                    s.registered_courses = [r[0] for r in cur.fetchall()]
                    sdb.students[sid] = s
                cur.execute("SELECT instructor_id, name, age, email FROM instructors")
                for iid, name, age, email in cur.fetchall():
                    ins = Instructor(name, age, email, iid)
                    cur.execute("SELECT course_name FROM courses WHERE instructor_id=?", (iid,))
                    ins.assigned_courses = [r[0] for r in cur.fetchall()]
                    sdb.instructors[iid] = ins
                cur.execute("SELECT course_id, course_name, instructor_id FROM courses")
                for cid, cname, iid in cur.fetchall():
                    instr = sdb.instructors.get(iid) if iid else None
                    c = Course(cid, cname, instr)
                    cur.execute("SELECT s.student_id, s.name FROM registrations r JOIN students s ON s.student_id=r.student_id WHERE r.course_id=?", (cid,))
                    for sid, name in cur.fetchall():
                        if sid in sdb.students:
                            c.enrolled_students.append(sdb.students[sid])
                    sdb.courses[cid] = c
            sdb.save_json(path)
            QMessageBox.information(self, "Success", f"JSON snapshot saved to {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def load_data(self):
        '''
        Functionality: it import a JSON snapshot to the database. this function first start by loading a SchoolDB JSON file.
        then it will insert the students, instructors, courses and registrations if they are missing and
        lastly it will refresh the dropdowns and the views. 

        Parameter: None

        Return Value: None but will show a message box on exceptions. 
        '''
        from models import SchoolDB
        path, _ = QFileDialog.getOpenFileName(self, "Import JSON Into DB", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            sdb = SchoolDB.load_json(path)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                for ins in sdb.instructors.values():
                    try:
                        dbapi.create_instructor(ins.instructor_id, ins.name, ins.age, ins._email)
                    except Exception:
                        pass
                for s in sdb.students.values():
                    try:
                        dbapi.create_student(s.student_id, s.name, s.age, s._email)
                    except Exception:
                        pass
                for c in sdb.courses.values():
                    iid = c.instructor.instructor_id if c.instructor else None
                    try:
                        dbapi.create_course(c.course_id, c.course_name, iid)
                    except Exception:
                        pass
                    for stu in c.enrolled_students:
                        try:
                            dbapi.create_registration(stu.student_id, c.course_id)
                        except Exception:
                            pass
            self.update_instructor_dropdowns()
            self.update_assign_course_dropdown()
            self.update_course_dropdown()
            if self.current_view == 'students':
                self.display_students()
            elif self.current_view == 'instructors':
                self.display_instructors()
            else:
                self.display_courses()
            QMessageBox.information(self, "Success", f"Imported JSON into database from {path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def get_selected_row(self):
        '''
        Functionality: this function gets the index of the selected row from the table.

        Parameter: None

        Return Value: the function will return an integer if a row is selected.
        if nothing is selected then it will return None. 

        User Feedback: the function will send a warning to the user if no row is selected. 
        '''
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Error", "No record selected!")
            return None
        return selected

    def edit_selected_record(self):
        '''
        Functionality: this function edit the selected record depending on the active view.
        If the students view is selected the function will let the user edit the name, the afe and the email of the student.
        If the instructors view is selected the function will let the user edit the name, the age and the email of the instructor.
        If the course view is selected the function will let the user edit the course name only.

        Parameter: None

        Return Value: None

        User Feedback: when the customer wants to edit, the function will open a small pop up which will allow the user to enter something new. 
        if an error occurs the function will send a message box telling the user that there is an error. 
        '''
        row = self.get_selected_row()
        if row is None:
            return
        if self.current_view == 'students':
            sid = self.table.item(row, 3).text()
            rec = dbapi.read_student(sid)
            if not rec:
                QMessageBox.warning(self, "Error", "Student not found.")
                return
            _, name0, age0, email0 = rec
            name, ok = QInputDialog.getText(self, "Edit Student Name", "Name:", text=name0)
            if not ok:
                return
            age, ok = QInputDialog.getInt(self, "Edit Student Age", "Age:", value=age0)
            if not ok:
                return
            email, ok = QInputDialog.getText(self, "Edit Student Email", "Email:", text=email0)
            if not ok:
                return
            dbapi.update_student(sid, name=name, age=age, email=email)
            self.display_students()
        elif self.current_view == 'instructors':
            iid = self.table.item(row, 3).text()
            rec = dbapi.read_instructor(iid)
            if not rec:
                QMessageBox.warning(self, "Error", "Instructor not found.")
                return
            _, name0, age0, email0 = rec
            name, ok = QInputDialog.getText(self, "Edit Instructor Name", "Name:", text=name0)
            if not ok:
                return
            age, ok = QInputDialog.getInt(self, "Edit Instructor Age", "Age:", value=age0)
            if not ok:
                return
            email, ok = QInputDialog.getText(self, "Edit Instructor Email", "Email:", text=email0)
            if not ok:
                return
            dbapi.update_instructor(iid, name=name, age=age, email=email)
            self.display_instructors()
            self.update_instructor_dropdowns()
        elif self.current_view == 'courses':
            cid = self.table.item(row, 0).text()
            rec = dbapi.read_course(cid)
            if not rec:
                QMessageBox.warning(self, "Error", "Course not found.")
                return
            _, cname0, _ = rec
            name, ok = QInputDialog.getText(self, "Edit Course Name", "Course Name:", text=cname0)
            if not ok:
                return
            dbapi.update_course(cid, course_name=name)
            self.display_courses()
            self.update_assign_course_dropdown()
            self.update_course_dropdown()

    def delete_selected_record(self):
        '''
        Functionality: this function deleted the selected record depending on the view that is active. 
        if its the student view that is active then i will delete the student and all their registration.
        if its the instructor view that is active then it will delete the instructor and unassign them from the courses.
        if its the course view that is active then it will delete the course and the related registrations.

        Parameter: None

        Return Value: None
        '''
        row = self.get_selected_row()
        if row is None:
            return
        if self.current_view == 'students':
            sid = self.table.item(row, 3).text()
            dbapi.delete_student(sid)
            self.display_students()
        elif self.current_view == 'instructors':
            iid = self.table.item(row, 3).text()
            dbapi.delete_instructor(iid)
            self.display_instructors()
            self.update_instructor_dropdowns()
            self.display_courses()
        elif self.current_view == 'courses':
            cid = self.table.item(row, 0).text()
            dbapi.delete_course(cid)
            self.display_courses()
            self.update_assign_course_dropdown()
            self.update_course_dropdown()

    def display_students(self, students=None):
        '''
        Functionality: it renders the students view in the table.

        Parameter: students is the only parameter for this function, the user can either enter a list of tupple if he has the information of the students
        or can enter nothing and the data will be read from the DB.

        Return Value: None
        '''
        self.table.clear()
        headers = ["Name", "Age", "Email", "Student ID", "Registered Courses"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            if students is None:
                cur.execute("SELECT student_id, name, age, email FROM students ORDER BY name")
                rows = cur.fetchall()
            else:
                rows = students
            self.table.setRowCount(len(rows))
            for r, (sid, name, age, email) in enumerate(rows):
                cur.execute(
                    "SELECT c.course_name FROM registrations r JOIN courses c ON c.course_id=r.course_id WHERE r.student_id=? ORDER BY c.course_name",
                    (sid,),
                )
                courses = ", ".join([x[0] for x in cur.fetchall()])
                self.table.setItem(r, 0, QTableWidgetItem(name))
                self.table.setItem(r, 1, QTableWidgetItem(str(age)))
                self.table.setItem(r, 2, QTableWidgetItem(email))
                self.table.setItem(r, 3, QTableWidgetItem(sid))
                self.table.setItem(r, 4, QTableWidgetItem(courses))
        self.current_view = 'students'

    def display_instructors(self, instructors=None):
        '''
        Functionality: it renders the instructors view in the table.

        Parameter: instructors is the only parameter for this function, the user can either enter a list of tupple if he has the information of the instructors
        or can enter nothing and the data will be read from the DB.

        Return Value: None
        '''
         
        self.table.clear()
        headers = ["Name", "Age", "Email", "Instructor ID"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        rows = instructors if instructors is not None else dbapi.list_instructors()
        self.table.setRowCount(len(rows))
        for r, (iid, name, age, email) in enumerate(rows):
            self.table.setItem(r, 0, QTableWidgetItem(name))
            self.table.setItem(r, 1, QTableWidgetItem(str(age)))
            self.table.setItem(r, 2, QTableWidgetItem(email))
            self.table.setItem(r, 3, QTableWidgetItem(iid))
        self.current_view = 'instructors'

    def display_courses(self, courses=None):
        '''
        Functionality: it renders the courses view in the table.

        Parameter: courses is the only parameter for this function, the user can either enter a list of tupple if he has the courses.
        or can enter nothing and the data will be read from the DB.

        Return Value: None
        '''
        self.table.clear()
        headers = ["Course ID", "Course Name", "Instructor", "Enrolled Students"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        if courses is None:
            rows = dbapi.list_courses()
        else:
            rows = courses
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            self.table.setRowCount(len(rows))
            for r, (cid, cname, iname) in enumerate(rows):
                cur.execute(
                    "SELECT s.name FROM registrations r JOIN students s ON s.student_id=r.student_id WHERE r.course_id=? ORDER BY s.name",
                    (cid,),
                )
                students = ", ".join([x[0] for x in cur.fetchall()])
                self.table.setItem(r, 0, QTableWidgetItem(cid))
                self.table.setItem(r, 1, QTableWidgetItem(cname))
                self.table.setItem(r, 2, QTableWidgetItem(iname))
                self.table.setItem(r, 3, QTableWidgetItem(students))
        self.current_view = 'courses'

    def search_records(self):
        '''
        Functionality: this function will search the current view based on what the user has typed.

        Parameter: None
        
        Return Value: None
        '''
        q = self.search_input.text().strip().lower()
        if not q:
            if self.current_view == 'students':
                self.display_students()
            elif self.current_view == 'instructors':
                self.display_instructors()
            else:
                self.display_courses()
            return
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            if self.current_view == 'students':
                like = f"%{q}%"
                cur.execute("""
                    SELECT s.student_id, s.name, s.age, s.email
                    FROM students s
                    LEFT JOIN registrations r ON r.student_id=s.student_id
                    LEFT JOIN courses c ON c.course_id=r.course_id
                    WHERE lower(s.name) LIKE ? OR lower(s.student_id) LIKE ? OR lower(c.course_name) LIKE ?
                    GROUP BY s.student_id
                    ORDER BY s.name
                """, (like, like, like))
                rows = cur.fetchall()
                self.display_students(rows)
            elif self.current_view == 'instructors':
                like = f"%{q}%"
                cur.execute("""
                    SELECT instructor_id, name, age, email
                    FROM instructors
                    WHERE lower(name) LIKE ? OR lower(instructor_id) LIKE ? OR lower(email) LIKE ?
                    ORDER BY name
                """, (like, like, like))
                rows = cur.fetchall()
                self.display_instructors(rows)
            elif self.current_view == 'courses':
                like = f"%{q}%"
                cur.execute("""
                    SELECT c.course_id, c.course_name, COALESCE(i.name,'')
                    FROM courses c
                    LEFT JOIN instructors i ON i.instructor_id=c.instructor_id
                    LEFT JOIN registrations r ON r.course_id=c.course_id
                    LEFT JOIN students s ON s.student_id=r.student_id
                    WHERE lower(c.course_name) LIKE ? OR lower(c.course_id) LIKE ? OR lower(i.name) LIKE ? OR lower(s.name) LIKE ?
                    GROUP BY c.course_id
                    ORDER BY c.course_name
                """, (like, like, like, like))
                rows = cur.fetchall()
                self.display_courses(rows)

    def update_instructor_dropdowns(self):
        '''
        Functionality: it refreshes the instructor dropdown in assignment and other forms

        Parameter: None

        Returns: None
        '''
        self.assign_instructor_dropdown.clear()
        for iid, name, _, _ in dbapi.list_instructors():
            self.assign_instructor_dropdown.addItem(f"{name} ({iid})", iid)

    def update_assign_course_dropdown(self):
        '''
        Functionality: it refreshes the course dropdown used to assign an instructor.

        Parameter: None

        Return Value: None
        '''
        self.assign_course_dropdown.clear()
        for cid, cname, _ in dbapi.list_courses():
            self.assign_course_dropdown.addItem(f"{cname} ({cid})", cid)

    def assign_instructor_to_course(self):
        '''
        Functionality: this function will assignt the instructor to the selected course. 
        but it will make sure before doing this that the instructor and the course already exist 
        and updates course's instructor_id via dbapi.

        Parameter: None

        Return Value: None

        User feedback: a message box will appear for the user to tell them if it was a success or if there was an error. 
        '''
        instructor_id = self.assign_instructor_dropdown.currentData()
        course_id = self.assign_course_dropdown.currentData()
        if not instructor_id or not course_id:
            QMessageBox.warning(self, "Error", "Select instructor and course.")
            return
        if not dbapi.read_instructor(instructor_id):
            QMessageBox.warning(self, "Error", "Instructor not found!")
            return
        if not dbapi.read_course(course_id):
            QMessageBox.warning(self, "Error", "Course not found!")
            return
        dbapi.update_course(course_id, instructor_id=instructor_id)
        QMessageBox.information(self, "Success", "Instructor assigned to course.")
        self.display_courses()

    def add_student(self):
        '''
        Functionality: this function add a new student record after checking that all fields are entered.
        and the student ID is unique, the age is a non-negative integer and the email has a valid format. 

        Parameter: None

        Return Value: None

        User Feedback: the function will send a message box to the user telling them if it was a success or if there has been an error.
        '''
        import re
        name = self.student_name.text().strip()
        age = self.student_age.text().strip()
        email = self.student_email.text().strip()
        student_id = self.student_id.text().strip()
        if not name or not age or not email or not student_id:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if not age.isdigit() or int(age) < 0:
            QMessageBox.warning(self, "Input Error", "Age must be a non-negative integer.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Input Error", "Invalid email format.")
            return
        if dbapi.read_student(student_id):
            QMessageBox.warning(self, "Input Error", "Student ID already exists.")
            return
        dbapi.create_student(student_id, name, int(age), email)
        QMessageBox.information(self, "Student Added", f"Student: {name}, Age: {age}, Email: {email}, ID: {student_id}")
        if self.current_view == 'students':
            self.display_students()

    def add_instructor(self):
        '''
        Functionality: this function add a new instructor record after checking that all fields are entered.
        and the instructor ID is unique, the age is a non-negative integer and the email has a valid format. 

        Parameter: None

        Return Value: None

        User Feedback: the function will send a message box to the user telling them if it was a success or if there has been an error.
        '''
        import re
        name = self.instructor_name.text().strip()
        age = self.instructor_age.text().strip()
        email = self.instructor_email.text().strip()
        instructor_id = self.instructor_id.text().strip()
        if not name or not age or not email or not instructor_id:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if not age.isdigit() or int(age) < 0:
            QMessageBox.warning(self, "Input Error", "Age must be a non-negative integer.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Input Error", "Invalid email format.")
            return
        if dbapi.read_instructor(instructor_id):
            QMessageBox.warning(self, "Input Error", "Instructor ID already exists.")
            return
        dbapi.create_instructor(instructor_id, name, int(age), email)
        QMessageBox.information(self, "Instructor Added", f"Instructor: {name}, Age: {age}, Email: {email}, ID: {instructor_id}")
        self.update_instructor_dropdowns()
        if self.current_view == 'instructors':
            self.display_instructors()

    def add_course(self):
        '''
        Functionality: this function add a new course record after checking that all fields are entered.
        and the Course ID is unique, and the instructor must exist.

        Parameter: None

        Return Value: None

        User Feedback: the function will send a message box to the user telling them if it was a success or if there has been an error.
        '''
        course_id = self.course_id.text().strip()
        course_name = self.course_name.text().strip()
        instructor_id = self.course_instructor_id.text().strip()
        if not course_id or not course_name or not instructor_id:
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return
        if dbapi.read_course(course_id):
            QMessageBox.warning(self, "Input Error", "Course ID already exists.")
            return
        if not dbapi.read_instructor(instructor_id):
            QMessageBox.warning(self, "Input Error", "Instructor ID not found!")
            return
        dbapi.create_course(course_id, course_name, instructor_id)
        QMessageBox.information(self, "Course Added", f"Course: {course_name}, ID: {course_id}")
        self.update_course_dropdown()
        self.update_assign_course_dropdown()
        if self.current_view == 'courses':
            self.display_courses()

def main():
    '''
    Functionality: its the application entry point.
    The main function first start by ensuring that the database tables already exist.
    and it starts the qt event loop and shows the mainwindow.

    Parameter: None

    Return Value: None
    '''
    dbapi.create_table()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
