# main.py

import tkinter as tk
from tkinter import ttk
from database import init_db
from logger_config import setup_logging
from subjects import SubjectApp
from rooms import RoomsApp
from days import DaysApp
from timeslots import TimeslotApp
from subject_offering import SubjectOfferingApp  # Ensure this import is correct

def main():
    setup_logging()
    init_db()

    root = tk.Tk()
    root.title("Management System")
    root.geometry("1200x800")  # Adjust window size as needed

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Subjects tab
    subject_app = SubjectApp(notebook)
    notebook.add(subject_app.frame, text="Subjects")

    # Rooms tab
    rooms_app = RoomsApp(notebook)
    notebook.add(rooms_app.frame, text="Rooms")

    # Days tab
    days_app = DaysApp(notebook)
    notebook.add(days_app.frame, text="Days")

    # Timeslots tab
    timeslots_app = TimeslotApp(notebook)
    notebook.add(timeslots_app.frame, text="Timeslots")

    # Subject Offering tab
    subject_offering_app = SubjectOfferingApp(notebook)
    notebook.add(subject_offering_app, text="Subject Offering")  # Add the instance directly

    root.mainloop()

if __name__ == "__main__":
    main()
