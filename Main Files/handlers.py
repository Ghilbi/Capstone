# handlers.py
from tkinter import messagebox
import database

def get_track_names():
    """Retrieve track names for the combobox."""
    tracks = database.fetch_tracks()
    track_names = [track[1] for track in tracks]
    track_names.insert(0, "All Tracks")
    return track_names

def submit_form(gui):
    """Handle the form submission to add or update a subject."""
    selected_track = gui.track_combobox.get()
    year_level = gui.year_level_combobox.get()
    trimester = gui.trimester_combobox.get()
    lecture_selected = gui.lecture_var.get()
    lab_selected = gui.lab_var.get()
    subject_code = gui.subject_code_entry.get()
    subject_description = gui.subject_description_entry.get()

    selected_type = ""
    if lecture_selected:
        selected_type = "Lecture"
    elif lab_selected:
        selected_type = "Lab"

    if selected_track and subject_code and subject_description and year_level and trimester:
        if selected_track != "All Tracks":
            cursor = database.cursor
            cursor.execute('SELECT id FROM Tracks WHERE track_name = ?', (selected_track,))
            track_row = cursor.fetchone()

            if track_row is None:
                gui.feedback_label.config(text="Error: Selected track does not exist.", fg="red")
                return

            track_id = track_row[0]
        else:
            track_id = None

        database.insert_subject(subject_code, subject_description, track_id, year_level, trimester, selected_type)
        gui.feedback_label.config(text=f"Subject '{subject_code}' added successfully!", fg="green")
        gui.refresh_subject_list()
    else:
        gui.feedback_label.config(text="Please fill in all fields.", fg="red")

def refresh_subject_list(gui):
    """Refresh the list of subjects displayed."""
    gui.subject_listbox.delete(0, 'end')
    selected_track = gui.track_combobox.get()
    selected_year_level = gui.year_level_combobox.get()
    selected_trimester = gui.trimester_combobox.get()

    subjects = database.fetch_subjects(selected_track, selected_year_level, selected_trimester)

    for subject in subjects:
        track_name = subject[3] if subject[3] else "All Tracks"
        gui.subject_listbox.insert('end', (subject[0], f"{subject[1]} - {subject[2]} | Track: {track_name} | Year: {subject[4]} | Trimester: {subject[5]} | Type: {subject[6]}"))

def edit_subject(gui):
    """Populate the form fields with the selected subject's data for editing."""
    selected_subject_index = gui.subject_listbox.curselection()
    if selected_subject_index:
        selected_subject = gui.subject_listbox.get(selected_subject_index)
        subject_id = selected_subject[0]

        cursor = database.cursor
        cursor.execute('SELECT * FROM Subjects WHERE id = ?', (subject_id,))
        subject = cursor.fetchone()

        if subject:
            gui.subject_code_entry.delete(0, 'end')
            gui.subject_code_entry.insert(0, subject[1])
            gui.subject_description_entry.delete(0, 'end')
            gui.subject_description_entry.insert(0, subject[2])
            gui.track_combobox.set(database.get_track_name_by_id(subject[3]))
            gui.year_level_combobox.set(subject[4])
            gui.trimester_combobox.set(subject[5])

            if subject[6] == "Lecture":
                gui.lecture_var.set(True)
                gui.lab_var.set(False)
            elif subject[6] == "Lab":
                gui.lecture_var.set(False)
                gui.lab_var.set(True)

            gui.submit_button.config(text="Update Subject", command=lambda: update_subject(gui, subject_id))
        else:
            gui.feedback_label.config(text="Error: Subject not found.", fg="red")

def update_subject(gui, subject_id):
    """Update the selected subject with new data."""
    selected_track = gui.track_combobox.get()
    year_level = gui.year_level_combobox.get()
    trimester = gui.trimester_combobox.get()
    lecture_selected = gui.lecture_var.get()
    lab_selected = gui.lab_var.get()
    subject_code = gui.subject_code_entry.get()
    subject_description = gui.subject_description_entry.get()

    selected_type = ""
    if lecture_selected:
        selected_type = "Lecture"
    elif lab_selected:
        selected_type = "Lab"

    if selected_track and subject_code and subject_description and year_level and trimester:
        if selected_track != "All Tracks":
            cursor = database.cursor
            cursor.execute('SELECT id FROM Tracks WHERE track_name = ?', (selected_track,))
            track_row = cursor.fetchone()

            if track_row is None:
                gui.feedback_label.config(text="Error: Selected track does not exist.", fg="red")
                return

            track_id = track_row[0]
        else:
            track_id = None

        database.update_subject_db(subject_id, subject_code, subject_description, track_id, year_level, trimester, selected_type)
        gui.feedback_label.config(text=f"Subject '{subject_code}' updated successfully!", fg="green")
        gui.refresh_subject_list()
        gui.submit_button.config(text="Submit", command=gui.submit_form)
    else:
        gui.feedback_label.config(text="Please fill in all fields.", fg="red")

def delete_subject(gui):
    """Delete the selected subject from the database."""
    selected_subject_index = gui.subject_listbox.curselection()
    if selected_subject_index:
        selected_subject = gui.subject_listbox.get(selected_subject_index)
        subject_id = selected_subject[0]

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the subject '{subject_id}'?")
        if confirm:
            database.delete_subject_db(subject_id)
            gui.feedback_label.config(text=f"Subject '{subject_id}' deleted successfully!", fg="green")
            gui.refresh_subject_list()
        else:
            gui.feedback_label.config(text="Deletion canceled.", fg="orange")
