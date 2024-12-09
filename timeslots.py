# timeslots.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import logging

class TimeslotApp:
    def __init__(self, parent):
        # Frame for the Timeslots tab
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        # Frame for form
        form_frame = tk.LabelFrame(self.frame, text="Timeslot Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        # Timeslot
        tk.Label(form_frame, text="Timeslot:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.timeslot_entry = tk.Entry(form_frame, width=50)
        self.timeslot_entry.grid(row=0, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Add Timeslot", command=self.add_timeslot)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(button_frame, text="Edit Timeslot", command=self.edit_timeslot)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Timeslot", command=self.delete_timeslot)
        self.delete_button.pack(side="left", padx=5)

        self.import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv_timeslots)
        self.import_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Frame for search
        search_frame = tk.LabelFrame(self.frame, text="Search Timeslots", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Timeslot:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_timeslot = tk.Entry(search_frame)
        self.search_timeslot.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_timeslots)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.reset_button = tk.Button(search_frame, text="Reset", command=self.populate_treeview)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5)

        # Treeview for displaying timeslots
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "timeslot")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("timeslot", text="Timeslot")
        self.tree.column("timeslot", width=400)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def add_timeslot(self):
        timeslot = self.timeslot_entry.get().strip()

        if not timeslot:
            messagebox.showerror("Input Error", "Timeslot is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO TimeslotsDatabase (Timeslot)
                VALUES (?)
            """, (timeslot,))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A timeslot with the same identifier already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Timeslot added successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error adding timeslot: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def edit_timeslot(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No timeslot selected to edit.")
            return

        item = self.tree.item(selected)
        timeslot_id = item['values'][0]

        timeslot = self.timeslot_entry.get().strip()

        if not timeslot:
            messagebox.showerror("Input Error", "Timeslot is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE OR IGNORE TimeslotsDatabase
                SET Timeslot = ?
                WHERE rowid = ?
            """, (timeslot, timeslot_id))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A timeslot with the same identifier already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Timeslot updated successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error editing timeslot: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def delete_timeslot(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No timeslot selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected timeslot?")
        if not confirm:
            return

        item = self.tree.item(selected)
        timeslot_id = item['values'][0]

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM TimeslotsDatabase WHERE rowid = ?", (timeslot_id,))
            conn.commit()
            messagebox.showinfo("Success", "Timeslot deleted successfully.")
            self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error deleting timeslot: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def import_csv_timeslots(self):
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
            required_headers = {'Timeslot'}
            if not required_headers.issubset(reader.fieldnames):
                messagebox.showerror("CSV Error", f"CSV file is missing required headers: {', '.join(required_headers)}")
                return

            for row in reader:
                try:
                    timeslot = row['Timeslot'].strip()

                    if not timeslot:
                        raise ValueError("Timeslot is missing.")

                    # Correct any typos if needed (following the pattern used in Subjects/Rooms)
                    if timeslot.upper() == 'INTERNALTIONAL':
                        timeslot = 'INTERNATIONAL'

                    cursor.execute("""
                        INSERT OR IGNORE INTO TimeslotsDatabase (Timeslot)
                        VALUES (?)
                    """, (timeslot,))
                    if cursor.rowcount == 1:
                        imported += 1
                    else:
                        errors += 1
                        logging.error(f"Duplicate timeslot entry skipped: {row}")

                except sqlite3.IntegrityError as ie:
                    logging.error(f"IntegrityError importing timeslot row {row}: {ie}")
                    errors += 1
                except Exception as e:
                    logging.error(f"Error importing timeslot row {row}: {e}")
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
        cursor.execute("SELECT rowid, Timeslot FROM TimeslotsDatabase")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected)
        timeslot = item['values']

        self.timeslot_entry.delete(0, tk.END)
        self.timeslot_entry.insert(0, timeslot[1])

    def clear_form(self):
        self.timeslot_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def search_timeslots(self):
        timeslot = self.search_timeslot.get().strip()

        query = "SELECT rowid, Timeslot FROM TimeslotsDatabase WHERE 1=1"
        params = []

        if timeslot:
            query += " AND Timeslot LIKE ?"
            params.append(f"%{timeslot}%")

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=row)
