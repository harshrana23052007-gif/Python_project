"""
UI Frames for Smart Expense Analyzer using CustomTkinter
Contains all frame classes for different views with modern styling
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime
import calendar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox, filedialog
import config
from utils.validators import validate_all_expense_fields, validate_budget
from utils.auth_utils import validate_username, validate_password
from reports.chart_generator import ChartGenerator
from reports.pdf_generator import export_report_to_pdf


class LoginFrame(ctk.CTkFrame):
    """Login and registration screen with modern design"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create login form widgets"""
        theme = self.controller.current_theme
        
        # Center container
        center_frame = ctk.CTkFrame(self, fg_color=theme['bg'])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            center_frame,
            text="💰 Smart Expense Analyzer",
            font=(config.FONT_FAMILY, 32, 'bold'),
            text_color=theme['accent']
        )
        title.pack(pady=(0, 10))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            center_frame,
            text="Manage your finances intelligently",
            font=(config.FONT_FAMILY, 14),
            text_color=theme['text_secondary']
        )
        subtitle.pack(pady=(0, 40))
        
        # Card frame
        card = ctk.CTkFrame(center_frame, fg_color=theme['card_bg'], corner_radius=15, border_width=2, border_color=theme['card_border'])
        card.pack(padx=20, pady=20)
        
        inner_frame = ctk.CTkFrame(card, fg_color=theme['card_bg'])
        inner_frame.pack(padx=30, pady=30)
        
        # Username
        ctk.CTkLabel(
            inner_frame,
            text="Username",
            font=(config.FONT_FAMILY, 12, 'bold'),
            text_color=theme['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            inner_frame,
            width=300,
            height=40,
            fg_color=theme['entry_bg'],
            text_color=theme['entry_fg'],
            border_color=theme['entry_border'],
            border_width=2,
            font=(config.FONT_FAMILY, 12),
            placeholder_text="Enter username",
            placeholder_text_color=theme['text_secondary']
        )
        self.username_entry.pack(pady=(0, 20))
        self.username_entry.bind('<Return>', lambda e: self.login())
        
        # Password
        ctk.CTkLabel(
            inner_frame,
            text="Password",
            font=(config.FONT_FAMILY, 12, 'bold'),
            text_color=theme['text_primary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            inner_frame,
            width=300,
            height=40,
            fg_color=theme['entry_bg'],
            text_color=theme['entry_fg'],
            border_color=theme['entry_border'],
            border_width=2,
            font=(config.FONT_FAMILY, 12),
            placeholder_text="Enter password",
            placeholder_text_color=theme['text_secondary'],
            show="●"
        )
        self.password_entry.pack(pady=(0, 30))
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Buttons
        button_frame = ctk.CTkFrame(inner_frame, fg_color=theme['card_bg'])
        button_frame.pack(fill="x")
        
        login_btn = ctk.CTkButton(
            button_frame,
            text="Login",
            font=(config.FONT_FAMILY, 14, 'bold'),
            height=40,
            corner_radius=8,
            fg_color=theme['button_bg'],
            hover_color=theme['button_hover'],
            text_color=theme['button_fg'],
            command=self.login
        )
        login_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        signup_btn = ctk.CTkButton(
            button_frame,
            text="Sign Up",
            font=(config.FONT_FAMILY, 14, 'bold'),
            height=40,
            corner_radius=8,
            fg_color=theme['accent_light'],
            hover_color=theme['button_hover'],
            text_color=theme['text_primary'],
            command=self.show_signup
        )
        signup_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # Error label
        self.error_label = ctk.CTkLabel(
            inner_frame,
            text="",
            font=(config.FONT_FAMILY, 11),
            text_color=theme['danger']
        )
        self.error_label.pack(pady=(20, 0))
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter username and password")
            return
        
        success, message, user_id = self.db.login_user(username, password)
        
        if success:
            self.controller.current_user_id = user_id
            self.controller.current_username = username
            self.controller.frames[DashboardFrame].refresh()
            self.controller.show_frame(DashboardFrame)
        else:
            self.error_label.configure(text=f"Login failed: {message}")
    
    def show_signup(self):
        """Show signup dialog"""
        signup_window = ctk.CTkToplevel(self.controller)
        signup_window.title("Sign Up")
        signup_window.geometry("450x550")
        signup_window.resizable(False, False)
        
        theme = self.controller.current_theme
        signup_window.configure(fg_color=theme['bg'])
        
        # Center window
        signup_window.transient(self.controller)
        signup_window.grab_set()
        
        frame = ctk.CTkFrame(signup_window, fg_color=theme['bg'])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            frame,
            text="Create New Account",
            font=(config.FONT_FAMILY, 24, 'bold'),
            text_color=theme['accent']
        ).pack(pady=(0, 30))
        
        # Username
        ctk.CTkLabel(frame, text="Username (3-20 chars):", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(5, 0))
        username_entry = ctk.CTkEntry(frame, width=300, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_width=2, font=(config.FONT_FAMILY, 11))
        username_entry.pack(fill="x", pady=(0, 20))
        
        # Password
        ctk.CTkLabel(frame, text="Password (6+ characters):", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(5, 0))
        password_entry = ctk.CTkEntry(frame, width=300, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_width=2, font=(config.FONT_FAMILY, 11), show="●")
        password_entry.pack(fill="x", pady=(0, 20))
        
        # Confirm Password
        ctk.CTkLabel(frame, text="Confirm Password:", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(5, 0))
        confirm_entry = ctk.CTkEntry(frame, width=300, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_width=2, font=(config.FONT_FAMILY, 11), show="●")
        confirm_entry.pack(fill="x", pady=(0, 20))
        
        # Error label
        error_label = ctk.CTkLabel(frame, text="", font=(config.FONT_FAMILY, 11), text_color=theme['danger'])
        error_label.pack(pady=10)
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            # Validate
            valid, msg = validate_username(username)
            if not valid:
                error_label.configure(text=f"Username: {msg}")
                return
            
            valid, msg = validate_password(password)
            if not valid:
                error_label.configure(text=f"Password: {msg}")
                return
            
            if password != confirm:
                error_label.configure(text="Passwords don't match")
                return
            
            # Register
            success, message, user_id = self.db.register_user(username, password)
            
            if success:
                messagebox.showinfo("Success", "Account created! You can now log in.")
                signup_window.destroy()
            else:
                error_label.configure(text=message)
        
        # Register button
        register_btn = ctk.CTkButton(
            frame,
            text="Create Account",
            height=45,
            font=(config.FONT_FAMILY, 14, 'bold'),
            corner_radius=10,
            fg_color=theme['button_bg'],
            hover_color=theme['button_hover'],
            command=register
        )
        register_btn.pack(pady=20, fill="x")


class DashboardFrame(ctk.CTkFrame):
    """Dashboard view showing expense overview"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        
        # Import utilities
        try:
            from utils.financial_advisor import FinancialAdvisor
            from utils.gamification import GamificationManager
            from utils.personality_analyzer import PersonalityAnalyzer
            from utils.simulation_engine import SimulationEngine
            self.advisor = None
            self.gamification = None
            self.personality_analyzer = None
            self.simulation_engine = None
        except Exception as e:
            self.advisor = None
            self.gamification = None
            self.personality_analyzer = None
            self.simulation_engine = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dashboard widgets"""
        theme = self.controller.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color=theme['accent'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(
            header,
            text="📊 Dashboard",
            font=(config.FONT_FAMILY, 28, 'bold'),
            text_color="#ffffff"
        )
        title.pack(pady=20)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(self, fg_color=theme['bg'])
        stats_frame.pack(fill="x", padx=20, pady=20)
        
        # Create stat cards
        self.total_label = self._create_stat_card(stats_frame, "This Month", "$0.00", "📊", theme['success'])
        self.budget_label = self._create_stat_card(stats_frame, "Monthly Budget", "$0.00", "💰", theme['info'])
        self.remaining_label = self._create_stat_card(stats_frame, "Remaining", "$0.00", "✅", theme['danger'])
        
        # Scrollable content
        scrollable = ctk.CTkScrollableFrame(self, fg_color=theme['bg'], label_text="")
        scrollable.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Financial Advisor
        advisor_frame = self._create_section_frame(scrollable, "💡 Financial Advisor", theme)
        self.advisor_text = tk.Text(
            advisor_frame,
            height=9,
            width=80,
            bg=theme['entry_bg'],
            fg=theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=theme['accent']
        )
        self.advisor_text.pack(fill="both", expand=True)
        self.advisor_text.insert(tk.END, "Loading advisor data...")
        
        # Achievements
        achievements_frame = self._create_section_frame(scrollable, "🏆 Achievements", theme)
        self.achievements_canvas = tk.Canvas(
            achievements_frame,
            height=120,
            bg=theme['entry_bg'],
            highlightthickness=0,
            relief=tk.FLAT
        )
        self.achievements_canvas.pack(fill="both", expand=True)
        
        self.streak_label = ctk.CTkLabel(
            achievements_frame,
            text="Loading achievements...",
            font=(config.FONT_FAMILY, 11),
            text_color=theme['text_primary']
        )
        self.streak_label.pack(pady=10)
        
        # What-If Simulator
        simulator_frame = self._create_section_frame(scrollable, "🎯 What-If Simulator", theme)
        
        sim_controls = ctk.CTkFrame(simulator_frame, fg_color=theme['bg'])
        sim_controls.pack(fill="x", pady=10)
        
        ctk.CTkLabel(sim_controls, text="Category:", font=(config.FONT_FAMILY, 11), text_color=theme['text_primary']).pack(side="left", padx=5)
        self.sim_category_var = tk.StringVar(value=config.EXPENSE_CATEGORIES[0])
        self.sim_category_combo = ctk.CTkComboBox(
            sim_controls,
            variable=self.sim_category_var,
            values=config.EXPENSE_CATEGORIES,
            width=120,
            height=35,
            font=(config.FONT_FAMILY, 11),
            fg_color=theme['entry_bg'],
            text_color=theme['entry_fg'],
            border_color=theme['entry_border']
        )
        self.sim_category_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(sim_controls, text="Reduce by:", font=(config.FONT_FAMILY, 11), text_color=theme['text_primary']).pack(side="left", padx=5)
        self.sim_percent_var = tk.StringVar(value="10")
        self.sim_percent_entry = ctk.CTkEntry(
            sim_controls,
            textvariable=self.sim_percent_var,
            width=60,
            height=35,
            font=(config.FONT_FAMILY, 11),
            fg_color=theme['entry_bg'],
            text_color=theme['entry_fg'],
            border_color=theme['entry_border']
        )
        self.sim_percent_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(sim_controls, text="%", font=(config.FONT_FAMILY, 11), text_color=theme['text_primary']).pack(side="left", padx=5)
        
        simulate_btn = ctk.CTkButton(
            sim_controls,
            text="📊 Simulate",
            height=35,
            font=(config.FONT_FAMILY, 11, 'bold'),
            fg_color=theme['button_bg'],
            hover_color=theme['button_hover'],
            command=self.run_simulation
        )
        simulate_btn.pack(side="left", padx=5)
        
        self.simulator_text = tk.Text(
            simulator_frame,
            height=8,
            width=80,
            bg=theme['entry_bg'],
            fg=theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=theme['accent']
        )
        self.simulator_text.pack(fill="both", expand=True, pady=10)
        
        # Category breakdown
        category_frame = self._create_section_frame(scrollable, "📊 Category Breakdown", theme)
        self.category_text = tk.Text(
            category_frame,
            height=8,
            width=80,
            bg=theme['entry_bg'],
            fg=theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=theme['accent']
        )
        self.category_text.pack(fill="both", expand=True)
        self.category_text.insert(tk.END, "Loading category breakdown...")
        
        # Recent transactions
        recent_frame = self._create_section_frame(scrollable, "📝 Recent Transactions", theme)
        self.recent_text = tk.Text(
            recent_frame,
            height=6,
            width=80,
            bg=theme['entry_bg'],
            fg=theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=theme['accent']
        )
        self.recent_text.pack(fill="both", expand=True)
        self.recent_text.insert(tk.END, "Loading recent transactions...")
    
    def _create_stat_card(self, parent, title, value, emoji, color):
        """Create a colorful stat card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.pack(side="left", padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(
            card,
            text=f"{emoji} {title}",
            font=(config.FONT_FAMILY, 12, 'bold'),
            text_color="#ffffff"
        ).pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(config.FONT_FAMILY, 20, 'bold'),
            text_color="#ffffff"
        )
        value_label.pack(pady=(5, 15))
        
        return value_label
    
    def _create_section_frame(self, parent, title, theme):
        """Create a section frame with title"""
        # Outer frame with border
        outer = ctk.CTkFrame(parent, fg_color=theme['card_bg'], corner_radius=10, border_width=2, border_color=theme['card_border'])
        outer.pack(fill="x", padx=20, pady=10)
        
        # Title
        ctk.CTkLabel(
            outer,
            text=title,
            font=(config.FONT_FAMILY, 14, 'bold'),
            text_color=theme['accent']
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Content frame
        content = ctk.CTkFrame(outer, fg_color=theme['card_bg'])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        return content
    
    def refresh(self):
        """Refresh dashboard data"""
        user_id = self.controller.current_user_id
        if not user_id:
            return
        
        theme = self.controller.current_theme
        
        try:
            from utils.financial_advisor import FinancialAdvisor
            from utils.gamification import GamificationManager
            from utils.personality_analyzer import PersonalityAnalyzer
            from utils.simulation_engine import SimulationEngine
            
            self.advisor = FinancialAdvisor(self.db, user_id)
            self.gamification = GamificationManager(self.db, user_id)
            self.personality_analyzer = PersonalityAnalyzer(self.db, user_id)
            self.simulation_engine = SimulationEngine(self.db, user_id)
        except Exception as e:
            pass
        
        try:
            current_total = self.db.get_current_month_total(user_id)
            settings = self.db.get_settings(user_id)
            budget = settings[0]
            remaining = budget - current_total
            
            self.total_label.configure(text=f"${current_total:.2f}")
            self.budget_label.configure(text=f"${budget:.2f}")
            self.remaining_label.configure(text=f"${remaining:.2f}")
            
            all_expenses = self.db.get_all_expenses(user_id)
            is_empty = len(all_expenses) == 0
            
            # Update advisor
            self.advisor_text.delete(1.0, tk.END)
            if is_empty:
                self.advisor_text.insert(tk.END, "Welcome to Smart Expense Analyzer!\n\n")
                self.advisor_text.insert(tk.END, "Getting Started:\n1. Add your first expense\n2. Track spending\n3. View insights\n4. Receive smart tips")
            else:
                if self.advisor:
                    analysis = self.advisor.analyze_spending_patterns()
                    self.advisor_text.insert(tk.END, f"Budget Status: {analysis['budget_status']}\n\n")
                    if analysis['overspending_categories']:
                        self.advisor_text.insert(tk.END, "Overspending Categories:\n")
                        for cat in analysis['overspending_categories']:
                            self.advisor_text.insert(tk.END, f"  • {cat['category']}: ${cat['amount']:.2f} - Save ${cat['savings_potential']:.2f}\n")
                    self.advisor_text.insert(tk.END, "\nSmart Tips:\n")
                    for i, tip in enumerate(analysis['saving_tips'], 1):
                        self.advisor_text.insert(tk.END, f"{i}. {tip}\n")
            
            # Update achievements
            try:
                current_streak, longest_streak, _ = self.db.get_streak_info(user_id)
                self.streak_label.configure(text=f"Current: {current_streak} days | Longest: {longest_streak} days")
            except:
                pass
            
            # Draw badges
            self.achievements_canvas.delete("all")
            try:
                if self.gamification:
                    earned_badges = self.gamification.get_earned_badges()
                    if earned_badges:
                        x_pos = 20
                        y_start = 15
                        for badge in earned_badges:
                            try:
                                self.achievements_canvas.create_text(x_pos, y_start, text=f"{badge['icon']}", font=("Arial", 40), anchor="nw")
                                self.achievements_canvas.create_text(x_pos + 50, y_start, text=f"{badge['name']}\n{badge['description']}", font=(config.FONT_FAMILY, 9), fill=theme['text_primary'], anchor="nw", width=150)
                                x_pos += 250
                            except (KeyError, ValueError):
                                continue
                    else:
                        self.achievements_canvas.create_text(10, 20, text="No badges earned yet. Add more expenses to earn achievements!", font=(config.FONT_FAMILY, 11), fill=theme['text_secondary'], anchor="nw")
                else:
                    self.achievements_canvas.create_text(10, 20, text="Loading achievements...", font=(config.FONT_FAMILY, 11), fill=theme['text_secondary'], anchor="nw")
            except Exception as e:
                self.achievements_canvas.create_text(10, 20, text="Achievement data unavailable", font=(config.FONT_FAMILY, 11), fill=theme['text_secondary'], anchor="nw")
            
            # Category breakdown
            now = datetime.now()
            categories = self.db.get_category_summary(user_id, now.year, now.month)
            self.category_text.delete(1.0, tk.END)
            self.category_text.insert(tk.END, "Category Breakdown: ═══════════════════════════════════════\n")
            for category, amount in categories:
                percentage = (amount / current_total * 100) if current_total > 0 else 0
                self.category_text.insert(tk.END, f"{category:15} ${amount:8.2f} ({percentage:5.1f}%)\n")
            
            # Recent transactions
            recent = self.db.get_recent_expenses(user_id, config.RECENT_LIMIT)
            self.recent_text.delete(1.0, tk.END)
            self.recent_text.insert(tk.END, "Date        Category      Amount   Description\n" + "═" * 80 + "\n")
            for expense in recent:
                _, _, amount, cat, date, desc, _ = expense
                d = desc[:30] if desc else "N/A"
                self.recent_text.insert(tk.END, f"{date} {cat:12} ${amount:7.2f} {d}\n")
        except Exception as e:
            pass
    
    def run_simulation(self):
        """Run what-if simulation"""
        try:
            category = self.sim_category_var.get()
            reduction_str = self.sim_percent_var.get()
            reduction = float(reduction_str)
            
            if reduction < 0 or reduction > 100:
                messagebox.showerror("Error", "Reduction must be 0-100%")
                return
            
            if self.simulation_engine:
                result = self.simulation_engine.simulate_category_reduction(category, reduction)
                summary = self.simulation_engine.get_simulation_summary(result)
                self.simulator_text.delete(1.0, tk.END)
                self.simulator_text.insert(tk.END, summary)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")


class AddExpenseFrame(ctk.CTkFrame):
    """Add expense view with modern form"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        
        self.voice_recognizer = None
        self.voice_parser = None
        try:
            from utils.voice_command import VoiceRecognizer, VoiceCommandParser
            self.voice_recognizer = VoiceRecognizer()
            self.voice_parser = VoiceCommandParser()
        except Exception as e:
            pass
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create form widgets"""
        theme = self.controller.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color=theme['warning'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(header, text="➕ Add Expense", font=(config.FONT_FAMILY, 28, 'bold'), text_color="#ffffff")
        title.pack(pady=20)
        
        # Form container
        form_container = ctk.CTkFrame(self, fg_color=theme['bg'])
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        form = ctk.CTkFrame(form_container, fg_color=theme['card_bg'], corner_radius=10, border_width=2, border_color=theme['card_border'])
        form.pack(fill="x", padx=20, pady=20)
        
        inner = ctk.CTkFrame(form, fg_color=theme['card_bg'])
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Amount
        ctk.CTkLabel(inner, text="Amount ($)", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.amount_entry = ctk.CTkEntry(inner, height=40, placeholder_text="0.00", fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 12))
        self.amount_entry.pack(fill="x", pady=(0, 15))
        
        # Category
        ctk.CTkLabel(inner, text="Category", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.category_var = tk.StringVar(value=config.EXPENSE_CATEGORIES[0])
        self.category_combo = ctk.CTkComboBox(inner, variable=self.category_var, values=config.EXPENSE_CATEGORIES, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 12))
        self.category_combo.pack(fill="x", pady=(0, 15))
        
        # Date
        ctk.CTkLabel(inner, text="Date (YYYY-MM-DD)", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.date_entry = ctk.CTkEntry(inner, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 12))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", pady=(0, 15))
        
        # Description
        ctk.CTkLabel(inner, text="Description (Optional)", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.desc_text = ctk.CTkTextbox(inner, height=80, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 11))
        self.desc_text.pack(fill="both", expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(inner, fg_color=theme['card_bg'])
        button_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save Expense", height=40, font=(config.FONT_FAMILY, 13, 'bold'), fg_color=theme['success'], hover_color='#1e7e34', text_color="#ffffff", command=self.save_expense)
        save_btn.pack(side="left", padx=5, fill="both", expand=True)
        
        clear_btn = ctk.CTkButton(button_frame, text="🔄 Clear", height=40, font=(config.FONT_FAMILY, 13, 'bold'), fg_color=theme['accent_light'], hover_color=theme['button_hover'], text_color=theme['text_primary'], command=self.clear_form)
        clear_btn.pack(side="left", padx=5, fill="both", expand=True)
        
        voice_btn = ctk.CTkButton(button_frame, text="🎤 Voice", height=40, font=(config.FONT_FAMILY, 13, 'bold'), fg_color=theme['info'], hover_color='#1a5f7a', text_color="#ffffff", command=self.add_by_voice)
        voice_btn.pack(side="left", padx=5, fill="both", expand=True)
        self.voice_button = voice_btn
        
        if not self.voice_recognizer:
            self.voice_button.configure(state="disabled")
    
    def add_by_voice(self):
        """Add expense using voice"""
        if not self.voice_recognizer:
            messagebox.showerror("Voice Not Available", "Voice recognition is not available.\nPlease install PyAudio.")
            return
        
        try:
            status_window = ctk.CTkToplevel(self.controller)
            status_window.title("Voice Input")
            status_window.geometry("300x120")
            
            ctk.CTkLabel(status_window, text="🎤 Listening...", font=(config.FONT_FAMILY, 16, 'bold')).pack(pady=20)
            ctk.CTkLabel(status_window, text='Say: "Add 500 food expense"', font=(config.FONT_FAMILY, 12)).pack(pady=10)
            
            status_window.update()
            
            success, text, error = self.voice_recognizer.listen()
            if not success:
                status_window.destroy()
                messagebox.showerror("Error", f"Voice input failed: {error}")
                return
            
            parsed = self.voice_parser.parse_command(text)
            status_window.destroy()
            
            if not parsed['success']:
                messagebox.showerror("Error", f"Could not parse: {parsed['message']}")
                return
            
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, str(parsed['amount']))
            if parsed['category']:
                self.category_var.set(parsed['category'])
            if parsed['description']:
                self.desc_text.insert("1.0", parsed['description'])
            
            messagebox.showinfo("Success", "Parsed! Please review and save.")
        except Exception as e:
            messagebox.showerror("Error", f"Voice command failed: {str(e)}")
    
    def save_expense(self):
        """Save expense"""
        try:
            amount = self.amount_entry.get()
            category = self.category_var.get()
            date = self.date_entry.get()
            description = self.desc_text.get("1.0", "end-1c").strip()
            
            valid, msg = validate_all_expense_fields(amount, category, date, config.EXPENSE_CATEGORIES)
            if not valid:
                messagebox.showerror("Invalid Input", msg)
                return
            
            if self.db.add_expense(self.controller.current_user_id, float(amount), category, date, description):
                messagebox.showinfo("Success", "Expense added!")
                self.clear_form()
                self.controller.frames[DashboardFrame].refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
    
    def clear_form(self):
        """Clear form"""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set(config.EXPENSE_CATEGORIES[0])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.desc_text.delete("1.0", tk.END)
    
    def refresh(self):
        """Refresh"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))


class ReportsFrame(ctk.CTkFrame):
    """Reports view with charts"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create report widgets"""
        theme = self.controller.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color=theme['info'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(header, text="📈 Reports", font=(config.FONT_FAMILY, 28, 'bold'), text_color="#ffffff")
        title.pack(pady=20)
        
        # Controls
        controls = ctk.CTkFrame(self, fg_color=theme['bg'])
        controls.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(controls, text="Month:", font=(config.FONT_FAMILY, 11), text_color=theme['text_primary']).pack(side="left", padx=5)
        self.month_var = tk.IntVar(value=datetime.now().month)
        month_combo = ctk.CTkComboBox(controls, variable=self.month_var, values=[str(i) for i in range(1, 13)], width=80, height=35, font=(config.FONT_FAMILY, 11), fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'])
        month_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(controls, text="Year:", font=(config.FONT_FAMILY, 11), text_color=theme['text_primary']).pack(side="left", padx=5)
        self.year_var = tk.IntVar(value=datetime.now().year)
        year_entry = ctk.CTkEntry(controls, textvariable=self.year_var, width=80, height=35, font=(config.FONT_FAMILY, 11), fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'])
        year_entry.pack(side="left", padx=5)
        
        gen_btn = ctk.CTkButton(controls, text="📊 Generate", height=35, font=(config.FONT_FAMILY, 11, 'bold'), fg_color=theme['button_bg'], hover_color=theme['button_hover'], command=self.generate_reports)
        gen_btn.pack(side="left", padx=5)
        
        pdf_btn = ctk.CTkButton(controls, text="📄 PDF", height=35, font=(config.FONT_FAMILY, 11, 'bold'), fg_color=theme['success'], hover_color='#1e7e34', command=self.export_pdf)
        pdf_btn.pack(side="left", padx=5)
        
        # Canvas
        self.canvas_frame = ctk.CTkFrame(self, fg_color=theme['bg'])
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def generate_reports(self):
        """Generate charts"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        year = self.year_var.get()
        month = self.month_var.get()
        categories = self.db.get_category_summary(self.controller.current_user_id, year, month)
        
        if not categories:
            ctk.CTkLabel(self.canvas_frame, text="No data available", font=(config.FONT_FAMILY, 14), text_color=self.controller.current_theme['text_secondary']).pack(pady=20)
            return
        
        monthly_totals = self.db.get_monthly_totals(self.controller.current_user_id, year)
        fig = ChartGenerator.create_report_figure(categories, monthly_totals, self.controller.current_theme, year)
        
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def export_pdf(self):
        """Export to PDF"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            year = self.year_var.get()
            month = self.month_var.get()
            categories = self.db.get_category_summary(self.controller.current_user_id, year, month)
            total = sum([c[1] for c in categories])
            
            export_report_to_pdf(file_path, categories, year, month, total)
            messagebox.showinfo("Success", f"PDF exported!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def refresh(self):
        """Refresh"""
        self.generate_reports()


class SettingsFrame(ctk.CTkFrame):
    """Settings view"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings"""
        theme = self.controller.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color=theme['warning'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(header, text="⚙️ Settings", font=(config.FONT_FAMILY, 28, 'bold'), text_color="#ffffff")
        title.pack(pady=20)
        
        # Settings card
        settings_card = ctk.CTkFrame(self, fg_color=theme['card_bg'], corner_radius=10, border_width=2, border_color=theme['card_border'])
        settings_card.pack(fill="both", expand=True, padx=20, pady=20)
        
        inner = ctk.CTkFrame(settings_card, fg_color=theme['card_bg'])
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(inner, text="Monthly Budget ($)", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.budget_entry = ctk.CTkEntry(inner, height=40, placeholder_text="5000", fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 12))
        self.budget_entry.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(inner, text="Currency", font=(config.FONT_FAMILY, 12, 'bold'), text_color=theme['text_primary']).pack(anchor="w", pady=(0, 5))
        self.currency_var = tk.StringVar()
        self.currency_combo = ctk.CTkComboBox(inner, variable=self.currency_var, values=config.CURRENCIES, height=40, fg_color=theme['entry_bg'], text_color=theme['entry_fg'], border_color=theme['entry_border'], border_width=2, font=(config.FONT_FAMILY, 12))
        self.currency_combo.pack(fill="x", pady=(0, 30))
        
        button_frame = ctk.CTkFrame(inner, fg_color=theme['card_bg'])
        button_frame.pack(fill="x")
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save", height=40, font=(config.FONT_FAMILY, 13, 'bold'), fg_color=theme['success'], hover_color='#1e7e34', text_color="#ffffff", command=self.save_settings)
        save_btn.pack(side="left", padx=5, fill="both", expand=True)
        
        excel_btn = ctk.CTkButton(button_frame, text="📊 Export Excel", height=40, font=(config.FONT_FAMILY, 13, 'bold'), fg_color=theme['info'], hover_color='#1a5f7a', text_color="#ffffff", command=self.export_excel)
        excel_btn.pack(side="left", padx=5, fill="both", expand=True)
        
        # Only load settings if user is logged in
        if self.controller.current_user_id:
            self.load_settings()
    
    def load_settings(self):
        """Load settings"""
        settings = self.db.get_settings(self.controller.current_user_id)
        self.budget_entry.insert(0, str(settings[0]))
        self.currency_var.set(settings[2])
    
    def save_settings(self):
        """Save settings"""
        try:
            budget = self.budget_entry.get()
            currency = self.currency_var.get()
            
            valid, msg = validate_budget(budget)
            if not valid:
                messagebox.showerror("Invalid Input", msg)
                return
            
            self.db.update_settings(user_id=self.controller.current_user_id, budget=float(budget), currency=currency)
            messagebox.showinfo("Success", "Settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving: {str(e)}")
    
    def export_excel(self):
        """Export to Excel"""
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        
        try:
            self.db.export_to_excel(file_path)
            messagebox.showinfo("Success", "Data exported!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
    
    def refresh(self):
        """Refresh"""
        self.budget_entry.delete(0, tk.END)
        self.load_settings()


class SpendingHeatmapFrame(ctk.CTkFrame):
    """Spending heatmap with calendar"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=controller.current_theme['bg'])
        self.controller = controller
        self.db = controller.db
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.create_widgets()
    
    def create_widgets(self):
        """Create heatmap"""
        theme = self.controller.current_theme
        
        # Header
        header = ctk.CTkFrame(self, fg_color=theme['danger'], corner_radius=0)
        header.pack(fill="x")
        
        title = ctk.CTkLabel(header, text="🔥 Spending Heatmap", font=(config.FONT_FAMILY, 28, 'bold'), text_color="#ffffff")
        title.pack(pady=20)
        
        # Controls
        controls = ctk.CTkFrame(self, fg_color=theme['bg'])
        controls.pack(fill="x", padx=20, pady=15)
        
        prev_btn = ctk.CTkButton(controls, text="◀ Prev", width=80, height=35, font=(config.FONT_FAMILY, 11, 'bold'), fg_color=theme['button_bg'], hover_color=theme['button_hover'], command=self.prev_month)
        prev_btn.pack(side="left", padx=5)
        
        self.month_label = ctk.CTkLabel(controls, text=self._get_month_name(), font=(config.FONT_FAMILY, 16, 'bold'), text_color=theme['accent'])
        self.month_label.pack(side="left", padx=20)
        
        next_btn = ctk.CTkButton(controls, text="Next ▶", width=80, height=35, font=(config.FONT_FAMILY, 11, 'bold'), fg_color=theme['button_bg'], hover_color=theme['button_hover'], command=self.next_month)
        next_btn.pack(side="left", padx=5)
        
        # Canvas
        canvas_frame = ctk.CTkFrame(self, fg_color=theme['bg'])
        canvas_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.calendar_canvas = tk.Canvas(
            canvas_frame,
            bg=theme['card_bg'],
            highlightthickness=0,
            height=500
        )
        self.calendar_canvas.pack(fill="both", expand=True)
        
        # Only draw calendar if user is logged in
        if self.controller.current_user_id:
            self.draw_calendar()
        else:
            self.calendar_canvas.create_text(250, 250, text="Please log in to view your spending heatmap", font=(config.FONT_FAMILY, 14), fill=theme['text_secondary'])
    
    def _get_month_name(self):
        """Get month name"""
        return datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
    
    def prev_month(self):
        """Previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.month_label.configure(text=self._get_month_name())
        self.draw_calendar()
    
    def next_month(self):
        """Next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.month_label.configure(text=self._get_month_name())
        self.draw_calendar()
    
    def draw_calendar(self):
        """Draw calendar"""
        self.calendar_canvas.delete("all")
        theme = self.controller.current_theme
        
        daily_spending = self.db.get_month_daily_spending(self.controller.current_user_id, self.current_year, self.current_month)
        spending_dict = {date: amount for date, amount in daily_spending}
        
        settings = self.db.get_settings(self.controller.current_user_id)
        budget = settings[0]
        daily_budget = budget / 30
        
        month_calendar = calendar.monthcalendar(self.current_year, self.current_month)
        
        cell_size = 60
        cell_margin = 5
        start_x = 20
        start_y = 30
        
        # Day names
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day_name in enumerate(day_names):
            x = start_x + i * (cell_size + cell_margin)
            self.calendar_canvas.create_text(x + cell_size // 2, start_y - 15, text=day_name, font=(config.FONT_FAMILY, 10, 'bold'), fill=theme['text_primary'])
        
        # Grid
        current_y = start_y
        for week in month_calendar:
            current_x = start_x
            for day in week:
                if day == 0:
                    current_x += cell_size + cell_margin
                    continue
                
                date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                amount = spending_dict.get(date_str, 0)
                
                intensity = 0 if amount == 0 else (1 if amount < daily_budget*0.5 else (3 if amount < daily_budget else (5 if amount < daily_budget*1.5 else (7 if amount < daily_budget*2 else 9))))
                color = self._get_intensity_color(intensity)
                
                self.calendar_canvas.create_rectangle(current_x, current_y, current_x+cell_size, current_y+cell_size, fill=color, outline=theme['text_secondary'])
                self.calendar_canvas.create_text(current_x+10, current_y+10, text=str(day), font=(config.FONT_FAMILY, 11, 'bold'), fill='white' if intensity > 5 else theme['text_primary'], anchor='nw')
                
                if amount > 0:
                    self.calendar_canvas.create_text(current_x+cell_size//2, current_y+cell_size-10, text=f"${amount:.0f}", font=(config.FONT_FAMILY, 9), fill='white' if intensity > 5 else theme['text_primary'])
                
                current_x += cell_size + cell_margin
            current_y += cell_size + cell_margin*2
    
    def _get_intensity_color(self, intensity):
        """Get color by intensity"""
        colors = ["#E8F5E9", "#C8E6C9", "#A5D6A7", "#81C784", "#66BB6A", "#FFE082", "#FFD54F", "#FFA726", "#EF5350", "#C62828"]
        return colors[min(intensity, 9)]
    
    def refresh(self):
        """Refresh"""
        self.draw_calendar()
