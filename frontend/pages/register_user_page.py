import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class RegisterUserPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Label(self, text="Register User Account", style="Header.TLabel").pack(pady=20)
        
        # Form
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text="Role:").grid(row=2, column=0, sticky="w", pady=5)
        self.role_combo = ttk.Combobox(form_frame, values=["staff", "nurse", "doctor", "admin"], width=28)
        self.role_combo.set("staff")
        self.role_combo.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text="Select Hospital:").grid(row=3, column=0, sticky="w", pady=5)
        self.hospital_combo = ttk.Combobox(form_frame, width=28)
        self.hospital_combo.grid(row=3, column=1, pady=5)
        
        # Load hospitals button
        ttk.Button(form_frame, text="Load Hospitals", command=self.load_hospitals).grid(row=4, columnspan=2, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Register User", command=self.register_user).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
        
        self.hospitals = []
    
    def load_hospitals(self):
        try:
            response = requests.get(f"{API_BASE_URL}/hospitals")
            if response.status_code == 200:
                self.hospitals = response.json()
                if self.hospitals:
                    hospital_names = [f"{h['id']} - {h['name']}" for h in self.hospitals]
                    self.hospital_combo['values'] = hospital_names
                    self.hospital_combo.current(0)
                    messagebox.showinfo("Success", f"Loaded {len(self.hospitals)} hospitals")
                else:
                    messagebox.showwarning("No Hospitals", "No hospitals found. Please register a hospital first.")
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
        
        try:
            hospital_id = int(self.hospital_combo.get().split(" - ")[0])
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Invalid hospital selection!")
            return
        
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
        self.hospital_combo.set("")