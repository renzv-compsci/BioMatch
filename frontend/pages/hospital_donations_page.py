import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalDonationsPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ttk.Button(header_frame, text="← Back", command=lambda: controller.show_frame("HospitalDashboardPage"),
                  style="Outline.TButton").pack(side="left")
        ttk.Label(header_frame, text="💉 Donations Management", style="Header.TLabel").pack(side="left", padx=20)
        
        ttk.Button(header_frame, text="🔄 Refresh", command=self.load_donations,
                  style="Primary.TButton").pack(side="right")
        
        # Stats frame
        self.stats_frame = ttk.Frame(self)
        self.stats_frame.pack(fill="x", padx=30, pady=10)
        
        # Add donation card
        add_card, add_content = UIComponents.create_card(self, "Add New Donation")
        add_card.pack(fill="x", padx=30, pady=(0, 20))
        
        form_frame = ttk.Frame(add_content)
        form_frame.pack(fill="x", pady=10)
        
        ttk.Label(form_frame, text="Donor Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.donor_name_entry = ttk.Entry(form_frame, width=20)
        self.donor_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Blood Type:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.blood_type_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                            state="readonly", width=10)
        self.blood_type_combo.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Units:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.units_entry = ttk.Entry(form_frame, width=10)
        self.units_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Add Donation", command=self.add_donation,
                 style="Primary.TButton").grid(row=0, column=6, padx=20, pady=5)
        
        # Donations table
        history_card, table_content = UIComponents.create_card(self, "Donation History")
        history_card.pack(fill="both", expand=True, padx=30, pady=10)
        
        table_container = ttk.Frame(table_content)
        table_container.pack(fill="both", expand=True, pady=10)
        
        columns = ("ID", "Donor Name", "Blood Type", "Units", "Date")
        self.tree = UIComponents.create_table(table_container, columns, height=10)
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Donor Name", width=200)
        self.tree.column("Blood Type", width=100, anchor="center")
        self.tree.column("Units", width=80, anchor="center")
        self.tree.column("Date", width=150)
    
    def add_donation(self):
        """Add a new donation"""
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
            units_int = int(units)
            if units_int <= 0:
                messagebox.showerror("Error", "Units must be positive!")
                return
            
            # Make actual API call
            response = requests.post(f"{API_BASE_URL}/donations", json={
                "donor_name": donor_name,
                "blood_type": blood_type,
                "units": units_int,
                "hospital_id": self.controller.current_hospital['id']
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Donation added successfully!")
                self.clear_form()
                self.load_donations()  # Refresh the list
            else:
                messagebox.showerror("Error", response.json().get('message', 'Failed to add donation'))
                
        except ValueError:
            messagebox.showerror("Error", "Units must be a number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add donation: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.donor_name_entry.delete(0, tk.END)
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)
    
    def load_donations(self):
        """Load donations from backend"""
        if not self.controller.current_hospital:
            return
        
        self.clear_table()
        self.clear_stats()
        
        try:
            response = requests.get(f"{API_BASE_URL}/donations/{self.controller.current_hospital['id']}")
            
            if response.status_code == 200:
                donations = response.json()
                if not donations:
                    self.show_no_data_message()
                    return
                    
                self.update_stats(donations)
                self.populate_table(donations)
            else:
                error_msg = response.json().get('message', 'Failed to load donations')
                messagebox.showerror("Error", error_msg)
                self.show_no_data_message()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.show_no_data_message()
    
    def clear_table(self):
        """Clear all rows from table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def clear_stats(self):
        """Clear statistics"""
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
    
    def show_no_data_message(self):
        """Show message when no data is available"""
        self.tree.insert("", tk.END, values=("No donations found", "", "", "", ""))
        UIComponents.create_stat_card(self.stats_frame, "Total Donations", 0, BioMatchTheme.PRIMARY)
        UIComponents.create_stat_card(self.stats_frame, "Total Units", 0, BioMatchTheme.SUCCESS)
        UIComponents.create_stat_card(self.stats_frame, "Blood Types", 0, BioMatchTheme.WARNING)
    
    def update_stats(self, donations):
        """Update statistics from donations data"""
        total_donations = len(donations)
        total_units = sum(d.get('units', 0) for d in donations)
        blood_types = set(d.get('blood_type') for d in donations)
        
        UIComponents.create_stat_card(self.stats_frame, "Total Donations", total_donations, BioMatchTheme.PRIMARY)
        UIComponents.create_stat_card(self.stats_frame, "Total Units", total_units, BioMatchTheme.SUCCESS)
        UIComponents.create_stat_card(self.stats_frame, "Blood Types", len(blood_types), BioMatchTheme.WARNING)
    
    def populate_table(self, donations):
        """Populate table with donations data"""
        for donation in donations:
            self.tree.insert("", tk.END, values=(
                donation.get('id', ''),
                donation.get('donor_name', ''),
                donation.get('blood_type', ''),
                donation.get('units', ''),
                donation.get('date', '')[:16] if donation.get('date') else ''
            ))
