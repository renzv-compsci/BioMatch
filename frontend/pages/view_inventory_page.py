import tkinter as tk
from tkinter import messagebox, ttk
import requests
import os
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class ViewInventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ttk.Button(header_frame, text="← Back", 
                  command=lambda: controller.show_frame("DashboardPage"),
                  style="Outline.TButton").pack(side="left")
        ttk.Label(header_frame, text="📦 Blood Inventory", 
                 style="Header.TLabel").pack(side="left", padx=20)
        
        ttk.Button(header_frame, text="🔄 Refresh", command=self.load_inventory,
                  style="Primary.TButton").pack(side="right", padx=5)
        ttk.Button(header_frame, text="📥 Export CSV", command=self.export_inventory,
                  style="Outline.TButton").pack(side="right", padx=10)
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=20)
        
        # ===== SUMMARY TAB =====
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="📊 Inventory Summary")
        
        # Create container for table to properly use pack
        summary_container = ttk.Frame(summary_frame)
        summary_container.pack(fill="both", expand=True, pady=10)
        
        self.inventory_tree = UIComponents.create_table(
            summary_container,
            ("Blood Type", "Units Available", "Last Updated", "Source"),
            height=10
        )
        
        self.inventory_tree.column("Blood Type", width=120, anchor="center")
        self.inventory_tree.column("Units Available", width=150, anchor="center")
        self.inventory_tree.column("Last Updated", width=150)
        self.inventory_tree.column("Source", width=200)
        
        # ===== APPROVED REQUESTS TAB =====
        approved_frame = ttk.Frame(self.notebook)
        self.notebook.add(approved_frame, text="✓ Approved Requests")
        
        # Stats frame for approved
        self.approved_stats_frame = ttk.Frame(approved_frame)
        self.approved_stats_frame.pack(fill="x", padx=10, pady=10)
        
        # Create container for approved tree
        approved_container = ttk.Frame(approved_frame)
        approved_container.pack(fill="both", expand=True, pady=10)
        
        self.approved_tree = UIComponents.create_table(
            approved_container,
            ("ID", "Hospital", "Blood Type", "Units", "Status", "Date", "Notes"),
            height=10
        )
        
        self.approved_tree.column("ID", width=50, anchor="center")
        self.approved_tree.column("Hospital", width=150)
        self.approved_tree.column("Blood Type", width=100, anchor="center")
        self.approved_tree.column("Units", width=80, anchor="center")
        self.approved_tree.column("Status", width=100, anchor="center")
        self.approved_tree.column("Date", width=130)
        self.approved_tree.column("Notes", width=200)
        
        # Configure tag for approved status
        self.approved_tree.tag_configure("approved", background="#C8E6C9")
        
        # Bind double-click to view full notes
        self.approved_tree.bind("<Double-1>", self.view_request_notes)
        
        # ===== RECENT DONATIONS TAB =====
        donations_frame = ttk.Frame(self.notebook)
        self.notebook.add(donations_frame, text="💉 Recent Donations")
        
        # Create container for donations tree
        donations_container = ttk.Frame(donations_frame)
        donations_container.pack(fill="both", expand=True, pady=10)
        
        self.donations_tree = UIComponents.create_table(
            donations_container,
            ("Blood Type", "Units", "Donor", "Source Hospital", "Date"),
            height=10
        )
        
        self.donations_tree.column("Blood Type", width=120, anchor="center")
        self.donations_tree.column("Units", width=100, anchor="center")
        self.donations_tree.column("Donor", width=150)
        self.donations_tree.column("Source Hospital", width=200)
        self.donations_tree.column("Date", width=150)
        
        # Load initial data
        self.after(100, self.load_inventory)
    
    def load_inventory(self):
        """Load inventory data from backend"""
        if not self.controller.current_user:
            return
        
        hospital_id = self.controller.current_user['hospital_id']
        
        # Clear existing data
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        for item in self.approved_tree.get_children():
            self.approved_tree.delete(item)
        
        for item in self.donations_tree.get_children():
            self.donations_tree.delete(item)
        
        for widget in self.approved_stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Get inventory
            inv_response = requests.get(f"{API_BASE_URL}/inventory/{hospital_id}")
            
            if inv_response.status_code == 200:
                inventory = inv_response.json()
                
                print(f"Received {len(inventory)} inventory items")
                
                if inventory and len(inventory) > 0:
                    # Populate summary tab
                    for item in inventory:
                        self.inventory_tree.insert("", tk.END, values=(
                            item.get('blood_type', ''),
                            item.get('units_available', 0),
                            item.get('last_updated', '')[:16] if item.get('last_updated') else '',
                            item.get('hospital_name', 'This Hospital')
                        ))
                    
                    # Populate recent donations tab
                    all_donations = []
                    for item in inventory:
                        recent_donations = item.get('recent_donations', [])
                        for donation in recent_donations:
                            all_donations.append({
                                'blood_type': item.get('blood_type', ''),
                                'units': donation.get('units', 0),
                                'donor': donation.get('donor_name', ''),
                                'source_hospital': donation.get('source_hospital', 'Unknown'),
                                'date': donation.get('date', '')
                            })
                    
                    # Sort by date descending
                    all_donations.sort(key=lambda x: x['date'], reverse=True)
                    
                    for donation in all_donations[:50]:  # Show last 50 donations
                        self.donations_tree.insert("", tk.END, values=(
                            donation['blood_type'],
                            donation['units'],
                            donation['donor'],
                            donation['source_hospital'],
                            donation['date'][:16] if donation['date'] else ''
                        ))
                    
                    if not all_donations:
                        self.donations_tree.insert("", tk.END, values=("No recent donations", "", "", "", ""))
                else:
                    # No inventory data
                    self.inventory_tree.insert("", tk.END, values=("No inventory data", "", "", ""))
                    self.donations_tree.insert("", tk.END, values=("No donations yet", "", "", "", ""))
            else:
                messagebox.showerror("Error", f"Failed to load inventory: {inv_response.status_code}")
                self.inventory_tree.insert("", tk.END, values=("Error loading inventory", "", "", ""))
            
            # Load approved blood requests
            self.load_approved_requests(hospital_id)
        
        except Exception as e:
            print(f"Error loading inventory: {e}")
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.inventory_tree.insert("", tk.END, values=("Connection failed", "", "", ""))

    def load_approved_requests(self, hospital_id):
        """Load approved blood requests from all hospitals"""
        try:
            response = requests.get(f"{API_BASE_URL}/blood_requests?status=approved")
            
            if response.status_code == 200:
                approved_requests = response.json()
                
                # Filter to show only approved requests
                approved_list = [r for r in approved_requests if r.get('status') == 'approved']
                
                # Display statistics
                total_approved = len(approved_list)
                total_units = sum(r.get('units_requested', 0) for r in approved_list)
                
                UIComponents.create_stat_card(self.approved_stats_frame, "Total Approved", 
                                           total_approved, BioMatchTheme.SUCCESS)
                UIComponents.create_stat_card(self.approved_stats_frame, "Total Units Approved", 
                                           total_units, BioMatchTheme.PRIMARY)
                
                # Populate table
                for req in approved_list:
                    notes_preview = req.get('notes', '')[:50]  # First 50 chars
                    if len(req.get('notes', '')) > 50:
                        notes_preview += "..."
                    
                    self.approved_tree.insert("", tk.END, values=(
                        req.get('id', ''),
                        req.get('requesting_hospital_name', 'Unknown'),
                        req.get('blood_type', ''),
                        req.get('units_requested', ''),
                        'APPROVED',
                        req.get('created_at', '')[:16] if req.get('created_at') else '',
                        notes_preview
                    ), tags=('approved',), iid=f"req_{req.get('id', '')}")
                
                if not approved_list:
                    self.approved_tree.insert("", tk.END, values=("No approved requests", "", "", "", "", "", ""))
        
        except Exception as e:
            print(f"Error loading approved requests: {e}")
    
    def view_request_notes(self, event):
        """View full notes for an approved request"""
        selected = self.approved_tree.selection()
        if not selected:
            return
        
        request_id = selected[0].replace("req_", "")
        
        try:
            response = requests.get(f"{API_BASE_URL}/blood_requests?status=approved")
            
            if response.status_code == 200:
                all_requests = response.json()
                
                # Find the request
                request_data = None
                for req in all_requests:
                    if str(req.get('id')) == request_id:
                        request_data = req
                        break
                
                if request_data:
                    # Create notes window
                    notes_window = tk.Toplevel(self.controller.root)
                    notes_window.title(f"Request #{request_id} Details")
                    notes_window.geometry("600x400")
                    
                    # Center the window
                    x = (notes_window.winfo_screenwidth() // 2) - (600 // 2)
                    y = (notes_window.winfo_screenheight() // 2) - (400 // 2)
                    notes_window.geometry(f"+{x}+{y}")
                    
                    # Title
                    ttk.Label(notes_window, text=f"Blood Request #{request_data['id']} - {request_data['requesting_hospital_name']}", 
                             style="Header.TLabel").pack(pady=20)
                    
                    # Details frame
                    details_frame = ttk.LabelFrame(notes_window, text="Request Details", padding=10)
                    details_frame.pack(fill="x", padx=20, pady=10)
                    
                    details_text = f"""
Blood Type: {request_data.get('blood_type', 'N/A')}
Units Requested: {request_data.get('units_requested', 'N/A')}
Priority: {request_data.get('priority_level', 'N/A')}
Status: {request_data.get('status', 'N/A').upper()}
Requested Date: {request_data.get('created_at', 'N/A')[:16]}
                    """
                    
                    ttk.Label(details_frame, text=details_text, justify="left").pack(anchor="w", pady=10)
                    
                    # Notes frame
                    notes_frame = ttk.LabelFrame(notes_window, text="Administrative Notes", padding=10)
                    notes_frame.pack(fill="both", expand=True, padx=20, pady=10)
                    
                    notes_text_widget = tk.Text(notes_frame, height=12, width=70, font=("Segoe UI", 10), wrap="word")
                    notes_text_widget.pack(fill="both", expand=True)
                    
                    notes_content = request_data.get('notes', 'No notes added')
                    notes_text_widget.insert("1.0", notes_content)
                    notes_text_widget.config(state="disabled")  # Make read-only
                    
                    # Close button
                    ttk.Button(notes_window, text="Close", command=notes_window.destroy,
                              style="Outline.TButton").pack(pady=15)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load request details: {e}")
    
    def export_inventory(self):
        """Export inventory data to CSV"""
        if not self.inventory_tree.get_children():
            messagebox.showwarning("No Data", "No inventory data to export.")
            return
        
        try:
            from datetime import datetime
            import csv
            
            filename = f"blood_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Blood Type", "Units Available", "Last Updated", "Source"])
                
                for item in self.inventory_tree.get_children():
                    values = self.inventory_tree.item(item, 'values')
                    writer.writerow(values)
            
            messagebox.showinfo("Success", f"Inventory exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
