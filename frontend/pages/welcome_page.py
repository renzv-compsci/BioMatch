import tkinter as tk
from tkinter import ttk

class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Title
        ttk.Label(self, text="Welcome to BioMatch", style="Header.TLabel").pack(pady=50)
        ttk.Label(self, text="Blood Bank Management System").pack(pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=50)
        
        ttk.Button(button_frame, text="Register New Hospital", width=25,
                   command=lambda: controller.show_frame("RegisterHospitalPage")).pack(pady=10)
        ttk.Button(button_frame, text="Register User Account", width=25,
                   command=lambda: controller.show_frame("RegisterUserPage")).pack(pady=10)
        ttk.Button(button_frame, text="Login", width=25,
                   command=lambda: controller.show_frame("LoginPage")).pack(pady=10)
        ttk.Button(button_frame, text="Hospital Portal Login", width=25,
                   command=lambda: controller.show_frame("HospitalLoginPage")).pack(pady=10)
