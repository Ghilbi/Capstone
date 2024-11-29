import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from home_page import clear_frame

def show_instructor_tab(frame):
    """Display the instructor management page."""
    clear_frame(frame)
    tk.Label(frame, text="Manage Instructors", font=("Arial", 16)).pack(pady=10)

    def refresh_instructors():
        """Refresh the instructor list."""
        instructor_list.delete(*instructor_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, specialty, subjects FROM instructors")
        for row in cursor.fetchall():
            instructor_list.insert("", tk.END, values=row)
        conn.close()

    def add_instructor():
        """Add a new instructor."""
        name = name_entry.get()
        specialty = specialty_combobox.get()
        subjects = subjects_entry.get()
        if not name or not specialty or not subjects:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO instructors (name, specialty, subjects) VALUES (?, ?, ?)", 
                       (name, specialty, subjects))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Instructor added successfully!")
        name_entry.delete(0, tk.END)
        specialty_combobox.set("")
        subjects_entry.delete(0, tk.END)
        refresh_instructors()

    def delete_instructor():
        """Delete the selected instructor."""
        selected_item = instructor_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an instructor to delete.")
            return
        instructor_id = instructor_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM instructors WHERE id = ?", (instructor_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Instructor deleted successfully!")
        refresh_instructors()

    def edit_instructor():
        """Edit the selected instructor."""
        selected_item = instructor_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an instructor to edit.")
            return

        # Fetch current details of the selected instructor
        instructor_id, name, specialty, subjects = instructor_list.item(selected_item[0], "values")

        def save_changes():
            """Save changes to the instructor."""
            new_name = name_entry.get()
            new_specialty = specialty_combobox.get()
            new_subjects = subjects_entry.get()
            if not new_name or not new_specialty or not new_subjects:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE instructors SET name = ?, specialty = ?, subjects = ? WHERE id = ?",
                (new_name, new_specialty, new_subjects, instructor_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Instructor updated successfully!")
            edit_window.destroy()
            refresh_instructors()

        # Edit window
        edit_window = tk.Toplevel()
        edit_window.title("Edit Instructor")
        tk.Label(edit_window, text="Name:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.insert(0, name)

        tk.Label(edit_window, text="Specialty:").grid(row=1, column=0, padx=10, pady=5)
        specialty_combobox = ttk.Combobox(edit_window, values=["Network and Security", "Web Technology", "ERP", "Data Analytics"])
        specialty_combobox.grid(row=1, column=1, padx=10, pady=5)
        specialty_combobox.set(specialty)

        tk.Label(edit_window, text="Subjects (comma-separated):").grid(row=2, column=0, padx=10, pady=5)
        subjects_entry = tk.Entry(edit_window)
        subjects_entry.grid(row=2, column=1, padx=10, pady=5)
        subjects_entry.insert(0, subjects)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new instructors
    tk.Label(frame, text="Name:").pack(pady=5)
    name_entry = tk.Entry(frame)
    name_entry.pack(pady=5)

    tk.Label(frame, text="Specialty:").pack(pady=5)
    specialty_combobox = ttk.Combobox(frame, values=["Network and Security", "Web Technology", "ERP", "Data Analytics"])
    specialty_combobox.pack(pady=5)

    tk.Label(frame, text="Subjects (comma-separated):").pack(pady=5)
    subjects_entry = tk.Entry(frame)
    subjects_entry.pack(pady=5)

    tk.Button(frame, text="Add Instructor", command=add_instructor).pack(pady=10)

    # Treeview for displaying instructors
    columns = ("ID", "Name", "Specialty", "Subjects")
    instructor_list = ttk.Treeview(frame, columns=columns, show="headings")
    instructor_list.heading("ID", text="ID")
    instructor_list.heading("Name", text="Name")
    instructor_list.heading("Specialty", text="Specialty")
    instructor_list.heading("Subjects", text="Subjects")
    instructor_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing instructors
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Instructor", command=delete_instructor).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Instructor", command=edit_instructor).pack(side=tk.LEFT, padx=5)

    refresh_instructors()
