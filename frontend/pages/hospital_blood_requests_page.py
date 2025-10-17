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
        ttk.Label(container, text="📋 Blood Requests (Received)", 
                 font=("Segoe UI", 18, "bold"),
                 foreground=BioMatchTheme.PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # Filter card
        filter_card, filter_content = UIComponents.create_card(container, "Filter Requests")
        filter_card.pack(fill="x", pady=(0, 20))
        
        filter_frame = ttk.Frame(filter_content)
        filter_frame.pack(fill="x", pady=10)
        
        ttk.Label(filter_frame, text="Status:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "pending", "approved", "rejected"],
                                         state="readonly", width=15)
        self.status_filter.set("pending")
        self.status_filter.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Priority:", font=("Segoe UI", 11)).grid(row=0, column=2, padx=5)
        self.priority_filter = ttk.Combobox(filter_frame, values=["All", "Low", "Medium", "High", "Critical"],
                                           state="readonly", width=15)
        self.priority_filter.set("All")
        self.priority_filter.grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.load_requests,
                  style="Primary.TButton").grid(row=0, column=4, padx=20)
        
        ttk.Button(filter_frame, text="🔄 Refresh Data", command=self.load_requests,
                  style="Secondary.TButton").grid(row=0, column=5, padx=20)
        
        # Stats frame
        self.stats_frame = ttk.Frame(container)
        self.stats_frame.pack(fill="x", pady=10)
        
        # Requests table with action buttons
        table_card, table_content = UIComponents.create_card(container, "Incoming Blood Requests")
        table_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Table container
        table_container = ttk.Frame(table_content)
        table_container.pack(fill="both", expand=True, pady=10)
        
        self.tree = UIComponents.create_table(
            table_container,
            ("ID", "From Hospital", "Blood Type", "Quantity", "Priority", "Status", "Date"),
            height=12
        )
        
        # Configure columns
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("From Hospital", width=200)
        self.tree.column("Blood Type", width=100, anchor="center")
        self.tree.column("Quantity", width=100, anchor="center")
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=150)
        
        # Configure tags for status
        self.tree.tag_configure("pending", background="#FFF9C4")
        self.tree.tag_configure("approved", background="#C8E6C9")
        self.tree.tag_configure("rejected", background="#FFCDD2")
        
        # Bind row selection
        self.tree.bind("<Double-1>", self.on_row_select)
        
        # Action buttons frame
        action_frame = ttk.Frame(table_content)
        action_frame.pack(fill="x", pady=10, padx=10)
        
        ttk.Button(action_frame, text="✓ Approve Selected", command=self.approve_request,
                  style="Primary.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="✕ Reject Selected", command=self.reject_request,
                  style="Secondary.TButton").pack(side="left", padx=5)
        ttk.Button(action_frame, text="📝 Add Notes", command=self.add_notes,
                  style="Outline.TButton").pack(side="left", padx=5)
        
        # Load initial data
        self.selected_request = None
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
        """Load incoming blood requests TO current hospital (for approval/rejection)"""
        if not self.controller.current_hospital:
            # Silently return if no hospital is logged in (page not active yet)
            return
            
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Build query parameters
            params = {}
            
            status_value = self.status_filter.get()
            if status_value != "All":
                params["status"] = status_value
            
            priority_value = self.priority_filter.get()
            if priority_value != "All":
                params["priority"] = priority_value
            
            print(f"Fetching incoming blood requests with params: {params}")
            
            # Get current hospital ID
            hospital_id = None
            if self.controller.current_hospital:
                hospital_id = self.controller.current_hospital.get('id')
            elif self.controller.current_user:
                hospital_id = self.controller.current_user.get('hospital_id')
            
            if not hospital_id:
                # Silently return if no hospital ID (user not logged in)
                return
            
            # Fetch incoming blood requests (TO current hospital) for approval/rejection
            response = requests.get(f"{API_BASE_URL}/hospital/{hospital_id}/incoming_requests", params=params)
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                blood_requests = data.get('requests', []) if isinstance(data, dict) else data
                stats = data.get('stats', {}) if isinstance(data, dict) else {}
                
                print(f"Received {len(blood_requests)} incoming blood requests")
                
                if isinstance(blood_requests, list) and len(blood_requests) > 0:
                    # Display statistics
                    UIComponents.create_stat_card(self.stats_frame, "Total Requests", 
                                               stats.get('total', 0), BioMatchTheme.PRIMARY)
                    UIComponents.create_stat_card(self.stats_frame, "Pending", 
                                               stats.get('pending', 0), BioMatchTheme.WARNING)
                    UIComponents.create_stat_card(self.stats_frame, "Approved", 
                                               stats.get('approved', 0), BioMatchTheme.SUCCESS)
                    UIComponents.create_stat_card(self.stats_frame, "Rejected", 
                                               stats.get('rejected', 0), BioMatchTheme.DANGER)
                    
                    # Populate table with incoming requests
                    for req in blood_requests:
                        status = str(req.get('status', 'pending')).lower()
                        tag = status
                        
                        # Get requesting hospital name
                        hospital_name = req.get('requesting_hospital_name', f"Hospital {req.get('requesting_hospital_id', 'Unknown')}")
                        
                        # Format date
                        date_str = req.get('created_at', '')
                        if date_str:
                            date_str = date_str[:16] if isinstance(date_str, str) else str(date_str)[:16]
                        
                        self.tree.insert("", tk.END, values=(
                            req.get('id', ''),
                            hospital_name,
                            req.get('blood_type', ''),
                            req.get('units_requested', ''),
                            req.get('priority_level', ''),
                            status.upper(),
                            date_str
                        ), tags=(tag,), iid=f"req_{req.get('id', '')}")
                else:
                    # No requests found
                    UIComponents.create_stat_card(self.stats_frame, "Total Requests", 0, BioMatchTheme.PRIMARY)
                    UIComponents.create_stat_card(self.stats_frame, "Pending", 0, BioMatchTheme.WARNING)
                    UIComponents.create_stat_card(self.stats_frame, "Approved", 0, BioMatchTheme.SUCCESS)
                    UIComponents.create_stat_card(self.stats_frame, "Rejected", 0, BioMatchTheme.DANGER)
                    self.tree.insert("", tk.END, values=("No incoming requests found", "", "", "", "", "", ""))
            else:
                error_msg = response.json().get('error', 'Failed to load requests') if response.text else 'No response from server'
                messagebox.showerror("Error", f"Failed to load requests: {error_msg}")
                
                # Show empty state
                UIComponents.create_stat_card(self.stats_frame, "Total Requests", 0, BioMatchTheme.PRIMARY)
                self.tree.insert("", tk.END, values=("Error loading requests", "", "", "", "", "", ""))
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to server. Please ensure the backend is running.")
            UIComponents.create_stat_card(self.stats_frame, "Total Requests", 0, BioMatchTheme.PRIMARY)
            self.tree.insert("", tk.END, values=("Connection failed", "", "", "", "", "", ""))
        except Exception as e:
            print(f"Error loading requests: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error loading requests: {str(e)}")
            UIComponents.create_stat_card(self.stats_frame, "Total Requests", 0, BioMatchTheme.PRIMARY)
            self.tree.insert("", tk.END, values=("Error occurred", "", "", "", "", "", ""))
    
    def on_row_select(self, event):
        """Handle row selection"""
        selected = self.tree.selection()
        if selected:
            self.selected_request = selected[0]
    
    def approve_request(self):
        """Approve selected blood request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to approve!")
            return
        
        request_id = selected[0].replace("req_", "")
        
        # Get current hospital ID (the one approving)
        approving_hospital_id = None
        if self.controller.current_hospital:
            approving_hospital_id = self.controller.current_hospital.get('id')
        elif self.controller.current_user:
            approving_hospital_id = self.controller.current_user.get('hospital_id')
        
        if not approving_hospital_id:
            messagebox.showerror("Error", "Cannot determine approving hospital!")
            return
        
        try:
            response = requests.put(
                f"{API_BASE_URL}/blood_requests/{request_id}/status",
                json={
                    "status": "approved",
                    "approving_hospital_id": approving_hospital_id
                }
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Request approved successfully! Inventory has been updated.")
                self.notify_hospital(request_id, "approved")
                self.load_requests()
                # Refresh dashboard if available
                if "UnifiedDashboardPage" in self.controller.frames:
                    self.controller.frames["UnifiedDashboardPage"].refresh_data()
            else:
                error_msg = response.json().get('error', 'Failed to approve request')
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve request: {e}")
    
    def reject_request(self):
        """Reject selected blood request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to reject!")
            return
        
        request_id = selected[0].replace("req_", "")
        
        try:
            response = requests.put(
                f"{API_BASE_URL}/blood_requests/{request_id}/status",
                json={"status": "rejected"}
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Request rejected successfully!")
                self.notify_hospital(request_id, "rejected")
                self.load_requests()
                # Refresh dashboard if available
                if "UnifiedDashboardPage" in self.controller.frames:
                    self.controller.frames["UnifiedDashboardPage"].refresh_data()
            else:
                error_msg = response.json().get('error', 'Failed to reject request')
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject request: {e}")
    
    def add_notes(self):
        """Add notes to a blood request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a request to add notes!")
            return
        
        request_id = selected[0].replace("req_", "")
        
        # Create notes window
        notes_window = tk.Toplevel(self.controller.root)
        notes_window.title("Add Notes to Request")
        notes_window.geometry("500x300")
        
        # Center the window
        x = (notes_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (notes_window.winfo_screenheight() // 2) - (300 // 2)
        notes_window.geometry(f"+{x}+{y}")
        
        ttk.Label(notes_window, text="Add Notes for Request", style="Header.TLabel").pack(pady=20)
        
        text_frame = ttk.Frame(notes_window)
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        notes_text = tk.Text(text_frame, height=10, width=50, font=("Segoe UI", 11), wrap="word")
        notes_text.pack(fill="both", expand=True)
        
        def save_notes():
            note_content = notes_text.get("1.0", tk.END).strip()
            
            if not note_content:
                messagebox.showwarning("Warning", "Please enter some notes!")
                return
            
            try:
                response = requests.put(
                    f"{API_BASE_URL}/blood_requests/{request_id}/notes",
                    json={"notes": note_content}
                )
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Notes added successfully!")
                    notes_window.destroy()
                    self.load_requests()
                else:
                    messagebox.showerror("Error", "Failed to add notes")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add notes: {e}")
        
        button_frame = ttk.Frame(notes_window)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Save Notes", command=save_notes,
                  style="Primary.TButton").pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", command=notes_window.destroy,
                  style="Outline.TButton").pack(side="left", padx=10)
    
    def notify_hospital(self, request_id, action):
        """Notify hospital of request approval/rejection"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/blood_requests/{request_id}/notify",
                json={"action": action}
            )
            if response.status_code == 200:
                print(f"Hospital notified of {action} action")
        except Exception as e:
            print(f"Error notifying hospital: {e}")
