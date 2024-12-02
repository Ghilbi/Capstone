# gui.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import handlers

class AppGUI:
    """The main GUI application class for Subjects."""
    def __init__(self, parent):
        self.parent = parent
        self.lecture_var = tk.BooleanVar(value=False)
        self.lab_var = tk.BooleanVar(value=False)

        self.build_gui()

    def build_gui(self):
        """Construct the GUI components."""
        track_label = tk.Label(self.parent, text="Select Track:")
        track_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.track_combobox = ttk.Combobox(self.parent, values=handlers.get_track_names())
        self.track_combobox.set('')
        self.track_combobox.grid(row=0, column=1, padx=10, pady=10)
        
        year_level_label = tk.Label(self.parent, text="Choose Year Level:")
        year_level_label.grid(row=1, column=0, padx=10, pady=10)
        
        year_levels = ['1st Year', '2nd Year', '3rd Year']
        self.year_level_combobox = ttk.Combobox(self.parent, values=year_levels)
        self.year_level_combobox.grid(row=1, column=1, padx=10, pady=10)
        
        trimester_label = tk.Label(self.parent, text="Choose Trimester:")
        trimester_label.grid(row=2, column=0, padx=10, pady=10)
        
        self.trimester_combobox = ttk.Combobox(self.parent)
        self.trimester_combobox.grid(row=2, column=1, padx=10, pady=10)
        
        lecture_checkbox = tk.Checkbutton(self.parent, text="Lecture", variable=self.lecture_var, command=self.set_lecture)
        lecture_checkbox.grid(row=3, column=0, padx=10, pady=10)
        
        lab_checkbox = tk.Checkbutton(self.parent, text="Lab", variable=self.lab_var, command=self.set_lab)
        lab_checkbox.grid(row=3, column=1, padx=10, pady=10)
        
        subject_code_label = tk.Label(self.parent, text="Subject Code:")
        subject_code_label.grid(row=4, column=0, padx=10, pady=10)
        self.subject_code_entry = tk.Entry(self.parent)
        self.subject_code_entry.grid(row=4, column=1, padx=10, pady=10)
        
        subject_description_label = tk.Label(self.parent, text="Subject Description:")
        subject_description_label.grid(row=5, column=0, padx=10, pady=10)
        self.subject_description_entry = tk.Entry(self.parent)
        self.subject_description_entry.grid(row=5, column=1, padx=10, pady=10)
        
        self.submit_button = tk.Button(self.parent, text="Submit", command=self.submit_form)
        self.submit_button.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.feedback_label = tk.Label(self.parent, text="")
        self.feedback_label.grid(row=7, column=0, columnspan=2)
        
        subject_list_label = tk.Label(self.parent, text="Subject List:")
        subject_list_label.grid(row=8, column=0, padx=10, pady=10)
        
        self.subject_listbox = tk.Listbox(self.parent, height=10, width=50)
        self.subject_listbox.grid(row=8, column=1, padx=10, pady=10)
        
        edit_button = tk.Button(self.parent, text="Edit Subject", command=self.edit_subject)
        edit_button.grid(row=9, column=0, padx=10, pady=10)
        
        delete_button = tk.Button(self.parent, text="Delete Subject", command=self.delete_subject)
        delete_button.grid(row=9, column=1, padx=10, pady=10)
        
        refresh_button = tk.Button(self.parent, text="Refresh List", command=self.refresh_subject_list)
        refresh_button.grid(row=10, column=0, columnspan=2, pady=10)

        self.year_level_combobox.bind('<<ComboboxSelected>>', self.update_trimester_options)
        self.refresh_subject_list()

    def set_lecture(self):
        self.lab_var.set(False)
        self.lecture_var.set(True)

    def set_lab(self):
        self.lecture_var.set(False)
        self.lab_var.set(True)

    def update_trimester_options(self, event=None):
        year_level = self.year_level_combobox.get()
        trimesters = ['1st Sem', '2nd Sem', '3rd Sem'] if year_level in ['1st Year', '2nd Year', '3rd Year'] else []
        self.trimester_combobox['values'] = trimesters
        self.trimester_combobox.set('')

    def submit_form(self):
        handlers.submit_form(self)

    def refresh_subject_list(self):
        handlers.refresh_subject_list(self)

    def edit_subject(self):
        handlers.edit_subject(self)

    def delete_subject(self):
        handlers.delete_subject(self)
