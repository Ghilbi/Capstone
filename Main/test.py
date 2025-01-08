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

def get_consecutive_time_slots(time_slots: List[TimeSlot], is_mwf: bool, num_slots: int) -> List[TimeSlot]:
    available_sequences = []
    for i in range(len(time_slots) - num_slots + 1):
        sequence = time_slots[i:i + num_slots]
        if all(slot.is_available(is_mwf) for slot in sequence):
            available_sequences.append(sequence)
    return available_sequences

def get_available_rooms(course: Course, all_rooms: Set[str], year_level: str, trimester: str) -> List[str]:
    # If it's an NSTP course, return only Auditorium
    if 'NSTP' in course.code:
        return ['Aud']
        
    # If it's a PathFit course, return only Gym
    if 'PathFit' in course.code or 'PATHFit' in course.code:
        return ['Gym']

    lab_rooms = {'M303', 'M304', 'M305', 'M306', 'M307', 'N3001', 'N3002', 'S312'}
    major_rooms = {'M301', 'M303', 'M304', 'M305', 'M306', 'M307', 'N3001', 'N3002', 'S312'}
    major_subjects = {
    'CC1', 'CC10', 'CC11', 'CC12', 'CC13', 'CC14', 'CC15', 'CC16', 'CC17', 'CC18', 'CC19', 'CC2',
    'CC21', 'CC22', 'CC23', 'CC24', 'CC3', 'CC4', 'CC5', 'CC6', 'CC7', 'CC8', 'CC9', 'CCS10',
    'CCS11', 'CCS12', 'CCS13', 'CCS14', 'CCS15', 'CCS16', 'CCS2', 'CCS3', 'CCS4', 'CCS5', 'CCS6',
    'CCS7', 'CCS8', 'CCS9', 'CDA1', 'CDA10', 'CDA11', 'CDA12', 'CDA2', 'CDA3', 'CDA4', 'CDA5',
    'CDA6', 'CDA7', 'CDA8', 'CDA9', 'CIT1', 'CIT10', 'CIT11', 'CIT12', 'CIT14', 'CIT15', 'CIT16',
    'CIT17', 'CIT18', 'CIT19', 'CIT26', 'CIT22', 'CIT23', 'CIT24', 'CIT25', 'CIT3', 'CIT4', 'CIT5',
    'CIT6', 'CIT7', 'CIT8', 'CIT9', 'CCS1', 'MCC1', 'MCC2', 'MCC3', 'MCC4', 'MCC5', 'MCC6', 'MCC7', 
    'MCC8', 'MM12', 'MMC1', 'MMC11', 'MMC13','MMC14', 'MMC15', 'MMC16', 'MMC17', 'MMC18', 'MMC19', 
    'MMC2', 'MMC3', 'MMC4', 'MMC5', 'MMC6', 'MMC7', 'MMC8', 'MMC9', 'CIT13'
}
    
    # Check if the course code matches any major subject code
    is_major = any(course.code.startswith(major_code) for major_code in major_subjects)
    
    # If it's a lab course, only return lab rooms
    if course.is_lab:
        return list(lab_rooms)
    
    # If it's a major subject but not a lab
    if is_major:
        return list(major_rooms)
        
    # For regular courses, return all rooms except restricted (Gym, Aud), lab, and major rooms
    restricted_rooms = {'Gym', 'Aud'}
    return list(all_rooms - restricted_rooms - lab_rooms - major_rooms)

def balance_and_shuffle_courses(courses: List[Course], year_level: str, trimester: str) -> List[Course]:
    # Initialize time slots
    base_times = [
        '7:30am', '8:50am', '10:10am', '11:30am',
        '12:50pm', '2:10pm', '3:30pm', '4:50pm', '6:10pm'
    ]
    time_slots = [TimeSlot(time) for time in base_times]
    
    # Track room assignments per course code
    course_room_history = {}
    
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
    
    def select_room(course: Course, available_rooms: List[str]) -> str:
        # For NSTP and PathFit courses, maintain strict room assignment
        if 'NSTP' in course.code:
            return 'Aud'
        if 'PathFit' in course.code or 'PATHFit' in course.code:
            return 'Gym'
            
        # Get the base course code (without section identifiers)
        base_code = course.code.split('(')[0].strip()
        
        # If this course code has been assigned rooms before
        if base_code in course_room_history:
            previously_used_rooms = [room for room in available_rooms if room in course_room_history[base_code]]
            if previously_used_rooms:
                # 70% chance to reuse a previously used room if available
                if random.random() < 0.6:
                    return random.choice(previously_used_rooms)
        
        # Either no room history or didn't select from history
        selected_room = random.choice(available_rooms)
        
        # Update room history
        if base_code not in course_room_history:
            course_room_history[base_code] = set()
        course_room_history[base_code].add(selected_room)
        
        return selected_room
    
    # Process paired courses
    pair_keys = list(paired_courses.keys())
    random.shuffle(pair_keys)
    
    for pair_key in pair_keys:
        pair = paired_courses[pair_key]
        
        # Get available rooms for each course in the pair
        rooms_per_course = []
        for course in pair:
            available_rooms = get_available_rooms(course, all_rooms, year_level, trimester)
            if not available_rooms:
                continue
            rooms_per_course.append(available_rooms)
        
        # Skip if we don't have rooms for all courses in the pair
        if len(rooms_per_course) != len(pair):
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
        for i, (course, slot, available_rooms) in enumerate(zip(pair, selected_sequence, rooms_per_course)):
            course.time = f"{slot.start_time_str}-{slot.end_time_str}"
            course.days = pattern
            course.room = select_room(course, available_rooms)
            course.time_obj = slot.start_time
            course.end_time_obj = slot.end_time
        
        if is_mwf:
            mwf_courses.extend(pair)
        else:
            tth_courses.extend(pair)
    
    # Process standalone courses
    random.shuffle(standalone_courses)
    for course in standalone_courses:
        available_rooms = get_available_rooms(course, all_rooms, year_level, trimester)
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
        course.room = select_room(course, available_rooms)
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
        self.root.title("Subject Offering")
        self.root.geometry("460x800")
        self.root.configure(bg="#f0f0f0")
        self.df = None
        # Define programs and their available years
        self.program_years = {
            "BSIT": ["First"],
            "BSIT(WebTech)": ["Second", "Third"],
            "BSIT(Netsec)": ["Second", "Third"],
            "BSIT(ERP)": ["Second", "Third"],
            "BSCS": ["First", "Second", "Third"],
            "BSDA": ["First", "Second", "Third"],
            "BMMA": ["First", "Second", "Third"]
        }
        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Custom.TLabelframe", padding=15)
        style.configure("Action.TButton", padding=10)
        style.configure("Subheader.TLabel", font=("Helvetica", 10, "bold"))
        
        # Title
        title_frame = ttk.Frame(main_container)
        title_frame.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        ttk.Label(title_frame, text="Subject Course Offering", style="Title.TLabel").pack()
        
        # File import frame
        import_frame = ttk.LabelFrame(main_container, text="Data Import", style="Custom.TLabelframe")
        import_frame.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        self.file_label = ttk.Label(import_frame, text="No file selected", font=("Helvetica", 10, "italic"))
        self.file_label.grid(row=0, column=1, padx=10)
        
        ttk.Button(import_frame, text="Import CSV File", command=self.import_csv, style="Action.TButton").grid(row=0, column=0, padx=10)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_container, text="Section Configuration", style="Custom.TLabelframe")
        config_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        
        # Trimester selection
        trim_frame = ttk.Frame(config_frame)
        trim_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        
        ttk.Label(trim_frame, text="Trimester:", style="Header.TLabel").grid(row=0, column=0, padx=(0, 10))
        
        self.trimester_var = tk.StringVar(value="First")
        trimester_combo = ttk.Combobox(
            trim_frame, 
            textvariable=self.trimester_var,
            values=["First", "Second", "Third"],
            width=15,
            state="readonly"
        )
        trimester_combo.grid(row=0, column=1)
        
        # Program sections configuration
        sections_frame = ttk.Frame(config_frame)
        sections_frame.grid(row=1, column=0, sticky="ew", columnspan=2)
        
        ttk.Label(sections_frame, text="Number of Sections per Program", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Dictionary to store all section count widgets
        self.section_counts = {}
        
        # Split programs into two columns
        left_programs = ["BSIT", "BSIT(WebTech)", "BSIT(Netsec)", "BSIT(ERP)"]
        right_programs = ["BSCS", "BSDA", "BMMA"]
        
        # Create left column
        left_frame = ttk.Frame(sections_frame)
        left_frame.grid(row=1, column=0, padx=20, sticky="n")

        current_row = 0
        for program in left_programs:
            # Program header
            ttk.Label(left_frame, text=program, style="Subheader.TLabel").grid(row=current_row, column=0, sticky="w")
            current_row += 1
            
            self.section_counts[program] = {}
            
            # Add year-specific section counts
            years = self.program_years[program]
            for year in years:
                container = ttk.Frame(left_frame)
                container.grid(row=current_row, column=0, pady=2, padx=20, sticky="w")
                
                # Year label
                ttk.Label(container, text=f"{year}:", width=8, anchor="e").grid(row=0, column=0, padx=(0, 10))
                
                # Section count spinbox
                spinbox = ttk.Spinbox(container, from_=1, to=10, width=5, justify="center")
                spinbox.grid(row=0, column=1)
                spinbox.set(0)
                self.section_counts[program][year] = spinbox
                
                current_row += 1
            
            # Add the "Third" spinbox specifically for "BSIT"
            if program == "BSIT":
                container = ttk.Frame(left_frame)
                container.grid(row=current_row, column=0, pady=2, padx=20, sticky="w")
                
                ttk.Label(container, text="Third:", width=8, anchor="e").grid(row=0, column=0, padx=(0, 10))
                
                spinbox = ttk.Spinbox(container, from_=1, to=10, width=5, justify="center")
                spinbox.grid(row=0, column=1)
                spinbox.set(0)
                self.section_counts[program]["Third"] = spinbox
                
                current_row += 1
            
            # Add spacing between programs
            current_row += 1
        
        # Create right column
        right_frame = ttk.Frame(sections_frame)
        right_frame.grid(row=1, column=1, padx=20, sticky="n")
        
        current_row = 0
        for program in right_programs:
            # Program header
            ttk.Label(right_frame, text=program, style="Subheader.TLabel").grid(row=current_row, column=0, sticky="w")
            current_row += 1
            
            self.section_counts[program] = {}
            
            # Add year-specific section counts
            years = self.program_years[program]
            for year in years:
                container = ttk.Frame(right_frame)
                container.grid(row=current_row, column=0, pady=2, padx=20, sticky="w")
                
                # Year label
                ttk.Label(container, text=f"{year}:", width=8, anchor="e").grid(row=0, column=0, padx=(0, 10))
                
                # Section count spinbox
                spinbox = ttk.Spinbox(container, from_=1, to=10, width=5, justify="center")
                spinbox.grid(row=0, column=1)
                spinbox.set(0)
                self.section_counts[program][year] = spinbox
                
                current_row += 1
            
            # Add spacing between programs
            current_row += 1
        
        # Generate button
        generate_frame = ttk.Frame(main_container)
        generate_frame.grid(row=3, column=0, pady=20)
        
        ttk.Button(generate_frame, text="Generate and Export Sections", command=self.generate_sections, style="Action.TButton", width=30).pack()

    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            file_name = file_path.split("/")[-1]
            self.file_label.config(text=f"Selected file: {file_name}")
            messagebox.showinfo("Success", "CSV file imported successfully!")

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
        
        # Pass year and trimester to balance_and_shuffle_courses
        return balance_and_shuffle_courses(courses, year, trimester)

    def generate_sections(self):
        if self.df is None:
            messagebox.showerror("Error", "Please import CSV file first")
            return
                
        wb = openpyxl.Workbook()
        
        # Year level mapping dictionary
        year_mapping = {
            "First": "1",
            "Second": "2",
            "Third": "3"
        }
        
        for group_name in ['A', 'B']:
            ws = wb.create_sheet(f"Group {group_name}")
            row = 1
            
            for program, year_sections in self.section_counts.items():
                for year, spinbox in year_sections.items():
                    num_sections = int(spinbox.get())
                    if num_sections > 0:
                        for section_num in range(num_sections):
                            section_letter = chr(65 + section_num)
                            section_name = f"{year_mapping[year]}{section_letter}"
                            
                            ws.cell(row=row, column=1, value=f"{program}, {year} Year, {self.trimester_var.get()} Trimester Section {section_name}")
                            row += 1
                            
                            headers = ["COURSE CODE", "DESCRIPTION", "TIME", "DAYS", "ROOM"]
                            for col, header in enumerate(headers, 1):
                                ws.cell(row=row, column=col, value=header)
                            row += 1
                            
                            courses = self.create_section_courses(program, year, self.trimester_var.get())
                            
                            for course in courses:
                                ws.cell(row=row, column=1, value=course.code)
                                ws.cell(row=row, column=2, value=course.description)
                                ws.cell(row=row, column=3, value=course.time)
                                ws.cell(row=row, column=4, value=course.days)
                                ws.cell(row=row, column=5, value=course.room)
                                row += 1
                            
                            row += 1
        
        wb.remove(wb['Sheet'])
        
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