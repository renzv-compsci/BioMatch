import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme
from .base_page import BasePage

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalBloodRequestsPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        
        # Create navigation
        self.refresh_data()
        
        # Main container (uses self.main_content from BasePage)
        container = ttk.Frame(self.main_content)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header within content area
        ttk.Label(container, text="🩸 Blood Requests Management", 
                 font=("Segoe UI", 18, "bold"),
                 foreground=BioMatchTheme.PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # Stats frame
        stats_card, stats_content = UIComponents.create_card(container, "Request Statistics")
        stats_card.pack(fill="x", pady=(0, 10))
        
        self.stats_frame = ttk.Frame(stats_content)
        self.stats_frame.pack(fill="x", pady=5)
        
        # New request form
        request_card, form_content = UIComponents.create_card(container, "New Blood Request")
        request_card.pack(fill="x", pady=(0, 20))
        
        form_frame = ttk.Frame(form_content)
        form_frame.pack(fill="x", pady=15, padx=10)
        
        # Form fields
        ttk.Label(form_frame, text="Blood Type:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
        self.blood_type_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                            state="readonly", width=10)
        self.blood_type_combo.grid(row=0, column=1, padx=10)
        self.blood_type_combo.set("A+")  # Default value
        
        ttk.Label(form_frame, text="Quantity:", font=("Segoe UI", 11)).grid(row=0, column=2, padx=5)
        self.quantity_entry = ttk.Entry(form_frame, width=10)
        self.quantity_entry.grid(row=0, column=3, padx=10)
        
        ttk.Label(form_frame, text="Priority:", font=("Segoe UI", 11)).grid(row=0, column=4, padx=5)
        self.priority_combo = ttk.Combobox(form_frame, values=["Low", "Medium", "High", "Critical"],
                                         state="readonly", width=10)
        self.priority_combo.grid(row=0, column=5, padx=10)
        self.priority_combo.set("Medium")  # Default value
        
        ttk.Button(form_frame, text="Submit Request", command=self.submit_request,
                  style="Primary.TButton").grid(row=0, column=6, padx=20)
        
        # Requests table
        table_card, table_content = UIComponents.create_card(container, "All Blood Requests")
        table_card.pack(fill="both", expand=True)
        
        self.tree = UIComponents.create_table(
            table_content, 
            ("ID", "Blood Type", "Quantity", "Priority", "Status", "Date"), 
            height=10
        )
        
        # Configure columns
        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Blood Type", width=100, anchor="center")
        self.tree.column("Quantity", width=100, anchor="center")
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=150, anchor="center")
        
        # Load initial data
        self.after(100, self.load_requests)
    
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
    
    def load_requests(self):
        """Load blood requests from backend"""
        if not self.controller.current_hospital:
            return
            
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Initialize default values
        blood_requests = []  # RENAMED from 'requests' to avoid conflict with requests module
        stats = {
            'total': 0,
            'pending': 0,
            'approved': 0,
            'rejected': 0
        }
            
        try:
            response = requests.get(
                f"{API_BASE_URL}/hospital/{self.controller.current_hospital['id']}/requests"
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        blood_requests = data.get('requests', [])
                        stats = data.get('stats', stats)  # Use default if not found
                    elif isinstance(data, list):  # Handle case where response is just a list
                        blood_requests = data
                except (ValueError, TypeError) as e:
                    print(f"Error parsing response: {e}")
            else:
                print(f"Server error: {response.status_code}")
                if response.content:
                    print(f"Response content: {response.content}")

            # Compute stats from client data to ensure correct values even if backend doesn't provide them
            computed = {
                'total': len(blood_requests),
                'pending': sum(1 for r in blood_requests if str(r.get('status', '')).lower() == 'pending'),
                'approved': sum(1 for r in blood_requests if str(r.get('status', '')).lower() == 'approved'),
                'rejected': sum(1 for r in blood_requests if str(r.get('status', '')).lower() == 'rejected'),
            }
            # Prefer backend stats if provided and non-zero; otherwise use computed
            def pick(k): 
                v = stats.get(k, 0) if isinstance(stats, dict) else 0
                try:
                    return int(v) if int(v) > 0 else computed[k]
                except Exception:
                    return computed[k]
            final_stats = {
                'total': pick('total'),
                'pending': pick('pending'),
                'approved': pick('approved'),
                'rejected': pick('rejected'),
            }
            
            # Render statistics
            UIComponents.create_stat_card(self.stats_frame, "Total Requests",
                                          final_stats['total'], BioMatchTheme.PRIMARY)
            UIComponents.create_stat_card(self.stats_frame, "Pending",
                                          final_stats['pending'], BioMatchTheme.WARNING)
            UIComponents.create_stat_card(self.stats_frame, "Approved",
                                          final_stats['approved'], BioMatchTheme.SUCCESS)
            UIComponents.create_stat_card(self.stats_frame, "Rejected",
                                          final_stats['rejected'], BioMatchTheme.DANGER)
            
            # Update table with normalized values (quantity/priority fallbacks)
            for req in blood_requests:
                qty = (req.get('quantity_needed') or
                       req.get('units_requested') or
                       req.get('quantity') or 'N/A')
                prio = (req.get('priority_level') or
                        req.get('priority') or 'N/A')
                date_val = req.get('created_at', 'N/A')
                date_val = date_val[:16] if date_val and isinstance(date_val, str) else 'N/A'
                status_val = str(req.get('status', 'N/A')).upper()
                self.tree.insert("", "end", values=(
                    req.get('id', 'N/A'),
                    req.get('blood_type', 'N/A'),
                    qty,
                    prio,
                    status_val,
                    date_val
                ))
                
        except requests.RequestException as e:
            print(f"Network error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # If no data loaded, show empty state
        if not self.tree.get_children():
            self.tree.insert("", "end", values=("No requests found", "", "", "", "", ""))
    
    def submit_request(self):
        """Submit a new blood request"""
        if not self.controller.current_hospital:
            messagebox.showerror("Error", "Please login first!")
            return
            
        blood_type = self.blood_type_combo.get()
        quantity = self.quantity_entry.get().strip()
        priority = self.priority_combo.get()
        
        if not all([blood_type, quantity, priority]):
            messagebox.showerror("Error", "All fields are required!")
            return
            
        try:
            quantity_int = int(quantity)
            if quantity_int <= 0:
                messagebox.showerror("Error", "Quantity must be positive!")
                return
            
            # Use /blood_requests endpoint with correct field names
            response = requests.post(f"{API_BASE_URL}/blood_requests", json={
                "blood_type": blood_type,
                "units_requested": quantity_int,
                "priority": priority,
                "requesting_hospital_id": self.controller.current_hospital['id']
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Blood request submitted successfully!")
                self.clear_form()
                self.load_requests()
            else:
                error_msg = response.json().get('error', 'Failed to submit request') if response.text else 'Unknown error'
                messagebox.showerror("Error", error_msg)
                
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number!")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Connection error: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit request: {e}")
            
    def clear_form(self):
        """Clear the request form"""
        self.blood_type_combo.set("A+")
        self.quantity_entry.delete(0, tk.END)
        self.priority_combo.set("Medium")
