# course_offering.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database  # Use the consolidated database module
import string  # For generating section letters
import random

class CourseOfferingPage:
    """GUI for Course Offering Generation."""
    def __init__(self, parent):
        self.parent = parent

        # Build the GUI components
        self.build_gui()

    def build_gui(self):
        """Construct the GUI components for the course offering page."""
        generate_button = tk.Button(
            self.parent, text="Generate Course Offerings",
            command=self.generate_course_offerings)
        generate_button.pack(pady=10)

        # Feedback Label
        self.feedback_label = tk.Label(self.parent, text="")
        self.feedback_label.pack()

        # Course Offerings Listbox with Scrollbar
        listbox_frame = tk.Frame(self.parent)
        listbox_frame.pack(pady=10, fill='both', expand=True)

        self.offerings_listbox = tk.Listbox(listbox_frame, width=100)
        self.offerings_listbox.pack(side='left', fill='both', expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient='vertical')
        scrollbar.config(command=self.offerings_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.offerings_listbox.config(yscrollcommand=scrollbar.set)

        # Refresh Button
        refresh_button = tk.Button(
            self.parent, text="Refresh List",
            command=self.refresh_offerings_list)
        refresh_button.pack(pady=10)

    def generate_course_offerings(self):
        """Generate course offerings with specific room assignments."""
        # Clear existing offerings
        database.clear_course_offerings()

        # Fetch subjects and rooms from the existing database
        subjects = database.fetch_all_subjects()
        rooms = database.fetch_rooms()

        if not subjects:
            messagebox.showwarning("No Subjects",
                                   "No subjects found in the database.")
            return

        if not rooms:
            messagebox.showwarning("No Rooms",
                                   "No rooms found in the database.")
            return

        # Generate schedules
        try:
            self.create_schedules(subjects, rooms)
            self.feedback_label.config(
                text="Course offerings generated successfully!", fg="green")
            self.refresh_offerings_list()
        except Exception as e:
            self.feedback_label.config(text=f"Error: {e}", fg="red")

    def create_schedules(self, subjects, rooms):
        """Create schedules with room assignment constraints."""
        # Time slots
        time_slots = [
            '7:30am - 8:50am',
            '8:50am - 10:10am',
            '10:10am - 11:30am',
            '11:30am - 12:50pm',
            '12:50pm - 2:10pm',
            '2:10pm - 3:30pm',
            '3:30pm - 4:50pm',
            '4:50pm - 6:10pm',
            '6:10pm - 7:30pm'
        ]

        # Days patterns
        day_patterns = ['MWF', 'TThS']

        # Groups
        groups = ['A', 'B']

        # Prepare rooms by type
        lecture_rooms = [room for room in rooms if room[2] == 'Lecture']
        lab_rooms = [room for room in rooms if room[2] == 'Lab']

        # Special rooms
        minor_rooms = [room for room in rooms if room[1] in ['U706', 'U402', 'U705']]
        aud_rooms = [room for room in rooms if room[1] == 'Aud']
        gym_rooms = [room for room in rooms if room[1] == 'Gym']

        # Group subjects by year level
        subjects_by_year = {'1': [], '2': [], '3': []}
        for subject in subjects:
            year_num = subject[4][0]  # Assuming year_level is like '1st Year'
            if year_num in subjects_by_year:
                subjects_by_year[year_num].append(subject)
            else:
                # Skip if year level is not recognized
                continue

        # For each group and year level, create sections and schedule subjects
        for group in groups:
            for year_num in ['1', '2', '3']:
                # Initialize section letters
                section_letters = list(string.ascii_uppercase)
                year_subjects = subjects_by_year[year_num]
                # Group subjects by subject code to handle Lecture and Lab together
                subjects_by_code = {}
                for subject in year_subjects:
                    subject_code = subject[1]
                    if subject_code not in subjects_by_code:
                        subjects_by_code[subject_code] = []
                    subjects_by_code[subject_code].append(subject)

                # List of subject codes to schedule
                subject_codes_to_schedule = list(subjects_by_code.keys())
                random.shuffle(subject_codes_to_schedule)  # Shuffle to vary

                # While there are subjects to schedule
                while subject_codes_to_schedule:
                    if not section_letters:
                        raise Exception(
                            f"No more sections available for Year {year_num}"
                            f" in Group {group}")
                    section_letter = section_letters.pop(0)
                    section_code = f"{year_num}{section_letter}"

                    # Initialize schedules
                    section_schedule = []  # List of (day_pattern, time_slot)
                    room_schedules = {}  # room_code: list of (day_pattern, time_slot)

                    for room in rooms:
                        room_schedules[room[1]] = []

                    # Distribute subjects between MWF and TThS
                    day_pattern_subjects = {'MWF': [], 'TThS': []}
                    # Alternate day patterns
                    pattern_switch = True
                    for subj_code in subject_codes_to_schedule:
                        if pattern_switch:
                            day_pattern_subjects['MWF'].append(subj_code)
                        else:
                            day_pattern_subjects['TThS'].append(subj_code)
                        pattern_switch = not pattern_switch

                    scheduled_subjects = []
                    for day_pattern in day_patterns:
                        for subject_code in day_pattern_subjects[day_pattern]:
                            subject_list = subjects_by_code[subject_code]
                            # Ensure we have both Lecture and Lab types if applicable
                            lecture_subject = next(
                                (s for s in subject_list if s[6] == 'Lecture'),
                                None)
                            lab_subject = next(
                                (s for s in subject_list if s[6] == 'Lab'),
                                None)

                            # Prepare the pair of subjects to schedule together
                            subjects_to_schedule = []
                            if lecture_subject:
                                subjects_to_schedule.append(lecture_subject)
                            if lab_subject:
                                subjects_to_schedule.append(lab_subject)

                            # Determine room list based on subject requirements
                            is_minor = lecture_subject and lecture_subject[3] == 'Minor'
                            is_ntsp = lecture_subject and lecture_subject[1] == 'NTSP'
                            is_pe = lecture_subject and lecture_subject[1] == 'PE'

                            scheduled = False
                            for i in range(len(time_slots) - len(subjects_to_schedule) + 1):
                                time_slot_sequence = time_slots[i:i+len(subjects_to_schedule)]
                                # Check if time slots are available in section schedule
                                if any((day_pattern, ts) in section_schedule
                                       for ts in time_slot_sequence):
                                    continue  # Time slots not available in section

                                # Check room availability for each subject
                                rooms_available = True
                                assigned_rooms = []
                                for idx, subj in enumerate(subjects_to_schedule):
                                    subj_type = subj[6]
                                    # Select rooms based on subject
                                    if is_minor:
                                        available_rooms = [room for room in minor_rooms
                                                           if room[2] == subj_type]
                                        random.shuffle(available_rooms)  # Shuffle minor rooms
                                    elif is_ntsp:
                                        available_rooms = [room for room in aud_rooms
                                                           if room[2] == subj_type]
                                    elif is_pe:
                                        available_rooms = [room for room in gym_rooms
                                                           if room[2] == subj_type]
                                    else:
                                        # General subjects
                                        available_rooms = lecture_rooms if subj_type == 'Lecture' else lab_rooms

                                    if not available_rooms:
                                        rooms_available = False
                                        break  # No rooms of this type available

                                    # Find an available room
                                    for room in available_rooms:
                                        room_code = room[1]
                                        if (day_pattern, time_slot_sequence[idx]) in room_schedules[room_code]:
                                            continue  # Room not available
                                        else:
                                            assigned_rooms.append(room_code)
                                            break
                                    else:
                                        rooms_available = False
                                        break  # No room available for this subject

                                if not rooms_available:
                                    continue  # Try next time slot

                                # Assign subjects to the time slots and rooms
                                for idx, subj in enumerate(subjects_to_schedule):
                                    room_code = assigned_rooms[idx]
                                    time_slot = time_slot_sequence[idx]

                                    # Insert the course offering into the database
                                    database.insert_course_offering(
                                        subject_code=subj[1],
                                        subject_description=subj[2],
                                        room_code=room_code,
                                        day_pattern=day_pattern,
                                        time_slot=time_slot,
                                        group=group,
                                        section_code=section_code
                                    )

                                    # Mark the time slots as occupied
                                    section_schedule.append((day_pattern, time_slot))
                                    room_schedules[room_code].append((day_pattern, time_slot))

                                scheduled = True
                                break  # Subjects scheduled, move to next
                            if scheduled:
                                scheduled_subjects.append(subject_code)
                            else:
                                continue  # Could not schedule this subject in this section

                    # Remove scheduled subjects from the list
                    for subj_code in scheduled_subjects:
                        if subj_code in subject_codes_to_schedule:
                            subject_codes_to_schedule.remove(subj_code)

    def refresh_offerings_list(self):
        """Refresh the list of course offerings displayed."""
        self.offerings_listbox.delete(0, 'end')
        offerings = database.fetch_course_offerings()

        # Define the time slot order
        time_slot_order = {
            '7:30am - 8:50am': 1,
            '8:50am - 10:10am': 2,
            '10:10am - 11:30am': 3,
            '11:30am - 12:50pm': 4,
            '12:50pm - 2:10pm': 5,
            '2:10pm - 3:30pm': 6,
            '3:30pm - 4:50pm': 7,
            '4:50pm - 6:10pm': 8,
            '6:10pm - 7:30pm': 9
        }

        # Sort offerings for better presentation
        offerings.sort(key=lambda x: (
            x[5],  # group_name
            x[6],  # section_code
            x[3],  # day_pattern
            time_slot_order.get(x[4], 0)  # time_slot order
        ))

        current_group_section = None
        for offering in offerings:
            subject_code, subject_description, room_code, day_pattern, time_slot, group_name, section_code = offering

            group_section = f"Group {group_name}, Section {section_code}"
            if group_section != current_group_section:
                current_group_section = group_section
                # Insert a separator and the group-section header
                self.offerings_listbox.insert('end', f"{'='*80}")
                self.offerings_listbox.insert('end', group_section)
                self.offerings_listbox.insert('end', f"{'-'*80}")

            # Create a formatted string for display
            display_text = (
                f"Subject: {subject_code} - {subject_description}\n"
                f"Room: {room_code}, Days: {day_pattern}, Time: {time_slot}"
            )
            self.offerings_listbox.insert('end', display_text)
            self.offerings_listbox.insert('end', "")  # Add an empty line
