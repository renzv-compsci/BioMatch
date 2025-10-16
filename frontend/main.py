# frontend/main_ui.py
import tkinter as tk
from tkinter import messagebox, ttk
import requests
import os

API_BASE_URL = "http://127.0.0.1:5000"

class BioMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioMatch - Blood Management System")
        self.root.attributes('-fullscreen', True)
        
        # Store logged-in user data
        self.current_user = None
        
        # Container for different pages
        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Configure grid layout for container
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dictionary to hold frames
        self.frames = {}
        
        # Initialize all pages and place them in the same grid cell
        for PageClass in (WelcomePage, RegisterHospitalPage, RegisterUserPage, LoginPage, 
                          DashboardPage, AddDonationPage, ViewInventoryPage, SearchBloodPage,
                          TransactionHistoryPage):
            page_name = PageClass.__name__
            frame = PageClass(parent=self.container, controller=self)
            self.frames[page_name] = frame
            # Place all frames in the same location (stacked)
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show welcome page first
        self.show_frame("WelcomePage")
        
        # Exit button (always visible)
        exit_btn = ttk.Button(root, text="Exit Fullscreen", command=self.exit_fullscreen)
        exit_btn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=10)
    
    def show_frame(self, page_name):
        """Switch to a specific page"""
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Refresh data for certain pages
        if page_name == "DashboardPage" and self.current_user:
            self.frames["DashboardPage"].refresh_data()
        elif page_name == "ViewInventoryPage" and self.current_user:
            self.frames["ViewInventoryPage"].load_inventory()
        elif page_name == "TransactionHistoryPage" and self.current_user:
            self.frames["TransactionHistoryPage"].load_transactions()
    
    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)
    
    def set_current_user(self, user_data):
        """Store logged-in user information"""
        self.current_user = user_data
    
    def logout(self):
        """Logout and return to welcome page"""
        self.current_user = None
        self.show_frame("WelcomePage")


# =============================================
# WELCOME PAGE
# =============================================

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        # Title
        tk.Label(self, text="Welcome to BioMatch", font=("Arial", 32, "bold"), bg="white").pack(pady=50)
        tk.Label(self, text="Blood Bank Management System", font=("Arial", 18), bg="white").pack(pady=10)
        
        # Action buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=50)
        
        ttk.Button(button_frame, text="Register New Hospital", width=25,
                   command=lambda: controller.show_frame("RegisterHospitalPage")).pack(pady=10)
        ttk.Button(button_frame, text="Register User Account", width=25,
                   command=lambda: controller.show_frame("RegisterUserPage")).pack(pady=10)
        ttk.Button(button_frame, text="Login", width=25,
                   command=lambda: controller.show_frame("LoginPage")).pack(pady=10)


# =============================================
# REGISTER HOSPITAL PAGE
# =============================================

class RegisterHospitalPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Register New Hospital", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Form
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Hospital Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Address:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.address_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.address_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Contact Person:", bg="white", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.contact_person_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.contact_person_entry.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="Contact Number:", bg="white", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.contact_number_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.contact_number_entry.grid(row=3, column=1, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Register Hospital", command=self.register_hospital).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
    
    def register_hospital(self):
        name = self.name_entry.get().strip()
        address = self.address_entry.get().strip()
        contact_person = self.contact_person_entry.get().strip()
        contact_number = self.contact_number_entry.get().strip()
        
        if not all([name, address, contact_person, contact_number]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/register_hospital", json={
                "name": name,
                "address": address,
                "contact_person": contact_person,
                "contact_number": contact_number
            })
            
            if response.status_code == 201:
                data = response.json()
                messagebox.showinfo("Success", f"Hospital registered! ID: {data['hospital_id']}")
                self.clear_form()
                self.controller.show_frame("WelcomePage")
            else:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.contact_person_entry.delete(0, tk.END)
        self.contact_number_entry.delete(0, tk.END)


# =============================================
# REGISTER USER PAGE
# =============================================

class RegisterUserPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Register User Account", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Form
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Username:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Password:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Role:", bg="white", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.role_combo = ttk.Combobox(form_frame, values=["staff", "nurse", "doctor", "admin"], font=("Arial", 12), width=28)
        self.role_combo.set("staff")
        self.role_combo.grid(row=2, column=1, pady=5)
        
        tk.Label(form_frame, text="Select Hospital:", bg="white", font=("Arial", 12)).grid(row=3, column=0, sticky="w", pady=5)
        self.hospital_combo = ttk.Combobox(form_frame, font=("Arial", 12), width=28, state="readonly")
        self.hospital_combo.grid(row=3, column=1, pady=5)
        
        # Load hospitals button
        ttk.Button(form_frame, text="Load Hospitals", command=self.load_hospitals).grid(row=4, columnspan=2, pady=10)
        
        # Buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Register User", command=self.register_user).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
        
        # Store hospital data
        self.hospitals = []
    
    def load_hospitals(self):
        try:
            response = requests.get(f"{API_BASE_URL}/hospitals")
            if response.status_code == 200:
                self.hospitals = response.json()
                hospital_names = [f"{h['id']} - {h['name']}" for h in self.hospitals]
                self.hospital_combo['values'] = hospital_names
                if hospital_names:
                    self.hospital_combo.current(0)
                messagebox.showinfo("Success", f"Loaded {len(self.hospitals)} hospitals")
            else:
                messagebox.showerror("Error", "Failed to load hospitals")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combo.get()
        
        if not self.hospital_combo.get():
            messagebox.showerror("Error", "Please load and select a hospital!")
            return
        
        # Extract hospital ID from combo selection
        hospital_id = int(self.hospital_combo.get().split(" - ")[0])
        
        if not all([username, password, role]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/register", json={
                "username": username,
                "password": password,
                "role": role,
                "hospital_id": hospital_id
            })
            
            if response.status_code == 201:
                messagebox.showinfo("Success", "User registered successfully!")
                self.clear_form()
                self.controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_combo.set("staff")


# =============================================
# LOGIN PAGE
# =============================================

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Login to BioMatch", font=("Arial", 24, "bold"), bg="white").pack(pady=50)
        
        # Form
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Username:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Password:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Login", command=self.login).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not all([username, password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.controller.set_current_user(data['user'])
                messagebox.showinfo("Success", f"Welcome, {data['user']['username']}!")
                self.clear_form()
                self.controller.show_frame("DashboardPage")
            else:
                messagebox.showerror("Error", response.json().get("message", "Login failed"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)


# =============================================
# DASHBOARD PAGE
# =============================================

class DashboardPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        # Header
        self.header_label = tk.Label(self, text="Dashboard", font=("Arial", 24, "bold"), bg="white")
        self.header_label.pack(pady=20)
        
        self.user_info_label = tk.Label(self, text="", font=("Arial", 14), bg="white")
        self.user_info_label.pack(pady=5)
        
        # Stats frame
        self.stats_frame = tk.Frame(self, bg="white")
        self.stats_frame.pack(pady=20)
        
        # Navigation buttons
        nav_frame = tk.Frame(self, bg="white")
        nav_frame.pack(pady=30)
        
        ttk.Button(nav_frame, text="Add Donation", width=20,
                   command=lambda: controller.show_frame("AddDonationPage")).grid(row=0, column=0, padx=10, pady=10)
        ttk.Button(nav_frame, text="View Inventory", width=20,
                   command=lambda: controller.show_frame("ViewInventoryPage")).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(nav_frame, text="Search Blood", width=20,
                   command=lambda: controller.show_frame("SearchBloodPage")).grid(row=1, column=0, padx=10, pady=10)
        ttk.Button(nav_frame, text="Transaction History", width=20,
                   command=lambda: controller.show_frame("TransactionHistoryPage")).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(nav_frame, text="Logout", width=20,
                   command=controller.logout).grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def refresh_data(self):
        """Refresh dashboard data"""
        if not self.controller.current_user:
            return
        
        user = self.controller.current_user
        self.user_info_label.config(text=f"User: {user['username']} | Role: {user['role']} | Hospital ID: {user['hospital_id']}")
        
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Fetch and display stats
        try:
            # Get inventory summary
            inv_response = requests.get(f"{API_BASE_URL}/inventory/{user['hospital_id']}")
            if inv_response.status_code == 200:
                inventory = inv_response.json()
                total_units = sum(item['units_available'] for item in inventory)
                tk.Label(self.stats_frame, text=f"Total Blood Units: {total_units}", 
                         font=("Arial", 16), bg="white").pack(pady=5)
            
            # Get donation count
            don_response = requests.get(f"{API_BASE_URL}/donations/{user['hospital_id']}")
            if don_response.status_code == 200:
                donations = don_response.json()
                tk.Label(self.stats_frame, text=f"Total Donations: {len(donations)}", 
                         font=("Arial", 16), bg="white").pack(pady=5)
        except Exception as e:
            tk.Label(self.stats_frame, text="Error loading stats", 
                     font=("Arial", 14), fg="red", bg="white").pack()


# =============================================
# ADD DONATION PAGE
# =============================================

class AddDonationPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Add Blood Donation", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Form
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Donor Name:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.donor_name_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.donor_name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Blood Type:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.blood_type_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                              font=("Arial", 12), width=28)
        self.blood_type_combo.grid(row=1, column=1, pady=5)
        
        tk.Label(form_frame, text="Units:", bg="white", font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=5)
        self.units_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.units_entry.grid(row=2, column=1, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Submit Donation", command=self.add_donation).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).grid(row=0, column=1, padx=10)
    
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
            else:
                messagebox.showerror("Error", response.json().get("message", "Failed to add donation"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        self.donor_name_entry.delete(0, tk.END)
        self.blood_type_combo.set("")
        self.units_entry.delete(0, tk.END)


# =============================================
# VIEW INVENTORY PAGE
# =============================================

class ViewInventoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Blood Inventory", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Table
        columns = ("Blood Type", "Units Available", "Last Updated")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Refresh", command=self.load_inventory).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).grid(row=0, column=1, padx=10)
    
    def load_inventory(self):
        if not self.controller.current_user:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            response = requests.get(f"{API_BASE_URL}/inventory/{self.controller.current_user['hospital_id']}")
            if response.status_code == 200:
                inventory = response.json()
                for item in inventory:
                    self.tree.insert("", tk.END, values=(item['blood_type'], item['units_available'], item['last_updated']))
            else:
                messagebox.showerror("Error", "Failed to load inventory")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")


# =============================================
# SEARCH BLOOD PAGE
# =============================================

class SearchBloodPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        tk.Label(self, text="Search Compatible Blood", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Search form
        form_frame = tk.Frame(self, bg="white")
        form_frame.pack(pady=20)
        
        tk.Label(form_frame, text="Blood Type Needed:", bg="white", font=("Arial", 12)).grid(row=0, column=0, sticky="w", pady=5)
        self.blood_type_combo = ttk.Combobox(form_frame, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                              font=("Arial", 12), width=28)
        self.blood_type_combo.grid(row=0, column=1, pady=5)
        
        tk.Label(form_frame, text="Units Needed:", bg="white", font=("Arial", 12)).grid(row=1, column=0, sticky="w", pady=5)
        self.units_entry = tk.Entry(form_frame, font=("Arial", 12), width=30)
        self.units_entry.grid(row=1, column=1, pady=5)
        
        ttk.Button(form_frame, text="Search", command=self.search_blood).grid(row=2, columnspan=2, pady=10)
        
        # Results table
        columns = ("Blood Type", "Units", "Hospital", "Address", "Contact")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=8)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(pady=20)
        
        # Back button
        ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_frame("DashboardPage")).pack(pady=10)
    
    def search_blood(self):
        blood_type = self.blood_type_combo.get()
        units = self.units_entry.get().strip()
        
        if not all([blood_type, units]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Clear existing results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            response = requests.post(f"{API_BASE_URL}/search_blood", json={
                "blood_type": blood_type,
                "units_needed": int(units)
            })
            
            if response.status_code == 200:
                results = response.json()
                if not results:
                    messagebox.showinfo("No Results", "No compatible blood found")
                for result in results:
                    self.tree.insert("", tk.END, values=(
                        result['blood_type'],
                        result['units_available'],
                        result['hospital_name'],
                        result['address'],
                        result['contact_number']
                    ))
            else:
                messagebox.showerror("Error", "Search failed")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")


# =============================================
# TRANSACTION HISTORY PAGE
# =============================================

class TransactionHistoryPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="white")
        self.controller = controller
        
        # Header
        tk.Label(self, text="Transaction History", font=("Arial", 24, "bold"), bg="white").pack(pady=20)
        
        # Filter controls frame
        filter_frame = tk.Frame(self, bg="white")
        filter_frame.pack(pady=10, fill="x", padx=50)
        
        # Transaction Type Filter
        tk.Label(filter_frame, text="Type:", bg="white", font=("Arial", 11)).grid(row=0, column=0, padx=5, sticky="w")
        self.type_filter = ttk.Combobox(filter_frame, values=["All", "donation", "request", "transfer"], 
                                        font=("Arial", 11), width=12, state="readonly")
        self.type_filter.set("All")
        self.type_filter.grid(row=0, column=1, padx=5)
        
        # Status Filter
        tk.Label(filter_frame, text="Status:", bg="white", font=("Arial", 11)).grid(row=0, column=2, padx=5, sticky="w")
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "pending", "completed", "cancelled"], 
                                          font=("Arial", 11), width=12, state="readonly")
        self.status_filter.set("All")
        self.status_filter.grid(row=0, column=3, padx=5)
        
        # Limit Filter
        tk.Label(filter_frame, text="Show:", bg="white", font=("Arial", 11)).grid(row=0, column=4, padx=5, sticky="w")
        self.limit_filter = ttk.Combobox(filter_frame, values=["50", "100", "200"], 
                                         font=("Arial", 11), width=8, state="readonly")
        self.limit_filter.set("100")
        self.limit_filter.grid(row=0, column=5, padx=5)
        
        # Apply Filter Button
        ttk.Button(filter_frame, text="Apply Filters", command=self.load_transactions).grid(row=0, column=6, padx=10)
        
        # Export Button
        ttk.Button(filter_frame, text="Export to CSV", command=self.export_to_csv).grid(row=0, column=7, padx=5)
        
        # Statistics Frame
        self.stats_frame = tk.Frame(self, bg="#f0f0f0", relief="ridge", borderwidth=2)
        self.stats_frame.pack(pady=10, fill="x", padx=50)
        
        # Treeview frame
        tree_frame = tk.Frame(self, bg="white")
        tree_frame.pack(pady=10, fill="both", expand=True, padx=50)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")
        
        # Treeview widget
        columns = ("ID", "Type", "Blood Type", "Units", "Hospital", "Target Hospital", 
                   "Status", "Priority", "Date", "Notes")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                                 yscrollcommand=tree_scroll_y.set, 
                                 xscrollcommand=tree_scroll_x.set)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Column headings and widths
        column_widths = {
            "ID": 60,
            "Type": 100,
            "Blood Type": 90,
            "Units": 70,
            "Hospital": 150,
            "Target Hospital": 150,
            "Status": 90,
            "Priority": 80,
            "Date": 150,
            "Notes": 200
        }
        
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False))
            self.tree.column(col, width=column_widths.get(col, 100), anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        
        # Color tags for different statuses
        self.tree.tag_configure("completed", background="#d4edda")
        self.tree.tag_configure("pending", background="#fff3cd")
        self.tree.tag_configure("cancelled", background="#f8d7da")
        
        # Button frame
        button_frame = tk.Frame(self, bg="white")
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Refresh", command=self.load_transactions).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back to Dashboard", 
                   command=lambda: controller.show_frame("DashboardPage")).grid(row=0, column=1, padx=10)
        
        # Store sort order
        self.sort_reverse = {}
    
    def load_transactions(self):
        """Load transaction history from API"""
        if not self.controller.current_user:
            return
        
        hospital_id = self.controller.current_user['hospital_id']
        
        # Build query parameters
        params = {"limit": self.limit_filter.get()}
        
        type_value = self.type_filter.get()
        if type_value != "All":
            params["type"] = type_value
        
        status_value = self.status_filter.get()
        if status_value != "All":
            params["status"] = status_value
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            # Fetch transactions
            response = requests.get(f"{API_BASE_URL}/transactions/{hospital_id}", params=params)
            
            if response.status_code == 200:
                data = response.json()
                transactions = data.get("transactions", [])
                
                # Load statistics
                self.load_statistics(hospital_id)
                
                # Populate treeview
                for transaction in transactions:
                    tag = transaction.get('status', 'completed')
                    
                    # Format date
                    created_at = transaction.get('created_at', '')
                    if created_at:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            created_at = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    self.tree.insert("", tk.END, values=(
                        transaction.get('id', ''),
                        transaction.get('transaction_type', ''),
                        transaction.get('blood_type', ''),
                        transaction.get('units', ''),
                        transaction.get('hospital_name', '')[:20] + '...' if len(transaction.get('hospital_name', '')) > 20 else transaction.get('hospital_name', ''),
                        transaction.get('target_hospital_name', 'N/A')[:20] + '...' if transaction.get('target_hospital_name') and len(transaction.get('target_hospital_name', '')) > 20 else transaction.get('target_hospital_name', 'N/A'),
                        transaction.get('status', ''),
                        transaction.get('priority_level', 'N/A'),
                        created_at,
                        (transaction.get('notes', '')[:30] + '...') if transaction.get('notes') and len(transaction.get('notes', '')) > 30 else transaction.get('notes', '')
                    ), tags=(tag,))
                
                if not transactions:
                    messagebox.showinfo("No Data", "No transactions found with the selected filters.")
            else:
                messagebox.showerror("Error", f"Failed to load transactions: {response.json().get('message', 'Unknown error')}")
        
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def load_statistics(self, hospital_id):
        """Load and display transaction statistics"""
        try:
            response = requests.get(f"{API_BASE_URL}/transactions/statistics/{hospital_id}")
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("statistics", {})
                
                # Create statistics display
                tk.Label(self.stats_frame, text="Transaction Statistics", 
                         font=("Arial", 12, "bold"), bg="#f0f0f0").pack(pady=5)
                
                stats_grid = tk.Frame(self.stats_frame, bg="#f0f0f0")
                stats_grid.pack(pady=5)
                
                # Display stats
                stat_items = [
                    ("Total Transactions", stats.get('total_transactions', 0)),
                    ("Donations", stats.get('total_donations', 0)),
                    ("Requests", stats.get('total_requests', 0)),
                    ("Transfers", stats.get('total_transfers', 0)),
                    ("Pending", stats.get('pending_transactions', 0)),
                    ("Completed", stats.get('completed_transactions', 0)),
                    ("Cancelled", stats.get('cancelled_transactions', 0))
                ]
                
                for idx, (label, value) in enumerate(stat_items):
                    row = idx // 4
                    col = idx % 4
                    
                    stat_frame = tk.Frame(stats_grid, bg="#ffffff", relief="solid", borderwidth=1)
                    stat_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                    
                    tk.Label(stat_frame, text=label, font=("Arial", 9), bg="#ffffff").pack()
                    tk.Label(stat_frame, text=str(value), font=("Arial", 14, "bold"), 
                             bg="#ffffff", fg="#007bff").pack()
        
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def sort_column(self, col, reverse):
        """Sort treeview column"""
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        
        # Try to sort numerically if possible
        try:
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        except ValueError:
            data.sort(reverse=reverse)
        
        # Rearrange items in sorted positions
        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)
        
        # Toggle sort order for next click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def export_to_csv(self):
        """Export transaction history to CSV file"""
        if not self.tree.get_children():
            messagebox.showwarning("No Data", "No transactions to export.")
            return
        
        try:
            from datetime import datetime
            import csv
            
            filename = f"transaction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(os.path.expanduser("~"), "Desktop", filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                headers = ["ID", "Type", "Blood Type", "Units", "Hospital", "Target Hospital", 
                          "Status", "Priority", "Date", "Notes"]
                writer.writerow(headers)
                
                # Write data
                for item in self.tree.get_children():
                    values = self.tree.item(item, 'values')
                    writer.writerow(values)
            
            messagebox.showinfo("Success", f"Transactions exported to:\n{filepath}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")


# =============================================
# MAIN APPLICATION
# =============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = BioMatchApp(root)
    root.mainloop()