import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class HospitalChangePasswordPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=30, pady=20)
        
        ttk.Button(header_frame, text="← Back", command=lambda: controller.show_frame("HospitalDashboardPage"),
                  style="Outline.TButton").pack(side="left")
        ttk.Label(header_frame, text="🔐 Change Password", style="Header.TLabel").pack(side="left", padx=20)
        
        # Main content
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=50, pady=20)
        
        # Password change card
        card, form_content = UIComponents.create_card(content, "Update Hospital Password")
        
        # Instructions
        info_frame = ttk.Frame(form_content)
        info_frame.pack(fill="x", pady=15)
        
        ttk.Label(info_frame, text="Password Security Requirements:", 
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        
        requirements = [
            "• Minimum 6 characters in length",
            "• Include at least one uppercase letter",
            "• Include at least one number",
            "• Do not use easy-to-guess passwords"
        ]
        
        for req in requirements:
            ttk.Label(info_frame, text=req, font=("Segoe UI", 11)).pack(anchor="w", pady=2)
        
        # Separator
        ttk.Separator(form_content, orient="horizontal").pack(fill="x", pady=15)
        
        # Form
        form_frame = ttk.Frame(form_content)
        form_frame.pack(fill="x", pady=20)
        
        ttk.Label(form_frame, text="Current Password:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=10, padx=(0, 20))
        self.current_password_entry = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11), show="●")
        self.current_password_entry.grid(row=0, column=1, pady=10, sticky="ew")
        
        ttk.Label(form_frame, text="New Password:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=10, padx=(0, 20))
        self.new_password_entry = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11), show="●")
        self.new_password_entry.grid(row=1, column=1, pady=10, sticky="ew")
        
        ttk.Label(form_frame, text="Confirm New Password:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="w", pady=10, padx=(0, 20))
        self.confirm_password_entry = ttk.Entry(form_frame, width=40, font=("Segoe UI", 11), show="●")
        self.confirm_password_entry.grid(row=2, column=1, pady=10, sticky="ew")
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Password strength indicator
        self.strength_var = tk.StringVar(value="Password strength: None")
        strength_label = ttk.Label(form_content, textvariable=self.strength_var)
        strength_label.pack(pady=10)
        
        self.strength_bar = ttk.Progressbar(form_content, orient="horizontal", length=400, mode="determinate")
        self.strength_bar.pack(pady=5)
        
        # Bind password entry to strength checker
        self.new_password_entry.bind("<KeyRelease>", self.check_password_strength)
        
        # Buttons
        button_frame = ttk.Frame(form_content)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Update Password", command=self.change_password,
                  style="Primary.TButton", width=20).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", command=lambda: self.controller.show_frame("HospitalDashboardPage"),
                  style="Outline.TButton", width=15).pack(side="left")
    
    def check_password_strength(self, event=None):
        """Check password strength and update indicator"""
        password = self.new_password_entry.get()
        
        # Reset strength
        strength = 0
        strength_text = "Weak"
        
        # Check length
        if len(password) >= 8:
            strength += 25
        elif len(password) >= 6:
            strength += 10
        
        # Check for uppercase
        if any(c.isupper() for c in password):
            strength += 25
        
        # Check for numbers
        if any(c.isdigit() for c in password):
            strength += 25
        
        # Check for special characters
        if any(not c.isalnum() for c in password):
            strength += 25
        
        # Update strength text
        if strength >= 75:
            strength_text = "Strong"
        elif strength >= 50:
            strength_text = "Moderate"
        elif strength >= 25:
            strength_text = "Fair"
        else:
            strength_text = "Weak"
        
        # Update UI
        self.strength_var.set(f"Password strength: {strength_text}")
        self.strength_bar["value"] = strength
    
    def change_password(self):
        """Process password change"""
        if not self.controller.current_hospital:
            messagebox.showerror("Error", "Not logged in!")
            return
        
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not all([current_password, new_password, confirm_password]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords don't match!")
            return
        
        if len(new_password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long!")
            return
        
        try:
            # Use the real API endpoint
            response = requests.post(
                f"{API_BASE_URL}/hospital/{self.controller.current_hospital['id']}/change-password",
                json={
                    "old_password": current_password,
                    "new_password": new_password
                }
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Password changed successfully!")
                self.clear_form()
                self.controller.show_frame("HospitalDashboardPage")
            else:
                error_msg = response.json().get("message", "Failed to change password")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        """Clear the form fields"""
        self.current_password_entry.delete(0, tk.END)
        self.new_password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.strength_var.set("Password strength: None")
        self.strength_bar["value"] = 0
