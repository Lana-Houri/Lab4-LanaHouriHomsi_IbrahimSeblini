import tkinter as tk
from tkinter import ttk, messagebox
import re
from database import (
    list_students, list_instructors, list_courses,
    create_student, update_student, delete_student, read_student,
    create_instructor, update_instructor, delete_instructor, read_instructor,
    create_course, update_course, delete_course, read_course,
    create_registration
)

'''
School Management System GUI (Tkinter)

This file implements a Tkinter-based GUI to manage:
- Students (create, read, update, delete, search)
- Instructors (create, read, update, delete, search)
- Courses (create, read, update, delete, search)
- Student registrations to courses
- Assign instructors to courses

All functions and methods include full docstrings describing purpose,
parameters, and return values. Inline comments explain step-by-step logic.
'''


class ScrollFrame(ttk.Frame):
    '''
    A scrollable frame widget using a Canvas and an inner Frame.

    This class is useful when the main content is taller than the window.
    A Canvas hosts the inner frame; the Canvas is connected with a vertical
    scrollbar and handles mouse wheel scrolling for Windows and Linux.

    Attributes:
        canvas (tk.Canvas): Canvas used for scrolling.
        inner (ttk.Frame): Frame where widgets should be placed.
    '''

    def __init__(self, parent):
        '''
        Initialize the ScrollFrame.

        Parameters:
            parent (tk.Widget): Parent widget in which ScrollFrame is placed.

        Returns:
            None
        '''
        super().__init__(parent)

        # Canvas that will show the scrollbar region
        self.canvas = tk.Canvas(self, highlightthickness=0)

        # Vertical scrollbar widget that will be attached to the canvas
        vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # Inner frame that contains user widgets (placed inside the canvas)
        self.inner = ttk.Frame(self.canvas)

        # When the size of the inner frame changes, update the canvas scrollregion
        # so scrolling covers all child widgets.
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Add the inner frame to the canvas as a window (top-left anchored)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        # Tell canvas to update the scrollbar when the canvas view changes
        self.canvas.configure(yscrollcommand=vbar.set)

        # Layout canvas and scrollbar in the ScrollFrame
        self.canvas.pack(side="left", fill="both", expand=True)
        vbar.pack(side="right", fill="y")

        # Bind mouse wheel events for cross-platform scrolling
        # Windows/Mac send <MouseWheel> with event.delta
        # Linux often sends Button-4 (scroll up) and Button-5 (scroll down)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        '''
        Handle mouse wheel events and convert them into canvas vertical scrolls.

        Parameters:
            event (tk.Event): The mouse wheel event object.

        Returns:
            None
        '''
        # Linux scrolling: event.num == 4 (up) or 5 (down)
        if getattr(event, 'num', None) == 4:
            self.canvas.yview_scroll(-1, "units")
        elif getattr(event, 'num', None) == 5:
            self.canvas.yview_scroll(1, "units")
        else:
            # Windows/Mac: event.delta is a multiple of 120 per wheel step
            # Multiply by -1 to have standard scroll direction.
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")


def run_app():
    '''
    Initialize and run the School Management System GUI.

    This function builds the entire Tkinter window: forms, treeviews,
    buttons, handlers, and the main event loop.

    Parameters:
        None

    Returns:
        None
    '''
    # -----------------------
    # Root window setup
    # -----------------------
    root = tk.Tk()
    root.title("School Management System")
    root.geometry("1100x750")

    # Styling for widgets
    style = ttk.Style(root)
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("TButton", padding=6)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # -----------------------
    # Menu bar
    # -----------------------
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    # Simple File -> Exit
    filemenu.add_command(label="Exit", command=root.destroy)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    # -----------------------
    # Scrollable content container
    # -----------------------
    scroll = ScrollFrame(root)
    scroll.pack(side="top", anchor="nw", fill="both", expand=True, padx=16, pady=8)
    content = scroll.inner  # place widgets inside content

    # Configure column weights for responsive layout
    for col in range(4):
        # Make column 1 and 3 expand; 0 and 2 remain fixed
        content.grid_columnconfigure(col, weight=(1 if col in (1, 3) else 0))

    # ======================================================================
    # STUDENT FORM
    # ======================================================================
    ttk.Label(content, text="Student Form", font=("Segoe UI", 11, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    # Student form inputs: Name, Age, Email, Student ID
    ttk.Label(content, text="Name:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=3)
    student_name_entry = ttk.Entry(content, width=32)
    student_name_entry.grid(row=1, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Age:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=3)
    student_age_entry = ttk.Entry(content, width=32)
    student_age_entry.grid(row=2, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Email:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=3)
    student_email_entry = ttk.Entry(content, width=32)
    student_email_entry.grid(row=3, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Student ID:").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=3)
    student_id_entry = ttk.Entry(content, width=32)
    student_id_entry.grid(row=4, column=1, sticky="ew", pady=3)

    def add_student_action():
        '''
        Validate student form inputs and create a new student record.

        Reads input fields: student_name_entry, student_age_entry, student_email_entry, student_id_entry.
        Validates:
            - All fields present
            - Age is a non-negative integer
            - Email has a basic valid format
            - Student ID does not already exist
        On success:
            - Calls create_student(sid, name, age, email)
            - Refreshes the students treeview with refresh_students_tree()
            - Shows a success messagebox

        Parameters:
            None (reads directly from GUI entries)

        Returns:
            None
        '''
        try:
            # Read and sanitize form inputs
            name = student_name_entry.get().strip()
            age_txt = student_age_entry.get().strip()
            email = student_email_entry.get().strip()
            sid = student_id_entry.get().strip()

            # Input validations
            if not name or not age_txt or not email or not sid:
                raise ValueError("All fields are required.")
            if not age_txt.isdigit() or int(age_txt) < 0:
                raise ValueError("Age must be a non-negative integer.")
            # basic regex for email validity
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                raise ValueError("Invalid email format.")
            # ensure unique student ID
            if read_student(sid):
                raise ValueError("Student ID already exists.")

            # Create the student via database module
            create_student(sid, name, int(age_txt), email)

            # Update UI table
            refresh_students_tree()

            # Inform the user
            messagebox.showinfo("Success", f"Student {name} added.")

            # Optionally clear inputs (not done here; could be added if desired)

        except Exception as e:
            # Show any errors in an error dialog
            messagebox.showerror("Error", str(e))

    # Submit button for student form
    ttk.Button(content, text="Submit", command=add_student_action).grid(
        row=5, column=0, columnspan=2, sticky="ew", pady=(6, 14)
    )

    # Horizontal separator between form sections
    ttk.Separator(content, orient="horizontal").grid(row=5, column=0, columnspan=4, sticky="ew", pady=(14, 14))

    # ======================================================================
    # INSTRUCTOR FORM
    # ======================================================================
    ttk.Label(content, text="Instructor Form", font=("Segoe UI", 11, "bold")).grid(
        row=6, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    # Instructor input fields
    ttk.Label(content, text="Name:").grid(row=7, column=0, sticky="e", padx=(0, 8), pady=3)
    instructor_name_entry = ttk.Entry(content, width=32)
    instructor_name_entry.grid(row=7, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Age:").grid(row=8, column=0, sticky="e", padx=(0, 8), pady=3)
    instructor_age_entry = ttk.Entry(content, width=32)
    instructor_age_entry.grid(row=8, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Email:").grid(row=9, column=0, sticky="e", padx=(0, 8), pady=3)
    instructor_email_entry = ttk.Entry(content, width=32)
    instructor_email_entry.grid(row=9, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Instructor ID:").grid(row=10, column=0, sticky="e", padx=(0, 8), pady=3)
    instructor_id_entry = ttk.Entry(content, width=32)
    instructor_id_entry.grid(row=10, column=1, sticky="ew", pady=3)

    def add_instructor_action():
        '''
        Validate instructor form inputs and create a new instructor record.

        Reads inputs: instructor_name_entry, instructor_age_entry, instructor_email_entry, instructor_id_entry.
        Validates:
            - All fields present
            - Age is a non-negative integer
            - Email format basic check
            - Instructor ID not already present
        On success:
            - Calls create_instructor(iid, name, age, email)
            - Refreshes instructors table and assign-course dropdowns
            - Shows success message

        Parameters:
            None

        Returns:
            None
        '''
        try:
            # Extract values from entry widgets
            name = instructor_name_entry.get().strip()
            age_txt = instructor_age_entry.get().strip()
            email = instructor_email_entry.get().strip()
            iid = instructor_id_entry.get().strip()

            # Validate inputs
            if not name or not age_txt or not email or not iid:
                raise ValueError("All fields are required.")
            if not age_txt.isdigit() or int(age_txt) < 0:
                raise ValueError("Age must be a non-negative integer.")
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                raise ValueError("Invalid email format.")
            if read_instructor(iid):
                raise ValueError("Instructor ID already exists.")

            # Create instructor record
            create_instructor(iid, name, int(age_txt), email)

            # Refresh instructors and assignment-related lists
            refresh_instructors_tree()
            update_assign_course_list()

            # Notify success
            messagebox.showinfo("Success", f"Instructor {name} added.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Submit button for instructor form
    ttk.Button(content, text="Submit", command=add_instructor_action).grid(
        row=11, column=0, columnspan=2, sticky="ew", pady=(6, 14)
    )

    ttk.Separator(content, orient="horizontal").grid(row=11, column=0, columnspan=4, sticky="ew", pady=(14, 14))

    # ======================================================================
    # COURSE FORM
    # ======================================================================
    ttk.Label(content, text="Course Form", font=("Segoe UI", 11, "bold")).grid(
        row=12, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    # Course input fields: Course ID, Course Name, Instructor ID (optional)
    ttk.Label(content, text="Course ID:").grid(row=13, column=0, sticky="e", padx=(0, 8), pady=3)
    course_id_entry = ttk.Entry(content, width=32)
    course_id_entry.grid(row=13, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Course Name:").grid(row=14, column=0, sticky="e", padx=(0, 8), pady=3)
    course_name_entry = ttk.Entry(content, width=32)
    course_name_entry.grid(row=14, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Instructor ID:").grid(row=15, column=0, sticky="e", padx=(0, 8), pady=3)
    course_instructor_id_entry = ttk.Entry(content, width=32)
    course_instructor_id_entry.grid(row=15, column=1, sticky="ew", pady=3)

    def add_course_action():
        '''
        Validate course inputs and create a new course.

        Reads inputs:
            course_id_entry, course_name_entry, course_instructor_id_entry

        Validations:
            - All course fields required (in your UI you required instructor id)
            - Course ID unique (not already existing)
            - Instructor ID exists in instructors table (read_instructor)
        On success:
            - Calls create_course(cid, cname, iid)
            - Refreshes courses tree and course selection widgets
            - Shows success message

        Parameters:
            None

        Returns:
            None
        '''
        try:
            # Read values
            cid = course_id_entry.get().strip()
            cname = course_name_entry.get().strip()
            iid = course_instructor_id_entry.get().strip()

            # Validate non-empty
            if not cid or not cname or not iid:
                raise ValueError("All course fields are required.")
            # Ensure course doesn't already exist
            if read_course(cid):
                raise ValueError("Course ID already exists.")
            # Ensure the instructor id refers to an existing instructor
            if not read_instructor(iid):
                raise ValueError("Instructor ID not found.")

            # Create new course
            create_course(cid, cname, iid)

            # Refresh UI elements showing courses
            refresh_courses_tree()
            update_course_list()
            update_assign_course_list()

            # Inform user
            messagebox.showinfo("Success", f"Course {cname} added.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Submit button for course form
    ttk.Button(content, text="Submit", command=add_course_action).grid(
        row=16, column=0, columnspan=2, sticky="ew", pady=(6, 14)
    )

    ttk.Separator(content, orient="horizontal").grid(row=16, column=0, columnspan=4, sticky="ew", pady=(14, 14))

    # ======================================================================
    # REGISTER STUDENT TO COURSE
    # ======================================================================
    ttk.Label(content, text="Register Student to Course", font=("Segoe UI", 11, "bold")).grid(
        row=17, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    ttk.Label(content, text="Student ID:").grid(row=18, column=0, sticky="e", padx=(0, 8), pady=3)
    reg_student_id_entry = ttk.Entry(content, width=32)
    reg_student_id_entry.grid(row=18, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Course:").grid(row=19, column=0, sticky="e", padx=(0, 8), pady=3)
    course_var = tk.StringVar()
    course_combobox = ttk.Combobox(content, textvariable=course_var, state="readonly", width=30)
    course_combobox.grid(row=19, column=1, sticky="ew", pady=3)

    def update_course_list():
        '''
        Update the course selection combobox used for registrations.

        Reads course list via list_courses() and sets combobox values.
        If there are courses and none selected, set current selection to first.

        Parameters:
            None

        Returns:
            None
        '''
        # Get list of course ids (first element in each row returned)
        vals = [row[0] for row in list_courses()]
        course_combobox["values"] = vals
        # If values exist and nothing selected, set first
        if vals and not course_combobox.get():
            course_combobox.current(0)

    def register_course_action():
        '''
        Register a student into a course.

        Reads:
            - Student ID from reg_student_id_entry
            - Course ID from course_var (combobox)

        Validations:
            - Both Student ID and Course are provided
            - Student exists (read_student)
            - Course exists (read_course)

        On success:
            - Calls create_registration(sid, cid)
            - Shows success message

        Parameters:
            None

        Returns:
            None
        '''
        try:
            sid = reg_student_id_entry.get().strip()
            cid = course_var.get().strip()

            # Validate presence
            if not sid or not cid:
                raise ValueError("Both Student ID and Course are required.")
            # Ensure student and course exist
            if not read_student(sid):
                raise ValueError("Student ID not found.")
            if not read_course(cid):
                raise ValueError("Course ID not found.")

            # Create registration record
            create_registration(sid, cid)

            # Inform user
            messagebox.showinfo("Success", "Registration saved.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Register button
    ttk.Button(content, text="Register", command=register_course_action).grid(
        row=20, column=0, columnspan=2, sticky="ew", pady=(6, 14)
    )

    ttk.Separator(content, orient="horizontal").grid(row=20, column=0, columnspan=4, sticky="ew", pady=(14, 14))

    # ======================================================================
    # ASSIGN COURSE TO INSTRUCTOR
    # ======================================================================
    ttk.Label(content, text="Assign Course to Instructor", font=("Segoe UI", 11, "bold")).grid(
        row=21, column=0, columnspan=2, sticky="w", pady=(0, 4)
    )

    ttk.Label(content, text="Instructor ID:").grid(row=22, column=0, sticky="e", padx=(0, 8), pady=3)
    assign_instructor_id_entry = ttk.Entry(content, width=32)
    assign_instructor_id_entry.grid(row=22, column=1, sticky="ew", pady=3)

    ttk.Label(content, text="Course:").grid(row=23, column=0, sticky="e", padx=(0, 8), pady=3)
    assign_course_var = tk.StringVar()
    assign_course_combobox = ttk.Combobox(content, textvariable=assign_course_var, state="readonly", width=30)
    assign_course_combobox.grid(row=23, column=1, sticky="ew", pady=3)

    def update_assign_course_list():
        '''
        Update the combobox used for assigning instructors to courses.

        Uses list_courses() to populate values and sets first item as default
        if none selected.

        Parameters:
            None

        Returns:
            None
        '''
        vals = [row[0] for row in list_courses()]
        assign_course_combobox["values"] = vals
        if vals and not assign_course_combobox.get():
            assign_course_combobox.current(0)

    def assign_course_action():
        '''
        Assign a course to an instructor.

        Reads:
            - Instructor ID from assign_instructor_id_entry
            - Course ID from assign_course_var combobox

        Validations:
            - Both instructor ID and course ID are provided
            - Instructor exists
            - Course exists

        On success:
            - Calls update_course(cid, instructor_id=iid)
            - Refreshes courses tree to reflect assignment
            - Shows success message

        Parameters:
            None

        Returns:
            None
        '''
        try:
            iid = assign_instructor_id_entry.get().strip()
            cid = assign_course_var.get().strip()

            # Validate presence
            if not iid or not cid:
                raise ValueError("Both Instructor ID and Course are required.")
            # Validate existence
            if not read_instructor(iid):
                raise ValueError("Instructor ID not found.")
            if not read_course(cid):
                raise ValueError("Course ID not found.")

            # Update the course record to set its instructor
            update_course(cid, instructor_id=iid)

            # Refresh UI
            refresh_courses_tree()
            messagebox.showinfo("Success", "Instructor assigned to course.")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Assign button
    ttk.Button(content, text="Assign", command=assign_course_action).grid(
        row=24, column=0, columnspan=2, sticky="ew", pady=(6, 14)
    )

    ttk.Separator(content, orient="horizontal").grid(row=24, column=0, columnspan=4, sticky="ew", pady=(14, 14))

    # ======================================================================
    # STUDENTS TABLE + SEARCH + EDIT + DELETE
    # ======================================================================
    ttk.Label(content, text="All Students", font=("Segoe UI", 11, "bold")).grid(row=25, column=0, sticky="w")
    student_search_entry = ttk.Entry(content)
    student_search_entry.grid(row=25, column=1, sticky="ew")
    ttk.Button(content, text="Search", command=lambda: search_students()).grid(row=25, column=2, sticky="e", padx=4)
    ttk.Button(content, text="Show All", command=lambda: (student_search_entry.delete(0, tk.END), refresh_students_tree())).grid(row=25, column=3, sticky="e")

    # Treeview to display students (columns: ID, Name, Age, Email)
    students_tree = ttk.Treeview(content, columns=("ID", "Name", "Age", "Email"), show="headings", height=6)
    # Configure headings and column sizes/anchors
    students_tree.heading("ID", text="Student ID")
    students_tree.column("ID", width=140, stretch=False, anchor="w")
    students_tree.heading("Name", text="Name")
    students_tree.column("Name", width=220, stretch=False, anchor="w")
    students_tree.heading("Age", text="Age")
    students_tree.column("Age", width=70, stretch=False, anchor="center")
    students_tree.heading("Email", text="Email")
    students_tree.column("Email", width=240, stretch=True, anchor="w")
    students_tree.grid(row=26, column=0, columnspan=4, sticky="nsew", pady=(4, 0))

    def refresh_students_tree():
        '''
        Refresh the students_tree with the latest data from list_students().

        Parameters:
            None

        Returns:
            None
        '''
        # Clear existing rows
        students_tree.delete(*students_tree.get_children())
        # Insert all students (sid, name, age, email)
        for sid, name, age, email in list_students():
            students_tree.insert("", "end", values=(sid, name, age, email))

    def search_students():
        '''
        Filter the students list according to the search query.

        Reads:
            student_search_entry - search text (case-insensitive)
        Behavior:
            - If a non-empty query q is present, only rows where q appears
              in sid, name, or email (lowercased) are shown.
            - If q is empty, full list is refreshed.

        Parameters:
            None

        Returns:
            None
        '''
        q = student_search_entry.get().strip().lower()
        # Clear tree
        students_tree.delete(*students_tree.get_children())
        rows = list_students()
        # Filter rows
        for sid, name, age, email in rows:
            if q in sid.lower() or q in name.lower() or q in email.lower():
                students_tree.insert("", "end", values=(sid, name, age, email))
        if not q:
            # If search box empty, show full list
            refresh_students_tree()

    def get_selected_student_id():
        '''
        Get the currently selected student ID from students_tree.

        Returns:
            str | None: The student ID string if a selection exists, otherwise None.
        '''
        sel = students_tree.selection()
        if not sel:
            # If nothing selected, prompt the user
            messagebox.showwarning("Select a student", "Please select a student in the table.")
            return None
        # Return the first selected row's ID value
        return students_tree.item(sel[0], "values")[0]

    def edit_student_action():
        '''
        Open an edit dialog for the selected student, validate and save changes.

        Steps:
            - Get selected student ID using get_selected_student_id()
            - Fetch full row via read_student(sid)
            - Create a Toplevel window with Name, Age, Email inputs prefilled
            - On Save, validate inputs and call update_student(sid, ...)
            - Refresh the students tree and close the dialog

        Parameters:
            None

        Returns:
            None
        '''
        sid = get_selected_student_id()
        if not sid:
            return  # no selection, exit
        row = read_student(sid)
        if not row:
            messagebox.showerror("Not found", "Student not found.")
            return

        # Create an edit window
        win = tk.Toplevel(root)
        win.title(f"Edit Student {sid}")

        # Labels and entries prefilled with existing values
        ttk.Label(win, text="Name").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(win, text="Age").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(win, text="Email").grid(row=2, column=0, sticky="e", padx=6, pady=4)

        name_e = ttk.Entry(win)
        name_e.grid(row=0, column=1, pady=4)
        name_e.insert(0, row[1])  # existing name

        age_e = ttk.Entry(win)
        age_e.grid(row=1, column=1, pady=4)
        age_e.insert(0, str(row[2]))  # existing age

        email_e = ttk.Entry(win)
        email_e.grid(row=2, column=1, pady=4)
        email_e.insert(0, row[3])  # existing email

        def save():
            '''
            Save callback for edit student window.

            Reads and validates name_e, age_e, email_e. On success calls:
                update_student(sid, name=name, age=int(age_txt), email=email)
            Then refreshes students tree and closes the window.

            Parameters:
                None

            Returns:
                None
            '''
            try:
                # Read new values
                name = name_e.get().strip()
                age_txt = age_e.get().strip()
                email = email_e.get().strip()

                # Basic validation
                if not name or not age_txt or not email:
                    raise ValueError("All fields are required.")
                if not age_txt.isdigit() or int(age_txt) < 0:
                    raise ValueError("Age must be a non-negative integer.")
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    raise ValueError("Invalid email format.")

                # Apply update via database function
                update_student(sid, name=name, age=int(age_txt), email=email)

                # Refresh UI and close dialog
                refresh_students_tree()
                win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Save button in the edit dialog
        ttk.Button(win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=8)

    def delete_student_action():
        '''
        Delete the currently selected student (after confirmation).

        Steps:
            - Get selected student id via get_selected_student_id()
            - Ask user for confirmation via askyesno
            - Call delete_student(sid)
            - Refresh students tree

        Parameters:
            None

        Returns:
            None
        '''
        sid = get_selected_student_id()
        if not sid:
            return
        if not messagebox.askyesno("Delete", f"Delete student {sid}?"):
            return
        # Call delete in database and refresh UI
        delete_student(sid)
        refresh_students_tree()

    # Small frame for Edit/Delete buttons aligned to the students table
    students_btns = ttk.Frame(content)
    students_btns.grid(row=26, column=3, sticky="ne", padx=6, pady=6)
    ttk.Button(students_btns, text="Edit", command=edit_student_action).grid(row=0, column=0, padx=2)
    ttk.Button(students_btns, text="Delete", command=delete_student_action).grid(row=0, column=1, padx=2)

    # ======================================================================
    # INSTRUCTORS TABLE + SEARCH + EDIT + DELETE
    # ======================================================================
    ttk.Label(content, text="All Instructors", font=("Segoe UI", 11, "bold")).grid(row=27, column=0, sticky="w", pady=(12, 0))
    instructor_search_entry = ttk.Entry(content)
    instructor_search_entry.grid(row=27, column=1, sticky="ew")
    ttk.Button(content, text="Search", command=lambda: search_instructors()).grid(row=27, column=2, sticky="e", padx=4)
    ttk.Button(content, text="Show All", command=lambda: (instructor_search_entry.delete(0, tk.END), refresh_instructors_tree())).grid(row=27, column=3, sticky="e")

    instructors_tree = ttk.Treeview(content, columns=("ID", "Name", "Age", "Email"), show="headings", height=6)
    instructors_tree.heading("ID", text="Instructor ID")
    instructors_tree.column("ID", width=140, stretch=False, anchor="w")
    instructors_tree.heading("Name", text="Name")
    instructors_tree.column("Name", width=220, stretch=False, anchor="w")
    instructors_tree.heading("Age", text="Age")
    instructors_tree.column("Age", width=70, stretch=False, anchor="center")
    instructors_tree.heading("Email", text="Email")
    instructors_tree.column("Email", width=240, stretch=True, anchor="w")
    instructors_tree.grid(row=28, column=0, columnspan=4, sticky="nsew", pady=(4, 0))

    def refresh_instructors_tree():
        '''
        Refresh the instructors_tree with data from list_instructors().

        Parameters:
            None

        Returns:
            None
        '''
        instructors_tree.delete(*instructors_tree.get_children())
        for iid, name, age, email in list_instructors():
            instructors_tree.insert("", "end", values=(iid, name, age, email))

    def search_instructors():
        '''
        Filter instructors based on the search query.

        Reads:
            instructor_search_entry - case-insensitive search text

        Behavior:
            - If query present, show only matching rows where the query
              appears in instructor id, name, or email.
            - If query empty, refresh to show all.

        Parameters:
            None

        Returns:
            None
        '''
        q = instructor_search_entry.get().strip().lower()
        instructors_tree.delete(*instructors_tree.get_children())
        rows = list_instructors()
        for iid, name, age, email in rows:
            if q in iid.lower() or q in name.lower() or q in email.lower():
                instructors_tree.insert("", "end", values=(iid, name, age, email))
        if not q:
            refresh_instructors_tree()

    def get_selected_instructor_id():
        '''
        Returns:
            str | None: Selected instructor ID if a row is selected, otherwise None.
        '''
        sel = instructors_tree.selection()
        if not sel:
            messagebox.showwarning("Select an instructor", "Please select an instructor in the table.")
            return None
        return instructors_tree.item(sel[0], "values")[0]

    def edit_instructor_action():
        '''
        Open a dialog to edit the selected instructor's details.

        Steps:
            - Get selected instructor id
            - Read instructor data via read_instructor(iid)
            - Populate Toplevel form and allow editing of name, age, email
            - On save: validate and call update_instructor(iid, ...)
            - Refresh instructors and courses (in case instructor names in courses displayed)

        Parameters:
            None

        Returns:
            None
        '''
        iid = get_selected_instructor_id()
        if not iid:
            return
        row = read_instructor(iid)
        if not row:
            messagebox.showerror("Not found", "Instructor not found.")
            return

        win = tk.Toplevel(root)
        win.title(f"Edit Instructor {iid}")

        # Labels and prefilled entries
        ttk.Label(win, text="Name").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(win, text="Age").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(win, text="Email").grid(row=2, column=0, sticky="e", padx=6, pady=4)

        name_e = ttk.Entry(win)
        name_e.grid(row=0, column=1, pady=4)
        name_e.insert(0, row[1])

        age_e = ttk.Entry(win)
        age_e.grid(row=1, column=1, pady=4)
        age_e.insert(0, str(row[2]))

        email_e = ttk.Entry(win)
        email_e.grid(row=2, column=1, pady=4)
        email_e.insert(0, row[3])

        def save():
            '''
            Save updated instructor data to the database and refresh UI.

            Parameters:
                None

            Returns:
                None
            '''
            try:
                name = name_e.get().strip()
                age_txt = age_e.get().strip()
                email = email_e.get().strip()

                # Validation
                if not name or not age_txt or not email:
                    raise ValueError("All fields are required.")
                if not age_txt.isdigit() or int(age_txt) < 0:
                    raise ValueError("Age must be a non-negative integer.")
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    raise ValueError("Invalid email format.")

                # Update DB
                update_instructor(iid, name=name, age=int(age_txt), email=email)

                # Refresh UI components that might show instructor info
                refresh_instructors_tree()
                refresh_courses_tree()
                win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Save", command=save).grid(row=3, column=0, columnspan=2, pady=8)

    def delete_instructor_action():
        '''
        Delete the selected instructor after confirmation.

        Steps:
            - Check selection
            - Confirm delete
            - Call delete_instructor(iid)
            - Refresh instructors and courses and assignment lists

        Parameters:
            None

        Returns:
            None
        '''
        iid = get_selected_instructor_id()
        if not iid:
            return
        if not messagebox.askyesno("Delete", f"Delete instructor {iid}?"):
            return
        delete_instructor(iid)
        refresh_instructors_tree()
        refresh_courses_tree()
        update_assign_course_list()

    # Buttons for instructor actions
    instructors_btns = ttk.Frame(content)
    instructors_btns.grid(row=28, column=3, sticky="ne", padx=6, pady=6)
    ttk.Button(instructors_btns, text="Edit", command=edit_instructor_action).grid(row=0, column=0, padx=2)
    ttk.Button(instructors_btns, text="Delete", command=delete_instructor_action).grid(row=0, column=1, padx=2)

 
    ttk.Label(content, text="All Courses", font=("Segoe UI", 11, "bold")).grid(row=29, column=0, sticky="w", pady=(12, 0))
    course_search_entry = ttk.Entry(content)
    course_search_entry.grid(row=29, column=1, sticky="ew")
    ttk.Button(content, text="Search", command=lambda: search_courses()).grid(row=29, column=2, sticky="e", padx=4)
    ttk.Button(content, text="Show All", command=lambda: (course_search_entry.delete(0, tk.END), refresh_courses_tree())).grid(row=29, column=3, sticky="e")

    courses_tree = ttk.Treeview(content, columns=("ID", "Name", "Instructor"), show="headings", height=6)
    courses_tree.heading("ID", text="Course ID")
    courses_tree.column("ID", width=140, stretch=False, anchor="w")
    courses_tree.heading("Name", text="Course Name")
    courses_tree.column("Name", width=240, stretch=False, anchor="w")
    courses_tree.heading("Instructor", text="Instructor")
    courses_tree.column("Instructor", width=200, stretch=True, anchor="w")
    courses_tree.grid(row=30, column=0, columnspan=4, sticky="nsew", pady=(4, 0))

    def refresh_courses_tree():
        '''
        Refresh the courses_tree with data from list_courses().

        Each row expected format: (course_id, course_name, instructor_name_or_id)

        Parameters:
            None

        Returns:
            None
        '''
        courses_tree.delete(*courses_tree.get_children())
        for cid, cname, iname in list_courses():
            courses_tree.insert("", "end", values=(cid, cname, iname))

    def search_courses():
        '''
        Filter the courses table based on search query.

        Reads:
            course_search_entry for query text

        Behavior:
            - Show rows where query appears in course id, course name, or instructor name
            - If empty query, refresh to show all

        Parameters:
            None

        Returns:
            None
        '''
        q = course_search_entry.get().strip().lower()
        courses_tree.delete(*courses_tree.get_children())
        rows = list_courses()
        for cid, cname, iname in rows:
            if q in cid.lower() or q in cname.lower() or q in iname.lower():
                courses_tree.insert("", "end", values=(cid, cname, iname))
        if not q:
            refresh_courses_tree()

    def get_selected_course_id():
        '''
        Get the selected course id from the courses_tree.

        Returns:
            str | None: The selected course ID or None if nothing selected.
        '''
        sel = courses_tree.selection()
        if not sel:
            messagebox.showwarning("Select a course", "Please select a course in the table.")
            return None
        return courses_tree.item(sel[0], "values")[0]

    def edit_course_action():
        '''
        Open an edit dialog for the chosen course.

        Steps:
            - Get selected course id via get_selected_course_id()
            - Read course row via read_course(cid)
            - Provide fields to edit: course name and instructor id (via combobox)
            - Validate inputs: non-empty course name, instructor id if provided must exist
            - Call update_course(cid, course_name=new_name, instructor_id=new_iid_or_None)
            - Refresh courses table

        Parameters:
            None

        Returns:
            None
        '''
        cid = get_selected_course_id()
        if not cid:
            return
        row = read_course(cid)
        if not row:
            messagebox.showerror("Not found", "Course not found.")
            return

        win = tk.Toplevel(root)
        win.title(f"Edit Course {cid}")

        ttk.Label(win, text="Course Name").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        ttk.Label(win, text="Instructor ID").grid(row=1, column=0, sticky="e", padx=6, pady=4)

        name_e = ttk.Entry(win)
        name_e.grid(row=0, column=1, pady=4)
        name_e.insert(0, row[1])  # current course name

        # Prefill instructor id in a combobox of instructor ids; allow empty string
        instr_var = tk.StringVar(value=(row[2] if row[2] else ""))
        instr_box = ttk.Combobox(win, textvariable=instr_var, state="readonly", values=[i[0] for i in list_instructors()])
        instr_box.grid(row=1, column=1, pady=4)

        def save():
            '''
            Save updated course information.

            Validates new course name and instructor id (if present) and updates DB.

            Parameters:
                None

            Returns:
                None
            '''
            try:
                new_name = name_e.get().strip()
                new_iid = instr_var.get().strip()

                # Validate name
                if not new_name:
                    raise ValueError("Course name cannot be empty.")
                # If instructor provided, ensure it exists
                if new_iid and not read_instructor(new_iid):
                    raise ValueError("Instructor ID not found.")

                # Update DB: if new_iid empty -> pass None to clear assignment
                update_course(cid, course_name=new_name, instructor_id=(new_iid if new_iid else None))

                # Refresh and close
                refresh_courses_tree()
                win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(win, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=8)

    def delete_course_action():
        '''
        Delete the selected course after user confirmation.

        Steps:
            - Get selected course id
            - Confirm deletion
            - Call delete_course(cid)
            - Refresh courses table and dependent comboboxes

        Parameters:
            None

        Returns:
            None
        '''
        cid = get_selected_course_id()
        if not cid:
            return
        if not messagebox.askyesno("Delete", f"Delete course {cid}?"):
            return
        delete_course(cid)
        refresh_courses_tree()
        update_course_list()
        update_assign_course_list()

    # Buttons for course actions
    courses_btns = ttk.Frame(content)
    courses_btns.grid(row=30, column=3, sticky="ne", padx=6, pady=6)
    ttk.Button(courses_btns, text="Edit", command=edit_course_action).grid(row=0, column=0, padx=2)
    ttk.Button(courses_btns, text="Delete", command=delete_course_action).grid(row=0, column=1, padx=2)


    # Populate initial data for all tables and comboboxes
    refresh_students_tree()
    refresh_instructors_tree()
    refresh_courses_tree()
    update_course_list()
    update_assign_course_list()

    # Bind Enter key in search entries to execute searches
    student_search_entry.bind("<Return>", lambda e: search_students())
    instructor_search_entry.bind("<Return>", lambda e: search_instructors())
    course_search_entry.bind("<Return>", lambda e: search_courses())

    # Run the Tkinter main loop
    root.mainloop()


# Entry point guard
if __name__ == "__main__":
    run_app()
