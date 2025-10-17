import tkinter as tk
from tkinter import messagebox, ttk
import requests
from datetime import datetime
from frontend.pages.base_page import BasePage
from frontend.theme import BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class BloodRequestPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        
        # Create navigation
        self.refresh_data()
        
        # Main container with padding
        container = ttk.Frame(self.main_content)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Request form
        form_frame = ttk.Frame(container, relief="solid", borderwidth=1)
        form_frame.pack(fill="x", pady=10)
        
        # Title
        ttk.Label(form_frame, text="Blood Request Form", 
                font=("Segoe UI", 14, "bold"),
                foreground=BioMatchTheme.PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))
        
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
                                          values=["Low", "Medium", "High", "Critical"],
                                          state="readonly", width=18)
        self.priority_combo.set("Medium")
        self.priority_combo.grid(row=2, column=3, sticky="w", pady=10)
        
        # Purpose/Reason
        ttk.Label(form_content, text="Purpose:").grid(row=3, column=0, sticky="nw", pady=10, padx=(0, 20))
        self.purpose_text = tk.Text(form_content, height=4, width=40)
        self.purpose_text.grid(row=3, column=1, columnspan=3, sticky="ew", pady=10)
        
        # Required Date
        ttk.Label(form_content, text="Required Date:").grid(row=4, column=0, sticky="w", pady=10, padx=(0, 20))
        self.required_date_entry = ttk.Entry(form_content, width=20)
        self.required_date_entry.insert(0, "YYYY-MM-DD")
        self.required_date_entry.grid(row=4, column=1, sticky="w", pady=10)
        
        # Source Hospital Selection
        ttk.Label(form_content, text="Source Hospital:").grid(row=4, column=2, sticky="w", pady=10, padx=(20, 20))
        self.source_hospital_combo = ttk.Combobox(form_content, state="normal", width=20)
        self.source_hospital_combo.grid(row=4, column=3, sticky="w", pady=10)
        
        ttk.Button(form_content, text="Search Available Hospitals",
                 command=self.search_hospitals).grid(row=5, column=0, columnspan=4, sticky="w", pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ttk.Button(button_frame, text="Submit Request", style="Primary.TButton",
                 command=self.submit_request).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Clear Form",
                 command=self.clear_form).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="🔄 Refresh Data", style="Secondary.TButton",
                 command=self.refresh_page_data).pack(side="left", padx=5)
        
        # Request Status
        status_frame = ttk.Frame(container, relief="solid", borderwidth=1)
        status_frame.pack(fill="both", expand=True, pady=10)
        
        ttk.Label(status_frame, text="Recent Requests", 
                font=("Segoe UI", 14, "bold"),
                foreground=BioMatchTheme.PRIMARY).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Status table container with grid
        table_container = ttk.Frame(status_frame)
        table_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Status table
        columns = ("ID", "Requesting Hospital", "Blood Type", "Units", "Priority", "Status", "Date Requested")
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
    
    def refresh_data(self):
        """Refresh navigation"""
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
        required_date = self.required_date_entry.get().strip()
        
        # Validate required fields
        if not all([blood_type, units, patient_name, patient_id, doctor, priority, required_date]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if required_date == "YYYY-MM-DD":
            messagebox.showerror("Error", "Please enter a valid date in YYYY-MM-DD format!")
            return
        
        try:
            # Get hospital_id - try both current_user and current_hospital
            hospital_id = self.controller.current_user.get('hospital_id')
            if not hospital_id and self.controller.current_hospital:
                hospital_id = self.controller.current_hospital.get('id')
            
            if not hospital_id:
                messagebox.showerror("Error", "Hospital information not found!")
                return
            
            # Use /blood_requests endpoint instead of /request_blood for consistency
            response = requests.post(f"{API_BASE_URL}/blood_requests", json={
                "blood_type": blood_type,
                "units_requested": int(units),
                "priority": priority,
                "requesting_hospital_id": hospital_id,
                "patient_name": patient_name,
                "patient_id": patient_id,
                "requesting_doctor": doctor,
                "purpose": purpose
            })
            
            print(f"Request response: {response.status_code}")
            print(f"Request data sent with hospital_id: {hospital_id}")
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Blood request submitted successfully!")
                self.clear_form()
                # Force refresh after successful submission
                self.after(500, self.load_recent_requests)  # Delay to ensure backend processing
            else:
                error_msg = response.json().get('error', 'Failed to submit request') if response.text else "Request failed"
                messagebox.showerror("Error", error_msg)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of units.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")

    def refresh_page_data(self):
        """Refresh page data"""
        self.load_recent_requests()
        # Also refresh transaction history if it exists
        if "TransactionHistoryPage" in self.controller.frames:
            self.controller.frames["TransactionHistoryPage"].load_requests()
        messagebox.showinfo("Success", "Data refreshed!")
    
    def load_recent_requests(self):
        """Load recent blood requests from current hospital only"""
        if not self.controller.current_user:
            return
        
        # Clear existing data
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        try:
            # Get hospital_id - try both current_user and current_hospital
            hospital_id = self.controller.current_user.get('hospital_id')
            if not hospital_id and self.controller.current_hospital:
                hospital_id = self.controller.current_hospital.get('id')
            
            if not hospital_id:
                print("No hospital_id found")
                return
            
            # Fetch blood requests for current hospital only
            response = requests.get(f"{API_BASE_URL}/hospital/{hospital_id}/requests")
            
            print(f"Loading requests for hospital_id: {hospital_id}")
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # Handle both dict and list responses
                requests_data = data.get('requests', []) if isinstance(data, dict) else data
                
                print(f"Found {len(requests_data)} requests for current hospital")
                
                # Show requests from current hospital only
                if isinstance(requests_data, list) and len(requests_data) > 0:
                    for request in requests_data[:20]:  # Show last 20 requests
                        date = request.get('created_at', '')
                        if date:
                            try:
                                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                                date = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        
                        # Use quantity_needed or units_requested with fallback
                        qty = request.get('quantity_needed') or request.get('units_requested', '')
                        
                        # Get hospital name
                        hospital_name = request.get('requesting_hospital_name', f"Hospital {request.get('requesting_hospital_id', '')}")
                        
                        self.status_tree.insert("", tk.END, values=(
                            request.get('id', ''),
                            hospital_name,
                            request.get('blood_type', ''),
                            qty,
                            request.get('priority_level', ''),
                            request.get('status', 'pending').upper(),
                            date
                        ))
                else:
                    self.status_tree.insert("", tk.END, values=("No requests found", "", "", "", "", "", ""))
            else:
                print(f"Error loading requests: {response.status_code}")
                self.status_tree.insert("", tk.END, values=("Error loading requests", "", "", "", "", "", ""))
        except Exception as e:
            print(f"Error loading requests: {e}")
            self.status_tree.insert("", tk.END, values=("Connection error", "", "", "", "", "", ""))
    
    def clear_form(self):
        """Clear all form fields"""
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)
        self.patient_name_entry.delete(0, tk.END)
        self.patient_id_entry.delete(0, tk.END)
        self.doctor_entry.delete(0, tk.END)
        self.priority_combo.set("Medium")
        self.purpose_text.delete("1.0", tk.END)
        self.required_date_entry.delete(0, tk.END)
        self.required_date_entry.insert(0, "YYYY-MM-DD")
        self.source_hospital_combo.set("")
