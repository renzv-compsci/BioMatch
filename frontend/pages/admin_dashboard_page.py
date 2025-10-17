import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents

API_BASE_URL = "http://127.0.0.1:5000"

class AdminDashboardPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(header_frame, text="Admin Dashboard - Hospital Management", 
                style="Header.TLabel").pack(side="left")
        
        ttk.Button(header_frame, text="Back to Dashboard",
                 command=lambda: controller.show_frame("DashboardPage")).pack(side="right", padx=5)
        
        ttk.Button(header_frame, text="Refresh",
                 command=self.load_hospitals_data).pack(side="right", padx=5)
        
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        table_card, table_content = UIComponents.create_card(main_container, "Registered Hospitals")
        
        columns = ("Hospital ID", "Hospital Name", "Address", "Contact Person", "Phone", "Pending Requests", "Total Donations", "Blood Units")
        self.tree = UIComponents.create_table(table_content, columns, height=15)
        
        self.tree.column("Hospital ID", width=70)
        self.tree.column("Hospital Name", width=120)
        self.tree.column("Address", width=150)
        self.tree.column("Contact Person", width=120)
        self.tree.column("Phone", width=100)
        self.tree.column("Pending Requests", width=100)
        self.tree.column("Total Donations", width=100)
        self.tree.column("Blood Units", width=100)
        
        self.stats_frame = ttk.Frame(main_container)
        self.stats_frame.pack(fill="x", pady=10)
        
        detail_frame = ttk.Frame(main_container)
        detail_frame.pack(fill="x", pady=10)
        
        ttk.Label(detail_frame, text="Hospital Details", 
                style="Subheader.TLabel").pack(anchor="w", pady=(0, 10))
        
        self.detail_text = tk.Text(detail_frame, height=6, width=100, relief="solid", borderwidth=1)
        self.detail_text.pack(fill="both", expand=True)
        self.detail_text.config(state="disabled")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_hospital_select)
    
    def on_hospital_select(self, event):
        """Display details when hospital is selected"""
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0], 'values')
        
        details = f"""
Hospital ID: {values[0]}
Hospital Name: {values[1]}
Address: {values[2]}
Contact Person: {values[3]}
Phone: {values[4]}
Pending Requests: {values[5]}
Total Donations: {values[6]}
Total Blood Units: {values[7]}
        """
        
        self.detail_text.config(state="normal")
        self.detail_text.delete("1.0", tk.END)
        self.detail_text.insert("1.0", details)
        self.detail_text.config(state="disabled")
    
    def load_hospitals_data(self):
        """Load hospitals data with statistics"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            response = requests.get(f"{API_BASE_URL}/hospitals")
            
            if response.status_code == 200:
                hospitals = response.json()
                
                if not hospitals:
                    messagebox.showinfo("No Data", "No hospitals found.")
                    return
                
                total_hospitals = len(hospitals)
                total_pending_requests = 0
                total_donations = 0
                total_blood_units = 0
                
                for hospital in hospitals:
                    hospital_id = hospital.get('id', '')
                    hospital_name = hospital.get('name', '')[:20]
                    address = hospital.get('address', '')[:30]
                    contact_person = hospital.get('contact_person', '')[:15]
                    phone = hospital.get('contact_number', '')
                    
                    try:
                        req_response = requests.get(f"{API_BASE_URL}/requests/{hospital_id}")
                        pending_requests = 0
                        if req_response.status_code == 200:
                            requests_data = req_response.json()
                            pending_requests = len([r for r in requests_data if r.get('status') == 'pending'])
                        
                        don_response = requests.get(f"{API_BASE_URL}/donations/{hospital_id}")
                        donations_count = 0
                        if don_response.status_code == 200:
                            donations_data = don_response.json()
                            donations_count = len(donations_data)
                        
                        inv_response = requests.get(f"{API_BASE_URL}/inventory/{hospital_id}")
                        blood_units = 0
                        if inv_response.status_code == 200:
                            inventory = inv_response.json()
                            blood_units = sum(item.get('units_available', 0) for item in inventory)
                        
                        total_pending_requests += pending_requests
                        total_donations += donations_count
                        total_blood_units += blood_units
                        
                        self.tree.insert("", tk.END, values=(
                            hospital_id,
                            hospital_name,
                            address,
                            contact_person,
                            phone,
                            pending_requests,
                            donations_count,
                            blood_units
                        ))
                    except Exception as e:
                        print(f"Error loading stats for hospital {hospital_id}: {e}")
                        self.tree.insert("", tk.END, values=(
                            hospital_id,
                            hospital_name,
                            address,
                            contact_person,
                            phone,
                            "N/A",
                            "N/A",
                            "N/A"
                        ))
                
                UIComponents.create_stat_card(self.stats_frame, "Total Hospitals", total_hospitals)
                UIComponents.create_stat_card(self.stats_frame, "Pending Requests", total_pending_requests)
                UIComponents.create_stat_card(self.stats_frame, "Total Donations", total_donations)
                UIComponents.create_stat_card(self.stats_frame, "Blood Units Available", total_blood_units)
            
            else:
                messagebox.showerror("Error", "Failed to load hospitals")
        
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
