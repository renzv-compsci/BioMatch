import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents

API_BASE_URL = "http://127.0.0.1:5000"

class SearchBloodPage(ttk.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(header_frame, text="Search Blood", style="Header.TLabel").pack(anchor="w")
        
        # Main container
        main_container = ttk.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Search form card
        search_card, search_content = UIComponents.create_card(main_container, "Search Criteria")
        
        search_grid = ttk.Frame(search_content)
        search_grid.pack(fill="x", pady=10)
        
        # Blood type
        ttk.Label(search_grid, text="Blood Type Needed:").grid(row=0, column=0, sticky="w", pady=5, padx=(0, 10))
        self.blood_type_combo = ttk.Combobox(search_grid, values=["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], 
                                           state="readonly", width=20)
        self.blood_type_combo.grid(row=0, column=1, sticky="w", pady=5)
        
        # Units needed
        ttk.Label(search_grid, text="Units Needed:").grid(row=0, column=2, sticky="w", pady=5, padx=(20, 10))
        self.units_entry = ttk.Entry(search_grid, width=15)
        self.units_entry.grid(row=0, column=3, sticky="w", pady=5)
        
        # Search button
        ttk.Button(search_grid, text="Search", style="Primary.TButton",
                 command=self.search_blood).grid(row=0, column=4, padx=10)
        
        # Results card
        results_card, results_content = UIComponents.create_card(main_container, "Search Results")
        
        # Results table container
        table_container = ttk.Frame(results_content)
        table_container.pack(fill="both", expand=True, pady=10)
        
        # Results table
        columns = ("Blood Type", "Units", "Hospital", "Address", "Contact")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Blood Type", width=80)
        self.tree.column("Units", width=70)
        self.tree.column("Hospital", width=150)
        self.tree.column("Address", width=200)
        self.tree.column("Contact", width=120)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Action buttons
        action_frame = ttk.Frame(results_content)
        action_frame.pack(fill="x", pady=10)
        
        ttk.Button(action_frame, text="Clear Results", 
                 command=self.clear_results).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="Back to Dashboard",
                 command=lambda: controller.show_frame("DashboardPage")).pack(side="right", padx=5)
        
        # Statistics frame
        self.stats_frame = ttk.Frame(results_content)
        self.stats_frame.pack(fill="x", pady=10, side="bottom")
    
    def search_blood(self):
        blood_type = self.blood_type_combo.get()
        units = self.units_entry.get().strip()
        
        if not all([blood_type, units]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Clear existing results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        try:
            response = requests.post(f"{API_BASE_URL}/search_blood", json={
                "blood_type": blood_type,
                "units_needed": int(units)
            })
            
            if response.status_code == 200:
                results = response.json()
                
                if not results:
                    messagebox.showinfo("No Results", "No compatible blood found in the network.")
                    return
                
                # Display statistics
                total_available = sum(r['units_available'] for r in results)
                total_hospitals = len(results)
                
                UIComponents.create_stat_card(self.stats_frame, "Total Available", total_available)
                UIComponents.create_stat_card(self.stats_frame, "Hospitals", total_hospitals)
                
                # Populate results table
                for result in results:
                    self.tree.insert("", tk.END, values=(
                        result['blood_type'],
                        result['units_available'],
                        result['hospital_name'][:30],
                        result['address'][:40],
                        result['contact_number']
                    ))
            else:
                messagebox.showerror("Error", "Search failed")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of units.")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def clear_results(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
