import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import ttk for the Notebook widget
import sqlite3

# Function to connect to SQLite database and create a table if it doesn't exist (Subjects)
def create_subjects_db():
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
                    track TEXT,
                    code TEXT,
                    desc TEXT,
                    type TEXT)''')
    conn.commit()
    conn.close()

# Function to connect to SQLite database and create a table if it doesn't exist (Rooms)
def create_rooms_db():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (
                    room_name TEXT,
                    room_type TEXT,
                    max_students INTEGER)''')
    conn.commit()
    conn.close()

# Function to add a new subject to the database
def add_subject():
    track = track_var.get()
    subject_code = subject_code_entry.get()
    subject_desc = subject_desc_entry.get()
    subject_type = subject_type_var.get()

    if track and subject_code and subject_desc and subject_type:
        conn = sqlite3.connect("subjects.db")
        c = conn.cursor()
        c.execute("INSERT INTO subjects (track, code, desc, type) VALUES (?, ?, ?, ?)",
                  (track, subject_code, subject_desc, subject_type))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"Subject {subject_code} added successfully!")
        subject_code_entry.delete(0, tk.END)
        subject_desc_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

# Function to add a new room to the database
def add_room():
    room_name = room_name_entry.get()
    room_type = room_type_var.get()
    max_students = max_students_entry.get()

    if room_name and room_type and max_students:
        try:
            max_students = int(max_students)
            conn = sqlite3.connect("rooms.db")
            c = conn.cursor()
            c.execute("INSERT INTO rooms (room_name, room_type, max_students) VALUES (?, ?, ?)",
                      (room_name, room_type, max_students))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", f"Room {room_name} added successfully!")
            room_name_entry.delete(0, tk.END)
            max_students_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Max students must be a number.")
    else:
        messagebox.showerror("Error", "Please fill in all fields.")

# Function to show all rooms from the database
def show_rooms():
    conn = sqlite3.connect("rooms.db")
    c = conn.cursor()
    c.execute("SELECT room_name, room_type, max_students FROM rooms")
    rooms = c.fetchall()
    conn.close()

    if rooms:
        rooms_list.delete(1.0, tk.END)
        for room in rooms:
            rooms_list.insert(tk.END, f"Room Name: {room[0]} | Room Type: {room[1]} | Max Students: {room[2]}\n")
            rooms_list.insert(tk.END, "-" * 40 + "\n")
    else:
        messagebox.showerror("Error", "No rooms available.")

# Function to generate and display subjects based on selected track
def generate_subjects():
    selected_track = track_var.get()  # Get the selected track from the dropdown
    conn = sqlite3.connect("subjects.db")
    c = conn.cursor()

    # Modify the SQL query to filter subjects based on the selected track
    if selected_track == "All Track":
        c.execute("SELECT track, code, desc, type FROM subjects")
    else:
        c.execute("SELECT track, code, desc, type FROM subjects WHERE track=?", (selected_track,))

    subjects = c.fetchall()
    conn.close()

    if subjects:
        subject_list.delete(1.0, tk.END)  # Clear the existing list
        for subject in subjects:
            subject_list.insert(tk.END, f"Track: {subject[0]} | Code: {subject[1]} | Description: {subject[2]} | Type: {subject[3]}\n")
            subject_list.insert(tk.END, "-" * 40 + "\n")
    else:
        messagebox.showerror("Error", "No subjects available for the selected track.")

# --- COURSE OFFERING PAGE ---
def generate_course_offering():
    conn_subjects = sqlite3.connect("subjects.db")
    conn_rooms = sqlite3.connect("rooms.db")
    
    c_subjects = conn_subjects.cursor()
    c_rooms = conn_rooms.cursor()

    # Get subjects data
    c_subjects.execute("SELECT track, code, desc, type FROM subjects")
    subjects = c_subjects.fetchall()

    # Get rooms data
    c_rooms.execute("SELECT room_name, room_type, max_students FROM rooms")
    rooms = c_rooms.fetchall()

    conn_subjects.close()
    conn_rooms.close()

    if subjects and rooms:
        course_offering_list.delete(1.0, tk.END)
        
        # Define class time slots from 7:30 AM to 7:30 PM, assuming 1-hour classes
        time_slots = []
        start_time = 7.5  # Starting at 7:30 AM
        for i in range(12):  # Schedule for 12 hours (7:30 AM - 7:30 PM)
            hour = int(start_time)
            minute = int((start_time - hour) * 60)
            formatted_time = f"{hour % 12 if hour % 12 != 0 else 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
            time_slots.append(formatted_time)
            start_time += 1

        # For each subject, assign a room, time slot, and create the offering
        for i, subject in enumerate(subjects):
            if i < len(rooms) and i < len(time_slots):  # Ensure there's a room and time slot available
                room = rooms[i]
                time_slot = time_slots[i]
                course_offering_list.insert(tk.END, f"Course Offering: {subject[0]} - {subject[1]} | {subject[2]} | Type: {subject[3]}\n")
                course_offering_list.insert(tk.END, f"Room: {room[0]} | Type: {room[1]} | Max Students: {room[2]}\n")
                course_offering_list.insert(tk.END, f"Time Slot: {time_slot}\n")
                course_offering_list.insert(tk.END, "-" * 40 + "\n")
            else:
                course_offering_list.insert(tk.END, f"Course Offering: {subject[0]} - {subject[1]} | {subject[2]} | Type: {subject[3]}\n")
                course_offering_list.insert(tk.END, f"No available room or time slot for this offering.\n")
                course_offering_list.insert(tk.END, "-" * 40 + "\n")
    else:
        messagebox.showerror("Error", "No subjects or rooms available.")

# Function to initialize the Tkinter window
def init_gui():
    global track_var, subject_code_entry, subject_desc_entry, subject_type_var
    global room_name_entry, room_type_var, max_students_entry
    global course_offering_list, subject_list, rooms_list

    window = tk.Tk()
    window.title("Course and Room Management")

    # Tab control
    notebook = ttk.Notebook(window)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create subject and room tabs
    subjects_tab = ttk.Frame(notebook)
    rooms_tab = ttk.Frame(notebook)
    course_offering_tab = ttk.Frame(notebook)

    notebook.add(subjects_tab, text="Subjects")
    notebook.add(rooms_tab, text="Rooms")
    notebook.add(course_offering_tab, text="Course Offering")

    # Subject Tab Layout
    track_label = tk.Label(subjects_tab, text="Select Track:")
    track_label.grid(row=0, column=0, padx=10, pady=5)
    track_var = ttk.Combobox(subjects_tab, values=["All Tracks", "Network & Security", "Web Technology", "Enterprise Resource Planning"])
    track_var.set("All Track")
    track_var.grid(row=0, column=1, padx=10, pady=5)

    subject_code_label = tk.Label(subjects_tab, text="Subject Code:")
    subject_code_label.grid(row=1, column=0, padx=10, pady=5)
    subject_code_entry = tk.Entry(subjects_tab)
    subject_code_entry.grid(row=1, column=1, padx=10, pady=5)

    subject_desc_label = tk.Label(subjects_tab, text="Subject Description:")
    subject_desc_label.grid(row=2, column=0, padx=10, pady=5)
    subject_desc_entry = tk.Entry(subjects_tab)
    subject_desc_entry.grid(row=2, column=1, padx=10, pady=5)

    subject_type_label = tk.Label(subjects_tab, text="Subject Type:")
    subject_type_label.grid(row=3, column=0, padx=10, pady=5)
    subject_type_var = ttk.Combobox(subjects_tab, values=["Lecture", "Lecture and Lab"])
    subject_type_var.set("Lecture")
    subject_type_var.grid(row=3, column=1, padx=10, pady=5)

    add_subject_button = tk.Button(subjects_tab, text="Add Subject", command=add_subject)
    add_subject_button.grid(row=4, column=0, columnspan=2, pady=10)

    generate_subjects_button = tk.Button(subjects_tab, text="Generate Subjects", command=generate_subjects)
    generate_subjects_button.grid(row=5, column=0, columnspan=2, pady=10)

    subject_list = tk.Text(subjects_tab, width=60, height=10)
    subject_list.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    # Room Tab Layout
    room_name_label = tk.Label(rooms_tab, text="Room Name:")
    room_name_label.grid(row=0, column=0, padx=10, pady=5)
    room_name_entry = tk.Entry(rooms_tab)
    room_name_entry.grid(row=0, column=1, padx=10, pady=5)

    room_type_label = tk.Label(rooms_tab, text="Room Type:")
    room_type_label.grid(row=1, column=0, padx=10, pady=5)
    room_type_var = ttk.Combobox(rooms_tab, values=["Lecture", "Lecture and Lab"])
    room_type_var.set("Lecture")
    room_type_var.grid(row=1, column=1, padx=10, pady=5)

    max_students_label = tk.Label(rooms_tab, text="Max Students:")
    max_students_label.grid(row=2, column=0, padx=10, pady=5)
    max_students_entry = tk.Entry(rooms_tab)
    max_students_entry.grid(row=2, column=1, padx=10, pady=5)

    add_room_button = tk.Button(rooms_tab, text="Add Room", command=add_room)
    add_room_button.grid(row=3, column=0, columnspan=2, pady=10)

    show_rooms_button = tk.Button(rooms_tab, text="Show Rooms", command=show_rooms)
    show_rooms_button.grid(row=4, column=0, columnspan=2, pady=10)

    rooms_list = tk.Text(rooms_tab, width=60, height=10)
    rooms_list.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    # Course Offering Tab Layout
    generate_course_button = tk.Button(course_offering_tab, text="Generate Course Offerings", command=generate_course_offering)
    generate_course_button.grid(row=0, column=0, columnspan=2, pady=10)

    course_offering_list = tk.Text(course_offering_tab, width=60, height=10)
    course_offering_list.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    window.mainloop()

# Initialize the databases and GUI
create_subjects_db()
create_rooms_db()
init_gui()
