import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from utils import clear_frame

def show_rooms_tab(frame):
    """Display the room management page."""
    clear_frame(frame)
    tk.Label(frame, text="Manage Rooms", font=("Arial", 16)).pack(pady=10)

    def refresh_rooms():
        """Refresh the room list."""
        room_list.delete(*room_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, subjects FROM rooms")
        for row in cursor.fetchall():
            room_list.insert("", tk.END, values=row)
        conn.close()

    def add_room():
        """Add a new room."""
        name = name_entry.get()
        room_type = type_combobox.get()
        subjects = subjects_entry.get()
        if not name or not room_type or not subjects:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO rooms (name, type, subjects) VALUES (?, ?, ?)", 
                       (name, room_type, subjects))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room added successfully!")
        name_entry.delete(0, tk.END)
        type_combobox.set("")
        subjects_entry.delete(0, tk.END)
        refresh_rooms()

    def delete_room():
        """Delete the selected room."""
        selected_item = room_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a room to delete.")
            return
        room_id = room_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Room deleted successfully!")
        refresh_rooms()

    def edit_room():
        """Edit the selected room."""
        selected_item = room_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a room to edit.")
            return

        # Fetch current details of the selected room
        room_id, name, room_type, subjects = room_list.item(selected_item[0], "values")

        def save_changes():
            """Save changes to the room."""
            new_name = name_entry.get()
            new_type = type_combobox.get()
            new_subjects = subjects_entry.get()
            if not new_name or not new_type or not new_subjects:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE rooms SET name = ?, type = ?, subjects = ? WHERE id = ?",
                (new_name, new_type, new_subjects, room_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Room updated successfully!")
            edit_window.destroy()
            refresh_rooms()

        # Edit window
        edit_window = tk.Toplevel()
        edit_window.title("Edit Room")
        tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, name)

        tk.Label(edit_window, text="Type:").grid(row=1, column=0, padx=10, pady=5)
        type_combobox = ttk.Combobox(edit_window, values=["Lecture", "Lecture and Lab"])
        type_combobox.grid(row=1, column=1, padx=10, pady=5)
        type_combobox.set(room_type)

        tk.Label(edit_window, text="Subjects (comma-separated):").grid(row=2, column=0, padx=10, pady=5)
        subjects_entry = tk.Entry(edit_window)
        subjects_entry.grid(row=2, column=1, padx=10, pady=5)
        subjects_entry.insert(0, subjects)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new rooms
    tk.Label(frame, text="Name:").pack(pady=5)
    name_entry = tk.Entry(frame)
    name_entry.pack(pady=5)

    tk.Label(frame, text="Type:").pack(pady=5)
    type_combobox = ttk.Combobox(frame, values=["Lecture", "Lecture and Lab"])
    type_combobox.pack(pady=5)

    tk.Label(frame, text="Subjects (comma-separated):").pack(pady=5)
    subjects_entry = tk.Entry(frame)
    subjects_entry.pack(pady=5)

    tk.Button(frame, text="Add Room", command=add_room).pack(pady=10)

    # Treeview for displaying rooms
    columns = ("ID", "Name", "Type", "Subjects")
    room_list = ttk.Treeview(frame, columns=columns, show="headings")
    room_list.heading("ID", text="ID")
    room_list.heading("Name", text="Name")
    room_list.heading("Type", text="Type")
    room_list.heading("Subjects", text="Subjects")
    room_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing rooms
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Room", command=delete_room).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Room", command=edit_room).pack(side=tk.LEFT, padx=5)

    refresh_rooms()
