# main.py
import tkinter as tk
from tkinter import ttk
import database
import gui
import rooms_page
import course_offering  # Import the course offering module

def main():
    """Initialize the application."""
    database.create_tables()  # Create all necessary tables in the main database

    tracks = database.fetch_tracks()
    if not tracks:
        database.add_track("Network & Security")
        database.add_track("Web Technology")
        database.add_track("Enterprise Resource Planning")
        database.add_track("Minor")

    root = tk.Tk()
    root.title("Track and Room Management System")

    # Create a Notebook (tabbed interface)
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    # Create frames for each tab
    subjects_frame = ttk.Frame(notebook)
    rooms_frame = ttk.Frame(notebook)
    course_offering_frame = ttk.Frame(notebook)  # New frame for Course Offering

    # Add tabs to the notebook
    notebook.add(subjects_frame, text='Subjects')
    notebook.add(rooms_frame, text='Rooms')
    notebook.add(course_offering_frame, text='Course Offering')  # Add the new tab

    # Initialize the GUI classes with the respective frames
    subjects_app = gui.AppGUI(subjects_frame)
    rooms_app = rooms_page.RoomsPage(rooms_frame)
    course_offering_app = course_offering.CourseOfferingPage(course_offering_frame)  # Initialize the new page

    root.mainloop()
    database.close_connection()  # Close the main database connection

if __name__ == "__main__":
    main()
