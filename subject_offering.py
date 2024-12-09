# subject_offering.py

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from typing import List, Dict
import logging
import string

class SubjectOfferingApp(ttk.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.notebook = notebook
        self.pack(fill="both", expand=True)  # Ensure the frame is visible
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Initialize the user interface components"""
        # Main controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill="x", padx=5, pady=5)
        
        # Group selection
        ttk.Label(controls_frame, text="Group:").pack(side="left", padx=5)
        self.group_var = tk.StringVar(value="A")
        ttk.Radiobutton(controls_frame, text="Group A", variable=self.group_var, 
                       value="A").pack(side="left", padx=5)
        ttk.Radiobutton(controls_frame, text="Group B", variable=self.group_var, 
                       value="B").pack(side="left", padx=5)
        
        # Program selection
        ttk.Label(controls_frame, text="Program:").pack(side="left", padx=5)
        self.program_var = tk.StringVar()
        self.program_combo = ttk.Combobox(controls_frame, textvariable=self.program_var, state="readonly")
        self.program_combo.pack(side="left", padx=5)
        
        # Year Level selection
        ttk.Label(controls_frame, text="Year Level:").pack(side="left", padx=5)
        self.year_var = tk.StringVar()
        self.year_combo = ttk.Combobox(controls_frame, textvariable=self.year_var, state="readonly")
        self.year_combo.pack(side="left", padx=5)
        
        # Term selection
        ttk.Label(controls_frame, text="Term:").pack(side="left", padx=5)
        self.term_var = tk.StringVar()
        self.term_combo = ttk.Combobox(controls_frame, textvariable=self.term_var, state="readonly")
        self.term_combo.pack(side="left", padx=5)
        
        # Number of sections input
        ttk.Label(controls_frame, text="Number of Sections:").pack(side="left", padx=5)
        self.sections_var = tk.StringVar(value="1")
        self.sections_entry = ttk.Entry(controls_frame, textvariable=self.sections_var, width=5)
        self.sections_entry.pack(side="left", padx=5)
        
        # Section selection
        ttk.Label(controls_frame, text="Section:").pack(side="left", padx=5)
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(controls_frame, textvariable=self.section_var, state="readonly")
        self.section_combo.pack(side="left", padx=5)
        
        # Generate button
        self.generate_btn = ttk.Button(controls_frame, text="Generate Schedule",
                                     command=self.generate_schedule)
        self.generate_btn.pack(side="left", padx=10)
        
        # Export button
        self.export_btn = ttk.Button(controls_frame, text="Export to Excel",
                                   command=self.export_to_excel)
        self.export_btn.pack(side="left", padx=5)
        
        # Results treeview
        self.tree = ttk.Treeview(self, columns=("Course Code", "Description", "Time", 
                                               "Days", "Room"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Bind events
        self.sections_var.trace('w', self.update_sections)
        self.year_var.trace('w', self.update_sections)

    def update_sections(self, *args):
        """Update the section dropdown based on number of sections and year level"""
        try:
            num_sections = int(self.sections_var.get())
            year_prefix = self.year_var.get()[0] if self.year_var.get() else ""
            
            if year_prefix and num_sections > 0:
                sections = [f"{year_prefix}{letter}" for letter in string.ascii_uppercase[:num_sections]]
                self.section_combo['values'] = sections
                if sections:
                    self.section_combo.set(sections[0])
                else:
                    self.section_combo.set('')
            else:
                self.section_combo['values'] = []
                self.section_combo.set('')
        except ValueError:
            self.section_combo['values'] = []
            self.section_combo.set('')

    def load_data(self):
        """Load initial data for dropdowns"""
        try:
            with sqlite3.connect("subjects.db") as conn:
                cursor = conn.cursor()
                
                # Load programs (including specializations)
                cursor.execute("""
                    SELECT DISTINCT Program 
                    FROM SubjectsDatabase 
                    WHERE Program != 'INTERNATIONAL'
                    AND Program != ''
                """)
                programs = [row[0].strip() for row in cursor.fetchall()]
                programs = sorted(list(set(programs)))  # Remove duplicates and sort
                
                # Handle specializations
                base_programs = set()
                specializations = set()
                for program in programs:
                    if '(' in program and ')' in program:
                        base_program = program.split('(')[0].strip()
                        specialization = program.strip()
                        base_programs.add(base_program)
                        specializations.add(specialization)
                    else:
                        base_programs.add(program)
                
                all_programs = sorted(list(base_programs)) + sorted(list(specializations))
                self.program_combo['values'] = all_programs
                
                # Set year levels
                self.year_combo['values'] = ["First Year", "Second Year", "Third Year"]
                self.year_combo.current(0)  # Set default to First Year
                
                # Set terms
                self.term_combo['values'] = ["First Term", "Second Term", "Third Term"]
                self.term_combo.current(0)  # Set default to First Term
                
                # Set sections
                self.update_sections()
                
        except Exception as e:
            logging.error(f"Error loading data: {str(e)}")
            messagebox.showerror("Error", "Failed to load initial data")

    def get_subject_schedule(self, program: str, year_level: str, term: str) -> List[Dict]:
        """Get subjects for given program, year and term"""
        try:
            # Mapping Year Level from string to integer
            year_level_map = {
                "First Year": 1,
                "Second Year": 2,
                "Third Year": 3
            }
            db_year_level = year_level_map.get(year_level, None)
            if db_year_level is None:
                logging.error(f"Invalid Year Level selected: {year_level}")
                messagebox.showerror("Error", f"Invalid Year Level selected: {year_level}")
                return []
            
            with sqlite3.connect("subjects.db") as conn:
                cursor = conn.cursor()
                
                # Handle base programs and specializations
                program_conditions = [program]
                if '(' in program and ')' in program:  # If it's a specialization, also get base program subjects
                    base_program = program.split('(')[0].strip()
                    program_conditions.append(base_program)
                
                # Build query with program conditions
                placeholders = ','.join(['?'] * len(program_conditions))
                query = f"""
                    SELECT CourseCode, Description, Type 
                    FROM SubjectsDatabase 
                    WHERE Program IN ({placeholders})
                    AND YearLevel = ? 
                    AND Semester = ?
                    GROUP BY CourseCode, Description, Type
                """
                
                cursor.execute(query, program_conditions + [db_year_level, term])
                fetched_subjects = cursor.fetchall()
                subjects = []
                for row in fetched_subjects:
                    course_code = row[0].strip()
                    description = row[1].strip()
                    type_ = row[2].strip()
                    subjects.append({
                        'CourseCode': course_code,
                        'Description': description,
                        'Type': type_
                    })
                
                # Log fetched subjects for debugging
                logging.debug(f"Fetched subjects: {subjects}")
                
                if not subjects:
                    logging.warning(f"No subjects found for Program: {program}, Year Level: {year_level}, Term: {term}")
                    messagebox.showinfo("No Subjects Found", f"No subjects found for Program: {program}, Year Level: {year_level}, Term: {term}")
                
                return subjects
        except sqlite3.Error as e:
            logging.error(f"Database error: {str(e)}")
            messagebox.showerror("Database Error", f"An error occurred while fetching subjects: {e}")
            return []
        except Exception as e:
            logging.error(f"Error getting subjects: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            return []

    def assign_schedule(self, subjects: List[Dict], section: str) -> List[Dict]:
        """Assign timeslots, days, and rooms to subjects"""
        scheduled_subjects = []
        available_timeslots = [
            "7:30-8:50", "8:50-10:10", "10:10-11:30", 
            "11:30-12:50", "12:50-2:10", "2:10-3:30",
            "3:30-4:50", "4:50-6:10"
        ]
        current_timeslot_index = 0
        used_slots = {}  # Format: {(day, time): room}
        
        # Group subjects by type
        lectures = [s for s in subjects if s['Type'] == 'Lec' or s['Type'] == 'Pure Lec']
        labs = [s for s in subjects if s['Type'] == 'Lab']
        
        # Schedule lectures first, then labs
        all_subjects = lectures + labs
        
        for subject in all_subjects:
            if current_timeslot_index >= len(available_timeslots):
                messagebox.showwarning("Scheduling Warning", "Not enough timeslots to schedule all subjects.")
                break
                
            subject_type = subject['Type']
            
            # Determine days pattern
            if subject_type == 'Pure Lec':
                days = 'MWF' if len(scheduled_subjects) % 2 == 0 else 'TTH'
            elif subject_type == 'Lec':
                days = 'MW' if len(scheduled_subjects) % 2 == 0 else 'TTH'
            else:  # Lab
                days = 'MWF' if len(scheduled_subjects) % 2 == 0 else 'TTHS'
            
            # Assign room
            if subject['CourseCode'] == 'NSTP1':
                room = 'Aud'
            elif subject['CourseCode'] in ['PathFit1', 'PathFit4']:
                room = 'Gym'
            elif subject_type == 'Lab':
                # Cycle through lab rooms (Assuming M302, M303, M304 exist)
                room = f"M30{2 + (len(scheduled_subjects) % 3)}"
            elif subject_type == 'Pure Lec':
                # Use U705 or U706
                room = f"U70{5 + (len(scheduled_subjects) % 2)}"
            else:
                # Cycle through lecture rooms (Assuming M301-M306 exist)
                room = f"M30{1 + (len(scheduled_subjects) % 6)}"
            
            # Check for conflicts
            conflict = False
            for day in days:
                slot_key = (day, available_timeslots[current_timeslot_index])
                if slot_key in used_slots:
                    conflict = True
                    break
            
            if conflict:
                current_timeslot_index += 1
                if current_timeslot_index >= len(available_timeslots):
                    messagebox.showwarning("Scheduling Warning", "Not enough timeslots to schedule all subjects.")
                    break
                continue
            
            # Mark slots as used
            for day in days:
                used_slots[(day, available_timeslots[current_timeslot_index])] = room
            
            scheduled_subjects.append({
                'CourseCode': subject['CourseCode'],
                'Description': subject['Description'],
                'Time': available_timeslots[current_timeslot_index],
                'Days': days,
                'Room': room,
                'Section': section
            })
            
            current_timeslot_index += 1
        
        # Log scheduled subjects for debugging
        logging.debug(f"Scheduled subjects: {scheduled_subjects}")
        
        return scheduled_subjects

    def generate_schedule(self):
        """Generate schedule based on selected parameters"""
        try:
            program = self.program_var.get()
            year_level = self.year_var.get()
            term = self.term_var.get()
            section = self.section_var.get()
            
            logging.info(f"Generating schedule for Program: {program}, Year Level: {year_level}, Term: {term}, Section: {section}")
            
            if not all([program, year_level, term, section]):
                messagebox.showwarning("Input Warning", "Please select all required fields.")
                return
                
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Get subjects and generate schedule
            subjects = self.get_subject_schedule(program, year_level, term)
            
            if not subjects:
                # No subjects found; already handled in get_subject_schedule
                return
                
            scheduled_subjects = self.assign_schedule(subjects, section)
            
            if not scheduled_subjects:
                messagebox.showinfo("Scheduling Info", "No subjects were scheduled.")
                return
            
            # Display in treeview
            for subject in scheduled_subjects:
                self.tree.insert("", "end", values=(
                    subject['CourseCode'],
                    subject['Description'],
                    subject['Time'],
                    subject['Days'],
                    subject['Room']
                ))
                
            logging.info(f"Successfully generated schedule for Program: {program}, Year Level: {year_level}, Term: {term}, Section: {section}")
                
        except Exception as e:
            logging.error(f"Error generating schedule: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate schedule: {e}")

    def export_to_excel(self):
        """Export the current schedule to Excel"""
        if not self.tree.get_children():
            messagebox.showwarning("Export Warning", "No schedule to export.")
            return
            
        try:
            data = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                data.append({
                    'Course Code': values[0],
                    'Description': values[1],
                    'Time': values[2],
                    'Days': values[3],
                    'Room': values[4]
                })
                
            df = pd.DataFrame(data)
            section = self.section_var.get()
            program = self.program_var.get().replace(" ", "_")
            filename = f"schedule_{program}_{section}.xlsx"
            df.to_excel(filename, index=False)
            messagebox.showinfo("Export Success", f"Schedule exported to {filename}")
            logging.info(f"Schedule exported to {filename}")
            
        except Exception as e:
            logging.error(f"Error exporting to Excel: {str(e)}")
            messagebox.showerror("Export Error", f"Failed to export schedule: {e}")
