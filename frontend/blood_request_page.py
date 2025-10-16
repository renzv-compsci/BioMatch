# frontend/blood_request_page.py
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class BloodRequestPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        # Title
        title = tk.Label(self, text="Request Blood", font=("Arial", 24, "bold"), bg="white")
        title.pack(pady=20)
        
        # Main container
        main_frame = tk.Frame(self, bg="white")
        main_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        # === REQUEST FORM SECTION ===
        form_frame = tk.LabelFrame(main_frame, text="Blood Request Form", 
                                    font=("Arial", 14, "bold"), bg="white", padx=20, pady=20)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Blood Type
        tk.Label(form_frame, text="Blood Type:", font=("Arial", 12), bg="white").grid(row=0, column=0, sticky="w", pady=10)
        self.blood_type_var = tk.StringVar()
        blood_type_combo = ttk.Combobox(form_frame, textvariable=self.blood_type_var, 
                                        values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                        state="readonly", width=25, font=("Arial", 11))
        blood_type_combo.grid(row=0, column=1, sticky="w", pady=10)
        blood_type_combo.current(0)  # Default to A+
        
        # Quantity Needed
        tk.Label(form_frame, text="Quantity Needed:", font=("Arial", 12), bg="white").grid(row=1, column=0, sticky="w", pady=10)
        self.quantity_var = tk.StringVar(value="1")
        quantity_spinbox = tk.Spinbox(form_frame, from_=1, to=100, textvariable=self.quantity_var,
                                       width=24, font=("Arial", 11))
        quantity_spinbox.grid(row=1, column=1, sticky="w", pady=10)
        
        # Priority Level
        tk.Label(form_frame, text="Priority Level:", font=("Arial", 12), bg="white").grid(row=2, column=0, sticky="w", pady=10)
        self.priority_var = tk.StringVar()
        priority_combo = ttk.Combobox(form_frame, textvariable=self.priority_var,
                                      values=["Low", "Medium", "High", "Critical"],
                                      state="readonly", width=25, font=("Arial", 11))
        priority_combo.grid(row=2, column=1, sticky="w", pady=10)
        priority_combo.current(1)  # Default to Medium
        
        # Required Date
        tk.Label(form_frame, text="Required Date:", font=("Arial", 12), bg="white").grid(row=3, column=0, sticky="w", pady=10)
        
        # Date input frame
        date_frame = tk.Frame(form_frame, bg="white")
        date_frame.grid(row=3, column=1, sticky="w", pady=10)
        
        # Year
        current_date = datetime.now()
        self.year_var = tk.StringVar(value=str(current_date.year))
        tk.Label(date_frame, text="Year:", font=("Arial", 10), bg="white").pack(side="left", padx=(0, 5))
        year_spinbox = tk.Spinbox(date_frame, from_=2025, to=2030, textvariable=self.year_var,
                                   width=6, font=("Arial", 10))
        year_spinbox.pack(side="left", padx=(0, 10))
        
        # Month
        self.month_var = tk.StringVar(value=str(current_date.month).zfill(2))
        tk.Label(date_frame, text="Month:", font=("Arial", 10), bg="white").pack(side="left", padx=(0, 5))
        month_spinbox = tk.Spinbox(date_frame, from_=1, to=12, textvariable=self.month_var,
                                    width=4, font=("Arial", 10), format="%02.0f")
        month_spinbox.pack(side="left", padx=(0, 10))
        
        # Day
        self.day_var = tk.StringVar(value=str(current_date.day).zfill(2))
        tk.Label(date_frame, text="Day:", font=("Arial", 10), bg="white").pack(side="left", padx=(0, 5))
        day_spinbox = tk.Spinbox(date_frame, from_=1, to=31, textvariable=self.day_var,
                                 width=4, font=("Arial", 10), format="%02.0f")
        day_spinbox.pack(side="left")
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg="white")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.search_btn = ttk.Button(button_frame, text="Search Available Blood", 
                                      command=self.search_blood, width=25)
        self.search_btn.pack(side="left", padx=10)
        
        ttk.Button(button_frame, text="Clear", command=self.clear_form, width=15).pack(side="left", padx=10)
        
        # Loading label
        self.loading_label = tk.Label(form_frame, text="", font=("Arial", 10, "italic"), 
                                      bg="white", fg="blue")
        self.loading_label.grid(row=5, column=0, columnspan=2)
        
        # === RESULTS SECTION ===
        results_frame = tk.LabelFrame(main_frame, text="Available Blood Units", 
                                       font=("Arial", 14, "bold"), bg="white", padx=20, pady=20)
        results_frame.pack(fill="both", expand=True)
        
        # Results info label
        self.results_info = tk.Label(results_frame, text="Submit a request to see available blood units",
                                     font=("Arial", 11), bg="white", fg="gray")
        self.results_info.pack(pady=10)
        
        # Results table
        table_frame = tk.Frame(results_frame, bg="white")
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(table_frame, orient="vertical")
        scrollbar_y.pack(side="right", fill="y")
        
        scrollbar_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Treeview for results
        columns = ("blood_type", "hospital_name", "units_available")
        self.results_tree = ttk.Treeview(table_frame, columns=columns, show="headings",
                                         yscrollcommand=scrollbar_y.set,
                                         xscrollcommand=scrollbar_x.set,
                                         height=10)
        
        # Configure columns
        self.results_tree.heading("blood_type", text="Blood Type")
        self.results_tree.heading("hospital_name", text="Hospital Name")
        self.results_tree.heading("units_available", text="Units Available")
        
        self.results_tree.column("blood_type", width=120, anchor="center")
        self.results_tree.column("hospital_name", width=350, anchor="w")
        self.results_tree.column("units_available", width=150, anchor="center")
        
        self.results_tree.pack(fill="both", expand=True)
        
        scrollbar_y.config(command=self.results_tree.yview)
        scrollbar_x.config(command=self.results_tree.xview)
        
        # Back button
        ttk.Button(self, text="← Back to Dashboard", 
                   command=lambda: controller.show_frame("DashboardPage")).pack(pady=20)
    
    def clear_form(self):
        """Reset form to default values"""
        self.blood_type_var.set("A+")
        self.quantity_var.set("1")
        self.priority_var.set("Medium")
        current_date = datetime.now()
        self.year_var.set(str(current_date.year))
        self.month_var.set(str(current_date.month).zfill(2))
        self.day_var.set(str(current_date.day).zfill(2))
        self.clear_results()
    
    def clear_results(self):
        """Clear results table"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results_info.config(text="Submit a request to see available blood units", fg="gray")
    
    def validate_form(self):
        """Validate form inputs"""
        # Validate quantity
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                messagebox.showerror("Validation Error", "Quantity must be greater than 0")
                return False
        except ValueError:
            messagebox.showerror("Validation Error", "Quantity must be a number")
            return False
        
        # Validate date
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())
            required_date = datetime(year, month, day)
            
            # Check if date is not in the past
            if required_date.date() < datetime.now().date():
                messagebox.showwarning("Date Warning", 
                                      "Required date is in the past. Are you sure?")
        except ValueError:
            messagebox.showerror("Validation Error", "Invalid date")
            return False
        
        return True
    
    def search_blood(self):
        """Submit blood request to API and display results"""
        if not self.validate_form():
            return
        
        # Show loading state
        self.loading_label.config(text="Searching available blood units...")
        self.search_btn.config(state="disabled")
        self.clear_results()
        self.update()
        
        try:
            # Build request payload
            required_date = f"{self.year_var.get()}-{self.month_var.get().zfill(2)}-{self.day_var.get().zfill(2)}"
            
            payload = {
                "blood_type": self.blood_type_var.get(),
                "quantity_needed": int(self.quantity_var.get()),
                "priority_level": self.priority_var.get(),
                "required_date": required_date
            }
            
            # Call API
            response = requests.post(f"{API_BASE_URL}/api/v1/blood/request", 
                                    json=payload, 
                                    timeout=10)
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                if results:
                    # Populate results table
                    for result in results:
                        self.results_tree.insert("", "end", values=(
                            result.get("blood_type", "N/A"),
                            result.get("hospital_name", "N/A"),
                            result.get("units_available", "N/A")
                        ))
                    
                    # Update info label
                    self.results_info.config(
                        text=f"✓ Found {len(results)} hospital(s) with matching blood units",
                        fg="green"
                    )
                else:
                    self.results_info.config(
                        text=f"✗ No matching blood units found for {self.blood_type_var.get()}",
                        fg="orange"
                    )
            
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("message", "Validation error")
                messagebox.showerror("Request Error", error_msg)
                self.results_info.config(text="Request failed - check your inputs", fg="red")
            
            else:
                messagebox.showerror("Error", f"Unexpected error: {response.status_code}")
                self.results_info.config(text="An error occurred", fg="red")
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", 
                               "Cannot connect to server. Make sure the backend is running.")
            self.results_info.config(text="Connection failed", fg="red")
        
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout Error", "Request timed out. Please try again.")
            self.results_info.config(text="Request timed out", fg="red")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.results_info.config(text="An error occurred", fg="red")
        
        finally:
            # Hide loading state
            self.loading_label.config(text="")
            self.search_btn.config(state="normal")
