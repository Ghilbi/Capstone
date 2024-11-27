import tkinter as tk
from ui import setup_ui
from initialize_db import initialize_db

def main():
    root = tk.Tk()
    root.title("Subject Load Scheduling System")
    initialize_db()
    setup_ui(root)
    root.mainloop()

if __name__ == "__main__":
    main()
