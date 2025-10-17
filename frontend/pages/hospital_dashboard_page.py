import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalDashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        self.header_label = ttk.Label(header_frame, text="🏥 Hospital Portal", style="Header.TLabel")
        self.header_label.pack(side="left")
        
        ttk.Button(header_frame, text="🚪 Logout", command=controller.logout,
                  style="Secondary.TButton").pack(side="right")
        
        # Hospital info card
        info_card, info_content = UIComponents.create_card(self, "Hospital Information")
        info_card.pack(fill="x", padx=30, pady=(0, 20))
        
        self.hospital_info_label = ttk.Label(info_content, text="", font=("Segoe UI", 11))
        self.hospital_info_label.pack(pady=15)
        
        # Stats frame
        stats_card, stats_content = UIComponents.create_card(self, "Statistics")
        stats_card.pack(fill="x", padx=30, pady=(0, 20))
        
        self.stats_frame = ttk.Frame(stats_content)
        self.stats_frame.pack(fill="x", pady=10)
        
        # Navigation cards
        nav_container = ttk.Frame(self)
        nav_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        nav_items = [
            ("📋", "Blood Requests", BioMatchTheme.PRIMARY, self.view_requests),
            ("💉", "Donations", BioMatchTheme.SUCCESS, self.view_donations),
            ("📦", "Inventory", BioMatchTheme.WARNING, self.view_inventory),
            ("🔐", "Change Password", BioMatchTheme.DANGER, self.change_password),
        ]
        
        for i, (icon, text, color, command) in enumerate(nav_items):
            card = self._create_action_card(nav_container, icon, text, color, command)
            card.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
        
        nav_container.grid_columnconfigure(0, weight=1)
        nav_container.grid_columnconfigure(1, weight=1)
    
    def _create_action_card(self, parent, icon, text, color, command):
        """Create action card"""
        card = tk.Frame(parent, bg="white", relief="solid", bd=1, cursor="hand2")
        card.bind("<Enter>", lambda e: card.config(bg=BioMatchTheme.LIGHT_BG))
        card.bind("<Leave>", lambda e: card.config(bg="white"))
        card.bind("<Button-1>", lambda e: command())
        
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 40), bg="white", fg=color)
        icon_label.pack(pady=25)
        icon_label.bind("<Button-1>", lambda e: command())
        
        text_label = tk.Label(card, text=text, font=("Segoe UI", 13, "bold"), 
                             fg=BioMatchTheme.TEXT_PRIMARY, bg="white")
        text_label.pack(pady=(0, 25))
        text_label.bind("<Button-1>", lambda e: command())
        
        return card
    
    def load_hospital_data(self):
        """Load hospital dashboard data"""
        if not self.controller.current_hospital:
            return
        
        hospital = self.controller.current_hospital
        self.header_label.config(text=f"🏥 Hospital Portal - {hospital['name']}")
        self.hospital_info_label.config(
            text=f"📞 {hospital['contact_number']} | 📍 {hospital['address']}"
        )
        
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get hospital dashboard data from the API
            inventory_response = requests.get(f"{API_BASE_URL}/inventory/{hospital['id']}")
            requests_response = requests.get(f"{API_BASE_URL}/blood_requests/{hospital['id']}")
            donations_response = requests.get(f"{API_BASE_URL}/donations/{hospital['id']}")
            
            blood_units = 0
            if inventory_response.status_code == 200:
                inventory = inventory_response.json()
                blood_units = sum(item.get('units_available', 0) for item in inventory)
            
            pending_requests = 0
            total_requests = 0
            if requests_response.status_code == 200:
                requests_data = requests_response.json()
                pending_requests = sum(1 for r in requests_data if r.get('status') == 'pending')
                total_requests = len(requests_data)
            
            total_donations = 0
            if donations_response.status_code == 200:
                donations = donations_response.json()
                total_donations = len(donations)
            
            UIComponents.create_stat_card(self.stats_frame, "Pending Requests", pending_requests, BioMatchTheme.WARNING)
            UIComponents.create_stat_card(self.stats_frame, "Total Requests", total_requests, BioMatchTheme.PRIMARY)
            UIComponents.create_stat_card(self.stats_frame, "Donations", total_donations, BioMatchTheme.SUCCESS)
            UIComponents.create_stat_card(self.stats_frame, "Blood Units", blood_units, BioMatchTheme.SECONDARY)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def view_requests(self):
        """Navigate to the blood requests page"""
        self.controller.show_frame("HospitalBloodRequestsPage")
    
    def view_donations(self):
        """Navigate to the donations page"""
        self.controller.show_frame("HospitalDonationsPage")
    
    def view_inventory(self):
        """Navigate to the inventory page"""
        self.controller.show_frame("HospitalInventoryPage")
    
    def change_password(self):
        """Navigate to the password change page"""
        self.controller.show_frame("HospitalChangePasswordPage")
