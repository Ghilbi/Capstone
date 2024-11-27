import tkinter as tk
from home_page import show_home_tab
from instructors_page import show_instructor_tab
from rooms_page import show_rooms_tab
from subjects_page import show_subjects_tab

def setup_ui(root):
    """Set up the UI and navigation."""
    navigation_frame = tk.Frame(root)
    navigation_frame.pack(side=tk.TOP, fill=tk.X)

    tk.Button(navigation_frame, text="Home", command=lambda: show_home_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Instructors", command=lambda: show_instructor_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Rooms", command=lambda: show_rooms_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)
    tk.Button(navigation_frame, text="Subjects", command=lambda: show_subjects_tab(main_frame)).pack(side=tk.LEFT, padx=10, pady=5)

    global main_frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
