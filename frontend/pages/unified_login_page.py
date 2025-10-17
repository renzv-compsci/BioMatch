import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class UnifiedLoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = tk.Frame(self, bg=BioMatchTheme.PRIMARY, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🩸 BioMatch Login", 
                font=("Segoe UI", 24, "bold"), 
                bg=BioMatchTheme.PRIMARY, fg="white").pack(pady=20)
        
        # Main content
        content_frame = ttk.Frame(self)
        content_frame.pack(fill="both", expand=True)
        
        # Center card
        card_container = ttk.Frame(content_frame)
        card_container.place(relx=0.5, rely=0.5, anchor="center")
        
        login_card = tk.Frame(card_container, bg="white", relief="flat", bd=0)
        login_card.pack(padx=60, pady=40)
        
        # Title
        title = ttk.Label(
            login_card,
            text="🩸 BioMatch Login",
            font=("Segoe UI", 28, "bold"),
            foreground=BioMatchTheme.PRIMARY
        )
        title.pack(pady=(0, 10))
        
        subtitle = ttk.Label(
            login_card,
            text="Unified Blood Management Portal",
            font=("Segoe UI", 11),
            foreground=BioMatchTheme.TEXT_SECONDARY
        )
        subtitle.pack(pady=(0, 30))
        
        # Single login form (hospital only)
        self.hospital_form = self.create_hospital_form(login_card)
        self.hospital_form.pack(fill="both", expand=True)
        
        # Back button
        back_btn = tk.Button(
            login_card,
            text="← Back",
            font=("Segoe UI", 10),
            bg=BioMatchTheme.SECONDARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=lambda: controller.show_frame("WelcomePage")
        )
        back_btn.pack(fill="x", ipady=8, pady=(10, 0))
    
    
    def create_hospital_form(self, parent):
        """Create hospital login form"""
        frame = ttk.Frame(parent)
        
        # Info
        info_label = ttk.Label(
            frame,
            text="💡 Default Password: hospital123",
            foreground=BioMatchTheme.INFO,
            font=("Segoe UI", 9)
        )
        info_label.pack(pady=(0, 20))
        
        # Hospital ID
        ttk.Label(frame, text="Hospital ID:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        self.hospital_id_entry = ttk.Entry(frame, font=("Segoe UI", 11), width=35)
        self.hospital_id_entry.pack(pady=(0, 15))
        
        # Password
        ttk.Label(frame, text="Password:", font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 5))
        self.hospital_password_entry = ttk.Entry(frame, font=("Segoe UI", 11), width=35, show="*")
        self.hospital_password_entry.pack(pady=(0, 25))
        
        # Login button
        login_btn = tk.Button(
            frame,
            text="� Login to Portal",
            font=("Segoe UI", 11, "bold"),
            bg=BioMatchTheme.PRIMARY,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.login_hospital
        )
        login_btn.pack(fill="x", ipady=10)
        
        return frame
    
    def login_hospital(self):
        """Login as hospital"""
        hospital_id = self.hospital_id_entry.get().strip()
        password = self.hospital_password_entry.get().strip()
        
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
                hospital = data['hospital']
                
                # Set hospital as current user for unified portal
                self.controller.set_current_hospital(hospital)
                
                # Create a pseudo-user object for hospital login
                pseudo_user = {
                    'id': hospital['id'],
                    'username': hospital['name'],
                    'role': 'hospital_admin',
                    'hospital_id': hospital['id']
                }
                self.controller.set_current_user(pseudo_user)
                
                messagebox.showinfo("Success", f"Welcome, {hospital['name']}!")
                self.clear_form()
                self.controller.show_frame("UnifiedDashboardPage")
            else:
                error_msg = response.json().get("message", "Login failed")
                messagebox.showerror("Login Error", error_msg)
        except ValueError:
            messagebox.showerror("Error", "Hospital ID must be a number!")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_form(self):
        """Clear form fields"""
        self.hospital_id_entry.delete(0, tk.END)
        self.hospital_password_entry.delete(0, tk.END)
