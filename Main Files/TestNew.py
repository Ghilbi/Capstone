import tkinter as tk
from tkinter import ttk
from tkinter import messagebox  # Import messagebox module
import sqlite3

# Create and connect to the database
conn = sqlite3.connect('subjects.db')
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS Tracks (
                    id INTEGER PRIMARY KEY,
                    track_name TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Subjects (
                    id INTEGER PRIMARY KEY,
                    subject_code TEXT,
                    subject_description TEXT,
                    track_id INTEGER,
                    year_level TEXT,
                    trimester TEXT,
                    type TEXT,
                    FOREIGN KEY (track_id) REFERENCES Tracks(id))''')

# Function to add a track to the database
def add_track(track_name):
    cursor.execute('INSERT INTO Tracks (track_name) VALUES (?)', (track_name,))
    conn.commit()

# Function to handle track, year level, trimester, type, and subject information
def submit_form():
    selected_track = track_combobox.get()
    year_level = year_level_combobox.get()
    trimester = trimester_combobox.get()
    lecture_selected = lecture_var.get()
    lab_selected = lab_var.get()
    subject_code = subject_code_entry.get()
    subject_description = subject_description_entry.get()

    # Determine the selected type
    selected_type = ""
    if lecture_selected:
        selected_type = "Lecture"
    elif lab_selected:
        selected_type = "Lab"

    if selected_track and subject_code and subject_description and year_level and trimester:
        if selected_track != "All Tracks":
            # Fetch the track id for the selected track
            cursor.execute('SELECT id FROM Tracks WHERE track_name = ?', (selected_track,))
            track_row = cursor.fetchone()

            if track_row is None:
                feedback_label.config(text="Error: Selected track does not exist.", fg="red")
                return  # Stop the function if the track doesn't exist

            track_id = track_row[0]
        else:
            # If "All Tracks" is selected, set track_id to None or 0 (depending on your requirements)
            track_id = None

        # Insert the new subject into the database
        cursor.execute('''INSERT INTO Subjects (subject_code, subject_description, track_id, year_level, trimester, type) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (subject_code, subject_description, track_id, year_level, trimester, selected_type))
        conn.commit()

        feedback_label.config(text=f"Subject '{subject_code}' added successfully!", fg="green")
        refresh_subject_list()
    else:
        feedback_label.config(text="Please fill in all fields.", fg="red")

# Function to update a selected subject in the database
def update_subject(subject_id):
    selected_track = track_combobox.get()
    year_level = year_level_combobox.get()
    trimester = trimester_combobox.get()
    lecture_selected = lecture_var.get()
    lab_selected = lab_var.get()
    subject_code = subject_code_entry.get()
    subject_description = subject_description_entry.get()

    # Determine the selected type
    selected_type = ""
    if lecture_selected:
        selected_type = "Lecture"
    elif lab_selected:
        selected_type = "Lab"

    if selected_track and subject_code and subject_description and year_level and trimester:
        if selected_track != "All Tracks":
            # Fetch the track id for the selected track
            cursor.execute('SELECT id FROM Tracks WHERE track_name = ?', (selected_track,))
            track_row = cursor.fetchone()

            if track_row is None:
                feedback_label.config(text="Error: Selected track does not exist.", fg="red")
                return  # Stop the function if the track doesn't exist

            track_id = track_row[0]
        else:
            # If "All Tracks" is selected, set track_id to None or 0 (depending on your requirements)
            track_id = None

        # Update the subject in the database
        cursor.execute('''UPDATE Subjects 
                          SET subject_code = ?, subject_description = ?, track_id = ?, year_level = ?, 
                              trimester = ?, type = ? 
                          WHERE id = ?''', 
                       (subject_code, subject_description, track_id, year_level, trimester, selected_type, subject_id))
        conn.commit()

        feedback_label.config(text=f"Subject '{subject_code}' updated successfully!", fg="green")
        refresh_subject_list()
    else:
        feedback_label.config(text="Please fill in all fields.", fg="red")
        
# Function to refresh the list of subjects in the Listbox
def refresh_subject_list():
    # Clear the current list
    subject_listbox.delete(0, tk.END)

    # Get the selected values from comboboxes
    selected_track = track_combobox.get()
    selected_year_level = year_level_combobox.get()
    selected_trimester = trimester_combobox.get()

    # Create the SQL query with conditions based on the selections
    query = '''SELECT s.id, s.subject_code, s.subject_description, t.track_name, s.year_level, s.trimester, s.type 
               FROM Subjects s 
               LEFT JOIN Tracks t ON s.track_id = t.id 
               WHERE 1=1'''  # Always true to allow conditional additions

    params = []

    # Add conditions for Track, Year Level, and Trimester
    if selected_track and selected_track != "All Tracks":
        query += ' AND t.track_name = ?'
        params.append(selected_track)
    
    if selected_year_level and selected_year_level != "All Year Levels":
        query += ' AND s.year_level = ?'
        params.append(selected_year_level)
    
    if selected_trimester and selected_trimester != "All Trimesters":
        query += ' AND s.trimester = ?'
        params.append(selected_trimester)

    # Execute the query with the dynamic conditions
    cursor.execute(query, tuple(params))
    subjects = cursor.fetchall()

    # Populate the listbox with the filtered subjects
    for subject in subjects:
        track_name = subject[3] if subject[3] else "All Tracks"  # If track_name is None, display "All Tracks"
        subject_listbox.insert(tk.END, (subject[0], f"{subject[1]} - {subject[2]} | Track: {track_name} | Year: {subject[4]} | Trimester: {subject[5]} | Type: {subject[6]}"))

# Function to handle editing a selected subject
def edit_subject():
    selected_subject_index = subject_listbox.curselection()
    if selected_subject_index:
        # Extract the subject_id from the tuple (the first element in the list item)
        selected_subject = subject_listbox.get(selected_subject_index)
        subject_id = selected_subject[0]  # The first element is the subject_id

        # Fetch the subject details using the ID
        cursor.execute('SELECT * FROM Subjects WHERE id = ?', (subject_id,))
        subject = cursor.fetchone()

        if subject:  # Make sure the subject exists
            # Populate the entry fields with the current subject's details
            subject_code_entry.delete(0, tk.END)
            subject_code_entry.insert(0, subject[1])
            
            subject_description_entry.delete(0, tk.END)
            subject_description_entry.insert(0, subject[2])
            
            # Set the combobox values
            track_combobox.set(get_track_name_by_id(subject[3]))
            year_level_combobox.set(subject[4])
            trimester_combobox.set(subject[5])

            if subject[6] == "Lecture":
                lecture_var.set(True)
                lab_var.set(False)
            elif subject[6] == "Lab":
                lecture_var.set(False)
                lab_var.set(True)

            # Update button text and command for updating the subject
            submit_button.config(text="Update Subject", command=lambda: update_subject(subject_id))
        else:
            feedback_label.config(text="Error: Subject not found.", fg="red")

# Function to delete a selected subject
def delete_subject():
    selected_subject_index = subject_listbox.curselection()
    if selected_subject_index:
        # Extract the subject_id from the tuple (the first element in the list item)
        selected_subject = subject_listbox.get(selected_subject_index)
        subject_id = selected_subject[0]  # The first element is the subject_id

        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the subject '{subject_id}'?")
        if confirm:
            cursor.execute('DELETE FROM Subjects WHERE id = ?', (subject_id,))
            conn.commit()

            feedback_label.config(text=f"Subject '{subject_id}' deleted successfully!", fg="green")
            refresh_subject_list()
        else:
            feedback_label.config(text="Deletion canceled.", fg="orange")

# Function to get track name by ID (for edit functionality)
def get_track_name_by_id(track_id):
    cursor.execute('SELECT track_name FROM Tracks WHERE id = ?', (track_id,))
    track_row = cursor.fetchone()
    return track_row[0] if track_row else "All Tracks"

# Initialize the tkinter window
root = tk.Tk()
root.title("Track and Subject Selection System")

# Track selection dropdown
track_label = tk.Label(root, text="Select Track:")
track_label.grid(row=0, column=0, padx=10, pady=10)

# Fetch available tracks from the database
def fetch_tracks():
    cursor.execute('SELECT * FROM Tracks')
    return cursor.fetchall()

tracks = fetch_tracks()
track_names = [track[1] for track in tracks]
track_names.insert(0, "All Tracks")  # Add "All Tracks" as the first option

# Track combobox (dropdown menu)
track_combobox = ttk.Combobox(root, values=track_names)
track_combobox.set('')  # Default to an empty string, meaning no selection
track_combobox.grid(row=0, column=1, padx=10, pady=10)

# Year Level dropdown
year_level_label = tk.Label(root, text="Choose Year Level:")
year_level_label.grid(row=1, column=0, padx=10, pady=10)

year_levels = ['1st Year', '2nd Year', '3rd Year']
year_level_combobox = ttk.Combobox(root, values=year_levels)
year_level_combobox.grid(row=1, column=1, padx=10, pady=10)

# Trimester dropdown
trimester_label = tk.Label(root, text="Choose Trimester:")
trimester_label.grid(row=2, column=0, padx=10, pady=10)

# Trimester options based on year level (populated dynamically)
def update_trimester_options(event=None):
    year_level = year_level_combobox.get()
    if year_level == '1st Year':
        trimesters = ['1st Sem', '2nd Sem', '3rd Sem']
    elif year_level == '2nd Year':
        trimesters = ['1st Sem', '2nd Sem', '3rd Sem']
    elif year_level == '3rd Year':
        trimesters = ['1st Sem', '2nd Sem', '3rd Sem']
    else:
        trimesters = []

    trimester_combobox['values'] = trimesters
    trimester_combobox.set('')  # Reset trimester combobox when year level changes

year_level_combobox.bind('<<ComboboxSelected>>', update_trimester_options)

trimester_combobox = ttk.Combobox(root)
trimester_combobox.grid(row=2, column=1, padx=10, pady=10)

# Type selection checkboxes (Only one can be checked)
def set_lecture():
    lab_var.set(False)  # Deselect the Lab checkbox
    lecture_var.set(True)  # Select the Lecture checkbox

def set_lab():
    lecture_var.set(False)  # Deselect the Lecture checkbox
    lab_var.set(True)  # Select the Lab checkbox

lecture_var = tk.BooleanVar(value=False)
lab_var = tk.BooleanVar(value=False)

lecture_checkbox = tk.Checkbutton(root, text="Lecture", variable=lecture_var, command=set_lecture)
lecture_checkbox.grid(row=3, column=0, padx=10, pady=10)

lab_checkbox = tk.Checkbutton(root, text="Lab", variable=lab_var, command=set_lab)
lab_checkbox.grid(row=3, column=1, padx=10, pady=10)

# Subject Code entry
subject_code_label = tk.Label(root, text="Subject Code:")
subject_code_label.grid(row=4, column=0, padx=10, pady=10)
subject_code_entry = tk.Entry(root)
subject_code_entry.grid(row=4, column=1, padx=10, pady=10)

# Subject Description entry
subject_description_label = tk.Label(root, text="Subject Description:")
subject_description_label.grid(row=5, column=0, padx=10, pady=10)
subject_description_entry = tk.Entry(root)
subject_description_entry.grid(row=5, column=1, padx=10, pady=10)

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_form)
submit_button.grid(row=6, column=0, columnspan=2, pady=10)

# Feedback label
feedback_label = tk.Label(root, text="")
feedback_label.grid(row=7, column=0, columnspan=2)

# Show subjects list in a Listbox
subject_list_label = tk.Label(root, text="Subject List:")
subject_list_label.grid(row=8, column=0, padx=10, pady=10)

subject_listbox = tk.Listbox(root, height=10, width=50)
subject_listbox.grid(row=8, column=1, padx=10, pady=10)

# Buttons to edit and delete subjects
edit_button = tk.Button(root, text="Edit Subject", command=edit_subject)
edit_button.grid(row=9, column=0, padx=10, pady=10)

delete_button = tk.Button(root, text="Delete Subject", command=delete_subject)
delete_button.grid(row=9, column=1, padx=10, pady=10)

# Refresh button
refresh_button = tk.Button(root, text="Refresh List", command=refresh_subject_list)
refresh_button.grid(row=10, column=0, columnspan=2, pady=10)

# Example to add tracks manually (can be customized based on the application)
if not tracks:  # Add default tracks if the table is empty
    add_track("Network & Security")
    add_track("Web Technology")
    add_track("Enterprise Resource Planning")
    add_track("Minor")

# Fetch the tracks again after adding default tracks, if needed
tracks = fetch_tracks()
track_names = [track[1] for track in tracks]
track_names.insert(0, "All Tracks")  # Ensure "All Tracks" is at the top

# Update the track combobox with the newly fetched tracks
track_combobox['values'] = track_names

# Refresh the subject list at the start
refresh_subject_list()

# Start the GUI loop
root.mainloop()

# Close the database connection when done
conn.close()
