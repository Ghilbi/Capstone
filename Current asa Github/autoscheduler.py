import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3


# Database Initialization
def initialize_db():
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            subjects TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            subjects TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            duration INTEGER
        )
    """)
    conn.commit()
    conn.close()


# Utility function to clear the frame
def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()


# Function to display the Home Tab
def show_home_tab():
    clear_frame()
    tk.Label(main_frame, text="Schedule Dashboard", font=("Arial", 16)).pack(pady=10)

    schedule_text = tk.Text(main_frame, width=80, height=20)
    schedule_text.pack(pady=10)

    def load_schedule():
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()

        # Fetch all data for scheduling
        cursor.execute("SELECT * FROM instructors")
        instructors = cursor.fetchall()
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()

        # Simple Scheduling Algorithm (replace with a more advanced logic if needed)
        schedule = []
        for subject in subjects:
            subject_name = subject[1]
            duration = subject[3]
            for instructor in instructors:
                for room in rooms:
                    if subject_name in instructor[3].split(",") and subject_name in room[3].split(","):
                        schedule.append(f"{subject_name}: {instructor[1]} in {room[1]} ({duration} mins)")
                        break

        # Display schedule
        schedule_text.delete("1.0", tk.END)
        schedule_text.insert(tk.END, "\n".join(schedule))
        conn.close()

    tk.Button(main_frame, text="Automatic Scheduling", command=load_schedule).pack(pady=10)


# Function to display the Instructor Management Tab
def show_instructor_tab():
    clear_frame()
    tk.Label(main_frame, text="Manage Instructors", font=("Arial", 16)).pack(pady=10)

    def refresh_instructors():
        """Refresh the instructor list."""
        instructor_list.delete(*instructor_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, specialty, subjects FROM instructors")
        for row in cursor.fetchall():
            instructor_list.insert("", tk.END, values=row)
        conn.close()

    def add_instructor():
        """Add a new instructor."""
        name = name_entry.get()
        specialty = specialty_combobox.get()
        subjects = subjects_entry.get()
        if not name or not specialty or not subjects:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO instructors (name, specialty, subjects) VALUES (?, ?, ?)", 
                       (name, specialty, subjects))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Instructor added successfully!")
        name_entry.delete(0, tk.END)
        specialty_combobox.set("")
        subjects_entry.delete(0, tk.END)
        refresh_instructors()

    def delete_instructor():
        """Delete the selected instructor."""
        selected_item = instructor_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an instructor to delete.")
            return
        instructor_id = instructor_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM instructors WHERE id = ?", (instructor_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Instructor deleted successfully!")
        refresh_instructors()

    def edit_instructor():
        """Edit the selected instructor."""
        selected_item = instructor_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an instructor to edit.")
            return

        # Fetch current details of the selected instructor
        instructor_id, name, specialty, subjects = instructor_list.item(selected_item[0], "values")

        def save_changes():
            """Save changes to the instructor."""
            new_name = name_entry.get()
            new_specialty = specialty_combobox.get()
            new_subjects = subjects_entry.get()
            if not new_name or not new_specialty or not new_subjects:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE instructors SET name = ?, specialty = ?, subjects = ? WHERE id = ?",
                (new_name, new_specialty, new_subjects, instructor_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Instructor updated successfully!")
            edit_window.destroy()
            refresh_instructors()

        # Edit window
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Instructor")
        tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, name)

        tk.Label(edit_window, text="Specialty:").grid(row=1, column=0, padx=10, pady=5)
        specialty_combobox = ttk.Combobox(
            edit_window, values=["Network and Security", "Web Technology", "ERP", "Computer Science", "Data Analytics"]
        )
        specialty_combobox.grid(row=1, column=1, padx=10, pady=5)
        specialty_combobox.set(specialty)

        tk.Label(edit_window, text="Subjects (comma-separated):").grid(row=2, column=0, padx=10, pady=5)
        subjects_entry = tk.Entry(edit_window)
        subjects_entry.grid(row=2, column=1, padx=10, pady=5)
        subjects_entry.insert(0, subjects)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new instructors
    tk.Label(main_frame, text="Name:").pack(pady=5)
    name_entry = tk.Entry(main_frame)
    name_entry.pack(pady=5)

    tk.Label(main_frame, text="Specialty:").pack(pady=5)
    specialty_combobox = ttk.Combobox(
        main_frame, values=["Network and Security", "Web Technology", "ERP", "Computer Science", "Data Analytics"]
    )
    specialty_combobox.pack(pady=5)

    tk.Label(main_frame, text="Subjects (comma-separated):").pack(pady=5)
    subjects_entry = tk.Entry(main_frame)
    subjects_entry.pack(pady=5)

    tk.Button(main_frame, text="Add Instructor", command=add_instructor).pack(pady=10)

    # Treeview for displaying instructors
    columns = ("ID", "Name", "Specialty", "Subjects")
    instructor_list = ttk.Treeview(main_frame, columns=columns, show="headings")
    instructor_list.heading("ID", text="ID")
    instructor_list.heading("Name", text="Name")
    instructor_list.heading("Specialty", text="Specialty")
    instructor_list.heading("Subjects", text="Subjects")
    instructor_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing instructors
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Instructor", command=delete_instructor).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Instructor", command=edit_instructor).pack(side=tk.LEFT, padx=5)

    refresh_instructors()


# Function to display the Subjects Page
def show_subjects_tab():
    clear_frame()
    tk.Label(main_frame, text="Manage Subjects", font=("Arial", 16)).pack(pady=10)

    def refresh_subjects():
        """Refresh the subject list."""
        subject_list.delete(*subject_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, duration FROM subjects")
        for row in cursor.fetchall():
            subject_list.insert("", tk.END, values=row)
        conn.close()

    def add_subject():
        """Add a new subject."""
        code = code_entry.get()
        title = title_entry.get()
        subject_type = type_combobox.get()
        if subject_type == "Pure Lecture":
            duration = 80  # 1 hour 20 minutes
        elif subject_type == "Lecture and Lab":
            duration = 160  # 2 hours 40 minutes
        else:
            messagebox.showerror("Error", "Please select a valid subject type.")
            return
        if not code or not title or not subject_type:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name, type, duration) VALUES (?, ?, ?)", 
                       (f"{code}: {title}", subject_type, duration))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Subject added successfully!")
        code_entry.delete(0, tk.END)
        title_entry.delete(0, tk.END)
        type_combobox.set("")
        refresh_subjects()

    def delete_subject():
        """Delete the selected subject."""
        selected_item = subject_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a subject to delete.")
            return
        subject_id = subject_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Subject deleted successfully!")
        refresh_subjects()

    def edit_subject():
        """Edit the selected subject."""
        selected_item = subject_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a subject to edit.")
            return

        # Fetch current details of the selected subject
        subject_id, current_name, current_type, current_duration = subject_list.item(selected_item[0], "values")
        code, title = current_name.split(": ", 1)

        def save_changes():
            """Save changes to the subject."""
            new_code = code_entry.get()
            new_title = title_entry.get()
            new_type = type_combobox.get()
            if new_type == "Pure Lecture":
                new_duration = 80  # 1 hour 20 minutes
            elif new_type == "Lecture and Lab":
                new_duration = 160  # 2 hours 40 minutes
            else:
                messagebox.showerror("Error", "Please select a valid subject type.")
                return
            if not new_code or not new_title or not new_type:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subjects SET name = ?, type = ?, duration = ? WHERE id = ?",
                (f"{new_code}: {new_title}", new_type, new_duration, subject_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Subject updated successfully!")
            edit_window.destroy()
            refresh_subjects()

        # Edit window
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Subject")
        tk.Label(edit_window, text="Subject Code:").grid(row=0, column=0, padx=10, pady=5)
        code_entry = tk.Entry(edit_window)
        code_entry.grid(row=0, column=1, padx=10, pady=5)
        code_entry.insert(0, code)

        tk.Label(edit_window, text="Subject Title:").grid(row=1, column=0, padx=10, pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.grid(row=1, column=1, padx=10, pady=5)
        title_entry.insert(0, title)

        tk.Label(edit_window, text="Subject Type:").grid(row=2, column=0, padx=10, pady=5)
        type_combobox = ttk.Combobox(edit_window, values=["Pure Lecture", "Lecture and Lab"])
        type_combobox.grid(row=2, column=1, padx=10, pady=5)
        type_combobox.set(current_type)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new subjects
    tk.Label(main_frame, text="Subject Code:").pack(pady=5)
    code_entry = tk.Entry(main_frame)
    code_entry.pack(pady=5)

    tk.Label(main_frame, text="Subject Title:").pack(pady=5)
    title_entry = tk.Entry(main_frame)
    title_entry.pack(pady=5)

    tk.Label(main_frame, text="Subject Type:").pack(pady=5)
    type_combobox = ttk.Combobox(main_frame, values=["Pure Lecture", "Lecture and Lab"])
    type_combobox.pack(pady=5)

    tk.Button(main_frame, text="Add Subject", command=add_subject).pack(pady=10)

    # Treeview for displaying subjects
    columns = ("ID", "Name", "Type", "Duration")
    subject_list = ttk.Treeview(main_frame, columns=columns, show="headings")
    subject_list.heading("ID", text="ID")
    subject_list.heading("Name", text="Subject")
    subject_list.heading("Type", text="Type")
    subject_list.heading("Duration", text="Duration (mins)")
    subject_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing subjects
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Subject", command=delete_subject).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Subject", command=edit_subject).pack(side=tk.LEFT, padx=5)

    refresh_subjects()


# Function to display the Rooms Page
def show_rooms_tab():
    clear_frame()
    tk.Label(main_frame, text="Manage Rooms", font=("Arial", 16)).pack(pady=10)

    def refresh_rooms():
        """Refresh the room list."""
        room_list.delete(*room_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, subjects FROM rooms")
        for row in cursor.fetchall():
            room_list.insert("", tk.END, values=row)
        conn.close()

    def add_room():
        """Add a new room."""
        name = name_entry.get()
        room_type = type_combobox.get()
        subjects = subjects_entry.get()
        if not name or not room_type or not subjects:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (name, type, subjects) VALUES (?, ?, ?)", 
                       (name, room_type, subjects))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room added successfully!")
        name_entry.delete(0, tk.END)
        type_combobox.set("")
        subjects_entry.delete(0, tk.END)
        refresh_rooms()

    def delete_room():
        """Delete the selected room."""
        selected_item = room_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a room to delete.")
            return
        room_id = room_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room deleted successfully!")
        refresh_rooms()

    def edit_room():
        """Edit the selected room."""
        selected_item = room_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a room to edit.")
            return

        # Fetch current details of the selected room
        room_id, name, room_type, subjects = room_list.item(selected_item[0], "values")

        def save_changes():
            """Save changes to the room."""
            new_name = name_entry.get()
            new_type = type_combobox.get()
            new_subjects = subjects_entry.get()
            if not new_name or not new_type or not new_subjects:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rooms SET name = ?, type = ?, subjects = ? WHERE id = ?",
                (new_name, new_type, new_subjects, room_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Room updated successfully!")
            edit_window.destroy()
            refresh_rooms()

        # Edit window
        edit_window = tk.Toplevel(root)
        edit_window.title("Edit Room")
        tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, name)

        tk.Label(edit_window, text="Type:").grid(row=1, column=0, padx=10, pady=5)
        type_combobox = ttk.Combobox(edit_window, values=["Lecture", "Lab"])
        type_combobox.grid(row=1, column=1, padx=10, pady=5)
        type_combobox.set(room_type)

        tk.Label(edit_window, text="Subjects (comma-separated):").grid(row=2, column=0, padx=10, pady=5)
        subjects_entry = tk.Entry(edit_window)
        subjects_entry.grid(row=2, column=1, padx=10, pady=5)
        subjects_entry.insert(0, subjects)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new rooms
    tk.Label(main_frame, text="Name:").pack(pady=5)
    name_entry = tk.Entry(main_frame)
    name_entry.pack(pady=5)

    tk.Label(main_frame, text="Type:").pack(pady=5)
    type_combobox = ttk.Combobox(main_frame, values=["Lecture", "Lab"])
    type_combobox.pack(pady=5)

    tk.Label(main_frame, text="Subjects (comma-separated):").pack(pady=5)
    subjects_entry = tk.Entry(main_frame)
    subjects_entry.pack(pady=5)

    tk.Button(main_frame, text="Add Room", command=add_room).pack(pady=10)

    # Treeview for displaying rooms
    columns = ("ID", "Name", "Type", "Subjects")
    room_list = ttk.Treeview(main_frame, columns=columns, show="headings")
    room_list.heading("ID", text="ID")
    room_list.heading("Name", text="Name")
    room_list.heading("Type", text="Type")
    room_list.heading("Subjects", text="Subjects")
    room_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing rooms
    button_frame = tk.Frame(main_frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Room", command=delete_room).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Room", command=edit_room).pack(side=tk.LEFT, padx=5)

    refresh_rooms()


# Main Application
root = tk.Tk()
root.title("Subject Load Scheduling System")

# Navigation Buttons
navigation_frame = tk.Frame(root)
navigation_frame.pack(side=tk.TOP, fill=tk.X)

tk.Button(navigation_frame, text="Home", command=show_home_tab).pack(side=tk.LEFT, padx=10, pady=5)
tk.Button(navigation_frame, text="Instructors", command=show_instructor_tab).pack(side=tk.LEFT, padx=10, pady=5)
tk.Button(navigation_frame, text="Rooms", command=show_rooms_tab).pack(side=tk.LEFT, padx=10, pady=5)
tk.Button(navigation_frame, text="Subjects", command=show_subjects_tab).pack(side=tk.LEFT, padx=10, pady=5)

# Main Content Frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Initialize Database
initialize_db()

# Show the Home Tab by default
show_home_tab()

# Run the application
root.mainloop()
