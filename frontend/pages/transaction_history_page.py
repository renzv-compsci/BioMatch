import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme
from .base_page import BasePage

API_BASE_URL = "http://127.0.0.1:5000"

class TransactionHistoryPage(BasePage):
    def __init__(self, parent, controller):
        BasePage.__init__(self, parent, controller)
        
        # Create navigation
        self.refresh_data()
        
        # Main container (uses self.main_content from BasePage)
        container = ttk.Frame(self.main_content)
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header within content area
        ttk.Label(container, text="� Transaction History", 
                 font=("Segoe UI", 18, "bold"),
                 foreground=BioMatchTheme.PRIMARY).pack(anchor="w", pady=(0, 20))
        
        # Filter card
        filter_card, filter_content = UIComponents.create_card(container, "Filter Transactions")
        filter_card.pack(fill="x", pady=(0, 20))
        
        filter_frame = ttk.Frame(filter_content)
        filter_frame.pack(fill="x", pady=10)
        
        ttk.Label(filter_frame, text="Status:", font=("Segoe UI", 11)).grid(row=0, column=0, padx=5)
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "approved", "rejected", "completed"],
                                         state="readonly", width=15)
        self.status_filter.set("All")
        self.status_filter.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Priority:", font=("Segoe UI", 11)).grid(row=0, column=2, padx=5)
        self.priority_filter = ttk.Combobox(filter_frame, values=["All", "Low", "Medium", "High", "Critical"],
                                           state="readonly", width=15)
        self.priority_filter.set("All")
        self.priority_filter.grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.load_transactions,
                  style="Primary.TButton").grid(row=0, column=4, padx=20)
        
        ttk.Button(filter_frame, text="🔄 Refresh Data", command=self.load_transactions,
                  style="Secondary.TButton").grid(row=0, column=5, padx=20)
        
        # Stats frame
        self.stats_frame = ttk.Frame(container)
        self.stats_frame.pack(fill="x", pady=10)
        
        # Transactions table
        table_card, table_content = UIComponents.create_card(container, "Completed Transactions")
        table_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Table container
        table_container = ttk.Frame(table_content)
        table_container.pack(fill="both", expand=True, pady=10)
        
        self.tree = UIComponents.create_table(
            table_container,
            ("ID", "Direction", "Hospital", "Blood Type", "Quantity", "Priority", "Status", "Date"),
            height=15
        )
        
        # Configure columns
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Direction", width=80, anchor="center")
        self.tree.column("Hospital", width=180)
        self.tree.column("Blood Type", width=100, anchor="center")
        self.tree.column("Quantity", width=100, anchor="center")
        self.tree.column("Priority", width=100, anchor="center")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Date", width=150)
        
        # Configure tags for status
        self.tree.tag_configure("approved", background="#C8E6C9")
        self.tree.tag_configure("rejected", background="#FFCDD2")
        self.tree.tag_configure("completed", background="#E1F5FE")
        
        # Bind row selection for view details
        self.tree.bind("<Double-1>", self.view_transaction_details)
        
        # Load initial data
        self.after(100, self.load_transactions)
    
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
    
    def load_transactions(self):
        """Load completed transaction history (approved/rejected/completed only)"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Build query parameters - exclude pending status
            params = {}
            
            status_value = self.status_filter.get()
            if status_value != "All":
                params["status"] = status_value
            
            priority_value = self.priority_filter.get()
            if priority_value != "All":
                params["priority"] = priority_value
            
            # Get current hospital ID
            hospital_id = None
            if self.controller.current_hospital:
                hospital_id = self.controller.current_hospital.get('id')
            elif self.controller.current_user:
                hospital_id = self.controller.current_user.get('hospital_id')
            
            if not hospital_id:
                # Silently return if no hospital ID (user not logged in)
                return
            
            # Fetch completed transactions (both sent and received, excluding pending)
            response = requests.get(f"{API_BASE_URL}/hospital/{hospital_id}/transactions", params=params)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', []) if isinstance(data, dict) else data
                stats = data.get('stats', {}) if isinstance(data, dict) else {}
                
                if isinstance(transactions, list) and len(transactions) > 0:
                    # Display statistics
                    UIComponents.create_stat_card(self.stats_frame, "Total Transactions", 
                                               stats.get('total', len(transactions)), BioMatchTheme.PRIMARY)
                    UIComponents.create_stat_card(self.stats_frame, "Approved", 
                                               stats.get('approved', 0), BioMatchTheme.SUCCESS)
                    UIComponents.create_stat_card(self.stats_frame, "Rejected", 
                                               stats.get('rejected', 0), BioMatchTheme.DANGER)
                    UIComponents.create_stat_card(self.stats_frame, "Completed", 
                                               stats.get('completed', 0), BioMatchTheme.INFO)
                    
                    # Populate table with transactions
                    for txn in transactions:
                        status = str(txn.get('status', '')).lower()
                        tag = status if status in ['approved', 'rejected', 'completed'] else ''
                        
                        # Determine direction and hospital name
                        requesting_id = txn.get('requesting_hospital_id')
                        source_id = txn.get('source_hospital_id')
                        
                        if requesting_id == hospital_id:
                            # We requested this blood (sent request)
                            direction = "→ Sent"
                            hospital_name = txn.get('source_hospital_name', f"Hospital {source_id}")
                        else:
                            # We fulfilled this request (received request)
                            direction = "← Received"
                            hospital_name = txn.get('requesting_hospital_name', f"Hospital {requesting_id}")
                        
                        # Format date
                        date_str = txn.get('created_at', '')
                        if date_str:
                            date_str = date_str[:16] if isinstance(date_str, str) else str(date_str)[:16]
                        
                        self.tree.insert("", tk.END, values=(
                            txn.get('id', ''),
                            direction,
                            hospital_name,
                            txn.get('blood_type', ''),
                            txn.get('units_requested', ''),
                            txn.get('priority_level', ''),
                            status.upper(),
                            date_str
                        ), tags=(tag,), iid=f"txn_{txn.get('id', '')}")
                else:
                    # No transactions found
                    UIComponents.create_stat_card(self.stats_frame, "Total Transactions", 0, BioMatchTheme.PRIMARY)
                    UIComponents.create_stat_card(self.stats_frame, "Approved", 0, BioMatchTheme.SUCCESS)
                    UIComponents.create_stat_card(self.stats_frame, "Rejected", 0, BioMatchTheme.DANGER)
                    UIComponents.create_stat_card(self.stats_frame, "Completed", 0, BioMatchTheme.INFO)
                    self.tree.insert("", tk.END, values=("No completed transactions found", "", "", "", "", "", "", ""))
            else:
                error_msg = response.json().get('error', 'Failed to load transactions') if response.text else 'No response from server'
                messagebox.showerror("Error", f"Failed to load transactions: {error_msg}")
                
                # Show empty state
                UIComponents.create_stat_card(self.stats_frame, "Total Transactions", 0, BioMatchTheme.PRIMARY)
                self.tree.insert("", tk.END, values=("Error loading transactions", "", "", "", "", "", "", ""))
        
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Cannot connect to server. Please ensure the backend is running.")
            UIComponents.create_stat_card(self.stats_frame, "Total Transactions", 0, BioMatchTheme.PRIMARY)
            self.tree.insert("", tk.END, values=("Connection failed", "", "", "", "", "", "", ""))
        except Exception as e:
            print(f"Error loading transactions: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Error loading transactions: {str(e)}")
            UIComponents.create_stat_card(self.stats_frame, "Total Transactions", 0, BioMatchTheme.PRIMARY)
            self.tree.insert("", tk.END, values=("Error occurred", "", "", "", "", "", "", ""))
    
    def view_transaction_details(self, event):
        """View details of selected transaction"""
        selected = self.tree.selection()
        if not selected:
            return
        
        transaction_id = selected[0].replace("txn_", "")
        
        # Create details window
        details_window = tk.Toplevel(self.controller.root)
        details_window.title("Transaction Details")
        details_window.geometry("600x400")
        
        # Center the window
        x = (details_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (details_window.winfo_screenheight() // 2) - (400 // 2)
        details_window.geometry(f"+{x}+{y}")
        
        ttk.Label(details_window, text=f"Transaction #{transaction_id}", 
                 style="Header.TLabel").pack(pady=20)
        
        # Get transaction details from tree
        item_values = self.tree.item(selected[0])['values']
        
        details_frame = ttk.Frame(details_window)
        details_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        if len(item_values) >= 8:
            ttk.Label(details_frame, text=f"Transaction ID: {item_values[0]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Direction: {item_values[1]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Hospital: {item_values[2]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Blood Type: {item_values[3]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Quantity: {item_values[4]} units", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Priority: {item_values[5]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Status: {item_values[6]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
            ttk.Label(details_frame, text=f"Date: {item_values[7]}", 
                     font=("Segoe UI", 11)).pack(anchor="w", pady=5)
        
        button_frame = ttk.Frame(details_window)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Close", command=details_window.destroy,
                  style="Primary.TButton").pack()