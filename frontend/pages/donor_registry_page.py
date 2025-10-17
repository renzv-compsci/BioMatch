import tkinter as tk
from tkinter import messagebox, ttk
import requests
from theme import BioMatchTheme, UIComponents

API_BASE_URL = "http://127.0.0.1:5000"

class DonorRegistryPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(header_frame, text="Donor Registry", 
                style="Header.TLabel").pack(side="left")
        
        ttk.Button(header_frame, text="Add New Donor", style="Primary.TButton",
                 command=self.show_add_donor_form).pack(side="right", padx=5)
        
        ttk.Button(header_frame, text="Refresh",
                 command=self.load_donors).pack(side="right", padx=5)
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Search/Filter card
        search_card, search_content = UIComponents.create_card(main_container, "Search Donors")
        
        search_grid = ttk.Frame(search_content)
        search_grid.pack(fill="x", pady=10)
        
        # Search by name
        ttk.Label(search_grid, text="Search by Name:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_entry = ttk.Entry(search_grid, width=25)
        self.search_entry.grid(row=0, column=1, sticky="w", padx=(0, 15))
        
        # Filter by blood type
        ttk.Label(search_grid, text="Blood Type:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.blood_filter = ttk.Combobox(search_grid, values=["All", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                        state="readonly", width=12)
        self.blood_filter.set("All")
        self.blood_filter.grid(row=0, column=3, sticky="w", padx=(0, 15))
        
        # Apply button
        ttk.Button(search_grid, text="Search", style="Primary.TButton",
                 command=self.apply_filter).grid(row=0, column=4, padx=5)
        
        # Clear button
        ttk.Button(search_grid, text="Clear", 
                 command=self.clear_search).grid(row=0, column=5, padx=5)
        
        # Donor list card
        donors_card, donors_content = UIComponents.create_card(main_container, "Registered Donors")
        
        # Donors table
        columns = ("ID", "Name", "Blood Type", "Phone", "Email", "Hospital", "Last Donation", "Status")
        self.tree = UIComponents.create_table(donors_content, columns, height=12)
        
        # Configure column widths
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=120)
        self.tree.column("Blood Type", width=80)
        self.tree.column("Phone", width=100)
        self.tree.column("Email", width=150)
        self.tree.column("Hospital", width=120)
        self.tree.column("Last Donation", width=110)
        self.tree.column("Status", width=80)
        
        # Configure tags for eligibility status
        self.tree.tag_configure('eligible', background='#E8F5E9')    # Light green - eligible
        self.tree.tag_configure('ineligible', background='#FFEBEE')  # Light red - ineligible
        self.tree.tag_configure('pending', background='#FFF3E0')     # Light orange - pending
        
        # Action buttons
        action_frame = ttk.Frame(donors_content)
        action_frame.pack(fill="x", pady=10)
        
        ttk.Button(action_frame, text="View Details", 
                 command=self.view_donor_details).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="Edit Donor", 
                 command=self.edit_donor).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="Delete Donor", style="Secondary.TButton",
                 command=self.delete_donor).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="Export List", 
                 command=self.export_list).pack(side="right", padx=5)
        
        # Statistics frame
        self.stats_frame = ttk.Frame(main_container, relief="solid", borderwidth=1)
        self.stats_frame.pack(fill="x", pady=10)
        
        self.load_donors()
    
    def load_donors(self):
        """Load all donors from API"""
        if not self.controller.current_user:
            return
        
        hospital_id = self.controller.current_user['hospital_id']
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            response = requests.get(f"{API_BASE_URL}/donors/{hospital_id}")
            
            if response.status_code == 200:
                donors = response.json()
                
                # Calculate statistics
                total_donors = len(donors)
                eligible = sum(1 for d in donors if d.get('eligibility_status') == 'eligible')
                ineligible = sum(1 for d in donors if d.get('eligibility_status') == 'ineligible')
                
                # Display statistics
                UIComponents.create_stat_card(self.stats_frame, "Total Donors", total_donors)
                UIComponents.create_stat_card(self.stats_frame, "Eligible", eligible, BioMatchTheme.SUCCESS)
                UIComponents.create_stat_card(self.stats_frame, "Ineligible", ineligible, BioMatchTheme.DANGER)
                
                # Populate table
                for donor in donors:
                    last_donation = donor.get('last_donation_date', 'Never')
                    if last_donation and last_donation != 'Never':
                        last_donation = last_donation[:10]
                    
                    status = donor.get('eligibility_status', 'pending')
                    tag = 'eligible' if status == 'eligible' else ('ineligible' if status == 'ineligible' else 'pending')
                    
                    self.tree.insert("", tk.END, values=(
                        donor.get('id', ''),
                        donor.get('name', ''),
                        donor.get('blood_type', ''),
                        donor.get('phone', ''),
                        donor.get('email', ''),
                        donor.get('hospital_name', ''),
                        last_donation,
                        status.title()
                    ), tags=(tag,))
            
            else:
                messagebox.showerror("Error", "Failed to load donors")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def apply_filter(self):
        """Apply search and filter criteria"""
        search_term = self.search_entry.get().strip().lower()
        blood_type = self.blood_filter.get()
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            hospital_id = self.controller.current_user['hospital_id']
            response = requests.get(f"{API_BASE_URL}/donors/{hospital_id}")
            
            if response.status_code == 200:
                donors = response.json()
                
                # Filter donors
                filtered = donors
                
                if search_term:
                    filtered = [d for d in filtered if search_term in d.get('name', '').lower()]
                
                if blood_type != "All":
                    filtered = [d for d in filtered if d.get('blood_type') == blood_type]
                
                # Populate table with filtered results
                for donor in filtered:
                    last_donation = donor.get('last_donation_date', 'Never')
                    if last_donation and last_donation != 'Never':
                        last_donation = last_donation[:10]
                    
                    status = donor.get('eligibility_status', 'pending')
                    tag = 'eligible' if status == 'eligible' else ('ineligible' if status == 'ineligible' else 'pending')
                    
                    self.tree.insert("", tk.END, values=(
                        donor.get('id', ''),
                        donor.get('name', ''),
                        donor.get('blood_type', ''),
                        donor.get('phone', ''),
                        donor.get('email', ''),
                        donor.get('hospital_name', ''),
                        last_donation,
                        status.title()
                    ), tags=(tag,))
                
                if not filtered:
                    messagebox.showinfo("No Results", "No donors match your search criteria.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_search(self):
        """Clear search and reload all donors"""
        self.search_entry.delete(0, tk.END)
        self.blood_filter.set("All")
        self.load_donors()
    
    def show_add_donor_form(self):
        """Show dialog to add new donor"""
        dialog = tk.Toplevel(self)
        dialog.title("Add New Donor")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.winfo_width() - width) // 2 + self.winfo_x()
        y = (self.winfo_height() - height) // 2 + self.winfo_y()
        dialog.geometry(f"+{x}+{y}")
        
        # Form frame
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill="both", expand=True)
        
        ttk.Label(form_frame, text="Add New Donor", 
                style="Subheader.TLabel").pack(anchor="w", pady=(0, 20))
        
        # Full name
        ttk.Label(form_frame, text="Full Name").pack(anchor="w", pady=(10, 5))
        name_entry = ttk.Entry(form_frame, width=40)
        name_entry.pack(fill="x", pady=(0, 10))
        
        # Blood type
        ttk.Label(form_frame, text="Blood Type").pack(anchor="w", pady=(10, 5))
        blood_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                  state="readonly", width=20)
        blood_combo.pack(fill="x", pady=(0, 10))
        
        # Phone
        ttk.Label(form_frame, text="Phone").pack(anchor="w", pady=(10, 5))
        phone_entry = ttk.Entry(form_frame, width=40)
        phone_entry.pack(fill="x", pady=(0, 10))
        
        # Email
        ttk.Label(form_frame, text="Email").pack(anchor="w", pady=(10, 5))
        email_entry = ttk.Entry(form_frame, width=40)
        email_entry.pack(fill="x", pady=(0, 10))
        
        # Age
        ttk.Label(form_frame, text="Age").pack(anchor="w", pady=(10, 5))
        age_entry = ttk.Entry(form_frame, width=10)
        age_entry.pack(fill="x", pady=(0, 10))
        
        # Notes
        ttk.Label(form_frame, text="Medical Notes").pack(anchor="w", pady=(10, 5))
        notes_text = tk.Text(form_frame, width=40, height=5)
        notes_text.pack(fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="Cancel", 
                 command=dialog.destroy).pack(side="left", padx=5)
        
        ttk.Button(button_frame, text="Add Donor", style="Primary.TButton",
                 command=lambda: self.add_donor(name_entry, blood_combo, phone_entry, 
                                              email_entry, age_entry, notes_text, dialog)).pack(side="right", padx=5)
    
    def add_donor(self, name_entry, blood_combo, phone_entry, email_entry, age_entry, notes_text, dialog):
        """Add new donor to database"""
        name = name_entry.get().strip()
        blood_type = blood_combo.get()
        phone = phone_entry.get().strip()
        email = email_entry.get().strip()
        age = age_entry.get().strip()
        notes = notes_text.get("1.0", tk.END).strip()
        
        if not all([name, blood_type, phone]):
            messagebox.showerror("Error", "Name, blood type and phone are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/donors", json={
                "name": name,
                "blood_type": blood_type,
                "phone": phone,
                "email": email,
                "age": int(age) if age else None,
                "hospital_id": self.controller.current_user['hospital_id'],
                "notes": notes
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "Donor added successfully!")
                dialog.destroy()
                self.load_donors()
            else:
                messagebox.showerror("Error", response.json().get("message", "Failed to add donor"))
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid age.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def view_donor_details(self):
        """View selected donor details"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor.")
            return
        
        item_values = self.tree.item(selected[0], 'values')
        donor_id = item_values[0]
        donor_name = item_values[1]
        
        try:
            response = requests.get(f"{API_BASE_URL}/donors/{donor_id}")
            
            if response.status_code == 200:
                donor = response.json()
                
                details = f"""
Donor Details:

Name: {donor.get('name', '')}
Blood Type: {donor.get('blood_type', '')}
Age: {donor.get('age', 'N/A')}
Phone: {donor.get('phone', '')}
Email: {donor.get('email', '')}
Hospital: {donor.get('hospital_name', '')}
Eligibility Status: {donor.get('eligibility_status', 'Unknown')}
Last Donation: {donor.get('last_donation_date', 'Never')}
Total Donations: {donor.get('total_donations', 0)}

Medical Notes:
{donor.get('notes', 'No notes')}
                """
                
                messagebox.showinfo(f"Donor: {donor_name}", details)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load donor details: {e}")
    
    def edit_donor(self):
        """Edit selected donor"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor.")
            return
        
        messagebox.showinfo("Feature", "Edit donor - Coming soon!")
    
    def delete_donor(self):
        """Delete selected donor"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor.")
            return
        
        item_values = self.tree.item(selected[0], 'values')
        donor_id = item_values[0]
        donor_name = item_values[1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {donor_name}?"):
            try:
                response = requests.delete(f"{API_BASE_URL}/donors/{donor_id}")
                
                if response.status_code == 200:
                    messagebox.showinfo("Success", "Donor deleted successfully!")
                    self.load_donors()
                else:
                    messagebox.showerror("Error", response.json().get("message", "Failed to delete donor"))
            except Exception as e:
                messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def export_list(self):
        """Export donor list to CSV"""
        import csv
        from datetime import datetime
        import os
        
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "No donors to export.")
            return
        
        try:
            filename = f"donor_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Name", "Blood Type", "Phone", "Email", "Hospital", "Last Donation", "Status"])
                
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    writer.writerow(values)
            
            messagebox.showinfo("Success", f"Donor list exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
