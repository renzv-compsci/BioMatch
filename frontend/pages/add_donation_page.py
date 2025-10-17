import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class AddDonationPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Label(self, text="Add Blood Donation", style="Header.TLabel").pack(pady=20)
        
        # Form
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Donor Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.donor_name_entry = ttk.Entry(form_frame, width=30)
        self.donor_name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Blood Type:").grid(row=1, column=0, sticky="w", pady=5)
        self.blood_type_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], width=28)
        self.blood_type_combo.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text="Units:").grid(row=2, column=0, sticky="w", pady=5)
        self.units_entry = ttk.Entry(form_frame, width=30)
        self.units_entry.grid(row=2, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Submit Donation", command=self.add_donation).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Refresh Data", command=self.refresh_data, style="Primary.TButton").grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).grid(row=0, column=2, padx=10)
    
    def add_donation(self):
        if not self.controller.current_user:
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
                "hospital_id": self.controller.current_user['hospital_id']
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Donation added successfully!")
                self.clear_form()
                self.refresh_data()
            else:
                messagebox.showerror("Error", response.json().get("message", "Failed to add donation"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            if "DashboardPage" in self.controller.frames:
                self.controller.frames["DashboardPage"].refresh_data()
            if "ViewInventoryPage" in self.controller.frames:
                self.controller.frames["ViewInventoryPage"].load_inventory()
            messagebox.showinfo("Success", "Data refreshed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
    
    def clear_form(self):
        self.donor_name_entry.delete(0, tk.END)
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)
