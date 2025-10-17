import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Label(self, text="Login to BioMatch", style="Header.TLabel").pack(pady=50)
        
        # Form
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(form_frame, width=30, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
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
