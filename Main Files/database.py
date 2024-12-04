# database.py
import sqlite3

# Create and connect to the main database
conn = sqlite3.connect('main.db')  # Renamed from 'subjects.db' to 'main.db' for clarity
cursor = conn.cursor()

def create_tables():
    """Create the necessary tables if they do not exist."""
    # Tracks Table with UNIQUE constraint on track_name
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tracks (
                        id INTEGER PRIMARY KEY,
                        track_name TEXT UNIQUE)''')  # Added UNIQUE constraint

    # Subjects Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Subjects (
                        id INTEGER PRIMARY KEY,
                        subject_code TEXT,
                        subject_description TEXT,
                        track_id INTEGER,
                        year_level TEXT,
                        trimester TEXT,
                        type TEXT,
                        FOREIGN KEY (track_id) REFERENCES Tracks(id))''')

    # Check if "course" column exists in "Subjects" table; if not, add it
    cursor.execute("PRAGMA table_info(Subjects)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'course' not in columns:
        cursor.execute('ALTER TABLE Subjects ADD COLUMN course TEXT')

    # Rooms Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS Rooms (
                        id INTEGER PRIMARY KEY,
                        room_code TEXT,
                        room_type TEXT)''')

    # Course Offerings Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS CourseOfferings (
                        subject_code TEXT,
                        subject_description TEXT,
                        room_code TEXT,
                        day_pattern TEXT,
                        time_slot TEXT,
                        group_name TEXT,
                        section_code TEXT)''')

    conn.commit()

# --- Existing functions for Tracks and Subjects ---

def add_track(track_name):
    """Add a new track to the database if it doesn't already exist."""
    if not track_exists(track_name):
        cursor.execute('INSERT INTO Tracks (track_name) VALUES (?)', (track_name,))
        conn.commit()

def track_exists(track_name):
    """Check if a track with the given name exists in the database."""
    cursor.execute('SELECT 1 FROM Tracks WHERE track_name = ?', (track_name,))
    return cursor.fetchone() is not None

def fetch_tracks():
    """Fetch all tracks from the database."""
    cursor.execute('SELECT * FROM Tracks')
    return cursor.fetchall()

def get_track_name_by_id(track_id):
    """Get the track name given its ID."""
    cursor.execute('SELECT track_name FROM Tracks WHERE id = ?', (track_id,))
    track_row = cursor.fetchone()
    return track_row[0] if track_row else "All Tracks"

def fetch_subjects(selected_track, selected_year_level, selected_trimester, selected_course):
    """Fetch subjects based on selected filters."""
    query = '''SELECT s.id, s.subject_code, s.subject_description, t.track_name, s.year_level, s.trimester, s.type, s.course 
               FROM Subjects s 
               LEFT JOIN Tracks t ON s.track_id = t.id 
               WHERE 1=1'''

    params = []

    if selected_track and selected_track != "All Tracks":
        query += ' AND t.track_name = ?'
        params.append(selected_track)
    
    if selected_year_level and selected_year_level != "All Year Levels":
        query += ' AND s.year_level = ?'
        params.append(selected_year_level)
    
    if selected_trimester and selected_trimester != "All Trimesters":
        query += ' AND s.trimester = ?'
        params.append(selected_trimester)
    
    if selected_course and selected_course != "All Courses":
        query += ' AND s.course = ?'
        params.append(selected_course)

    cursor.execute(query, tuple(params))
    subjects = cursor.fetchall()
    return subjects

def fetch_all_subjects():
    """Fetch all subjects from the database."""
    cursor.execute('''SELECT s.id, s.subject_code, s.subject_description, t.track_name, s.year_level, s.trimester, s.type, s.course 
                      FROM Subjects s 
                      LEFT JOIN Tracks t ON s.track_id = t.id''')
    subjects = cursor.fetchall()
    return subjects

def insert_subject(subject_code, subject_description, track_id, year_level, trimester, selected_type, course):
    """Insert a new subject into the database."""
    cursor.execute('''INSERT INTO Subjects (subject_code, subject_description, track_id, year_level, trimester, type, course) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (subject_code, subject_description, track_id, year_level, trimester, selected_type, course))
    conn.commit()

def update_subject_db(subject_id, subject_code, subject_description, track_id, year_level, trimester, selected_type, course):
    """Update an existing subject in the database."""
    cursor.execute('''UPDATE Subjects 
                      SET subject_code = ?, subject_description = ?, track_id = ?, year_level = ?, 
                          trimester = ?, type = ?, course = ? 
                      WHERE id = ?''', 
                   (subject_code, subject_description, track_id, year_level, trimester, selected_type, course, subject_id))
    conn.commit()

def delete_subject_db(subject_id):
    """Delete a subject from the database."""
    cursor.execute('DELETE FROM Subjects WHERE id = ?', (subject_id,))
    conn.commit()

# --- Existing functions for Rooms ---

def insert_room(room_code, room_type):
    """Insert a new room into the database."""
    cursor.execute('INSERT INTO Rooms (room_code, room_type) VALUES (?, ?)', (room_code, room_type))
    conn.commit()

def fetch_rooms():
    """Fetch all rooms from the database."""
    cursor.execute('SELECT * FROM Rooms')
    return cursor.fetchall()

def update_room_db(room_id, room_code, room_type):
    """Update an existing room in the database."""
    cursor.execute('''UPDATE Rooms 
                      SET room_code = ?, room_type = ? 
                      WHERE id = ?''', 
                   (room_code, room_type, room_id))
    conn.commit()

def delete_room_db(room_id):
    """Delete a room from the database."""
    cursor.execute('DELETE FROM Rooms WHERE id = ?', (room_id,))
    conn.commit()

# --- Course Offering Functions ---

def clear_course_offerings():
    """Clear all course offerings."""
    cursor.execute('DELETE FROM CourseOfferings')
    conn.commit()

def insert_course_offering(subject_code, subject_description, room_code, day_pattern, time_slot, group, section_code):
    """Insert a new course offering into the database."""
    cursor.execute('''INSERT INTO CourseOfferings 
                      (subject_code, subject_description, room_code, day_pattern, time_slot, group_name, section_code) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (subject_code, subject_description, room_code, day_pattern, time_slot, group, section_code))
    conn.commit()

def fetch_course_offerings():
    """Fetch all course offerings."""
    cursor.execute('SELECT * FROM CourseOfferings')
    return cursor.fetchall()

def close_connection():
    """Close the database connection."""
    conn.close()
