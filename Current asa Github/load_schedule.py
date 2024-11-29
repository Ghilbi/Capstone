def load_schedule():
    """Generate and display the schedule."""
    schedule_table.delete(*schedule_table.get_children())  # Clear previous schedule

    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()

    # Fetch all necessary data with specific columns
    cursor.execute("SELECT id, name, type, duration FROM subjects")
    subjects = cursor.fetchall()
    cursor.execute("SELECT id, name, specialty, subjects FROM instructors")
    instructors = cursor.fetchall()
    cursor.execute("SELECT id, name, type, subjects FROM rooms")
    rooms = cursor.fetchall()

    # Initialize the schedule and start time
    schedule = []
    time_slot = 8  # Start time in 24-hour format (8:00 AM)

    for subject in subjects:
        subject_id, subject_name, subject_type, duration = subject

        # Find a qualified instructor
        instructor = next(
            (inst for inst in instructors if subject_name in inst[3].split(",")), None
        )
        if not instructor:
            continue  # Skip if no instructor is available
        instructor_name = instructor[1]

        # Find a suitable room
        room = next(
            (rm for rm in rooms if subject_name in rm[3].split(",") and rm[2] == subject_type),
            None,
        )
        if not room:
            continue  # Skip if no room is available
        room_name = room[1]

        # Assign time slot
        start_time = f"{time_slot:02}:00"
        end_time = f"{(time_slot + duration // 60):02}:{duration % 60:02}"
        time_slot += duration // 60  # Increment for the next subject

        # Add entry to schedule
        schedule.append((subject_name, instructor_name, room_name, f"{start_time} - {end_time}"))

    conn.close()

    # Display the schedule in the table
    for entry in schedule:
        schedule_table.insert("", tk.END, values=entry)
