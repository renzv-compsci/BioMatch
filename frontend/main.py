# frontend/main_ui.py
import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.theme import UIComponents, BioMatchTheme

# Import all page classes from the pages module
from frontend.pages import (
    WelcomePage,
    RegisterHospitalPage,
    RegisterUserPage,
    LoginPage,
    HospitalLoginPage,
    DashboardPage,
    HospitalDashboardPage,
    AddDonationPage,
    ViewInventoryPage,
    SearchBloodPage,
    TransactionHistoryPage,
    AdminDashboardPage,
    HospitalBloodRequestsPage,
    HospitalDonationsPage,
    HospitalChangePasswordPage,
    HospitalInventoryPage,
    BloodRequestPage,
    UnifiedLoginPage,
    UnifiedDashboardPage
)

API_BASE_URL = "http://127.0.0.1:5000"

class BioMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioMatch - Blood Management System")
        self.root.attributes('-fullscreen', True)
        
        # Apply theme
        BioMatchTheme.apply_theme(root)
        UIComponents.setup_styles()
        
        # Set window background
        self.root.configure(bg=BioMatchTheme.BACKGROUND)
        
        # Store logged-in user data
        self.current_user = None
        self.current_hospital = None
        
        # Container for different pages
        self.container = tk.Frame(root, bg=BioMatchTheme.BACKGROUND)
        self.container.pack(fill="both", expand=True)
        
        # Configure grid layout for container
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to hold frames
        self.frames = {}
        
        # Initialize all pages and place them in the same grid cell
        for PageClass in (WelcomePage, RegisterHospitalPage, RegisterUserPage, 
                          UnifiedLoginPage, UnifiedDashboardPage,
                          AdminDashboardPage, BloodRequestPage,
                          HospitalBloodRequestsPage, HospitalDonationsPage,
                          HospitalChangePasswordPage, HospitalInventoryPage,
                          TransactionHistoryPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show welcome page first
        self.show_frame("WelcomePage")
        
        # Modern exit button
        exit_btn = ttk.Button(root, text="✕ Exit Fullscreen", command=self.exit_fullscreen, style="Outline.TButton")
        exit_btn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=10)
    
    def show_frame(self, page_name):
        """Switch to a specific page"""
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Refresh data for pages that need it
        if hasattr(frame, 'refresh_data') and self.current_user:
            frame.refresh_data()
        
        # Legacy support for old pages
        if page_name == "ViewInventoryPage" and self.current_user:
            if hasattr(self.frames["ViewInventoryPage"], 'load_inventory'):
                self.frames["ViewInventoryPage"].load_inventory()
        elif page_name == "AdminDashboardPage" and self.current_user:
            if hasattr(self.frames["AdminDashboardPage"], 'load_hospitals_data'):
                self.frames["AdminDashboardPage"].load_hospitals_data()
        elif page_name == "HospitalDashboardPage" and self.current_hospital:
            if hasattr(self.frames["HospitalDashboardPage"], 'load_hospital_data'):
                self.frames["HospitalDashboardPage"].load_hospital_data()
        elif page_name == "HospitalBloodRequestsPage" and self.current_hospital:
            if hasattr(self.frames["HospitalBloodRequestsPage"], 'load_requests'):
                self.frames["HospitalBloodRequestsPage"].load_requests()
    
    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)
    
    def set_current_user(self, user_data):
        """Store logged-in user information"""
        self.current_user = user_data
    
    def set_current_hospital(self, hospital_data):
        """Store logged-in hospital information"""
        self.current_hospital = hospital_data
    
    def logout(self):
        """Logout and return to welcome page"""
        self.current_user = None
        self.current_hospital = None
        self.show_frame("WelcomePage")


# =============================================
# MAIN APPLICATION
# =============================================
if __name__ == "__main__":
    root = tk.Tk()
    app = BioMatchApp(root)
    root.mainloop()
