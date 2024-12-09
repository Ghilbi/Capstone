# rooms.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import logging

class RoomsApp:
    def __init__(self, parent):
        # Frame for the Rooms tab
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        # Frame for form
        form_frame = tk.LabelFrame(self.frame, text="Room Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        # Room Code
        tk.Label(form_frame, text="Room Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.room_code_entry = tk.Entry(form_frame)
        self.room_code_entry.grid(row=0, column=1, padx=5, pady=5)

        # Lec
        tk.Label(form_frame, text="Lec:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.lec_entry = tk.Entry(form_frame)
        self.lec_entry.grid(row=0, column=3, padx=5, pady=5)

        # Lab
        tk.Label(form_frame, text="Lab:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.lab_entry = tk.Entry(form_frame)
        self.lab_entry.grid(row=1, column=1, padx=5, pady=5)

        # Pure Lec
        tk.Label(form_frame, text="Pure Lec:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.pure_lec_entry = tk.Entry(form_frame)
        self.pure_lec_entry.grid(row=1, column=3, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)

        self.add_button = tk.Button(button_frame, text="Add Room", command=self.add_room)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(button_frame, text="Edit Room", command=self.edit_room)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Room", command=self.delete_room)
        self.delete_button.pack(side="left", padx=5)

        self.import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv_rooms)
        self.import_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Frame for search
        search_frame = tk.LabelFrame(self.frame, text="Search Rooms", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Room Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_room_code = tk.Entry(search_frame)
        self.search_room_code.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_rooms)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.reset_button = tk.Button(search_frame, text="Reset", command=self.populate_treeview)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5)

        # Treeview for displaying rooms
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "room_code", "lec", "lab", "pure_lec")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("room_code", text="Room Code")
        self.tree.column("room_code", width=150, anchor="center")
        self.tree.heading("lec", text="Lec")
        self.tree.column("lec", width=100, anchor="center")
        self.tree.heading("lab", text="Lab")
        self.tree.column("lab", width=100, anchor="center")
        self.tree.heading("pure_lec", text="Pure Lec")
        self.tree.column("pure_lec", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def add_room(self):
        room_code = self.room_code_entry.get().strip()
        lec = self.lec_entry.get().strip()
        lab = self.lab_entry.get().strip()
        pure_lec = self.pure_lec_entry.get().strip()

        if not room_code:
            messagebox.showerror("Input Error", "Room Code is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO RoomsDatabase (RoomCode, IsLecture, IsLab, IsPureLecture)
                VALUES (?, ?, ?, ?)
            """, (room_code, lec, lab, pure_lec))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A room with the same Room Code already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Room added successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error adding room: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def edit_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No room selected to edit.")
            return

        item = self.tree.item(selected)
        room_id = item['values'][0]

        room_code = self.room_code_entry.get().strip()
        lec = self.lec_entry.get().strip()
        lab = self.lab_entry.get().strip()
        pure_lec = self.pure_lec_entry.get().strip()

        if not room_code:
            messagebox.showerror("Input Error", "Room Code is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE OR IGNORE RoomsDatabase
                SET RoomCode = ?, IsLecture = ?, IsLab = ?, IsPureLecture = ?
                WHERE rowid = ?
            """, (room_code, lec, lab, pure_lec, room_id))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A room with the same Room Code already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Room updated successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error editing room: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def delete_room(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No room selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected room?")
        if not confirm:
            return

        item = self.tree.item(selected)
        room_id = item['values'][0]

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM RoomsDatabase WHERE rowid = ?", (room_id,))
            conn.commit()
            messagebox.showinfo("Success", "Room deleted successfully.")
            self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error deleting room: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def import_csv_rooms(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if not file_path:
            return

        if not os.path.isfile(file_path):
            messagebox.showerror("File Error", "Selected file does not exist.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        imported = 0
        errors = 0

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_headers = {'Room_Code', 'Lec', 'Lab', 'Pure_Lec'}
            if not required_headers.issubset(reader.fieldnames):
                messagebox.showerror("CSV Error", f"CSV file is missing required headers: {', '.join(required_headers)}")
                return

            for row in reader:
                try:
                    room_code = row['Room_Code'].strip()
                    lec = row.get('Lec', '').strip()
                    lab = row.get('Lab', '').strip()
                    pure_lec = row.get('Pure_Lec', '').strip()

                    if not room_code:
                        raise ValueError("Room_Code is missing.")

                    # Correct any typos if needed (following the pattern used in Subjects/Rooms)
                    if room_code.upper() == 'INTERNALTIONAL':
                        room_code = 'INTERNATIONAL'
                    if lec.upper() == 'INTERNALTIONAL':
                        lec = 'INTERNATIONAL'
                    if lab.upper() == 'INTERNALTIONAL':
                        lab = 'INTERNATIONAL'
                    if pure_lec.upper() == 'INTERNALTIONAL':
                        pure_lec = 'INTERNATIONAL'

                    cursor.execute("""
                        INSERT OR IGNORE INTO RoomsDatabase (RoomCode, IsLecture, IsLab, IsPureLecture)
                        VALUES (?, ?, ?, ?)
                    """, (room_code, lec, lab, pure_lec))
                    if cursor.rowcount == 1:
                        imported += 1
                    else:
                        errors += 1
                        logging.error(f"Duplicate room entry skipped: {row}")

                except sqlite3.IntegrityError as ie:
                    logging.error(f"IntegrityError importing room row {row}: {ie}")
                    errors += 1
                except Exception as e:
                    logging.error(f"Error importing room row {row}: {e}")
                    errors += 1

        conn.commit()
        conn.close()
        messagebox.showinfo("Import Completed", f"Imported: {imported}\nDuplicates/Errors: {errors}")
        self.populate_treeview()

    def populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        cursor.execute("SELECT rowid, RoomCode, IsLecture, IsLab, IsPureLecture FROM RoomsDatabase")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected)
        room = item['values']

        self.room_code_entry.delete(0, tk.END)
        self.room_code_entry.insert(0, room[1])

        self.lec_entry.delete(0, tk.END)
        self.lec_entry.insert(0, room[2])

        self.lab_entry.delete(0, tk.END)
        self.lab_entry.insert(0, room[3])

        self.pure_lec_entry.delete(0, tk.END)
        self.pure_lec_entry.insert(0, room[4])

    def clear_form(self):
        self.room_code_entry.delete(0, tk.END)
        self.lec_entry.delete(0, tk.END)
        self.lab_entry.delete(0, tk.END)
        self.pure_lec_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def search_rooms(self):
        room_code = self.search_room_code.get().strip()

        query = "SELECT rowid, RoomCode, IsLecture, IsLab, IsPureLecture FROM RoomsDatabase WHERE 1=1"
        params = []

        if room_code:
            query += " AND RoomCode LIKE ?"
            params.append(f"%{room_code}%")

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=row)
