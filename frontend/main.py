# frontend/main_ui.py

import tkinter as tk
from tkinter import messagebox, ttk
import requests

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
                          DashboardPage, AddDonationPage, ViewInventoryPage, SearchBloodPage):
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
        ttk.Button(nav_frame, text="Logout", width=20,
                   command=controller.logout).grid(row=1, column=1, padx=10, pady=10)
    
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
# MAIN APPLICATION
# =============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = BioMatchApp(root)
    root.mainloop()