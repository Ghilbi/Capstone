import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from home_page import clear_frame

def show_subjects_tab(frame):
    """Display the subject management page."""
    clear_frame(frame)
    tk.Label(frame, text="Manage Subjects", font=("Arial", 16)).pack(pady=10)

    def refresh_subjects():
        """Refresh the subject list."""
        subject_list.delete(*subject_list.get_children())
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, type, duration FROM subjects")
        for row in cursor.fetchall():
            subject_list.insert("", tk.END, values=row)
        conn.close()

    def add_subject():
        """Add a new subject."""
        code = code_entry.get()
        title = title_entry.get()
        subject_type = type_combobox.get()
        duration = 80 if subject_type == "Pure Lecture" else 160
        if not code or not title or not subject_type:
            messagebox.showerror("Error", "All fields are required.")
            return
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO subjects (name, type, duration) VALUES (?, ?, ?)", 
                       (f"{code}: {title}", subject_type, duration))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Subject added successfully!")
        code_entry.delete(0, tk.END)
        title_entry.delete(0, tk.END)
        type_combobox.set("")
        refresh_subjects()

    def delete_subject():
        """Delete the selected subject."""
        selected_item = subject_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a subject to delete.")
            return
        subject_id = subject_list.item(selected_item[0], "values")[0]
        conn = sqlite3.connect("schedule.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE id = ?", (subject_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Subject deleted successfully!")
        refresh_subjects()

    def edit_subject():
        """Edit the selected subject."""
        selected_item = subject_list.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a subject to edit.")
            return

        # Fetch current details of the selected subject
        subject_id, current_name, current_type, current_duration = subject_list.item(selected_item[0], "values")
        code, title = current_name.split(": ", 1)

        def save_changes():
            """Save changes to the subject."""
            new_code = code_entry.get()
            new_title = title_entry.get()
            new_type = type_combobox.get()
            new_duration = 80 if new_type == "Pure Lecture" else 160
            if not new_code or not new_title or not new_type:
                messagebox.showerror("Error", "All fields are required.")
                return
            conn = sqlite3.connect("schedule.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE subjects SET name = ?, type = ?, duration = ? WHERE id = ?",
                (f"{new_code}: {new_title}", new_type, new_duration, subject_id),
            )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Subject updated successfully!")
            edit_window.destroy()
            refresh_subjects()

        # Edit window
        edit_window = tk.Toplevel()
        edit_window.title("Edit Subject")
        tk.Label(edit_window, text="Subject Code:").grid(row=0, column=0, padx=10, pady=5)
        code_entry = tk.Entry(edit_window)
        code_entry.grid(row=0, column=1, padx=10, pady=5)
        code_entry.insert(0, code)

        tk.Label(edit_window, text="Subject Title:").grid(row=1, column=0, padx=10, pady=5)
        title_entry = tk.Entry(edit_window)
        title_entry.grid(row=1, column=1, padx=10, pady=5)
        title_entry.insert(0, title)

        tk.Label(edit_window, text="Subject Type:").grid(row=2, column=0, padx=10, pady=5)
        type_combobox = ttk.Combobox(edit_window, values=["Pure Lecture", "Lecture and Lab"])
        type_combobox.grid(row=2, column=1, padx=10, pady=5)
        type_combobox.set(current_type)

        tk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    # Input form for adding new subjects
    tk.Label(frame, text="Subject Code:").pack(pady=5)
    code_entry = tk.Entry(frame)
    code_entry.pack(pady=5)

    tk.Label(frame, text="Subject Title:").pack(pady=5)
    title_entry = tk.Entry(frame)
    title_entry.pack(pady=5)

    tk.Label(frame, text="Subject Type:").pack(pady=5)
    type_combobox = ttk.Combobox(frame, values=["Pure Lecture", "Lecture and Lab"])
    type_combobox.pack(pady=5)

    tk.Button(frame, text="Add Subject", command=add_subject).pack(pady=10)

    # Treeview for displaying subjects
    columns = ("ID", "Name", "Type", "Duration")
    subject_list = ttk.Treeview(frame, columns=columns, show="headings")
    subject_list.heading("ID", text="ID")
    subject_list.heading("Name", text="Subject")
    subject_list.heading("Type", text="Type")
    subject_list.heading("Duration", text="Duration (mins)")
    subject_list.pack(fill=tk.BOTH, expand=True, pady=10)

    # Buttons for managing subjects
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Delete Subject", command=delete_subject).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Edit Subject", command=edit_subject).pack(side=tk.LEFT, padx=5)

    refresh_subjects()
