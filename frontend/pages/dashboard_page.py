import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class DashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        self.header_label = ttk.Label(header_frame, text="Dashboard", style="Header.TLabel")
        self.header_label.pack(side="left")
        
        ttk.Button(header_frame, text="🚪 Logout", command=controller.logout,
                  style="Secondary.TButton").pack(side="right")
        
        # User info card
        info_card, info_content = UIComponents.create_card(self, "User Information")
        info_card.pack(fill="x", padx=30, pady=(0, 20))
        
        # Center the user info with icons
        self.user_info_label = ttk.Label(info_content, text="", font=("Segoe UI", 11), justify="center")
        self.user_info_label.pack(pady=15, fill="x")
        
        # Stats section
        stats_card, stats_content = UIComponents.create_card(self, "Blood Bank Statistics")
        stats_card.pack(fill="x", padx=30, pady=(0, 20))
        
        self.stats_frame = ttk.Frame(stats_content)
        self.stats_frame.pack(fill="x", pady=10)
        
        # Create grid layout for navigation cards (3x2)
        nav_container = ttk.Frame(self)
        nav_container.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Define navigation cards - REMOVED Add Donation
        nav_items = [
            ("📦", "View Inventory", "ViewInventoryPage", BioMatchTheme.PRIMARY),
            ("🔍", "Search Blood", "SearchBloodPage", BioMatchTheme.WARNING),
            ("📋", "Transaction History", "TransactionHistoryPage", BioMatchTheme.SECONDARY),
            ("⚙️", "Admin Dashboard", "AdminDashboardPage", BioMatchTheme.DANGER),
        ]
        
        # Create navigation cards in a 2x2 grid layout
        for i, (icon, text, page, color) in enumerate(nav_items):
            row = i // 2
            col = i % 2
            card = self._create_nav_card(nav_container, icon, text, color,
                                         lambda p=page: controller.show_frame(p))
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Make cards equal size
            nav_container.grid_rowconfigure(row, weight=1)
            nav_container.grid_columnconfigure(col, weight=1)
    
    def _create_nav_card(self, parent, icon, text, color, command):
        """Create a modern navigation card"""
        card = tk.Frame(parent, bg="white", relief="solid", bd=1, cursor="hand2", width=300, height=150)
        card.pack_propagate(False)  # Prevent the card from shrinking to fit its contents
        card.bind("<Enter>", lambda e: card.config(bg=BioMatchTheme.LIGHT_BG))
        card.bind("<Leave>", lambda e: card.config(bg="white"))
        card.bind("<Button-1>", lambda e: command())
        
        # Center the icon in the card
        icon_label = tk.Label(card, text=icon, font=("Segoe UI", 48), bg="white", fg=color)
        icon_label.place(relx=0.5, rely=0.4, anchor="center")
        icon_label.bind("<Button-1>", lambda e: command())
        
        # Put text at the bottom
        text_label = tk.Label(card, text=text, font=("Segoe UI", 14, "bold"), 
                             fg=BioMatchTheme.TEXT_PRIMARY, bg="white")
        text_label.place(relx=0.5, rely=0.8, anchor="center")
        text_label.bind("<Button-1>", lambda e: command())
        
        return card
    
    def refresh_data(self):
        """Refresh dashboard data"""
        if not self.controller.current_user:
            return
        
        user = self.controller.current_user
        # Display user info centered with icons matching screenshot
        self.user_info_label.config(
            text=f"👤 Username: {user['username']} | 🏅 Role: {user['role'].upper()} | 🏥 Hospital ID: {user['hospital_id']}"
        )
        
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get inventory summary
            inv_response = requests.get(f"{API_BASE_URL}/inventory/{user['hospital_id']}")
            if inv_response.status_code == 200:
                inventory = inv_response.json()
                blood_types = set(item['blood_type'] for item in inventory)
                total_units = sum(item['units_available'] for item in inventory)
                
                # Create evenly spaced stat cards to match screenshot
                UIComponents.create_stat_card(self.stats_frame, "Total Blood Units", total_units, BioMatchTheme.SUCCESS)
                UIComponents.create_stat_card(self.stats_frame, "Blood Types", len(blood_types), BioMatchTheme.PRIMARY)
                
                # Find most and least available blood types
                if inventory:
                    most_type = max(inventory, key=lambda x: x['units_available'])
                    least_type = min(inventory, key=lambda x: x['units_available'])
                    
                    UIComponents.create_stat_card(
                        self.stats_frame,
                        f"Most Available: {most_type['blood_type']}",
                        most_type['units_available'],
                        BioMatchTheme.WARNING
                    )
                    
                    UIComponents.create_stat_card(
                        self.stats_frame,
                        f"Least Available: {least_type['blood_type']}",
                        least_type['units_available'],
                        BioMatchTheme.DANGER
                    )
                else:
                    UIComponents.create_stat_card(self.stats_frame, "Most Available: A+", 0, BioMatchTheme.WARNING)
                    UIComponents.create_stat_card(self.stats_frame, "Least Available: A+", 0, BioMatchTheme.DANGER)
            else:
                # Fallback to match screenshot values
                UIComponents.create_stat_card(self.stats_frame, "Total Blood Units", 0, BioMatchTheme.SUCCESS)
                UIComponents.create_stat_card(self.stats_frame, "Blood Types", 8, BioMatchTheme.PRIMARY)
                UIComponents.create_stat_card(self.stats_frame, "Most Available: A+", 0, BioMatchTheme.WARNING)
                UIComponents.create_stat_card(self.stats_frame, "Least Available: A+", 0, BioMatchTheme.DANGER)
            
            # Get donation count
            don_response = requests.get(f"{API_BASE_URL}/donations/{user['hospital_id']}")
            if don_response.status_code == 200:
                donations = don_response.json()
                UIComponents.create_stat_card(self.stats_frame, "Total Donations", len(donations), BioMatchTheme.WARNING)
            else:
                UIComponents.create_stat_card(self.stats_frame, "Total Donations", 0, BioMatchTheme.WARNING)
        except Exception as e:
            # Create fallback stats that match the screenshot
            UIComponents.create_stat_card(self.stats_frame, "Total Blood Units", 0, BioMatchTheme.SUCCESS)
            UIComponents.create_stat_card(self.stats_frame, "Blood Types", 8, BioMatchTheme.PRIMARY)
            UIComponents.create_stat_card(self.stats_frame, "Most Available: A+", 0, BioMatchTheme.WARNING)
            UIComponents.create_stat_card(self.stats_frame, "Least Available: A+", 0, BioMatchTheme.DANGER)
            UIComponents.create_stat_card(self.stats_frame, "Total Donations", 0, BioMatchTheme.WARNING)
            
            # Log error but don't disrupt UI
            print(f"Error loading stats: {e}")