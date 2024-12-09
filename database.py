# database.py

import sqlite3

def init_db():
    conn = sqlite3.connect("subjects.db")
    cursor = conn.cursor()

    # Subjects Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SubjectsDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseCode TEXT,
            Description TEXT,
            Program TEXT,
            YearLevel INTEGER,
            Semester TEXT,
            Type TEXT
        );
    """)

    # Rooms Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS RoomsDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            RoomCode TEXT UNIQUE,
            IsLecture BOOLEAN,
            IsLab BOOLEAN,
            IsPureLecture BOOLEAN
        );
    """)

    # Days Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DaysDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Days_Code TEXT UNIQUE,
            Description TEXT
        );
    """)

    # Timeslots Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TimeslotsDatabase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timeslot TEXT UNIQUE
        );
    """)

    # Schedule Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            GroupName TEXT,
            Program TEXT,
            YearLevel INTEGER,
            Term TEXT,
            Section TEXT,
            CourseCode TEXT,
            Description TEXT,
            Time TEXT,
            Days TEXT,
            Room TEXT
        );
    """)

    conn.commit()
    conn.close()

def reset_subjects_database():
    conn = sqlite3.connect("subjects.db")
    cursor = conn.cursor()

    # Create a new table without unique constraints
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SubjectsDatabase_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            CourseCode TEXT,
            Description TEXT,
            Program TEXT,
            YearLevel INTEGER,
            Semester TEXT,
            Type TEXT
        );
    """)

    # Copy data from the old table to the new table
    cursor.execute("""
        INSERT INTO SubjectsDatabase_new (CourseCode, Description, Program, YearLevel, Semester, Type)
        SELECT CourseCode, Description, Program, YearLevel, Semester, Type FROM SubjectsDatabase;
    """)

    # Drop the old table
    cursor.execute("DROP TABLE SubjectsDatabase;")

    # Rename the new table to the original name
    cursor.execute("ALTER TABLE SubjectsDatabase_new RENAME TO SubjectsDatabase;")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    reset_subjects_database()  # Execute this line once to reset the SubjectsDatabase
    # After the first run, comment out the above line to prevent data loss
