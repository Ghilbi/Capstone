# gui.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database

class AppGUI:
    """GUI for managing subjects."""
    def __init__(self, parent):
        self.parent = parent

        # Build the GUI components
        self.build_gui()

    def build_gui(self):
        """Construct the GUI components for the subjects page."""
        # Filters Frame
        filter_frame = tk.Frame(self.parent)
        filter_frame.pack(pady=5)

        # Course Filter
        tk.Label(filter_frame, text="Course:").grid(row=0, column=0, padx=5)
        self.course_filter_var = tk.StringVar()
        self.course_filter = ttk.Combobox(filter_frame, textvariable=self.course_filter_var)
        self.course_filter['values'] = ["All Courses", "BSIT", "BSCS", "BSDA", "BSMMA"]
        self.course_filter.current(0)
        self.course_filter.grid(row=0, column=1, padx=5)

        # Track Filter
        tk.Label(filter_frame, text="Track:").grid(row=0, column=2, padx=5)
        self.track_filter_var = tk.StringVar()
        self.track_filter = ttk.Combobox(filter_frame, textvariable=self.track_filter_var)
        tracks = ["All Tracks"] + [track[1] for track in database.fetch_tracks()]
        self.track_filter['values'] = tracks
        self.track_filter.current(0)
        self.track_filter.grid(row=0, column=3, padx=5)

        # Year Level Filter
        tk.Label(filter_frame, text="Year Level:").grid(row=0, column=4, padx=5)
        self.year_level_filter_var = tk.StringVar()
        self.year_level_filter = ttk.Combobox(filter_frame, textvariable=self.year_level_filter_var)
        self.year_level_filter['values'] = ["All Year Levels", "1st Year", "2nd Year", "3rd Year", "4th Year"]
        self.year_level_filter.current(0)
        self.year_level_filter.grid(row=0, column=5, padx=5)

        # Trimester Filter
        tk.Label(filter_frame, text="Trimester:").grid(row=0, column=6, padx=5)
        self.trimester_filter_var = tk.StringVar()
        self.trimester_filter = ttk.Combobox(filter_frame, textvariable=self.trimester_filter_var)
        self.trimester_filter['values'] = ["All Trimesters", "1st Trimester", "2nd Trimester", "3rd Trimester"]
        self.trimester_filter.current(0)
        self.trimester_filter.grid(row=0, column=7, padx=5)

        # Filter Button
        filter_button = tk.Button(filter_frame, text="Filter", command=self.refresh_subjects_list)
        filter_button.grid(row=0, column=8, padx=5)

        # Subjects Listbox
        self.subjects_listbox = tk.Listbox(self.parent, width=120)
        self.subjects_listbox.pack(pady=5)
        self.subjects_listbox.bind('<<ListboxSelect>>', self.on_subject_select)

        # Form Frame
        form_frame = tk.Frame(self.parent)
        form_frame.pack(pady=5)

        # Subject Code
        tk.Label(form_frame, text="Subject Code:").grid(row=0, column=0, padx=5)
        self.subject_code_entry = tk.Entry(form_frame)
        self.subject_code_entry.grid(row=0, column=1, padx=5)

        # Subject Description
        tk.Label(form_frame, text="Subject Description:").grid(row=0, column=2, padx=5)
        self.subject_description_entry = tk.Entry(form_frame)
        self.subject_description_entry.grid(row=0, column=3, padx=5)

        # Course
        tk.Label(form_frame, text="Course:").grid(row=1, column=0, padx=5)
        self.course_var = tk.StringVar()
        self.course_combobox = ttk.Combobox(form_frame, textvariable=self.course_var)
        self.course_combobox['values'] = ["BSIT", "BSCS", "BSDA", "BSMMA"]
        self.course_combobox.grid(row=1, column=1, padx=5)

        # Track
        tk.Label(form_frame, text="Track:").grid(row=1, column=2, padx=5)
        self.track_var = tk.StringVar()
        self.track_combobox = ttk.Combobox(form_frame, textvariable=self.track_var)
        self.track_combobox['values'] = [track[1] for track in database.fetch_tracks()]
        self.track_combobox.grid(row=1, column=3, padx=5)

        # Year Level
        tk.Label(form_frame, text="Year Level:").grid(row=2, column=0, padx=5)
        self.year_level_var = tk.StringVar()
        self.year_level_combobox = ttk.Combobox(form_frame, textvariable=self.year_level_var)
        self.year_level_combobox['values'] = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
        self.year_level_combobox.grid(row=2, column=1, padx=5)

        # Trimester
        tk.Label(form_frame, text="Trimester:").grid(row=2, column=2, padx=5)
        self.trimester_var = tk.StringVar()
        self.trimester_combobox = ttk.Combobox(form_frame, textvariable=self.trimester_var)
        self.trimester_combobox['values'] = ["1st Trimester", "2nd Trimester", "3rd Trimester"]
        self.trimester_combobox.grid(row=2, column=3, padx=5)

        # Type
        tk.Label(form_frame, text="Type:").grid(row=3, column=0, padx=5)
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(form_frame, textvariable=self.type_var)
        self.type_combobox['values'] = ["Lecture", "Lab"]
        self.type_combobox.grid(row=3, column=1, padx=5)

        # Buttons Frame
        buttons_frame = tk.Frame(self.parent)
        buttons_frame.pack(pady=5)

        add_button = tk.Button(buttons_frame, text="Add Subject", command=self.add_subject)
        add_button.pack(side='left', padx=5)

        update_button = tk.Button(buttons_frame, text="Update Subject", command=self.update_subject)
        update_button.pack(side='left', padx=5)

        delete_button = tk.Button(buttons_frame, text="Delete Subject", command=self.delete_subject)
        delete_button.pack(side='left', padx=5)

        self.selected_subject_id = None  # To keep track of the selected subject for updating

        self.refresh_subjects_list()

    def refresh_subjects_list(self):
        """Refresh the list of subjects displayed."""
        self.subjects_listbox.delete(0, 'end')
        selected_course = self.course_filter_var.get()
        selected_track = self.track_filter_var.get()
        selected_year_level = self.year_level_filter_var.get()
        selected_trimester = self.trimester_filter_var.get()

        subjects = database.fetch_subjects(selected_track, selected_year_level, selected_trimester, selected_course)

        for subject in subjects:
            subject_id, subject_code, subject_description, track_name, year_level, trimester, subj_type, course = subject
            display_text = f"{subject_code} - {subject_description} | {course} | {track_name} | {year_level} | {trimester} | {subj_type}"
            self.subjects_listbox.insert('end', display_text)

    def add_subject(self):
        """Add a new subject to the database."""
        subject_code = self.subject_code_entry.get()
        subject_description = self.subject_description_entry.get()
        course = self.course_var.get()
        track_name = self.track_var.get()
        year_level = self.year_level_var.get()
        trimester = self.trimester_var.get()
        selected_type = self.type_var.get()

        # Get track_id
        track_id = None
        tracks = database.fetch_tracks()
        for track in tracks:
            if track[1] == track_name:
                track_id = track[0]
                break

        if track_id is None:
            messagebox.showerror("Error", "Invalid track selected.")
            return

        database.insert_subject(subject_code, subject_description, track_id, year_level, trimester, selected_type, course)
        self.clear_form()
        self.refresh_subjects_list()

    def update_subject(self):
        """Update an existing subject."""
        if self.selected_subject_id is None:
            messagebox.showwarning("No Selection", "Please select a subject to update.")
            return

        subject_code = self.subject_code_entry.get()
        subject_description = self.subject_description_entry.get()
        course = self.course_var.get()
        track_name = self.track_var.get()
        year_level = self.year_level_var.get()
        trimester = self.trimester_var.get()
        selected_type = self.type_var.get()

        # Get track_id
        track_id = None
        tracks = database.fetch_tracks()
        for track in tracks:
            if track[1] == track_name:
                track_id = track[0]
                break

        if track_id is None:
            messagebox.showerror("Error", "Invalid track selected.")
            return

        database.update_subject_db(self.selected_subject_id, subject_code, subject_description, track_id, year_level, trimester, selected_type, course)
        self.clear_form()
        self.refresh_subjects_list()
        self.selected_subject_id = None

    def delete_subject(self):
        """Delete a subject."""
        if self.selected_subject_id is None:
            messagebox.showwarning("No Selection", "Please select a subject to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this subject?")
        if confirm:
            database.delete_subject_db(self.selected_subject_id)
            self.clear_form()
            self.refresh_subjects_list()
            self.selected_subject_id = None

    def on_subject_select(self, event):
        """Handle the selection of a subject in the listbox."""
        try:
            index = self.subjects_listbox.curselection()[0]
            selected_text = self.subjects_listbox.get(index)
            subject_code = selected_text.split(' - ')[0]

            # Fetch subject details
            subjects = database.fetch_all_subjects()
            for subject in subjects:
                if subject[1] == subject_code:
                    self.selected_subject_id = subject[0]
                    self.subject_code_entry.delete(0, tk.END)
                    self.subject_code_entry.insert(0, subject[1])
                    self.subject_description_entry.delete(0, tk.END)
                    self.subject_description_entry.insert(0, subject[2])
                    self.course_var.set(subject[7])
                    self.track_var.set(subject[3])
                    self.year_level_var.set(subject[4])
                    self.trimester_var.set(subject[5])
                    self.type_var.set(subject[6])
                    break
        except IndexError:
            pass

    def clear_form(self):
        """Clear the form fields."""
        self.subject_code_entry.delete(0, tk.END)
        self.subject_description_entry.delete(0, tk.END)
        self.course_var.set('')
        self.track_var.set('')
        self.year_level_var.set('')
        self.trimester_var.set('')
        self.type_var.set('')
