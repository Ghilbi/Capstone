import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import random
from typing import List, Dict, Tuple, Set
import openpyxl
from datetime import datetime, timedelta
import copy

class Course:
    def __init__(self, code: str, description: str, time: str, days: str, room: str):
        self.code = code
        self.description = description
        self.time = time
        self.days = days
        self.room = room
        self.time_obj = datetime.strptime(time.split('-')[0], '%I:%M%p')
        self.end_time_obj = datetime.strptime(time.split('-')[1], '%I:%M%p')
        self.is_lab = '(Lab)' in description
        self.is_lec = '(Lec)' in description
        self.base_code = self.get_base_code()
        self.pair_key = self.get_pair_key()

    def get_base_code(self) -> str:
        return self.code.split('(')[0].strip()
    
    def get_pair_key(self) -> str:
        base_desc = self.description.split('(')[0].strip()
        return f"{self.base_code}_{base_desc}"

    def __lt__(self, other):
        return self.time_obj < other.time_obj

    def clone(self):
        return copy.deepcopy(self)

    def is_restricted_room_course(self) -> bool:
        restricted_codes = {'NSTP1', 'PathFit', 'PATHFit'}
        return any(code in self.code for code in restricted_codes)

class TimeSlot:
    def __init__(self, start_time: str):
        self.start_time = datetime.strptime(start_time, '%I:%M%p')
        self.end_time = self.start_time + timedelta(minutes=80)
        self.start_time_str = start_time
        self.end_time_str = self.end_time.strftime('%I:%M%p')
        self.mwf_used = False
        self.tth_used = False

    def is_available(self, is_mwf: bool) -> bool:
        return not (self.mwf_used if is_mwf else self.tth_used)

    def mark_used(self, is_mwf: bool):
        if is_mwf:
            self.mwf_used = True
        else:
            self.tth_used = True

    def __lt__(self, other):
        return self.start_time < other.start_time

def get_available_rooms(course: Course, all_rooms: Set[str]) -> List[str]:
    restricted_rooms = {'Gym', 'Aud'}
    if course.is_restricted_room_course():
        return list(restricted_rooms)
    return list(all_rooms - restricted_rooms)

def get_consecutive_time_slots(time_slots: List[TimeSlot], is_mwf: bool, num_slots: int) -> List[TimeSlot]:
    available_sequences = []
    for i in range(len(time_slots) - num_slots + 1):
        sequence = time_slots[i:i + num_slots]
        if all(slot.is_available(is_mwf) for slot in sequence):
            available_sequences.append(sequence)
    return available_sequences

def balance_and_shuffle_courses(courses: List[Course]) -> List[Course]:
    # Initialize time slots
    base_times = [
        '7:30am', '8:50am', '10:10am', '11:30am',
        '12:50pm', '2:10pm', '3:30pm', '4:50pm', '6:10pm'
    ]
    time_slots = [TimeSlot(time) for time in base_times]
    
    # Group courses
    paired_courses = {}
    standalone_courses = []
    
    for course in courses:
        if course.is_lab or course.is_lec:
            if course.pair_key not in paired_courses:
                paired_courses[course.pair_key] = []
            paired_courses[course.pair_key].append(course.clone())
        else:
            standalone_courses.append(course.clone())
    
    all_rooms = set(course.room for course in courses)
    mwf_patterns = ['MWF', 'MW']
    tth_patterns = ['TTH', 'TTHS']
    
    mwf_courses = []
    tth_courses = []
    
    # Process paired courses
    pair_keys = list(paired_courses.keys())
    random.shuffle(pair_keys)
    
    for pair_key in pair_keys:
        pair = paired_courses[pair_key]
        available_rooms = get_available_rooms(pair[0], all_rooms)
        if not available_rooms:
            continue
        
        # Choose pattern first
        is_mwf = len(mwf_courses) <= len(tth_courses)
        pattern = random.choice(mwf_patterns if is_mwf else tth_patterns)
        
        # Find consecutive available time slots
        available_sequences = get_consecutive_time_slots(time_slots, is_mwf, len(pair))
        if not available_sequences:
            continue
            
        # Choose a random sequence of slots
        selected_sequence = random.choice(available_sequences)
        
        # Mark slots as used
        for slot in selected_sequence:
            slot.mark_used(is_mwf)
        
        # Assign rooms and times
        room_assignments = random.sample(available_rooms, len(pair))
        for i, (course, slot) in enumerate(zip(pair, selected_sequence)):
            course.time = f"{slot.start_time_str}-{slot.end_time_str}"
            course.days = pattern
            course.room = room_assignments[i]
            course.time_obj = slot.start_time
            course.end_time_obj = slot.end_time
        
        if is_mwf:
            mwf_courses.extend(pair)
        else:
            tth_courses.extend(pair)
    
    # Process standalone courses
    random.shuffle(standalone_courses)
    for course in standalone_courses:
        available_rooms = get_available_rooms(course, all_rooms)
        if not available_rooms:
            continue
        
        is_mwf = len(mwf_courses) <= len(tth_courses)
        pattern = random.choice(mwf_patterns if is_mwf else tth_patterns)
        
        # Find available single time slot
        available_slots = [slot for slot in time_slots if slot.is_available(is_mwf)]
        if not available_slots:
            continue
            
        selected_slot = random.choice(available_slots)
        selected_slot.mark_used(is_mwf)
        
        course.time = f"{selected_slot.start_time_str}-{selected_slot.end_time_str}"
        course.days = pattern
        course.room = random.choice(available_rooms)
        course.time_obj = selected_slot.start_time
        course.end_time_obj = selected_slot.end_time
        
        if is_mwf:
            mwf_courses.append(course)
        else:
            tth_courses.append(course)
    
    # Sort both groups chronologically
    mwf_courses.sort()
    tth_courses.sort()
    
    return mwf_courses + tth_courses

class SectionCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Section Creator")
        self.df = None
        self.programs = ["BSIT", "BSIT(WebTech)", "BSIT(Netsec)", "BSIT(ERP)", "BSCS", "BSDA", "BMMA"]
        self.setup_ui()
        
    def setup_ui(self):
        # File import frame
        import_frame = ttk.LabelFrame(self.root, text="Import Data", padding="10")
        import_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Button(import_frame, text="Import CSV", command=self.import_csv).grid(row=0, column=0, padx=5)
        
        # Section configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding="10")
        config_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        # Program section counts
        self.section_counts = {}
        row = 0
        for program in self.programs:
            ttk.Label(config_frame, text=f"{program} Sections:").grid(row=row, column=0, padx=5)
            spinbox = ttk.Spinbox(config_frame, from_=1, to=10, width=5)
            spinbox.grid(row=row, column=1, padx=5)
            spinbox.set(1)
            self.section_counts[program] = spinbox
            row += 1
        
        # Trimester selection
        ttk.Label(config_frame, text="Trimester:").grid(row=row, column=0, padx=5)
        self.trimester_var = tk.StringVar(value="First")
        trimester_combo = ttk.Combobox(config_frame, textvariable=self.trimester_var, values=["First", "Second", "Third"])
        trimester_combo.grid(row=row, column=1, padx=5)
        
        # Generate button
        ttk.Button(self.root, text="Generate and Export", command=self.generate_sections).grid(row=2, column=0, pady=10)
        
    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            
    def create_section_courses(self, program: str, year: str, trimester: str) -> List[Course]:
        # Filter courses for the specific program, year, and trimester
        filtered_df = self.df[
            (self.df['Program'] == program) & 
            (self.df['Year_Level'] == year) & 
            (self.df['Trimester'] == trimester)
        ]
        
        courses = []
        for _, row in filtered_df.iterrows():
            course = Course(
                row['Course_Code'],
                row['Description'],
                row['Time'],
                row['Days'],
                row['Room']
            )
            courses.append(course)
        
        # Shuffle and balance courses
        return balance_and_shuffle_courses(courses)
    
    def generate_sections(self):
        if self.df is None:
            messagebox.showerror("Error", "Please import CSV file first")
            return
            
        # Create workbook for export
        wb = openpyxl.Workbook()
        
        # Generate sections for Group A and B
        for group_name in ['A', 'B']:
            ws = wb.create_sheet(f"Group {group_name}")
            row = 1
            
            for program in self.programs:
                num_sections = int(self.section_counts[program].get())
                for year in ['First', 'Second', 'Third']:
                    # Generate sections for each year
                    for section_num in range(num_sections):
                        section_name = f"{year[0]}{section_num + 1}{group_name}"
                        
                        # Write section header
                        ws.cell(row=row, column=1, value=f"{program}, {year} Year, {self.trimester_var.get()} Term Section {section_name}")
                        row += 1
                        
                        # Write column headers
                        headers = ["COURSE CODE", "DESCRIPTION", "TIME", "DAYS", "ROOM"]
                        for col, header in enumerate(headers, 1):
                            ws.cell(row=row, column=col, value=header)
                        row += 1
                        
                        # Get courses for this section
                        courses = self.create_section_courses(program, year, self.trimester_var.get())
                        
                        # Write courses
                        for course in courses:
                            ws.cell(row=row, column=1, value=course.code)
                            ws.cell(row=row, column=2, value=course.description)
                            ws.cell(row=row, column=3, value=course.time)
                            ws.cell(row=row, column=4, value=course.days)
                            ws.cell(row=row, column=5, value=course.room)
                            row += 1
                        
                        row += 1  # Add space between sections
        
        # Remove default sheet
        wb.remove(wb['Sheet'])
        
        # Save workbook
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            wb.save(file_path)
            messagebox.showinfo("Success", "Sections generated and exported successfully!")

def main():
    root = tk.Tk()
    app = SectionCreatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()