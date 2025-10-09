import tkinter as tk
from tkinter import messagebox
import requests  # For sending requests to Flask backend

class BioMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("BioMatch - Blood Management System")
        self.root.geometry("400x300")

        # Example: Login form (expand as needed)
        self.label = tk.Label(root, text="Welcome to BioMatch")
        self.label.pack(pady=10)

        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        # Example: Send to Flask backend (update with your endpoints)
        try:
            response = requests.post('http://127.0.0.1:5000/login', json={'username': username, 'password': password})
            if response.status_code == 200:
                messagebox.showinfo("Success", "Logged in!")
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BioMatchApp(root)
    root.mainloop()