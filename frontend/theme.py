import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class BioMatchTheme:
    # Color palette
    PRIMARY = "#1976D2"  # Medical blue
    SECONDARY = "#E53935"  # Medical red
    BACKGROUND = "#FFFFFF"
    LIGHT_BG = "#F5F5F5"
    CARD_BG = "#FFFFFF"
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    BORDER = "#E0E0E0"
    SUCCESS = "#4CAF50"
    WARNING = "#FFC107"
    DANGER = "#F44336"
    
    # Font settings
    FONT_FAMILY = "Segoe UI"  # Cross-platform font that looks modern
    
    # Font sizes
    FONT_LARGE = 18
    FONT_MEDIUM = 14
    FONT_SMALL = 12
    FONT_MINI = 10
    
    # Font styles
    HEADER = (FONT_FAMILY, FONT_LARGE, "bold")
    SUBHEADER = (FONT_FAMILY, FONT_MEDIUM, "bold")
    BODY = (FONT_FAMILY, FONT_SMALL)
    BODY_BOLD = (FONT_FAMILY, FONT_SMALL, "bold")
    CAPTION = (FONT_FAMILY, FONT_MINI)
    
    # UI dimensions
    PADDING = 10
    MARGIN = 15
    BORDER_RADIUS = 5  # Not directly applicable in tkinter, but used as a design reference
    
    @staticmethod
    def apply_theme(root):
        """Apply the theme to the root window and configure styles"""
        style = ttk.Style()
        style.theme_use('clam')  # Use clam as base theme for better customization
        
        # Configure general styles
        style.configure('TFrame', background=BioMatchTheme.BACKGROUND)
        style.configure('Card.TFrame', background=BioMatchTheme.CARD_BG, relief='solid', borderwidth=1)
        style.configure('TLabel', background=BioMatchTheme.BACKGROUND, foreground=BioMatchTheme.TEXT_PRIMARY, font=BioMatchTheme.BODY)
        style.configure('Header.TLabel', font=BioMatchTheme.HEADER, foreground=BioMatchTheme.TEXT_PRIMARY)
        style.configure('Subheader.TLabel', font=BioMatchTheme.SUBHEADER, foreground=BioMatchTheme.TEXT_PRIMARY)
        
        # Button styles
        style.configure('TButton', font=BioMatchTheme.BODY_BOLD, background=BioMatchTheme.PRIMARY, foreground=BioMatchTheme.BACKGROUND)
        style.map('TButton',
                 background=[('active', BioMatchTheme.PRIMARY)],
                 foreground=[('active', BioMatchTheme.BACKGROUND)])
        
        # Primary button
        style.configure('Primary.TButton', background=BioMatchTheme.PRIMARY, foreground="white")
        style.map('Primary.TButton',
                 background=[('active', "#1565C0")],  # Darker blue on hover
                 foreground=[('active', "white")])
                 
        # Secondary button
        style.configure('Secondary.TButton', background=BioMatchTheme.SECONDARY, foreground="white")
        style.map('Secondary.TButton',
                 background=[('active', "#D32F2F")],  # Darker red on hover
                 foreground=[('active', "white")])
                 
        # Outline button
        style.configure('Outline.TButton', background="white", foreground=BioMatchTheme.PRIMARY)
        style.map('Outline.TButton',
                 background=[('active', "#E3F2FD")],  # Light blue on hover
                 foreground=[('active', BioMatchTheme.PRIMARY)])
        
        # Sidebar button
        style.configure('Sidebar.TButton', font=BioMatchTheme.BODY, background=BioMatchTheme.LIGHT_BG, 
                        foreground=BioMatchTheme.TEXT_PRIMARY, relief='flat', padding=10)
        style.map('Sidebar.TButton',
                 background=[('active', BioMatchTheme.PRIMARY)],
                 foreground=[('active', "white")])
        
        # Entry widget
        style.configure('TEntry', font=BioMatchTheme.BODY, fieldbackground="white", bordercolor=BioMatchTheme.BORDER)
        
        # Combobox
        style.configure('TCombobox', font=BioMatchTheme.BODY, fieldbackground="white")
        
        # Treeview (for tables)
        style.configure("Treeview", 
                        background="white", 
                        foreground=BioMatchTheme.TEXT_PRIMARY, 
                        rowheight=25, 
                        fieldbackground="white",
                        font=BioMatchTheme.BODY)
        style.configure("Treeview.Heading", 
                        font=BioMatchTheme.BODY_BOLD, 
                        background=BioMatchTheme.LIGHT_BG, 
                        foreground=BioMatchTheme.TEXT_PRIMARY)
        style.map("Treeview",
                 background=[('selected', BioMatchTheme.PRIMARY)],
                 foreground=[('selected', "white")])
        
        # Status-specific styles
        style.configure('Success.TLabel', foreground=BioMatchTheme.SUCCESS)
        style.configure('Warning.TLabel', foreground=BioMatchTheme.WARNING)
        style.configure('Danger.TLabel', foreground=BioMatchTheme.DANGER)

    @staticmethod
    def load_image(path, width=None, height=None):
        """Load and resize an image from path"""
        try:
            img = Image.open(path)
            if width and height:
                img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

class UIComponents:
    """Helper class for creating consistent UI components"""
    
    # Color scheme
    PRIMARY_COLOR = "#2196F3"
    SECONDARY_COLOR = "#1976D2"
    SUCCESS_COLOR = "#4CAF50"
    WARNING_COLOR = "#FF9800"
    ERROR_COLOR = "#F44336"
    BACKGROUND_COLOR = "#F5F5F5"
    SURFACE_COLOR = "#FFFFFF"
    TEXT_COLOR = "#212121"
    SUBTITLE_COLOR = "#757575"
    BORDER_COLOR = "#BDBDBD"
    
    @staticmethod
    def setup_styles():
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=UIComponents.BACKGROUND_COLOR)
        style.configure('TLabel', background=UIComponents.BACKGROUND_COLOR, foreground=UIComponents.TEXT_COLOR)
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TEntry', font=('Segoe UI', 10))
        style.configure('TCombobox', font=('Segoe UI', 10))
        
        # Primary button style
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton',
                 background=[('active', UIComponents.SECONDARY_COLOR)],
                 foreground=[('active', 'white')])
        
        # Header label style
        style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), 
                       foreground=UIComponents.TEXT_COLOR)
        
        # Subheader label style
        style.configure('Subheader.TLabel', font=('Segoe UI', 14, 'bold'), 
                       foreground=UIComponents.TEXT_COLOR)
        
        # Stat label style
        style.configure('Stat.TLabel', font=('Segoe UI', 12), 
                       background=UIComponents.SURFACE_COLOR)
        
        # Treeview style
        style.configure('Treeview', font=('Segoe UI', 10), rowheight=25)
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
    
    @staticmethod
    def create_card(parent, title=""):
        """Create a card container with optional title"""
        card = ttk.Frame(parent, relief="solid", borderwidth=1)
        card.pack(fill="x", pady=10)
        
        if title:
            title_label = ttk.Label(card, text=title, style="Subheader.TLabel")
            title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        content = ttk.Frame(card)
        content.pack(fill="both", expand=True, padx=15, pady=10)
        
        return card, content
    
    @staticmethod
    def create_table(parent, columns, height=10):
        """Create a styled treeview table"""
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        return tree
    
    @staticmethod
    def create_stat_card(parent, label, value, color=None):
        """Create a statistics card"""
        if color is None:
            color = UIComponents.PRIMARY_COLOR
        
        stat_frame = ttk.Frame(parent)
        stat_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        value_label = tk.Label(stat_frame, text=str(value), font=('Segoe UI', 24, 'bold'),
                              fg=color, bg=UIComponents.BACKGROUND_COLOR)
        value_label.pack()
        
        label_text = tk.Label(stat_frame, text=label, font=('Segoe UI', 10),
                             fg=UIComponents.SUBTITLE_COLOR, bg=UIComponents.BACKGROUND_COLOR)
        label_text.pack()
    
    @staticmethod
    def create_input_field(parent, label_text, row, column, width=30, is_password=False):
        """Create a labeled input field"""
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, sticky="w", pady=5, padx=(0, 10))
        
        entry = ttk.Entry(parent, width=width, show="*" if is_password else "")
        entry.grid(row=row, column=column + 1, pady=5)
        
        return entry
    
    @staticmethod
    def show_info_message(title, message):
        """Display an info message dialog"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_error_message(title, message):
        """Display an error message dialog"""
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_warning_message(title, message):
        """Display a warning message dialog"""
        from tkinter import messagebox
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_success_message(title, message):
        """Display a success message dialog"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
