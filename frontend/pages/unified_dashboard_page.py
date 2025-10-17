import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme
from .base_page import BasePage

API_BASE_URL = "http://127.0.0.1:5000"

class UnifiedDashboardPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        
        # Main scrollable container
        canvas = tk.Canvas(self.main_content, bg=BioMatchTheme.LIGHT_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.main_content, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== SECTION 1: STATS CARDS =====
        stats_section = ttk.Frame(scrollable_frame)
        stats_section.pack(fill="x", padx=20, pady=(20, 10))
        
        ttk.Label(
            stats_section,
            text="📊 Dashboard Overview",
            font=("Segoe UI", 16, "bold"),
            foreground=BioMatchTheme.PRIMARY
        ).pack(anchor="w", pady=(0, 15))
        
        self.stats_container = ttk.Frame(stats_section)
        self.stats_container.pack(fill="x")
        
        # ===== SECTION 2: BLOOD INVENTORY + ADD DONATION (COMPACT) =====
        inventory_section = ttk.Frame(scrollable_frame)
        inventory_section.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Main: Blood Inventory (70% width)
        left_panel = ttk.Frame(inventory_section)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(
            left_panel,
            text="🩸 Blood Inventory",
            font=("Segoe UI", 14, "bold"),
            foreground=BioMatchTheme.PRIMARY
        ).pack(anchor="w", pady=(0, 10))
        
        # Inventory table
        inv_frame = ttk.Frame(left_panel)
        inv_frame.pack(fill="both", expand=True)
        
        inv_scroll = ttk.Scrollbar(inv_frame)
        inv_scroll.pack(side="right", fill="y")
        
        self.inventory_tree = ttk.Treeview(
            inv_frame,
            columns=("Blood Type", "Units", "Last Updated"),
            show="headings",
            height=10,
            yscrollcommand=inv_scroll.set
        )
        inv_scroll.config(command=self.inventory_tree.yview)
        
        self.inventory_tree.heading("Blood Type", text="Blood Type")
        self.inventory_tree.heading("Units", text="Units Available")
        self.inventory_tree.heading("Last Updated", text="Last Updated")
        
        self.inventory_tree.column("Blood Type", width=100)
        self.inventory_tree.column("Units", width=120)
        self.inventory_tree.column("Last Updated", width=150)
        
        self.inventory_tree.pack(side="left", fill="both", expand=True)
        
        # Side: Add Donation (30% width - COMPACT)
        right_panel = ttk.Frame(inventory_section, width=250)
        right_panel.pack(side="left", fill="y")
        right_panel.pack_propagate(False)
        
        ttk.Label(
            right_panel,
            text="💉 Quick Donate",
            font=("Segoe UI", 12, "bold"),
            foreground=BioMatchTheme.SUCCESS
        ).pack(anchor="w", pady=(0, 10))
        
        # Compact form (always visible)
        # Donor Name
        ttk.Label(right_panel, text="Donor:", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 2))
        self.donor_name_entry = ttk.Entry(right_panel, font=("Segoe UI", 9))
        self.donor_name_entry.pack(fill="x", pady=(0, 8))
        
        # Blood Type
        ttk.Label(right_panel, text="Type:", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 2))
        self.blood_type_combo = ttk.Combobox(
            right_panel,
            values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            state="readonly",
            font=("Segoe UI", 9),
            width=15
        )
        self.blood_type_combo.pack(fill="x", pady=(0, 8))
        
        # Units
        ttk.Label(right_panel, text="Units:", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 2))
        self.units_entry = ttk.Entry(right_panel, font=("Segoe UI", 9))
        self.units_entry.pack(fill="x", pady=(0, 8))
        
        # Submit button
        tk.Button(
            right_panel,
            text="✓ Add Donation",
            font=("Segoe UI", 9, "bold"),
            bg=BioMatchTheme.SUCCESS,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.add_donation
        ).pack(fill="x", pady=(5, 0), ipady=8)
        
        # Recent Activity (compact)
        ttk.Label(
            right_panel,
            text="Recent:",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(15, 5))
        
        activity_frame = ttk.Frame(right_panel)
        activity_frame.pack(fill="both", expand=True)
        
        activity_scroll = ttk.Scrollbar(activity_frame)
        activity_scroll.pack(side="right", fill="y")
        
        self.activity_text = tk.Text(
            activity_frame,
            height=8,
            font=("Segoe UI", 8),
            wrap="word",
            yscrollcommand=activity_scroll.set,
            state="disabled"
        )
        activity_scroll.config(command=self.activity_text.yview)
        self.activity_text.pack(side="left", fill="both", expand=True)
    
    def refresh_data(self):
        """Refresh ALL dashboard data"""
        if not self.controller.current_user:
            return
        
        user = self.controller.current_user
        hospital = self.controller.current_hospital
        
        # Update header info
        if hospital:
            role_text = user.get('role', 'user').replace('_', ' ').title()
            self.user_info_label.config(text=f"{role_text} | {hospital['name']}")
        
        # Navigation items
        nav_items = [
            ("📊", "Dashboard", "UnifiedDashboardPage", BioMatchTheme.PRIMARY),
            ("🩸", "Request Blood", "BloodRequestPage", BioMatchTheme.DANGER),
            ("📋", "Blood Requests", "HospitalBloodRequestsPage", BioMatchTheme.WARNING),
            ("📜", "Transactions", "TransactionHistoryPage", BioMatchTheme.INFO),
        ]
        
        self.create_nav_buttons(nav_items)
        
        # Load dashboard data only
        self.load_stats()
        self.load_inventory()
        self.load_recent_activity()
    
    def load_stats(self):
        """Load and display statistics"""
        # Clear existing stats
        for widget in self.stats_container.winfo_children():
            widget.destroy()
        
        if not self.controller.current_hospital:
            return
        
        hospital_id = self.controller.current_hospital['id']
        
        try:
            # Get inventory
            inv_response = requests.get(f"{API_BASE_URL}/inventory/{hospital_id}")
            total_units = 0
            low_stock = 0
            
            if inv_response.status_code == 200:
                inventory = inv_response.json()
                total_units = sum(item.get('units_available', 0) for item in inventory)
                low_stock = sum(1 for item in inventory if item.get('units_available', 0) < 5)
            
            # Get requests
            req_response = requests.get(f"{API_BASE_URL}/blood_requests/{hospital_id}")
            pending_requests = 0
            total_requests = 0
            
            if req_response.status_code == 200:
                requests_data = req_response.json()
                total_requests = len(requests_data)
                pending_requests = sum(1 for req in requests_data if req.get('status') == 'pending')
            
            # Get all hospitals count
            hosp_response = requests.get(f"{API_BASE_URL}/hospitals")
            total_hospitals = 0
            
            if hosp_response.status_code == 200:
                hospitals = hosp_response.json()
                total_hospitals = len(hospitals)
            
            # Create stat cards
            UIComponents.create_stat_card(
                self.stats_container, "Total Blood Units", 
                str(total_units), BioMatchTheme.PRIMARY
            ).pack(side="left", padx=10)
            
            UIComponents.create_stat_card(
                self.stats_container, "Low Stock Alerts", 
                str(low_stock), BioMatchTheme.WARNING
            ).pack(side="left", padx=10)
            
            UIComponents.create_stat_card(
                self.stats_container, "Pending Requests", 
                str(pending_requests), BioMatchTheme.DANGER
            ).pack(side="left", padx=10)
            
            UIComponents.create_stat_card(
                self.stats_container, "Total Requests", 
                str(total_requests), BioMatchTheme.INFO
            ).pack(side="left", padx=10)
            
        except Exception as e:
            print(f"Error loading stats: {e}")
    
    def load_inventory(self):
        """Load inventory into table"""
        if not self.controller.current_hospital:
            return
        
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        try:
            response = requests.get(f"{API_BASE_URL}/inventory/{self.controller.current_hospital['id']}")
            
            if response.status_code == 200:
                inventory = response.json()
                for item in inventory:
                    self.inventory_tree.insert("", tk.END, values=(
                        item['blood_type'],
                        item['units_available'],
                        item['last_updated'][:16] if item['last_updated'] else 'N/A'
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {e}")
    
    def load_recent_activity(self):
        """Load recent donations"""
        if not self.controller.current_hospital:
            return
        
        try:
            response = requests.get(f"{API_BASE_URL}/donations/{self.controller.current_hospital['id']}")
            
            if response.status_code == 200:
                donations = response.json()
                
                self.activity_text.config(state="normal")
                self.activity_text.delete("1.0", tk.END)
                
                if donations:
                    for donation in donations[:10]:
                        date_str = donation['date'][:16] if donation['date'] else 'N/A'
                        text = f"💉 {donation['donor_name']} | {donation['blood_type']} | {donation['units']} units | {date_str}\n"
                        self.activity_text.insert(tk.END, text)
                else:
                    self.activity_text.insert(tk.END, "No recent donations")
                
                self.activity_text.config(state="disabled")
        except Exception as e:
            pass
    
    def add_donation(self):
        """Submit donation form"""
        if not self.controller.current_hospital:
            messagebox.showerror("Error", "Please login first!")
            return
        
        donor_name = self.donor_name_entry.get().strip()
        blood_type = self.blood_type_combo.get()
        units = self.units_entry.get().strip()
        
        if not all([donor_name, blood_type, units]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/add_donation", json={
                "donor_name": donor_name,
                "blood_type": blood_type,
                "units": int(units),
                "hospital_id": self.controller.current_hospital['id']
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Donation added successfully!")
                self.clear_donation_form()
                self.refresh_data()
            else:
                messagebox.showerror("Error", response.json().get("message", "Failed to add donation"))
        except ValueError:
            messagebox.showerror("Error", "Units must be a number!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_donation_form(self):
        """Clear donation form fields"""
        self.donor_name_entry.delete(0, tk.END)
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)
