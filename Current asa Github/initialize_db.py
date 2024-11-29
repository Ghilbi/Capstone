import sqlite3
import datetime

# Define constants for the time range and maximum load
START_TIME = datetime.datetime.strptime("07:30", "%H:%M")
END_TIME = datetime.datetime.strptime("19:30", "%H:%M")
MAX_LOAD = 8  # Instructor's maximum load in hours
BREAK_TIME = datetime.timedelta(hours=0.5)  # 30-minute break

def initialize_db():
    """Initialize the SQLite database and create required tables."""
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
            duration INTEGER,
            load REAL
        )
    """)
    conn.commit()
    conn.close()

# Function to fetch subjects from database
def get_subject_details():
    """Get subjects from the database with their load."""
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, duration FROM subjects")
    subjects = cursor.fetchall()
    subject_details = []
    for subject in subjects:
        subject_id, name, subject_type, duration = subject
        load = 1 if subject_type == "Lecture" else 1.33
        subject_details.append({
            "id": subject_id,
            "name": name,
            "type": subject_type,
            "duration": duration,
            "load": load
        })
    conn.close()
    return subject_details

# Function to fetch instructor's schedule
def get_instructor_schedule(instructor_id):
    """Get the current schedule of the instructor."""
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT subject_id, start_time, end_time FROM schedule WHERE instructor_id = ?
    """, (instructor_id,))
    schedule = cursor.fetchall()
    conn.close()
    return schedule

# Function to check if instructor's time is available
def is_time_available(instructor_schedule, start_time, end_time):
    """Check if the instructor has a conflict with the given time range."""
    for subject in instructor_schedule:
        subject_start_time = datetime.datetime.strptime(subject[1], "%H:%M")
        subject_end_time = datetime.datetime.strptime(subject[2], "%H:%M")
        if (start_time < subject_end_time and end_time > subject_start_time):
            return False  # Conflict found
    return True

# Function to check if the instructor can handle more load
def can_instructor_handle_load(instructor_id, additional_load):
    """Check if the instructor's total load will exceed the max load."""
    total_load = 0
    instructor_schedule = get_instructor_schedule(instructor_id)
    for subject in instructor_schedule:
        subject_id = subject[0]
        subject_details = get_subject_details()
        for sub in subject_details:
            if sub['id'] == subject_id:
                total_load += sub['load']
    if total_load + additional_load > MAX_LOAD:
        return False  # Exceeds max load
    return True

# Function to schedule an instructor with constraints
def schedule_instructor(instructor_id, subject_id, start_time, duration):
    """Assign a subject to an instructor while adhering to the constraints."""
    subject_details = get_subject_details()
    for sub in subject_details:
        if sub["id"] == subject_id:
            subject_load = sub["load"]
            break

    # Check if the instructor can handle the load
    if not can_instructor_handle_load(instructor_id, subject_load):
        print("Instructor cannot handle additional load.")
        return False

    # Check if the time is available for the instructor
    end_time = start_time + datetime.timedelta(hours=duration)
    if not is_time_available(get_instructor_schedule(instructor_id), start_time, end_time):
        print("Time conflict with the instructor's schedule.")
        return False

    # Schedule the subject
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO schedule (instructor_id, subject_id, start_time, end_time) 
        VALUES (?, ?, ?, ?)
    """, (instructor_id, subject_id, start_time.strftime("%H:%M"), end_time.strftime("%H:%M")))
    conn.commit()
    conn.close()
    print(f"Subject {subject_id} successfully scheduled for Instructor {instructor_id}")
    return True
