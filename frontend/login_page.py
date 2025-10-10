import tkinter as tk
from tkinter import messagebox
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class LoginPage(tk.Frame):
    def __init__(self, master, on_login_success, on_show_signup):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.on_show_signup = on_show_signup
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Login", font=("Arial", 16)).pack(pady=10)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Label(self, text="Don't have an account?").pack()
        tk.Button(self, text="Sign Up", command=self.on_show_signup).pack(pady=5)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            response = requests.post(f"{API_BASE_URL}/login", json={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                messagebox.showinfo("Success", f"Welcome, {data['username']} (Role: {data['role']})!")
                self.on_login_success(data)  # Pass user info to main app
            else:
                messagebox.showerror("Error", response.json().get('message', 'Login failed.'))
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")