import tkinter as tk
from tkinter import messagebox, ttk
import requests

API_BASE_URL = "http://127.0.0.1:5000"

class RegisterHospitalPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        ttk.Label(self, text="Register New Hospital", style="Header.TLabel").pack(pady=20)
        
        # Form
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Hospital Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(form_frame, text="Address:").grid(row=1, column=0, sticky="w", pady=5)
        self.address_entry = ttk.Entry(form_frame, width=30)
        self.address_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(form_frame, text="Contact Person:").grid(row=2, column=0, sticky="w", pady=5)
        self.contact_person_entry = ttk.Entry(form_frame, width=30)
        self.contact_person_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(form_frame, text="Contact Number:").grid(row=3, column=0, sticky="w", pady=5)
        self.contact_number_entry = ttk.Entry(form_frame, width=30)
        self.contact_number_entry.grid(row=3, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        ttk.Button(button_frame, text="Register Hospital", command=self.register_hospital).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back", command=lambda: controller.show_frame("WelcomePage")).grid(row=0, column=1, padx=10)
        
        # Success message frame
        self.success_frame = ttk.Frame(self)
        self.success_frame.pack(pady=20)
    
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
                hospital_id = data['hospital_id']
                
                # Clear success frame
                for widget in self.success_frame.winfo_children():
                    widget.destroy()
                
                # Display success message with Hospital ID
                success_label = ttk.Label(
                    self.success_frame,
                    text=f"Hospital registered successfully!\n\nHospital ID: {hospital_id}\nDefault Password: hospital123\n\nSave this ID - you'll need it to login",
                    justify="center",
                    foreground="green"
                )
                success_label.pack(pady=10)
                
                # Copy to clipboard button
                copy_btn = ttk.Button(
                    self.success_frame,
                    text="Copy Hospital ID to Clipboard",
                    command=lambda: self.copy_to_clipboard(str(hospital_id))
                )
                copy_btn.pack(pady=5)
                
                self.clear_form()
            else:
                messagebox.showerror("Error", response.json().get("message", "Registration failed"))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.controller.root.clipboard_clear()
        self.controller.root.clipboard_append(text)
        messagebox.showinfo("Success", "Hospital ID copied to clipboard!")
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.contact_person_entry.delete(0, tk.END)
        self.contact_number_entry.delete(0, tk.END)
