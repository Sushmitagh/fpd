# app.py - Main application file for Fake Profile Detector

import os
import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import datetime

# Sample data (in a real app, this would come from an API)
sample_followers = [
    {"username": "user1", "profile_pic": True, "bio": True, "links": True, 
     "posts_count": 120, "creation_date": "2020-05-15", "engagement_ratio": 0.8},
    {"username": "bot_account123", "profile_pic": False, "bio": False, "links": False, 
     "posts_count": 2, "creation_date": "2023-12-01", "engagement_ratio": 0.1},
    {"username": "real_person22", "profile_pic": True, "bio": True, "links": True, 
     "posts_count": 67, "creation_date": "2021-09-23", "engagement_ratio": 0.6},
    {"username": "suspicious_user", "profile_pic": True, "bio": False, "links": False, 
     "posts_count": 5, "creation_date": "2023-11-20", "engagement_ratio": 0.2},
    {"username": "active_user99", "profile_pic": True, "bio": True, "links": True, 
     "posts_count": 230, "creation_date": "2019-03-10", "engagement_ratio": 0.75},
    {"username": "new_account444", "profile_pic": False, "bio": True, "links": False, 
     "posts_count": 1, "creation_date": "2024-04-01", "engagement_ratio": 0.05},
    {"username": "regular_poster", "profile_pic": True, "bio": True, "links": False, 
     "posts_count": 85, "creation_date": "2022-07-18", "engagement_ratio": 0.5},
]

class FakeProfileDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake Profile Detector")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self.current_user = None
        self.setup_login_screen()
    
    def setup_login_screen(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Login frame
        login_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        login_frame.pack(expand=True)
        
        # App title
        title_label = tk.Label(login_frame, text="Fake Profile Detector", 
                              font=("Arial", 24, "bold"), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # Username field
        username_label = tk.Label(login_frame, text="Username:", 
                                 font=("Arial", 12), bg="#f0f0f0")
        username_label.pack(anchor="w", pady=(10, 0))
        
        self.username_entry = tk.Entry(login_frame, font=("Arial", 12), width=30)
        self.username_entry.pack(pady=(5, 15), ipady=5)
        
        # Password field
        password_label = tk.Label(login_frame, text="Password:", 
                                 font=("Arial", 12), bg="#f0f0f0")
        password_label.pack(anchor="w", pady=(10, 0))
        
        self.password_entry = tk.Entry(login_frame, font=("Arial", 12), 
                                      width=30, show="•")
        self.password_entry.pack(pady=(5, 20), ipady=5)
        
        # Login button
        login_button = tk.Button(login_frame, text="Login", font=("Arial", 12, "bold"),
                               bg="#4285f4", fg="white", width=15, pady=5,
                               command=self.authenticate_user)
        login_button.pack(pady=10)
    
    def authenticate_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Simple authentication (in a real app, you'd verify against a database)
        if username and password:  # Just check if fields aren't empty
            self.current_user = username
            messagebox.showinfo("Success", f"Welcome, {username}!")
            self.display_main_interface()
        else:
            messagebox.showerror("Error", "Please enter both username and password")
    
    def display_main_interface(self):
        # Clear login screen
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # Create a notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create tabs
        dashboard_tab = ttk.Frame(notebook)
        analysis_tab = ttk.Frame(notebook)
        suspicious_tab = ttk.Frame(notebook)
        
        notebook.add(dashboard_tab, text="Dashboard")
        notebook.add(analysis_tab, text="Follower Analysis")
        notebook.add(suspicious_tab, text="Suspicious Accounts")
        
        # Dashboard Tab
        self.setup_dashboard(dashboard_tab)
        
        # Analysis Tab
        self.setup_analysis_tab(analysis_tab)
        
        # Suspicious Accounts Tab
        self.setup_suspicious_tab(suspicious_tab)
        
        # Logout button in the main window
        logout_btn = tk.Button(self.root, text="Logout", 
                              command=self.setup_login_screen,
                              bg="#f44336", fg="white")
        logout_btn.pack(side="bottom", pady=10)
    
    def setup_dashboard(self, parent):
        # Welcome message
        welcome_frame = tk.Frame(parent, bg="#f0f0f0")
        welcome_frame.pack(fill="x", pady=10)
        
        welcome_label = tk.Label(welcome_frame, 
                                text=f"Welcome {self.current_user}!",
                                font=("Arial", 16, "bold"),
                                bg="#f0f0f0")
        welcome_label.pack(pady=5)
        
        # Display date and time
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        date_label = tk.Label(welcome_frame, 
                             text=f"Today is {current_date}",
                             font=("Arial", 12),
                             bg="#f0f0f0")
        date_label.pack()
        
        # Summary frame
        summary_frame = tk.Frame(parent, bg="white", padx=20, pady=20)
        summary_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create a pie chart of real vs fake accounts
        fig, ax = plt.subplots(figsize=(5, 4))
        
        # Analyze followers and get counts
        real, fake = self.analyze_followers()
        
        # Create pie chart
        labels = ['Real Accounts', 'Suspicious Accounts']
        sizes = [real, fake]
        colors = ['#4CAF50', '#F44336']
        explode = (0, 0.1)  # explode the 2nd slice (fake accounts)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
              autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Create canvas to display the matplotlib figure
        canvas = FigureCanvasTkAgg(fig, summary_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Summary stats
        stats_frame = tk.Frame(summary_frame, bg="white")
        stats_frame.pack(fill="x", pady=10)
        
        total_label = tk.Label(stats_frame, 
                              text=f"Total Followers: {len(sample_followers)}",
                              font=("Arial", 12, "bold"),
                              bg="white")
        total_label.pack(side="left", padx=20)
        
        real_label = tk.Label(stats_frame, 
                             text=f"Real Accounts: {real}",
                             font=("Arial", 12),
                             fg="#4CAF50",
                             bg="white")
        real_label.pack(side="left", padx=20)
        
        fake_label = tk.Label(stats_frame, 
                             text=f"Suspicious Accounts: {fake}",
                             font=("Arial", 12),
                             fg="#F44336",
                             bg="white")
        fake_label.pack(side="left", padx=20)
    
    def setup_analysis_tab(self, parent):
        # Create a frame for the analysis view
        analysis_frame = tk.Frame(parent, bg="white")
        analysis_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(analysis_frame, 
                              text="Follower Account Analysis",
                              font=("Arial", 16, "bold"),
                              bg="white")
        title_label.pack(pady=10)
        
        # Create treeview
        columns = ("Username", "Profile Pic", "Bio", "Posts", "Creation Date", "Engagement", "Status")
        tree = ttk.Treeview(analysis_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        # Add data to the treeview
        for follower in sample_followers:
            # Calculate if account is suspicious
            is_suspicious = self.is_suspicious_account(follower)
            status = "Suspicious" if is_suspicious else "Genuine"
            status_color = "#F44336" if is_suspicious else "#4CAF50"
            
            # Add row
            tree.insert("", "end", values=(
                follower["username"],
                "Yes" if follower["profile_pic"] else "No",
                "Yes" if follower["bio"] else "No",
                follower["posts_count"],
                follower["creation_date"],
                f"{follower['engagement_ratio']:.2f}",
                status
            ), tags=(status,))
        
        # Apply colors
        tree.tag_configure("Suspicious", background="#FFEBEE")
        tree.tag_configure("Genuine", background="#E8F5E9")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(analysis_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(expand=True, fill="both")
    
    def setup_suspicious_tab(self, parent):
        # Create a frame for suspicious accounts
        suspicious_frame = tk.Frame(parent, bg="white")
        suspicious_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(suspicious_frame, 
                              text="Suspicious Accounts Detected",
                              font=("Arial", 16, "bold"),
                              bg="white")
        title_label.pack(pady=10)
        
        # Create a frame for each suspicious account
        suspicious_accounts = [f for f in sample_followers if self.is_suspicious_account(f)]
        
        if not suspicious_accounts:
            no_accounts_label = tk.Label(suspicious_frame, 
                                        text="No suspicious accounts detected!",
                                        font=("Arial", 12),
                                        bg="white")
            no_accounts_label.pack(pady=50)
            return
        
        # Create a canvas with scrollbar for the suspicious accounts
        canvas = tk.Canvas(suspicious_frame, bg="white")
        scrollbar = ttk.Scrollbar(suspicious_frame, orient="vertical", command=canvas.yview)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create a frame inside the canvas
        accounts_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=accounts_frame, anchor="nw")
        
        # Add suspicious accounts to the frame
        for i, account in enumerate(suspicious_accounts):
            self.create_account_card(accounts_frame, account, i)
        
        # Update scroll region
        accounts_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
    
    def create_account_card(self, parent, account, index):
        # Create a frame for each account
        card = tk.Frame(parent, bg="#FFEBEE", padx=15, pady=15, relief="raised", bd=1)
        card.pack(fill="x", pady=10, padx=20)
        
        # Username header
        username_label = tk.Label(card, 
                                 text=account["username"],
                                 font=("Arial", 14, "bold"),
                                 bg="#FFEBEE")
        username_label.pack(anchor="w")
        
        # Details
        details_frame = tk.Frame(card, bg="#FFEBEE")
        details_frame.pack(fill="x", pady=5)
        
        # Left column - Account details
        left_col = tk.Frame(details_frame, bg="#FFEBEE")
        left_col.pack(side="left", fill="both", expand=True)
        
        tk.Label(left_col, text=f"Created: {account['creation_date']}", 
                bg="#FFEBEE").pack(anchor="w")
        tk.Label(left_col, text=f"Posts: {account['posts_count']}", 
                bg="#FFEBEE").pack(anchor="w")
        tk.Label(left_col, text=f"Engagement Ratio: {account['engagement_ratio']:.2f}", 
                bg="#FFEBEE").pack(anchor="w")
        
        # Right column - Flags
        right_col = tk.Frame(details_frame, bg="#FFEBEE")
        right_col.pack(side="right", fill="both", expand=True)
        
        # Flags
        flags = []
        if not account["profile_pic"]:
            flags.append("No Profile Picture")
        if not account["bio"]:
            flags.append("No Bio")
        if account["posts_count"] < 10:
            flags.append("Low Post Count")
        if account["engagement_ratio"] < 0.3:
            flags.append("Low Engagement")
        
        tk.Label(right_col, text="Suspicious flags:", font=("Arial", 10, "bold"), 
                bg="#FFEBEE").pack(anchor="w")
        
        for flag in flags:
            flag_label = tk.Label(right_col, text=f"• {flag}", bg="#FFEBEE")
            flag_label.pack(anchor="w")
    
    def analyze_followers(self):
        # Count real and fake accounts
        real_count = 0
        fake_count = 0
        
        for follower in sample_followers:
            if self.is_suspicious_account(follower):
                fake_count += 1
            else:
                real_count += 1
                
        return real_count, fake_count
    
    def is_suspicious_account(self, account):
        # Define criteria for suspicious accounts
        suspicious_flags = 0
        
        # Check profile completeness
        if not account["profile_pic"]:
            suspicious_flags += 1
        if not account["bio"]:
            suspicious_flags += 1
        if not account["links"]:
            suspicious_flags += 0.5
            
        # Check activity and engagement
        if account["posts_count"] < 5:
            suspicious_flags += 1
        if account["engagement_ratio"] < 0.3:
            suspicious_flags += 1
            
        # Check account age (assuming date format YYYY-MM-DD)
        creation_date = datetime.datetime.strptime(account["creation_date"], "%Y-%m-%d")
        today = datetime.datetime.now()
        account_age = (today - creation_date).days
        
        if account_age < 30:  # Less than a month old
            suspicious_flags += 1
            
        # Determine if account is suspicious based on flags
        return suspicious_flags >= 2

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FakeProfileDetector(root)
    root.mainloop()


