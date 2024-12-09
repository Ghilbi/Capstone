# subjects.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import logging

class SubjectApp:
    def __init__(self, parent):
        self.conn = sqlite3.connect("subjects.db")  # Open DB connection once
        self.cursor = self.conn.cursor()
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        # Frame for form
        form_frame = tk.LabelFrame(self.frame, text="Subject Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        # Subject Details Form
        self.course_code_entry = self.create_entry(form_frame, "Course Code:", 0)
        self.description_entry = self.create_entry(form_frame, "Description:", 1)
        self.program_entry = self.create_entry(form_frame, "Program:", 2)
        self.year_level_entry = self.create_entry(form_frame, "Year Level:", 3)

        # Semester & Type Comboboxes
        self.semester_combobox = self.create_combobox(form_frame, "Semester:", ["First Term", "Second Term", "Third Term"], 4)
        self.type_combobox = self.create_combobox(form_frame, "Type:", ["Lec", "Lab", "Pure Lec"], 5)

        # Buttons
        self.create_buttons(form_frame)

        # Search Frame
        search_frame = self.create_search_frame()
        search_frame.pack(fill="x", padx=10, pady=5)

        # Treeview for displaying subjects
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = self.create_treeview(tree_frame)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_entry(self, frame, label, row):
        tk.Label(frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        entry = tk.Entry(frame, width=50)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry

    def create_combobox(self, frame, label, values, row):
        tk.Label(frame, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="e")
        var = tk.StringVar()
        combobox = ttk.Combobox(frame, textvariable=var, values=values, state="readonly")
        combobox.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        return combobox

    def create_buttons(self, frame):
        button_frame = tk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Add Subject", command=self.add_subject)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(button_frame, text="Edit Subject", command=self.edit_subject)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Subject", command=self.delete_subject)
        self.delete_button.pack(side="left", padx=5)

        self.import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv)
        self.import_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

    def create_search_frame(self):
        search_frame = tk.LabelFrame(self.frame, text="Search Subjects", padx=10, pady=10)
        
        # Adjusted to have separate entries for Course Code and Program
        tk.Label(search_frame, text="Course Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_course_code = tk.Entry(search_frame)
        self.search_course_code.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(search_frame, text="Program:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.search_program = tk.Entry(search_frame)
        self.search_program.grid(row=0, column=3, padx=5, pady=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_subjects)
        self.search_button.grid(row=0, column=4, padx=5, pady=5)

        self.reset_button = tk.Button(search_frame, text="Reset", command=self.populate_treeview)
        self.reset_button.grid(row=0, column=5, padx=5, pady=5)
        
        return search_frame

    def create_treeview(self, frame):
        columns = ("id", "CourseCode", "Description", "Program", "YearLevel", "Semester", "Type")
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            # Adjusted widths for better visibility
            if col == "Description":
                tree.column(col, width=200)
            elif col == "Program":
                tree.column(col, width=150)
            elif col == "Type":
                tree.column(col, width=100)
            else:
                tree.column(col, width=100, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        
        return tree

    def add_subject(self):
        subject_details = self.get_form_data()
        if not subject_details:
            return
        
        course_code, description, program, year_level, semester, type_ = subject_details
        try:
            self.cursor.execute("""
                INSERT INTO SubjectsDatabase (CourseCode, Description, Program, YearLevel, Semester, Type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_code, description, program, year_level, semester, type_))
            self.conn.commit()
            messagebox.showinfo("Success", "Subject added successfully.")
            self.clear_form()
            self.populate_treeview()
        except sqlite3.IntegrityError as ie:
            logging.error(f"IntegrityError adding subject: {ie}")
            messagebox.showerror("Integrity Error", f"An integrity error occurred: {ie}")
        except Exception as e:
            logging.error(f"Unexpected error adding subject: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def edit_subject(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No subject selected to edit.")
            return

        item = self.tree.item(selected)
        subject_id = item['values'][0]

        subject_details = self.get_form_data()
        if not subject_details:
            return

        course_code, description, program, year_level, semester, type_ = subject_details
        try:
            self.cursor.execute("""
                UPDATE SubjectsDatabase
                SET CourseCode = ?, Description = ?, Program = ?, YearLevel = ?, Semester = ?, Type = ?
                WHERE id = ?
            """, (course_code, description, program, year_level, semester, type_, subject_id))
            self.conn.commit()
            messagebox.showinfo("Success", "Subject updated successfully.")
            self.clear_form()
            self.populate_treeview()
        except sqlite3.IntegrityError as ie:
            logging.error(f"IntegrityError editing subject: {ie}")
            messagebox.showerror("Integrity Error", f"An integrity error occurred: {ie}")
        except Exception as e:
            logging.error(f"Unexpected error updating subject: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def delete_subject(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No subject selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected subject?")
        if not confirm:
            return

        item = self.tree.item(selected)
        subject_id = item['values'][0]
        try:
            self.cursor.execute("DELETE FROM SubjectsDatabase WHERE id = ?", (subject_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Subject deleted successfully.")
            self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error deleting subject: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if not file_path:
            return

        if not os.path.isfile(file_path):
            messagebox.showerror("File Error", "Selected file does not exist.")
            return

        imported, errors = self.import_csv_data(file_path)
        messagebox.showinfo("Import Completed", f"Imported: {imported}\nDuplicates/Errors: {errors}")
        self.populate_treeview()

    def import_csv_data(self, file_path):
        imported = 0
        errors = 0
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_headers = {'Course_Code', 'Description', 'Program', 'Year_Level', 'Semester', 'Type'}
            if not required_headers.issubset(reader.fieldnames):
                messagebox.showerror("CSV Format Error", "CSV file is missing required columns.")
                return 0, 0
            
            for row in reader:
                course_code = row['Course_Code'].strip()
                description = row['Description'].strip()
                program = row['Program'].strip()
                year_level = row['Year_Level'].strip()
                semester = row['Semester'].strip()
                type_ = row['Type'].strip()

                # Map 'Course_Code' to 'CourseCode' for database consistency
                if not course_code:
                    logging.error(f"Missing CourseCode in row: {row}")
                    errors += 1
                    continue

                try:
                    self.cursor.execute("""
                        INSERT INTO SubjectsDatabase (CourseCode, Description, Program, YearLevel, Semester, Type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (course_code, description, program, year_level, semester, type_))
                    self.conn.commit()
                    imported += 1
                except sqlite3.IntegrityError as ie:
                    logging.error(f"IntegrityError importing subject row {row}: {ie}")
                    errors += 1
                except Exception as e:
                    logging.error(f"Error importing subject row {row}: {e}")
                    errors += 1
        return imported, errors

    def populate_treeview(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.cursor.execute("SELECT * FROM SubjectsDatabase")
        for row in self.cursor.fetchall():
            self.tree.insert("", "end", values=row)

    def search_subjects(self):
        course_code = self.search_course_code.get().strip()
        program = self.search_program.get().strip()

        query = "SELECT * FROM SubjectsDatabase WHERE 1=1"
        params = []

        if course_code:
            query += " AND CourseCode LIKE ?"
            params.append(f"%{course_code}%")
        if program:
            query += " AND Program LIKE ?"
            params.append(f"%{program}%")

        self.cursor.execute(query, tuple(params))
        rows = self.cursor.fetchall()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in rows:
            self.tree.insert("", "end", values=row)

    def clear_form(self):
        self.course_code_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.program_entry.delete(0, tk.END)
        self.year_level_entry.delete(0, tk.END)
        self.semester_combobox.set('')
        self.type_combobox.set('')
        self.tree.selection_remove(self.tree.selection())
    
    def get_form_data(self):
        course_code = self.course_code_entry.get().strip()
        description = self.description_entry.get().strip()
        program = self.program_entry.get().strip()
        year_level = self.year_level_entry.get().strip()
        semester = self.semester_combobox.get().strip()
        type_ = self.type_combobox.get().strip()

        if not course_code or not description or not program or not year_level or not semester or not type_:
            messagebox.showerror("Input Error", "All fields are required.")
            return None

        return course_code, description, program, year_level, semester, type_

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item)
        values = item['values']
        self.course_code_entry.delete(0, tk.END)
        self.course_code_entry.insert(0, values[1])
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, values[2])
        self.program_entry.delete(0, tk.END)
        self.program_entry.insert(0, values[3])
        self.year_level_entry.delete(0, tk.END)
        self.year_level_entry.insert(0, values[4])
        self.semester_combobox.set(values[5])
        self.type_combobox.set(values[6])

    def __del__(self):
        self.conn.close()  # Close DB connection when app is closed
