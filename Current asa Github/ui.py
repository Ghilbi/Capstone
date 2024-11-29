import tkinter as tk
from home_page import show_home_tab
from instructors_page import show_instructor_tab
from rooms_page import show_rooms_tab
from subjects_page import show_subjects_tab
from initialize_db import schedule_instructor, get_subject_details, get_instructor_schedule
import datetime


def generate_schedule():
    # Example: Schedule a subject for an instructor (ID = 1, Subject ID = 2)
    instructor_id = 1
    subject_id = 2
    start_time = datetime.datetime.strptime("08:00", "%H:%M")  # Example start time
    duration = 1  # 1 hour class duration

    if schedule_instructor(instructor_id, subject_id, start_time, duration):
        print("Class successfully scheduled.")
    else:
        print("Failed to schedule the class.")

def setup_ui(root):
    """Set up the UI and navigation."""
    navigation_frame = tk.Frame(root)
    navigation_frame.pack(side=tk.TOP, fill=tk.X)

    tk.Button(navigation_frame, text="Home", command=lambda: show_home_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Instructors", command=lambda: show_instructor_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Rooms", command=lambda: show_rooms_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Subjects", command=lambda: show_subjects_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)

    global main_frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
