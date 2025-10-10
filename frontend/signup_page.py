import tkinter as tk
from tkinter import messagebox
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class SignupPage(tk.Frame):
    def __init__(self, master, on_signup_success, on_show_login):
        super().__init__(master)
        self.on_signup_success = on_signup_success
        self.on_show_login = on_show_login
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Sign Up", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Label(self, text="Role:").pack()
        self.role_entry = tk.Entry(self)
        self.role_entry.insert(0, "hospital_staff")
        self.role_entry.pack()

        tk.Label(self, text="Hospital ID (optional):").pack()
        self.hospital_id_entry = tk.Entry(self)
        self.hospital_id_entry.pack()

        tk.Button(self, text="Register", command=self.register).pack(pady=10)
        tk.Button(self, text="Back to Login", command=self.on_show_login).pack()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_entry.get()
        hospital_id = self.hospital_id_entry.get()
        payload = {
            "username": username,
            "password": password,
            "role": role
        }
        if hospital_id:
            try:
                payload["hospital_id"] = int(hospital_id)
            except ValueError:
                messagebox.showerror("Error", "Hospital ID must be a number.")
                return
        try:
            response = requests.post(f"{API_BASE_URL}/register", json=payload)
            if response.status_code == 201:
                messagebox.showinfo("Success", "Registration successful! Please log in.")
                self.on_signup_success()
            else:
                messagebox.showerror("Error", response.json().get('message', 'Registration failed.'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")