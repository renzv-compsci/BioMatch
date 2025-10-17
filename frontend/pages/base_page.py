import tkinter as tk
from tkinter import messagebox, ttk
import requests
from frontend.theme import UIComponents, BioMatchTheme

API_BASE_URL = "http://127.0.0.1:5000"

class BasePage(ttk.Frame):
    """Base class for all authenticated pages with header and sidebar"""
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        # Main container with background
        self.configure(style='TFrame')
        
        # ===== HEADER =====
        self.header = tk.Frame(self, bg=BioMatchTheme.PRIMARY, height=70)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        
        # Logo
        logo_label = tk.Label(self.header, text="🩸 BioMatch", 
                             font=("Segoe UI", 18, "bold"), 
                             bg=BioMatchTheme.PRIMARY, fg="white")
        logo_label.pack(side="left", padx=20)
        
        # Search bar (for blood search)
        search_frame = tk.Frame(self.header, bg=BioMatchTheme.PRIMARY)
        search_frame.pack(side="left", padx=20, expand=True)
        
        self.search_entry = ttk.Entry(search_frame, font=("Segoe UI", 11), width=40)
        self.search_entry.pack(side="left", padx=5, ipady=5)
        self.search_entry.bind('<Return>', lambda e: self.perform_search())
        
        search_btn = tk.Button(search_frame, text="🔍 Search Blood", 
                              command=self.perform_search,
                              bg="white", fg=BioMatchTheme.PRIMARY,
                              font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=15, pady=5,
                              cursor="hand2")
        search_btn.pack(side="left")
        
        # User info
        self.user_info_label = tk.Label(self.header, text="", 
                                        font=("Segoe UI", 11), 
                                        bg=BioMatchTheme.PRIMARY, fg="white")
        self.user_info_label.pack(side="right", padx=20)
        
        # ===== SIDEBAR =====
        self.sidebar = tk.Frame(self, bg=BioMatchTheme.SIDEBAR_BG, width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        tk.Label(self.sidebar, text="Navigation", 
                font=("Segoe UI", 14, "bold"), 
                bg=BioMatchTheme.SIDEBAR_BG, fg="white").pack(pady=20)
        
        # Sidebar buttons container
        self.nav_container = tk.Frame(self.sidebar, bg=BioMatchTheme.SIDEBAR_BG)
        self.nav_container.pack(fill="both", expand=True)
        
        # Logout button container (to prevent duplication)
        self.logout_container = tk.Frame(self.sidebar, bg=BioMatchTheme.SIDEBAR_BG)
        self.logout_container.pack(side="bottom", fill="x", pady=20, padx=10)
        
        self.logout_btn = tk.Button(
            self.logout_container,
            text="🚪 Logout",
            font=("Segoe UI", 11, "bold"),
            bg=BioMatchTheme.DANGER,
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.logout
        )
        self.logout_btn.pack(fill="x", ipady=12)
        
        # ===== MAIN CONTENT AREA =====
        self.main_content = tk.Frame(self, bg=BioMatchTheme.LIGHT_BG)
        self.main_content.pack(side="right", fill="both", expand=True, padx=15, pady=15)
    
    def create_nav_buttons(self, nav_items):
        """Create navigation buttons in sidebar with active highlighting"""
        # Clear existing buttons
        for widget in self.nav_container.winfo_children():
            widget.destroy()
        
        # Get current page name
        current_page = self.__class__.__name__
        
        for icon, label, page, color in nav_items:
            # Darker color if this is the active page
            if page == current_page:
                btn_color = self.darken_color(color, 0.3)  # 30% darker
                font_weight = "bold"
            else:
                btn_color = color
                font_weight = "normal"
            
            btn = tk.Button(
                self.nav_container,
                text=f"{icon} {label}",
                font=("Segoe UI", 11, font_weight),
                bg=btn_color,
                fg="white",
                relief="flat",
                cursor="hand2",
                anchor="w",
                padx=20,
                command=lambda p=page: self.controller.show_frame(p)
            )
            btn.pack(fill="x", pady=5, ipady=12)
    
    def darken_color(self, hex_color, factor=0.3):
        """Darken a hex color by a factor (0-1)"""
        # Remove '#' if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Darken
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
        
        # Hover effects
        btn.bind("<Enter>", lambda e: btn.config(bg=color))
        btn.bind("<Leave>", lambda e: btn.config(bg=BioMatchTheme.SIDEBAR_BG))
    
    def perform_search(self):
        """Handle search bar - search for blood type"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Search", "Please enter a blood type to search (e.g., A+, O-, AB+)")
            return
        
        # Validate blood type format
        valid_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        query_upper = query.upper()
        
        if query_upper not in valid_types:
            messagebox.showwarning("Invalid Blood Type", 
                                 f"Please enter a valid blood type: {', '.join(valid_types)}")
            return
        
        # Perform search
        try:
            response = requests.post(f"{API_BASE_URL}/search_blood", json={
                "blood_type": query_upper,
                "units_needed": 1
            })
            
            if response.status_code == 200:
                results = response.json()
                if not results:
                    messagebox.showinfo("Search Results", 
                                      f"No compatible blood found for {query_upper}")
                else:
                    self.show_search_results(query_upper, results)
            else:
                messagebox.showerror("Error", "Search failed")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
    
    def show_search_results(self, blood_type, results):
        """Display search results in a popup window"""
        results_window = tk.Toplevel(self)
        results_window.title(f"Search Results for {blood_type}")
        results_window.geometry("800x450")
        
        # Header
        header = tk.Frame(results_window, bg=BioMatchTheme.PRIMARY, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text=f"Compatible Blood for {blood_type}", 
                font=("Segoe UI", 16, "bold"), 
                bg=BioMatchTheme.PRIMARY, fg="white").pack(pady=15)
        
        # Results table
        table_frame = tk.Frame(results_window, bg="white")
        table_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        columns = ("Blood Type", "Units", "Hospital", "Address", "Contact")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(fill="both", expand=True)
        
        for result in results:
            tree.insert("", tk.END, values=(
                result['blood_type'],
                result['units_available'],
                result['hospital_name'],
                result.get('address', 'N/A'),
                result.get('contact_number', 'N/A')
            ))
        
        # Close button
        ttk.Button(results_window, text="Close", 
                  command=results_window.destroy,
                  style="Primary.TButton").pack(pady=10)
    
    def update_user_info(self):
        """Update user info in header - to be overridden by subclasses"""
        pass
    
    def refresh_data(self):
        """Refresh page data - to be overridden by subclasses"""
        pass
    
    def logout(self):
        """Handle logout"""
        self.controller.set_current_user(None)
        self.controller.set_current_hospital(None)
        self.controller.show_frame("WelcomePage")
