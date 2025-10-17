import tkinter as tk
from tkinter import messagebox, ttk
import requests
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:5000"

class BloodRequestPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(header_frame, text="Request Blood", 
                style="Header.TLabel").pack(side="left")
        
        ttk.Button(header_frame, text="Back to Dashboard",
                 command=lambda: controller.show_frame("DashboardPage")).pack(side="right", padx=5)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Request form
        form_frame = ttk.Frame(main_container, relief="solid", borderwidth=1)
        form_frame.pack(fill="x", pady=10)
        
        # Title
        ttk.Label(form_frame, text="Blood Request Form", 
                style="Subheader.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
        
        # Form content
        form_content = ttk.Frame(form_frame)
        form_content.pack(fill="x", padx=15, pady=10)
        
        # Blood Type
        ttk.Label(form_content, text="Blood Type:").grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        self.blood_type_combo = ttk.Combobox(form_content, 
                                            values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                            state="readonly", width=20)
        self.blood_type_combo.grid(row=0, column=1, sticky="w", pady=10)
        
        # Units Requested
        ttk.Label(form_content, text="Units Requested:").grid(row=0, column=2, sticky="w", pady=10, padx=(20, 20))
        self.units_entry = ttk.Entry(form_content, width=15)
        self.units_entry.grid(row=0, column=3, sticky="w", pady=10)
        
        # Patient Name
        ttk.Label(form_content, text="Patient Name:").grid(row=1, column=0, sticky="w", pady=10, padx=(0, 20))
        self.patient_name_entry = ttk.Entry(form_content, width=30)
        self.patient_name_entry.grid(row=1, column=1, sticky="w", pady=10)
        
        # Patient ID/Medical Record
        ttk.Label(form_content, text="Patient ID:").grid(row=1, column=2, sticky="w", pady=10, padx=(20, 20))
        self.patient_id_entry = ttk.Entry(form_content, width=20)
        self.patient_id_entry.grid(row=1, column=3, sticky="w", pady=10)
        
        # Requesting Doctor
        ttk.Label(form_content, text="Requesting Doctor:").grid(row=2, column=0, sticky="w", pady=10, padx=(0, 20))
        self.doctor_entry = ttk.Entry(form_content, width=30)
        self.doctor_entry.grid(row=2, column=1, sticky="w", pady=10)
        
        # Priority
        ttk.Label(form_content, text="Priority:").grid(row=2, column=2, sticky="w", pady=10, padx=(20, 20))
        self.priority_combo = ttk.Combobox(form_content, 
                                          values=["Normal", "Urgent", "Emergency"],
                                          state="readonly", width=18)
        self.priority_combo.set("Normal")
        self.priority_combo.grid(row=2, column=3, sticky="w", pady=10)
        
        # Purpose/Reason
        ttk.Label(form_content, text="Purpose:").grid(row=3, column=0, sticky="nw", pady=10, padx=(0, 20))
        self.purpose_text = tk.Text(form_content, height=4, width=40)
        self.purpose_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=10)
        
        # Source Hospital Selection
        ttk.Label(form_content, text="Source Hospital:").grid(row=4, column=0, sticky="w", pady=10, padx=(0, 20))
        self.source_hospital_combo = ttk.Combobox(form_content, state="normal", width=30)
        self.source_hospital_combo.grid(row=4, column=1, sticky="w", pady=10)
        
        ttk.Button(form_content, text="Search Available Hospitals",
                 command=self.search_hospitals).grid(row=4, column=2, columnspan=2, sticky="e", padx=20)
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ttk.Button(button_frame, text="Submit Request", style="Primary.TButton",
                 command=self.submit_request).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Clear Form",
                 command=self.clear_form).pack(side="left", padx=5)
        
        # Request Status
        status_frame = ttk.Frame(main_container, relief="solid", borderwidth=1)
        status_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(status_frame, text="Recent Requests", 
                style="Subheader.TLabel").pack(anchor="w", padx=15, pady=(15, 10))
        
        # Status table container with grid
        table_container = ttk.Frame(status_frame)
        table_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Status table
        columns = ("ID", "Blood Type", "Units", "Status", "Date Requested")
        self.status_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.status_tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.status_tree.xview)
        self.status_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.status_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Refresh button for status (use pack on a separate frame)
        button_container = ttk.Frame(status_frame)
        button_container.pack(padx=15, pady=(0, 10))
        ttk.Button(button_container, text="Refresh Status",
                 command=self.load_recent_requests).pack()
        
        # Store hospital data
        self.hospitals = []
        self.load_recent_requests()
    
    def search_hospitals(self):
        """Search for hospitals with available blood"""
        blood_type = self.blood_type_combo.get()
        units = self.units_entry.get().strip()
        
        if not blood_type or not units:
            messagebox.showerror("Error", "Please select blood type and enter units needed!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/search_blood", json={
                "blood_type": blood_type,
                "units_needed": int(units)
            })
            
            if response.status_code == 200:
                self.hospitals = response.json()
                hospital_names = [f"{h['hospital_name']} - {h['units_available']} units" 
                                for h in self.hospitals]
                self.source_hospital_combo['values'] = hospital_names
                self.source_hospital_combo.config(state="readonly")
                if hospital_names:
                    self.source_hospital_combo.current(0)
                messagebox.showinfo("Success", f"Found {len(self.hospitals)} hospitals with available blood")
            else:
                messagebox.showerror("Error", "Search failed")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of units.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def submit_request(self):
        """Submit blood request"""
        if not self.controller.current_user:
            messagebox.showerror("Error", "Please login first!")
            return
        
        blood_type = self.blood_type_combo.get()
        units = self.units_entry.get().strip()
        patient_name = self.patient_name_entry.get().strip()
        patient_id = self.patient_id_entry.get().strip()
        doctor = self.doctor_entry.get().strip()
        priority = self.priority_combo.get()
        purpose = self.purpose_text.get("1.0", tk.END).strip()
        source_hospital = self.source_hospital_combo.get()
        
        if not all([blood_type, units, patient_name, patient_id, doctor, purpose, source_hospital]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/request_blood", json={
                "blood_type": blood_type,
                "units_requested": int(units),
                "patient_name": patient_name,
                "patient_id": patient_id,
                "requesting_doctor": doctor,
                "priority": priority,
                "purpose": purpose,
                "requesting_hospital_id": self.controller.current_user['hospital_id'],
                "source_hospital": source_hospital
            })
            
            if response.status_code == 201:
                data = response.json()
                messagebox.showinfo("Success", f"Blood request submitted! Request ID: {data.get('request_id', 'N/A')}")
                self.clear_form()
                self.load_recent_requests()
            else:
                messagebox.showerror("Error", response.json().get("message", "Request failed"))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of units.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def load_recent_requests(self):
        """Load recent blood requests"""
        if not self.controller.current_user:
            return
        
        # Clear existing data
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/requests/{self.controller.current_user['hospital_id']}"
            )
            
            if response.status_code == 200:
                requests_data = response.json()
                for request in requests_data[:10]:  # Show last 10 requests
                    date = request.get('created_at', '')
                    if date:
                        try:
                            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                            date = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    self.status_tree.insert("", tk.END, values=(
                        request.get('id', ''),
                        request.get('blood_type', ''),
                        request.get('units_requested', ''),
                        request.get('status', 'pending'),
                        date
                    ))
        except Exception as e:
            print(f"Error loading requests: {e}")
    
    def clear_form(self):
        """Clear all form fields"""
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)
        self.patient_name_entry.delete(0, tk.END)
        self.patient_id_entry.delete(0, tk.END)
        self.doctor_entry.delete(0, tk.END)
        self.priority_combo.set("Normal")
        self.purpose_text.delete("1.0", tk.END)
        self.source_hospital_combo.set("")
