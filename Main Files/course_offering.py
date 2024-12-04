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

        # Individual Days
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        # Groups
        groups = ['A', 'B']

        # Number of sections per year level per group
        num_sections = 4  # Adjust this number as needed

        # Prepare rooms by type, excluding Gym and Aud from general rooms
        lecture_rooms = [room for room in rooms if room[2] == 'Lecture' and room[1] not in ['Gym', 'Aud']]
        lab_rooms = [room for room in rooms if room[2] == 'Lab' and room[1] not in ['Gym', 'Aud']]

        # Shuffle lecture and lab rooms to distribute usage
        random.shuffle(lecture_rooms)
        random.shuffle(lab_rooms)

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
                if num_sections > len(section_letters):
                    raise Exception("Number of sections exceeds available letters.")
                section_codes = [f"{year_num}{section_letters[i]}" for i in range(num_sections)]

                # Initialize schedules
                section_schedules = {section_code: [] for section_code in section_codes}
                room_schedules = {room[1]: [] for room in rooms}

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

                # Identify NSTP 1
                nstp1_subject_code = None
                for subject_code in subject_codes_to_schedule:
                    if subject_code.startswith('NSTP 1'):
                        nstp1_subject_code = subject_code
                        break  # Assuming only one NSTP 1 subject code
                if nstp1_subject_code:
                    # Schedule NSTP 1 for all sections at the same time
                    # Remove NSTP 1 from subject_codes_to_schedule
                    subject_codes_to_schedule.remove(nstp1_subject_code)

                    # Get NSTP 1 subject details
                    nstp1_subject_list = subjects_by_code[nstp1_subject_code]
                    lecture_subject = next(
                        (s for s in nstp1_subject_list if s[6] == 'Lecture'),
                        None)
                    lab_subject = next(
                        (s for s in nstp1_subject_list if s[6] == 'Lab'),
                        None)
                    # Prepare subjects to schedule
                    subjects_to_schedule = []
                    if lecture_subject:
                        subjects_to_schedule.append(lecture_subject)
                    if lab_subject:
                        subjects_to_schedule.append(lab_subject)
                    # Determine room list
                    is_special = lecture_subject and lecture_subject[3] == 'Special'
                    is_ntsp = is_special and lecture_subject[1].startswith('NSTP')
                    if is_ntsp:
                        available_rooms = [room for room in aud_rooms if room[2] == lecture_subject[6]]
                    else:
                        # Should not happen
                        available_rooms = []

                    # Shuffle time slots and days to vary the schedule
                    nstp_time_slots = time_slots.copy()
                    nstp_days = days.copy()
                    random.shuffle(nstp_time_slots)
                    random.shuffle(nstp_days)

                    # Try to find a time slot where the room is available
                    scheduled = False
                    for day in nstp_days:
                        for time_slot in nstp_time_slots:
                            # Check if time slot is available in all sections
                            if any((day, time_slot) in section_schedules[section_code]
                                   for section_code in section_codes):
                                continue  # Time slot not available
                            # Check room availability
                            room_available = False
                            for room in available_rooms:
                                room_code = room[1]
                                if (day, time_slot) not in room_schedules[room_code]:
                                    # Room is available
                                    assigned_room = room_code
                                    room_available = True
                                    break
                            if not room_available:
                                continue
                            # Schedule NSTP 1 for all sections
                            for section_code in section_codes:
                                # Insert into database
                                database.insert_course_offering(
                                    subject_code=lecture_subject[1],
                                    subject_description=lecture_subject[2],
                                    room_code=assigned_room,
                                    day_pattern=day,
                                    time_slot=time_slot,
                                    group=group,
                                    section_code=section_code
                                )
                                # Mark the time slot as occupied
                                section_schedules[section_code].append((day, time_slot))
                                room_schedules[assigned_room].append((day, time_slot))
                            scheduled = True
                            break  # NSTP 1 scheduled
                        if scheduled:
                            break
                    if not scheduled:
                        # Could not schedule NSTP 1
                        raise Exception(f"Could not schedule NSTP 1 for group {group}, year {year_num}")

                # Now proceed to schedule other subjects per section
                for section_code in section_codes:
                    # Initialize per-section variables
                    section_schedule = section_schedules[section_code]
                    # Create a copy of subject_codes_to_schedule
                    subjects_to_schedule_for_section = subject_codes_to_schedule.copy()
                    # Distribute subjects between days
                    day_subjects = {day: [] for day in days}
                    # Shuffle subjects to vary scheduling
                    random.shuffle(subjects_to_schedule_for_section)
                    day_index = 0
                    for subj_code in subjects_to_schedule_for_section:
                        day = days[day_index % len(days)]
                        day_subjects[day].append(subj_code)
                        day_index += 1

                    scheduled_subjects = []
                    for day in days:
                        # Shuffle time slots to vary scheduling
                        available_time_slots = time_slots.copy()
                        random.shuffle(available_time_slots)
                        for subject_code in day_subjects[day]:
                            subject_list = subjects_by_code[subject_code]
                            # Ensure we have both Lecture and Lab types if applicable
                            lecture_subject = next(
                                (s for s in subject_list if s[6] == 'Lecture'),
                                None)
                            lab_subject = next(
                                (s for s in subject_list if s[6] == 'Lab'),
                                None)

                            # Prepare the pair of subjects to schedule together
                            subjects_to_schedule_pair = []
                            if lecture_subject:
                                subjects_to_schedule_pair.append(lecture_subject)
                            if lab_subject:
                                subjects_to_schedule_pair.append(lab_subject)

                            # Determine room list based on subject requirements
                            is_minor = lecture_subject and lecture_subject[3] == 'Minor'
                            is_special = lecture_subject and lecture_subject[3] == 'Special'
                            is_ntsp = is_special and lecture_subject[1].startswith('NSTP')
                            is_pe = is_special and lecture_subject[1].startswith('PE')

                            scheduled = False
                            # Try all combinations of available time slots
                            for i in range(len(available_time_slots) - len(subjects_to_schedule_pair) + 1):
                                time_slot_sequence = available_time_slots[i:i+len(subjects_to_schedule_pair)]
                                # Check if time slots are available in section schedule
                                if any((day, ts) in section_schedule
                                       for ts in time_slot_sequence):
                                    continue  # Time slots not available in section

                                # Check room availability for each subject
                                rooms_available = True
                                assigned_rooms = []
                                for idx, subj in enumerate(subjects_to_schedule_pair):
                                    subj_type = subj[6]
                                    # Select rooms based on subject
                                    if is_minor:
                                        available_rooms = [room for room in minor_rooms
                                                           if room[2] == subj_type]
                                        random.shuffle(available_rooms)  # Shuffle minor rooms
                                    elif is_ntsp:
                                        continue  # NSTP 1 already scheduled
                                    elif is_pe:
                                        available_rooms = [room for room in gym_rooms
                                                           if room[2] == subj_type]
                                    else:
                                        # General subjects
                                        if subj_type == 'Lecture':
                                            available_rooms = lecture_rooms.copy()
                                        else:
                                            available_rooms = lab_rooms.copy()
                                        random.shuffle(available_rooms)  # Shuffle general rooms

                                        # Exclude Gym and Aud from general subjects
                                        available_rooms = [room for room in available_rooms if room[1] not in ['Gym', 'Aud']]

                                    # Exclude M301, M303, M305, M307 on Saturdays
                                    if day == 'Saturday':
                                        excluded_rooms = ['M301', 'M303', 'M305', 'M307']
                                        available_rooms = [room for room in available_rooms if room[1] not in excluded_rooms]

                                    if not available_rooms:
                                        rooms_available = False
                                        break  # No rooms of this type available

                                    # Find an available room
                                    for room in available_rooms:
                                        room_code = room[1]
                                        if (day, time_slot_sequence[idx]) in room_schedules[room_code]:
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
                                for idx, subj in enumerate(subjects_to_schedule_pair):
                                    room_code = assigned_rooms[idx]
                                    time_slot = time_slot_sequence[idx]

                                    # Insert the course offering into the database
                                    database.insert_course_offering(
                                        subject_code=subj[1],
                                        subject_description=subj[2],
                                        room_code=room_code,
                                        day_pattern=day,
                                        time_slot=time_slot,
                                        group=group,
                                        section_code=section_code
                                    )

                                    # Mark the time slots as occupied
                                    section_schedule.append((day, time_slot))
                                    room_schedules[room_code].append((day, time_slot))

                                scheduled = True
                                break  # Subjects scheduled, move to next
                            if scheduled:
                                scheduled_subjects.append(subject_code)
                            else:
                                raise Exception(
                                    f"Could not schedule subject {subject_code} for section {section_code} "
                                    f"in group {group}, year {year_num}"
                                )

                    # Remove scheduled subjects from the list
                    for subj_code in scheduled_subjects:
                        if subj_code in subjects_to_schedule_for_section:
                            subjects_to_schedule_for_section.remove(subj_code)

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

        # Define the day order
        day_order = {
            'Monday': 1,
            'Tuesday': 2,
            'Wednesday': 3,
            'Thursday': 4,
            'Friday': 5,
            'Saturday': 6
        }

        # Sort offerings for better presentation
        offerings.sort(key=lambda x: (
            x[5],  # group_name
            x[6],  # section_code
            day_order.get(x[3], 0),  # day order
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
                f"Room: {room_code}, Day: {day_pattern}, Time: {time_slot}"
            )
            self.offerings_listbox.insert('end', display_text)
            self.offerings_listbox.insert('end', "")  # Add an empty line
