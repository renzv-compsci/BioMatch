import tkinter as tk
from login_page import LoginPage
from signup_page import SignupPage

class BioMatchApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BioMatch")
        self.geometry("400x350")
        self.resizable(False, False)
        self.user_info = None
        self.show_login_page()

    def show_login_page(self):
        self.clear_frame()
        self.login_page = LoginPage(self, self.on_login_success, self.show_signup_page)
        self.login_page.pack(fill="both", expand=True)

    def show_signup_page(self):
        self.clear_frame()
        self.signup_page = SignupPage(self, self.show_login_page, self.show_login_page)
        self.signup_page.pack(fill="both", expand=True)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

    def on_login_success(self, user_info):
        self.user_info = user_info
        self.clear_frame()
        # For now, just show a welcome message after login
        tk.Label(self, text=f"Welcome, {user_info['username']}!", font=("Arial", 16)).pack(pady=20)
        tk.Label(self, text=f"Role: {user_info['role']}").pack(pady=5)
        tk.Button(self, text="Logout", command=self.show_login_page).pack(pady=20)

if __name__ == "__main__":
    app = BioMatchApp()
    app.mainloop()