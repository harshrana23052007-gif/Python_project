"""
Main Application for Smart Expense Analyzer
Core application logic and window management with CustomTkinter
"""

import tkinter as tk
import customtkinter as ctk
import config
from database.db_manager import DatabaseManager
from ui.themes import ThemeManager
from ui.frames import LoginFrame, DashboardFrame, AddExpenseFrame, ReportsFrame, SettingsFrame, SpendingHeatmapFrame

# Set appearance and default theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SmartExpenseAnalyzer(ctk.CTk):
    """Main application class using CustomTkinter"""
    
    def __init__(self):
        super().__init__()
        
        self.title(config.WINDOW_TITLE)
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.MIN_WIDTH, config.MIN_HEIGHT)
        
        # Initialize database
        self.db = DatabaseManager()
        
        # User authentication
        self.current_user_id = None
        self.current_username = None
        
        # Default theme (light mode with colorful colors)
        self.dark_mode = False
        self.current_theme = ThemeManager.get_theme(self.dark_mode)
        
        # Configure appearance
        ctk.set_appearance_mode("light")
        self.configure(fg_color=self.current_theme['bg'])
        
        # Create main layout
        self.create_widgets()
    
    def create_widgets(self):
        """Create main UI components"""
        # Main container - will hold sidebar + content
        self.main_container = ctk.CTkFrame(self, fg_color=self.current_theme['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar container (left side) - created but will be hidden initially
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=250,
            fg_color=self.current_theme['sidebar_bg'],
            border_width=2,
            border_color=self.current_theme['border']
        )
        self.sidebar.pack_propagate(False)  # Fixed width
        # DON'T pack initially - will be packed on demand
        
        # Content container (right side) - will hold the actual page frames
        self.content_container = ctk.CTkFrame(self.main_container, fg_color=self.current_theme['bg'])
        self.content_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create frames dictionary to hold different pages
        self.frames = {}
        
        # Create all frames inside content_container
        for F in (LoginFrame, DashboardFrame, AddExpenseFrame, ReportsFrame, SpendingHeatmapFrame, SettingsFrame):
            frame = F(self.content_container, self)
            self.frames[F] = frame
            frame.pack(fill=tk.BOTH, expand=True)
            frame.pack_forget()  # Hide all frames initially
        
        # Show login frame first (will hide sidebar)
        self.show_frame(LoginFrame)
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        # Clear any existing widgets
        for widget in self.sidebar.winfo_children():
            widget.destroy()
        
        # Header
        header = ctk.CTkLabel(
            self.sidebar,
            text="Navigation",
            font=(config.FONT_FAMILY, 14, 'bold'),
            text_color=self.current_theme['text_primary']
        )
        header.pack(padx=15, pady=(20, 30))
        
        # Navigation buttons with icons/emojis
        buttons = [
            ("📊 Dashboard", DashboardFrame),
            ("➕ Add Expense", AddExpenseFrame),
            ("📈 Reports", ReportsFrame),
            ("🔥 Spending Heat", SpendingHeatmapFrame),
            ("⚙️ Settings", SettingsFrame),
        ]
        
        for label, frame_class in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label,
                command=lambda f=frame_class: self.show_frame(f),
                fg_color=self.current_theme['button_bg'],
                hover_color=self.current_theme['button_hover'],
                text_color=self.current_theme['button_fg'],
                font=(config.FONT_FAMILY, 12, 'bold'),
                height=50,
                corner_radius=8,
                border_width=0
            )
            btn.pack(padx=15, pady=8, fill=tk.X)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            command=self.logout,
            fg_color=self.current_theme['danger'],
            hover_color='#c0392b',
            text_color='#ffffff',
            font=(config.FONT_FAMILY, 12, 'bold'),
            height=40,
            corner_radius=8,
            border_width=0
        )
        logout_btn.pack(padx=15, pady=(30, 20), fill=tk.X, side=tk.BOTTOM)
        
        # Pack sidebar
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
    
    def show_frame(self, cont):
        """Show specified frame"""
        # IMPORTANT: Hide ALL frames first
        for frame_class in self.frames:
            self.frames[frame_class].pack_forget()
        
        # Get the frame to show
        frame = self.frames[cont]
        
        # Call refresh if available
        if hasattr(frame, 'refresh'):
            frame.refresh()
        
        # Hide sidebar for login frame
        if cont == LoginFrame:
            self.sidebar.pack_forget()
        else:
            self.create_sidebar()
        
        # NOW pack the selected frame (without tkraise)
        frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
    
    def logout(self):
        """Handle logout"""
        self.current_user_id = None
        self.current_username = None
        self.show_frame(LoginFrame)


if __name__ == "__main__":
    app = SmartExpenseAnalyzer()
    app.mainloop()
