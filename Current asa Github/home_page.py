import tkinter as tk
from tkinter import ttk
import sqlite3
from utils import clear_frame

def show_home_tab(frame):
    """Display the home page."""
    clear_frame(frame)
    tk.Label(frame, text="Schedule Dashboard", font=("Arial", 16)).pack(pady=10)

    # Treeview for displaying the schedule
    schedule_table = ttk.Treeview(frame, columns=("Subject", "Instructor", "Room", "Time Slot"), show="headings")
    schedule_table.heading("Subject", text="Subject")
    schedule_table.heading("Instructor", text="Instructor")
    schedule_table.heading("Room", text="Room")
    schedule_table.heading("Time Slot", text="Time Slot")
    schedule_table.pack(fill=tk.BOTH, expand=True, pady=10)

    def load_schedule():
        """Generate and display the schedule."""
        schedule_table.delete(*schedule_table.get_children())  # Clear previous schedule

        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()

        # Fetch all necessary data
        cursor.execute("SELECT id, name, type, duration FROM subjects")
        subjects = cursor.fetchall()  # [(id, name, type, duration), ...]

        cursor.execute("SELECT id, name, specialty, subjects FROM instructors")
        instructors = cursor.fetchall()  # [(id, name, specialty, subjects), ...]

        cursor.execute("SELECT id, name, type, subjects FROM rooms")
        rooms = cursor.fetchall()  # [(id, name, type, subjects), ...]

        # Initialize the schedule and time slot
        schedule = []
        time_slot = 8  # Start time in 24-hour format (8:00 AM)

        for subject in subjects:
            subject_id, subject_name, subject_type, duration = subject

            # Find a qualified instructor
            instructor = next(
                (inst for inst in instructors if subject_name.split(":")[0].strip() in inst[3].split(", ")), None
            )
            if not instructor:
                print(f"No instructor found for subject: {subject_name}")  # Debug: Missing instructor
                continue
            instructor_name = instructor[1]

            # Find a suitable room
            room = next(
                (rm for rm in rooms if subject_name.split(":")[0].strip() in rm[3].split(", ") and rm[2] == subject_type),
                None,
            )
            if not room:
                print(f"No room found for subject: {subject_name}")  # Debug: Missing room
                continue
            room_name = room[1]

            # Assign time slot
            start_time = f"{time_slot:02}:00"
            end_time = f"{(time_slot + duration // 60):02}:{duration % 60:02}"
            time_slot += duration // 60  # Increment for the next subject

            # Add entry to schedule
            schedule.append((subject_name, instructor_name, room_name, f"{start_time} - {end_time}"))

        conn.close()

        # Display the schedule in the table
        if not schedule:
            print("No schedule generated.")  # Debug: Empty schedule
        for entry in schedule:
            schedule_table.insert("", tk.END, values=entry)

    # Button to generate the schedule
    tk.Button(frame, text="Generate Schedule", command=load_schedule).pack(pady=10)
