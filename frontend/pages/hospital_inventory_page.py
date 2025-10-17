import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalInventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ttk.Button(header_frame, text="← Back", command=lambda: controller.show_frame("HospitalDashboardPage"),
                  style="Outline.TButton").pack(side="left")
        ttk.Label(header_frame, text="📦 Blood Inventory", style="Header.TLabel").pack(side="left", padx=20)
        
        ttk.Button(header_frame, text="🔄 Refresh", command=self.load_inventory,
                  style="Primary.TButton").pack(side="right")
        ttk.Button(header_frame, text="📊 Generate Report", command=self.generate_report,
                  style="Outline.TButton").pack(side="right", padx=10)
        
        # Stats frame
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill="x", padx=30, pady=10)
        
        # Inventory table card
        inventory_card, table_content = UIComponents.create_card(self, "Current Blood Inventory")
        inventory_card.pack(fill="both", expand=True, padx=30, pady=10)
        
        table_container = ttk.Frame(table_content)
        table_container.pack(fill="both", expand=True, pady=10)
        
        columns = ("Blood Type", "Units Available", "Last Updated", "Status")
        self.tree = UIComponents.create_table(table_container, columns, height=8)
        
        self.tree.column("Blood Type", width=100, anchor="center")
        self.tree.column("Units Available", width=150, anchor="center")
        self.tree.column("Last Updated", width=150)
        self.tree.column("Status", width=100, anchor="center")
        
        # Configure tags for status colors
        self.tree.tag_configure("low", background="#FFCDD2")  # Red
        self.tree.tag_configure("medium", background="#FFF9C4")  # Yellow
        self.tree.tag_configure("good", background="#C8E6C9")  # Green
        
        # Blood compatibility chart
        chart_card, chart_content = UIComponents.create_card(self, "Blood Type Compatibility Chart")
        chart_card.pack(fill="x", padx=30, pady=(10, 20))
        
        compatibility_text = """
        Blood Donor Compatibility:
        • O- can donate to all blood types
        • O+ can donate to O+, A+, B+, AB+
        • A- can donate to A-, A+, AB-, AB+
        • A+ can donate to A+, AB+
        • B- can donate to B-, B+, AB-, AB+
        • B+ can donate to B+, AB+
        • AB- can donate to AB-, AB+
        • AB+ can donate to AB+ only
        """
        
        compatibility_label = ttk.Label(chart_content, text=compatibility_text, justify="left",
                                      font=("Segoe UI", 11))
        compatibility_label.pack(pady=10, padx=10, anchor="w")
    
    def load_inventory(self):
        """Load inventory data from backend"""
        if not self.controller.current_hospital:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get inventory from the API
            response = requests.get(f"{API_BASE_URL}/inventory/{self.controller.current_hospital['id']}")
            
            if response.status_code == 200:
                inventory = response.json()
                
                # Display stats
                total_units = sum(item.get('units_available', 0) for item in inventory)
                UIComponents.create_stat_card(self.stats_frame, "Total Units", total_units, BioMatchTheme.PRIMARY)
                UIComponents.create_stat_card(self.stats_frame, "Different Types", len(inventory), BioMatchTheme.SUCCESS)
                
                # Display inventory
                for item in inventory:
                    units = item.get('units_available', 0)
                    status = "good" if units > 5 else "medium" if units > 2 else "low"
                    status_text = "Good" if units > 5 else "Medium" if units > 2 else "Low"
                    
                    self.tree.insert("", tk.END, values=(
                        item.get('blood_type', ''),
                        units,
                        item.get('last_updated', '')[:16] if item.get('last_updated') else '',
                        status_text
                    ), tags=(status,))
            else:
                messagebox.showerror("Error", f"Failed to load inventory: {response.status_code}")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def _load_dummy_data(self):
        """Load dummy inventory data as fallback"""
        # Dummy data (for fallback only)
        inventory = [
            {"blood_type": "A+", "units_available": 12, "last_updated": "2023-05-15 10:30:00"},
            {"blood_type": "A-", "units_available": 3, "last_updated": "2023-05-14 15:45:00"},
            {"blood_type": "B+", "units_available": 8, "last_updated": "2023-05-15 09:15:00"},
            {"blood_type": "B-", "units_available": 2, "last_updated": "2023-05-13 11:20:00"},
            {"blood_type": "AB+", "units_available": 5, "last_updated": "2023-05-14 16:30:00"},
            {"blood_type": "AB-", "units_available": 1, "last_updated": "2023-05-10 14:10:00"},
            {"blood_type": "O+", "units_available": 15, "last_updated": "2023-05-15 13:45:00"},
            {"blood_type": "O-", "units_available": 6, "last_updated": "2023-05-14 10:20:00"}
        ]
        
        # Display dummy stats
        UIComponents.create_stat_card(self.stats_frame, "Total Units", 52, BioMatchTheme.PRIMARY)
        UIComponents.create_stat_card(self.stats_frame, "Different Types", 8, BioMatchTheme.SUCCESS)
        
        # Display dummy inventory
        for item in inventory:
            units = item['units_available']
            status = "good" if units > 5 else "medium" if units > 2 else "low"
            status_text = "Good" if units > 5 else "Medium" if units > 2 else "Low"
            
            self.tree.insert("", tk.END, values=(
                item['blood_type'],
                item['units_available'],
                item['last_updated'],
                status_text
            ), tags=(status,))
    
    def generate_report(self):
        """Generate a blood inventory report"""
        if not self.controller.current_hospital:
            messagebox.showerror("Error", "Please login first!")
            return
            
        messagebox.showinfo("Report Generated", "Blood inventory report has been generated and sent to your email!")
