"""
Base dialog class with common functionality
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any


class BaseDialog:
    """Base class for all dialog windows with common functionality"""
    
    def __init__(self, parent: tk.Tk, title: str, size: tuple = (400, 300)):
        self.parent = parent
        self.title = title
        self.size = size
        self.window = None
        self.result = None
        
    def create_window(self) -> tk.Toplevel:
        """Create and configure the dialog window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.geometry(f"{self.size[0]}x{self.size[1]}")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        self._center_window()
        return self.window
    
    def _center_window(self):
        """Center the window on screen"""
        if not self.window:
            return
            
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.size[0] // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.size[1] // 2)
        self.window.geometry(f"{self.size[0]}x{self.size[1]}+{x}+{y}")
    
    def create_main_frame(self, padding: str = "20") -> ttk.Frame:
        """Create main frame with padding"""
        main_frame = ttk.Frame(self.window, padding=padding)
        main_frame.pack(fill="both", expand=True)
        return main_frame
    
    def create_title_label(self, frame: ttk.Frame, text: str, font: tuple = ('Arial', 14, 'bold')):
        """Create a title label"""
        title_label = ttk.Label(frame, text=text, font=font)
        title_label.pack(pady=(0, 15))
        return title_label
    
    def create_button_frame(self, frame: ttk.Frame) -> ttk.Frame:
        """Create a button frame at the bottom"""
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=(15, 0))
        return button_frame
    
    def close_dialog(self):
        """Close the dialog window"""
        if self.window:
            self.window.destroy()
    
    def wait_for_result(self) -> Any:
        """Wait for dialog to close and return result"""
        if self.window:
            self.window.wait_window()
        return self.result 