import pandas as pd

# Step 1: Data Retrieval
subjects_df = pd.read_csv('SubjectsUC_CSV.csv')
rooms_df = pd.read_csv('RoomsUC_CSV.csv')
days_df = pd.read_csv('DaysUC_CSV.csv')
timeslots_df = pd.read_csv('TimeslotUC_CSV.csv')

# Step 2: Group Creation
group_a_programs = ['BSIT', 'BSIT(Netsec)', 'BSIT(WebTech)', 'BSIT(ERP)', 'BSCS', 'BSDA', 'BSMMA']
group_b_programs = group_a_programs.copy()

group_a = []
group_b = []

for program in group_a_programs:
    for year in ['First year', 'Second Year', 'Third Year']:
        for term in ['First Term', 'Second Term', 'Third Term']:
            group_a.append((program, year, term))

for program in group_b_programs:
    for year in ['First year', 'Second Year', 'Third Year']:
        for term in ['First Term', 'Second Term', 'Third Term']:
            group_b.append((program, year, term))

# Step 3: Section and Table Structure Creation
all_groups = group_a + group_b
section_tables = {}

for program, year, term in all_groups:
    sections = [f"{year[0]}{'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i]}" for i in range(5)]
    section_tables[(program, year, term)] = pd.DataFrame(columns=['CourseCode', 'Description', 'Time', 'Days', 'Room'])

# Step 4: Data Population and Scheduling Rules
for program, year, term in all_groups:
    section_table = section_tables[(program, year, term)]
    program_courses = subjects_df[(subjects_df['Program'] == program) & (subjects_df['Year_Level'] == year) & (subjects_df['Semester'] == term)]

    for _, course in program_courses.iterrows():
        course_code = course['Course_Code']
        description = course['Description']
        course_type = course['Type']
        course_days = course['Days']

        # Assign timeslots and rooms
        available_timeslots = timeslots_df['Timeslot'].tolist()
        available_rooms = rooms_df[(rooms_df[course_type] == 'Yes')]['Room_Code'].tolist()

        # Check if the course has a valid day specified in the DaysUC_CSV.csv file
        if course_days in days_df['Description'].values:
            day_code = days_df.loc[days_df['Description'] == course_days]['Days_Code'].values[0]
            if 'S' in day_code:
                unavailable_rooms = ['M301', 'M303', 'M305', 'M307']
                available_rooms = [room for room in available_rooms if room not in unavailable_rooms]

            if course_code == 'Aud':
                available_rooms = ['Aud']
            elif course_code == 'Gym':
                available_rooms = ['Gym']

            timeslot = available_timeslots.pop(0)
            room = available_rooms.pop(0)

            # Add course to section table
            section_table = section_table.append({
                'CourseCode': course_code,
                'Description': description,
                'Time': timeslot,
                'Days': day_code,
                'Room': room
            }, ignore_index=True)

            # Handle consecutive timeslots for the same course
            if course['Type'] != 'Pure Lec':
                timeslot = available_timeslots.pop(0)
                section_table = section_table.append({
                    'CourseCode': course_code,
                    'Description': description,
                    'Time': timeslot,
                    'Days': day_code,
                    'Room': room
                }, ignore_index=True)
        else:
            print(f"Warning: Course '{course_code}' does not have a valid day specified in the DaysUC_CSV.csv file. Skipping this course.")

    # Group by days and arrange chronologically
    section_table = section_table.sort_values(['Days', 'Time'])
    section_tables[(program, year, term)] = section_table

# Step 5: Iterative Process for All Groups
# (This step is already handled in the previous code)

# Step 6: Final Conflict Checks
for program, year, term in group_a:
    group_a_table = section_tables[(program, year, term)]
    for room in group_a_table['Room'].unique():
        room_conflicts = group_a_table[group_a_table['Room'] == room]
        if len(room_conflicts[room_conflicts['Time'].duplicated()]) > 0:
            print(f"Conflict found in Group A for {program}, {year}, {term} in room {room}")

for program, year, term in group_b:
    group_b_table = section_tables[(program, year, term)]
    for room in group_b_table['Room'].unique():
        room_conflicts = group_b_table[group_b_table['Room'] == room]
        if len(room_conflicts[room_conflicts['Time'].duplicated()]) > 0:
            print(f"Conflict found in Group B for {program}, {year}, {term} in room {room}")

# Step 7: Export to Excel
for (program, year, term), section_table in section_tables.items():
    section_table.to_excel(f"{program}_{year}_{term}.xlsx", index=False)