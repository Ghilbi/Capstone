# rooms_page.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import database

class RoomsPage:
    """GUI for managing rooms."""
    def __init__(self, parent):
        self.parent = parent
        self.lecture_var = tk.BooleanVar(value=False)
        self.lab_var = tk.BooleanVar(value=False)
        self.editing_room_id = None

        self.build_gui()

    def build_gui(self):
        """Construct the GUI components for the rooms page."""
        # Room Code Entry
        room_code_label = tk.Label(self.parent, text="Room Code:")
        room_code_label.grid(row=0, column=0, padx=10, pady=10)
        self.room_code_entry = tk.Entry(self.parent)
        self.room_code_entry.grid(row=0, column=1, padx=10, pady=10)

        # Room Type Checkboxes
        type_label = tk.Label(self.parent, text="Room Type:")
        type_label.grid(row=1, column=0, padx=10, pady=10)

        lecture_checkbox = tk.Checkbutton(self.parent, text="Lecture", variable=self.lecture_var, command=self.set_lecture)
        lecture_checkbox.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        lab_checkbox = tk.Checkbutton(self.parent, text="Lab", variable=self.lab_var, command=self.set_lab)
        lab_checkbox.grid(row=2, column=1, padx=10, pady=5, sticky='w')

        # Submit Button
        self.submit_button = tk.Button(self.parent, text="Submit", command=self.submit_form)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Feedback Label
        self.feedback_label = tk.Label(self.parent, text="")
        self.feedback_label.grid(row=4, column=0, columnspan=2)

        # Rooms Listbox
        rooms_list_label = tk.Label(self.parent, text="Rooms List:")
        rooms_list_label.grid(row=5, column=0, padx=10, pady=10)

        self.rooms_listbox = tk.Listbox(self.parent, height=10, width=50)
        self.rooms_listbox.grid(row=5, column=1, padx=10, pady=10)

        # Edit and Delete Buttons
        edit_button = tk.Button(self.parent, text="Edit Room", command=self.edit_room)
        edit_button.grid(row=6, column=0, padx=10, pady=10)

        delete_button = tk.Button(self.parent, text="Delete Room", command=self.delete_room)
        delete_button.grid(row=6, column=1, padx=10, pady=10)

        # Refresh Button
        refresh_button = tk.Button(self.parent, text="Refresh List", command=self.refresh_rooms_list)
        refresh_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Initially refresh the rooms list
        self.refresh_rooms_list()

    def set_lecture(self):
        """Ensure only Lecture is selected."""
        self.lab_var.set(False)
        self.lecture_var.set(True)

    def set_lab(self):
        """Ensure only Lab is selected."""
        self.lecture_var.set(False)
        self.lab_var.set(True)

    def submit_form(self):
        """Handle submission of new or edited room."""
        room_code = self.room_code_entry.get()
        lecture_selected = self.lecture_var.get()
        lab_selected = self.lab_var.get()

        room_type = ""
        if lecture_selected:
            room_type = "Lecture"
        elif lab_selected:
            room_type = "Lab"

        if room_code and room_type:
            if self.submit_button['text'] == "Submit":
                # Insert new room
                database.insert_room(room_code, room_type)
                self.feedback_label.config(text=f"Room '{room_code}' added successfully!", fg="green")
            else:
                # Update existing room
                database.update_room_db(self.editing_room_id, room_code, room_type)
                self.feedback_label.config(text=f"Room '{room_code}' updated successfully!", fg="green")
                self.submit_button.config(text="Submit")
                self.editing_room_id = None
            self.clear_form()
            self.refresh_rooms_list()
        else:
            self.feedback_label.config(text="Please fill in all fields.", fg="red")

    def refresh_rooms_list(self):
        """Refresh the list of rooms displayed."""
        self.rooms_listbox.delete(0, 'end')
        rooms = database.fetch_rooms()
        for room in rooms:
            self.rooms_listbox.insert('end', (room[0], f"{room[1]} - {room[2]}"))

    def edit_room(self):
        """Populate the form fields with the selected room's data for editing."""
        selected_room_index = self.rooms_listbox.curselection()
        if selected_room_index:
            selected_room = self.rooms_listbox.get(selected_room_index)
            room_id = selected_room[0]

            cursor = database.cursor
            cursor.execute('SELECT * FROM Rooms WHERE id = ?', (room_id,))
            room = cursor.fetchone()

            if room:
                self.room_code_entry.delete(0, 'end')
                self.room_code_entry.insert(0, room[1])

                if room[2] == "Lecture":
                    self.lecture_var.set(True)
                    self.lab_var.set(False)
                elif room[2] == "Lab":
                    self.lecture_var.set(False)
                    self.lab_var.set(True)

                self.submit_button.config(text="Update Room")
                self.editing_room_id = room_id
            else:
                self.feedback_label.config(text="Error: Room not found.", fg="red")

    def delete_room(self):
        """Delete the selected room from the database."""
        selected_room_index = self.rooms_listbox.curselection()
        if selected_room_index:
            selected_room = self.rooms_listbox.get(selected_room_index)
            room_id = selected_room[0]

            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the room '{room_id}'?")
            if confirm:
                database.delete_room_db(room_id)
                self.feedback_label.config(text=f"Room '{room_id}' deleted successfully!", fg="green")
                self.refresh_rooms_list()
            else:
                self.feedback_label.config(text="Deletion canceled.", fg="orange")

    def clear_form(self):
        """Clear the form fields."""
        self.room_code_entry.delete(0, 'end')
        self.lecture_var.set(False)
        self.lab_var.set(False)
        self.feedback_label.config(text="")
