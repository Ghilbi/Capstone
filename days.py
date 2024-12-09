# days.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import os
import logging

class DaysApp:
    def __init__(self, parent):
        # Frame for the Days tab
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        self.populate_treeview()

    def create_widgets(self):
        # Frame for form
        form_frame = tk.LabelFrame(self.frame, text="Days Details", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        # Days Code
        tk.Label(form_frame, text="Days Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.days_code_entry = tk.Entry(form_frame)
        self.days_code_entry.grid(row=0, column=1, padx=5, pady=5)

        # Description
        tk.Label(form_frame, text="Description:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.description_entry = tk.Entry(form_frame, width=50)
        self.description_entry.grid(row=0, column=3, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)

        self.add_button = tk.Button(button_frame, text="Add Day", command=self.add_day)
        self.add_button.pack(side="left", padx=5)

        self.edit_button = tk.Button(button_frame, text="Edit Day", command=self.edit_day)
        self.edit_button.pack(side="left", padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete Day", command=self.delete_day)
        self.delete_button.pack(side="left", padx=5)

        self.import_button = tk.Button(button_frame, text="Import CSV", command=self.import_csv_days)
        self.import_button.pack(side="left", padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side="left", padx=5)

        # Frame for search
        search_frame = tk.LabelFrame(self.frame, text="Search Days", padx=10, pady=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(search_frame, text="Days Code:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_days_code = tk.Entry(search_frame)
        self.search_days_code.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = tk.Button(search_frame, text="Search", command=self.search_days)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.reset_button = tk.Button(search_frame, text="Reset", command=self.populate_treeview)
        self.reset_button.grid(row=0, column=3, padx=5, pady=5)

        # Treeview for displaying days
        tree_frame = tk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "days_code", "description")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Define headings
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50, anchor="center")
        self.tree.heading("days_code", text="Days Code")
        self.tree.column("days_code", width=150, anchor="center")
        self.tree.heading("description", text="Description")
        self.tree.column("description", width=400)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def add_day(self):
        days_code = self.days_code_entry.get().strip()
        description = self.description_entry.get().strip()

        if not days_code:
            messagebox.showerror("Input Error", "Days Code is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO DaysDatabase (Days_Code, Description)
                VALUES (?, ?)
            """, (days_code, description))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A day with the same Days Code already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Day added successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error adding day: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def edit_day(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No day selected to edit.")
            return

        item = self.tree.item(selected)
        day_id = item['values'][0]

        days_code = self.days_code_entry.get().strip()
        description = self.description_entry.get().strip()

        if not days_code:
            messagebox.showerror("Input Error", "Days Code is required.")
            return

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE OR IGNORE DaysDatabase
                SET Days_Code = ?, Description = ?
                WHERE rowid = ?
            """, (days_code, description, day_id))
            if cursor.rowcount == 0:
                messagebox.showwarning("Duplicate Entry", "A day with the same Days Code already exists.")
            else:
                conn.commit()
                messagebox.showinfo("Success", "Day updated successfully.")
                self.clear_form()
                self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error editing day: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def delete_day(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Selection Error", "No day selected to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected day?")
        if not confirm:
            return

        item = self.tree.item(selected)
        day_id = item['values'][0]

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM DaysDatabase WHERE rowid = ?", (day_id,))
            conn.commit()
            messagebox.showinfo("Success", "Day deleted successfully.")
            self.populate_treeview()
        except Exception as e:
            logging.error(f"Unexpected error deleting day: {e}")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        finally:
            conn.close()

    def import_csv_days(self):
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
            required_headers = {'Days_Code', 'Description'}
            if not required_headers.issubset(reader.fieldnames):
                messagebox.showerror("CSV Error", f"CSV file is missing required headers: {', '.join(required_headers)}")
                return

            for row in reader:
                try:
                    days_code = row['Days_Code'].strip()
                    description = row.get('Description', '').strip()

                    if not days_code:
                        raise ValueError("Days_Code is missing.")

                    # Correct any typos if needed (following the pattern used in Subjects/Rooms)
                    if days_code.upper() == 'INTERNALTIONAL':
                        days_code = 'INTERNATIONAL'
                    if description.upper() == 'INTERNALTIONAL':
                        description = 'INTERNATIONAL'

                    cursor.execute("""
                        INSERT OR IGNORE INTO DaysDatabase (Days_Code, Description)
                        VALUES (?, ?)
                    """, (days_code, description))
                    if cursor.rowcount == 1:
                        imported += 1
                    else:
                        errors += 1
                        logging.error(f"Duplicate day entry skipped: {row}")

                except sqlite3.IntegrityError as ie:
                    logging.error(f"IntegrityError importing day row {row}: {ie}")
                    errors += 1
                except Exception as e:
                    logging.error(f"Error importing day row {row}: {e}")
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
        cursor.execute("SELECT rowid, Days_Code, Description FROM DaysDatabase")
        rows = cursor.fetchall()
        for row in rows:
            self.tree.insert("", "end", values=row)
        conn.close()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected)
        day = item['values']

        self.days_code_entry.delete(0, tk.END)
        self.days_code_entry.insert(0, day[1])

        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, day[2])

    def clear_form(self):
        self.days_code_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.tree.selection_remove(self.tree.selection())

    def search_days(self):
        days_code = self.search_days_code.get().strip()

        query = "SELECT rowid, Days_Code, Description FROM DaysDatabase WHERE 1=1"
        params = []

        if days_code:
            query += " AND Days_Code LIKE ?"
            params.append(f"%{days_code}%")

        conn = sqlite3.connect("subjects.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in rows:
            self.tree.insert("", "end", values=row)
