import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalLoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(header_frame, text="Hospital Portal Login", style="Header.TLabel").pack(anchor="w")
        
        info_label = ttk.Label(
            self, 
            text="Default Password: hospital123\nChange your password after first login",
            foreground="blue",
            justify="center"
        )
        info_label.pack(pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Hospital ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.hospital_id_entry = ttk.Entry(form_frame, width=30)
        self.hospital_id_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Login", command=self.login).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
    
    def login(self):
        hospital_id = self.hospital_id_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not all([hospital_id, password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        try:
            response = requests.post(f"{API_BASE_URL}/hospital/login", json={
                "hospital_id": int(hospital_id),
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.controller.set_current_hospital(data['hospital'])
                messagebox.showinfo("Success", f"Welcome, {data['hospital']['name']}!")
                self.clear_form()
                self.controller.show_frame("HospitalDashboardPage")
            else:
                error_msg = response.json().get("message", "Login failed")
                messagebox.showerror("Login Error", error_msg)
        except ValueError:
            messagebox.showerror("Error", "Hospital ID must be a number!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        self.hospital_id_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
