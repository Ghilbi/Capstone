def clear_frame(frame):
    """Clear all widgets in a frame."""
    for widget in frame.winfo_children():
        widget.destroy()
