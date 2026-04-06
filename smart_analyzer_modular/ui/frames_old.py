"""
UI Frames for Smart Expense Analyzer
Contains all frame classes for different views
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import calendar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config
from utils.validators import validate_all_expense_fields, validate_budget
from utils.auth_utils import validate_username, validate_password
from reports.chart_generator import ChartGenerator
from reports.pdf_generator import export_report_to_pdf


class LoginFrame(ttk.Frame):
    """Login and registration screen"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create login form widgets"""
        theme = self.controller.current_theme
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Title
        title = ttk.Label(
            main_frame, 
            text="Smart Expense Analyzer",
            style='Title.TLabel'
        )
        title.pack(pady=(0, 40))
        
        # Subtitle
        subtitle = ttk.Label(
            main_frame,
            text="Manage your finances intelligently",
            style='Secondary.TLabel'
        )
        subtitle.pack(pady=(0, 30))
        
        # Username
        ttk.Label(main_frame, text="Username:", style='Normal.TLabel').pack(anchor=tk.W, pady=(10, 5))
        self.username_entry = ttk.Entry(main_frame, width=40, font=(config.FONT_FAMILY, 11))
        self.username_entry.pack(fill=tk.X, pady=(0, 15))
        self.username_entry.bind('<Return>', lambda e: self.login())
        
        # Password
        ttk.Label(main_frame, text="Password:", style='Normal.TLabel').pack(anchor=tk.W, pady=(10, 5))
        self.password_entry = ttk.Entry(main_frame, width=40, font=(config.FONT_FAMILY, 11), show='*')
        self.password_entry.pack(fill=tk.X, pady=(0, 30))
        self.password_entry.bind('<Return>', lambda e: self.login())
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        login_btn = ttk.Button(button_frame, text="Login", command=self.login)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        signup_btn = ttk.Button(button_frame, text="Sign Up", command=self.show_signup)
        signup_btn.pack(side=tk.LEFT, padx=5)
        
        # Error label
        self.error_label = ttk.Label(main_frame, text="", style='Normal.TLabel', foreground='red')
        self.error_label.pack(pady=(20, 0))
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.config(text="Please enter username and password")
            return
        
        success, message, user_id = self.db.login_user(username, password)
        
        if success:
            self.controller.current_user_id = user_id
            self.controller.current_username = username
            self.controller.show_frame(DashboardFrame)
        else:
            self.error_label.config(text=f"Login failed: {message}")
    
    def show_signup(self):
        """Show signup dialog"""
        signup_window = tk.Toplevel(self.controller)
        signup_window.title("Sign Up")
        signup_window.geometry("400x480")
        signup_window.resizable(False, False)
        
        # Center window
        signup_window.transient(self.controller)
        signup_window.grab_set()
        
        frame = ttk.Frame(signup_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Create New Account", style='Title.TLabel').pack(pady=(0, 20))
        
        # Username
        ttk.Label(frame, text="Username (3-20 chars, alphanumeric):", style='Normal.TLabel').pack(anchor=tk.W, pady=(5, 0))
        username_entry = ttk.Entry(frame, width=40, font=(config.FONT_FAMILY, 11))
        username_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Password
        ttk.Label(frame, text="Password (6+ characters):", style='Normal.TLabel').pack(anchor=tk.W, pady=(5, 0))
        password_entry = ttk.Entry(frame, width=40, font=(config.FONT_FAMILY, 11), show='*')
        password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Confirm Password
        ttk.Label(frame, text="Confirm Password:", style='Normal.TLabel').pack(anchor=tk.W, pady=(5, 0))
        confirm_entry = ttk.Entry(frame, width=40, font=(config.FONT_FAMILY, 11), show='*')
        confirm_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Error label
        error_label = ttk.Label(frame, text="", style='Normal.TLabel', foreground='red')
        error_label.pack(pady=10)
        
        def register():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            # Validate
            valid, msg = validate_username(username)
            if not valid:
                error_label.config(text=f"Username: {msg}")
                return
            
            valid, msg = validate_password(password)
            if not valid:
                error_label.config(text=f"Password: {msg}")
                return
            
            if password != confirm:
                error_label.config(text="Passwords don't match")
                return
            
            # Register
            success, message, user_id = self.db.register_user(username, password)
            
            if success:
                messagebox.showinfo("Success", f"Account created! You can now log in.")
                signup_window.destroy()
            else:
                error_label.config(text=message)
        
        # Register button
        ttk.Button(frame, text="Create Account", command=register).pack(pady=20)


class DashboardFrame(ttk.Frame):
    """Dashboard view showing expense overview"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Import advisor and gamification
        try:
            from utils.financial_advisor import FinancialAdvisor
            from utils.gamification import GamificationManager
            from utils.personality_analyzer import PersonalityAnalyzer
            from utils.simulation_engine import SimulationEngine
            # These will be initialized with user_id in refresh()
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
        # Header with background
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # Title
        title_label = ttk.Label(header_frame, text="📊 Dashboard", style='Title.TLabel')
        title_label.pack(pady=20, padx=20)
        
        ttk.Separator(header_frame, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Top stats row
        stats_frame = ttk.Frame(self)
        stats_frame.pack(fill=tk.X, pady=20, padx=20)
        
        # Total expenses this month
        self.total_label = self.create_stat_card(
            stats_frame, "This Month", "$0.00", "📊"
        )
        
        # Monthly budget
        self.budget_label = self.create_stat_card(
            stats_frame, "Monthly Budget", "$0.00", "💰"
        )
        
        # Remaining
        self.remaining_label = self.create_stat_card(
            stats_frame, "Remaining", "$0.00", "✅"
        )
        
        # Main scrollable area
        canvas = tk.Canvas(self, highlightthickness=0, bg=self.controller.current_theme['frame_bg'])
        canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas_window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Bind canvas to update width when resized
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window_id, width=event.width)
        
        canvas.bind('<Configure>', on_canvas_configure)
        
        # Financial Advisor Section - Always create
        advisor_frame = ttk.LabelFrame(scrollable_frame, text="💡 Financial Advisor", padding=15)
        advisor_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.advisor_text = tk.Text(
            advisor_frame, height=9, width=80,
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.advisor_text.pack(fill=tk.BOTH, expand=True)
        self.advisor_text.insert(tk.END, "Loading advisor data...")
        
        # Achievements Section - Always create
        achievements_frame = ttk.LabelFrame(scrollable_frame, text="🏆 Achievements", padding=15)
        achievements_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.achievements_canvas = tk.Canvas(
            achievements_frame, height=100,
            bg=self.controller.current_theme['entry_bg'],
            highlightthickness=0
        )
        self.achievements_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Streak info
        self.streak_label = ttk.Label(achievements_frame, text="Loading achievements...", style='Normal.TLabel')
        self.streak_label.pack(pady=10)
        
        # Financial Personality Section - Always create
        personality_frame = ttk.LabelFrame(scrollable_frame, text="🎭 Your Spending Personality", padding=15)
        personality_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.personality_text = tk.Text(
            personality_frame, height=8, width=80,
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.personality_text.pack(fill=tk.BOTH, expand=True)
        self.personality_text.insert(tk.END, "Loading personality analysis...")
        
        # What-If Simulator Section - Always create
        simulator_frame = ttk.LabelFrame(scrollable_frame, text="🎯 What-If Simulator", padding=15)
        simulator_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Simulation controls
        sim_controls = ttk.Frame(simulator_frame)
        sim_controls.pack(fill=tk.X, pady=10)
        
        ttk.Label(sim_controls, text="Reduce category by:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.sim_category_var = tk.StringVar(value=config.EXPENSE_CATEGORIES[0])
        self.sim_category_combo = ttk.Combobox(
            sim_controls, textvariable=self.sim_category_var,
            values=config.EXPENSE_CATEGORIES, state='readonly', width=15
        )
        self.sim_category_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(sim_controls, text="%:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.sim_percent_var = tk.StringVar(value="10")
        self.sim_percent_entry = ttk.Entry(sim_controls, textvariable=self.sim_percent_var, width=5)
        self.sim_percent_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(sim_controls, text="📊 Simulate", command=self.run_simulation).pack(side=tk.LEFT, padx=5)
        
        # Simulation results
        self.simulator_text = tk.Text(
            simulator_frame, height=8, width=80,
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.simulator_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Category breakdown
        category_frame = ttk.LabelFrame(scrollable_frame, text="📊 Category Breakdown", padding=15)
        category_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.category_text = tk.Text(
            category_frame, height=8, width=80,
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.category_text.pack(fill=tk.BOTH, expand=True)
        self.category_text.insert(tk.END, "Loading category breakdown...")
        
        # Recent transactions
        recent_frame = ttk.LabelFrame(scrollable_frame, text="📝 Recent Transactions", padding=15)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.recent_text = tk.Text(
            recent_frame, height=6, width=80,
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary'],
            font=(config.FONT_FAMILY, config.FONT_SIZES['normal']),
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.recent_text.pack(fill=tk.BOTH, expand=True)
        self.recent_text.insert(tk.END, "Loading recent transactions...")
    
    def create_stat_card(self, parent, title, value, emoji):
        """Create a stat card"""
        card = ttk.Frame(parent, padding=20)
        card.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        ttk.Label(card, text=f"{emoji} {title}", style='Normal.TLabel').pack()
        value_label = ttk.Label(card, text=value, style='Heading.TLabel')
        value_label.pack(pady=10)
        
        return value_label
    
    def refresh(self):
        """Refresh dashboard data"""
        print(f"[DASHBOARD] Refreshing dashboard for user_id: {self.controller.current_user_id}")
        
        # Get user ID
        user_id = self.controller.current_user_id
        if not user_id:
            print("[ERROR] No user_id found!")
            return
        
        try:
            # Initialize utilities with current user
            from utils.financial_advisor import FinancialAdvisor
            from utils.gamification import GamificationManager
            from utils.personality_analyzer import PersonalityAnalyzer
            from utils.simulation_engine import SimulationEngine
            
            self.advisor = FinancialAdvisor(self.db, user_id)
            self.gamification = GamificationManager(self.db, user_id)
            self.personality_analyzer = PersonalityAnalyzer(self.db, user_id)
            self.simulation_engine = SimulationEngine(self.db, user_id)
            print("[OK] Utilities initialized successfully")
        except Exception as e:
            print(f"[ERROR] Failed to initialize utilities: {e}")
            self.advisor = None
            self.gamification = None
            self.personality_analyzer = None
            self.simulation_engine = None
        
        try:
            # Fetch data for current user
            print(f"[DATA] Fetching data for user_id={user_id}")
            current_total = self.db.get_current_month_total(user_id)
            settings = self.db.get_settings(user_id)
            budget = settings[0]
            remaining = budget - current_total
            
            print(f"[DATA] Current total: ${current_total:.2f}, Budget: ${budget:.2f}, Remaining: ${remaining:.2f}")
            
            # Update stat cards
            self.total_label.configure(text=f"${current_total:.2f}")
            self.budget_label.configure(text=f"${budget:.2f}")
            self.remaining_label.configure(text=f"${remaining:.2f}")
            
            # Check if dashboard is empty (no expenses)
            all_expenses = self.db.get_all_expenses(user_id)
            is_empty = len(all_expenses) == 0
            print(f"[DATA] Total expenses found: {len(all_expenses)}, is_empty: {is_empty}")
            
            # Update financial advisor
            self.advisor_text.delete(1.0, tk.END)
            
            if is_empty:
                # Show welcome message
                self.advisor_text.insert(tk.END, "Welcome to Smart Expense Analyzer!\n\n")
                self.advisor_text.insert(tk.END, "Getting Started:\n\n")
                self.advisor_text.insert(tk.END, "1. Add your first expense using the 'Add Expense' tab\n")
                self.advisor_text.insert(tk.END, "2. Track spending across different categories\n")
                self.advisor_text.insert(tk.END, "3. Set a monthly budget to stay on track\n")
                self.advisor_text.insert(tk.END, "4. View insights and receive smart spending tips\n\n")
                self.advisor_text.insert(tk.END, "Features:\n\n")
                self.advisor_text.insert(tk.END, "* Financial Advisor: Get personalized spending insights\n")
                self.advisor_text.insert(tk.END, "* Gamification: Earn badges and maintain streaks\n")
                self.advisor_text.insert(tk.END, "* Spending Heatmap: Visualize your spending patterns\n")
                self.advisor_text.insert(tk.END, "* Reports: Generate detailed PDF reports\n")
            else:
                if self.advisor:
                    analysis = self.advisor.analyze_spending_patterns()
                    
                    self.advisor_text.insert(tk.END, f"Budget Status: {analysis['budget_status']}\n\n")
                    
                    if analysis['overspending_categories']:
                        self.advisor_text.insert(tk.END, "Overspending Categories:\n")
                        for cat in analysis['overspending_categories']:
                            self.advisor_text.insert(tk.END, 
                                f"  * {cat['category']}: ${cat['amount']:.2f} "
                                f"({cat['percentage']:.1f}%) - Save ${cat['savings_potential']:.2f}\n"
                            )
                        self.advisor_text.insert(tk.END, "\n")
                    
                    if analysis['most_expensive_day']:
                        day = analysis['most_expensive_day']
                        self.advisor_text.insert(tk.END, 
                            f"Priciest Day: {day['day_name']} ({day['date']}) - ${day['amount']:.2f}\n\n"
                        )
                    
                    self.advisor_text.insert(tk.END, "Smart Tips:\n")
                    for i, tip in enumerate(analysis['saving_tips'], 1):
                        self.advisor_text.insert(tk.END, f"{i}. {tip}\n")
                else:
                    self.advisor_text.insert(tk.END, "Financial advisor data not available\n")
            
            # Update achievements
            try:
                current_streak, longest_streak, _ = self.db.get_streak_info(user_id)
                self.streak_label.configure(
                    text=f"Current Streak: {current_streak} days | Longest: {longest_streak} days"
                )
                print(f"[OK] Streaks loaded: current={current_streak}, longest={longest_streak}")
            except Exception as e:
                print(f"[ERROR] Failed to load streaks: {e}")
                self.streak_label.configure(text="Streak data not available")
            
            # Draw earned badges
            self.achievements_canvas.delete("all")
            if self.gamification:
                earned_badges = self.gamification.get_earned_badges()
                
                if earned_badges:
                    x_pos = 20
                    for badge in earned_badges:
                        self.achievements_canvas.create_text(
                            x_pos, 20, text=f"{badge['icon']}", font=("Arial", 40),
                            anchor="nw"
                        )
                        self.achievements_canvas.create_text(
                            x_pos + 50, 20, text=f"{badge['name']}\n{badge['description']}",
                            font=(config.FONT_FAMILY, config.FONT_SIZES['small']),
                            fill=self.controller.current_theme['text_primary'],
                            anchor="nw", width=150
                        )
                        x_pos += 250
                    print(f"[OK] {len(earned_badges)} badges displayed")
                else:
                    # Show helpful message about earning badges
                    help_text = "🎯 Badges Earned Here!\n\n"
                    help_text += "👑 Budget Master - Stay under budget 7 days\n"
                    help_text += "💎 Smart Saver - Spend 30% less than budget\n"
                    help_text += "📊 Consistent Tracker - Track 20 days\n"
                    help_text += "⚡ Weekend Warrior - No overspending on weekends\n"
                    help_text += "🏆 Financial Champion - Earn 3 badges"
                    
                    self.achievements_canvas.create_text(
                        20, 10, text=help_text,
                        font=(config.FONT_FAMILY, config.FONT_SIZES['small']),
                        fill=self.controller.current_theme['text_primary'],
                        anchor="nw", justify=tk.LEFT
                    )
                    print("[OK] Badge requirements displayed")
            
            # Update category breakdown
            now = datetime.now()
            categories = self.db.get_category_summary(user_id, now.year, now.month)
            print(f"[DATA] Categories fetched: {len(categories)} categories found")
            
            self.category_text.delete(1.0, tk.END)
            self.category_text.insert(tk.END, "Category Breakdown:\n" + "="*80 + "\n")
            
            if is_empty:
                self.category_text.insert(tk.END, "\nNo expenses yet. Start tracking to see category breakdown!\n\n")
                self.category_text.insert(tk.END, "Sample categories: Food, Transport, Shopping, Entertainment, Utilities\n")
            else:
                for category, amount in categories:
                    percentage = (amount / current_total * 100) if current_total > 0 else 0
                    self.category_text.insert(tk.END, f"{category:15} ${amount:8.2f} ({percentage:5.1f}%)\n")
            
            # Update recent transactions
            recent = self.db.get_recent_expenses(user_id, config.RECENT_LIMIT)
            print(f"[DATA] Recent expenses fetched: {len(recent)} transactions found")
            
            self.recent_text.delete(1.0, tk.END)
            self.recent_text.insert(tk.END, "Date        Category      Amount   Description\n" + "="*80 + "\n")
            
            if is_empty:
                self.recent_text.insert(tk.END, "\nNo transactions yet. Add your first expense to get started!\n")
            else:
                for expense in recent:
                    _, user_id_check, amount, category, date, description, _ = expense
                    desc = description[:30] if description else "N/A"
                    self.recent_text.insert(tk.END, f"{date} {category:12} ${amount:7.2f} {desc}\n")
            
            # Update personality analysis
            self.personality_text.delete(1.0, tk.END)
            
            if is_empty:
                self.personality_text.insert(tk.END, "Spending Personality\n\n")
                self.personality_text.insert(tk.END, "Your spending personality will be revealed once you add expenses.\n\n")
                self.personality_text.insert(tk.END, "We analyze your spending patterns to categorize you as:\n\n")
                self.personality_text.insert(tk.END, "* Budget Master - Carefully controlled spending\n")
                self.personality_text.insert(tk.END, "* Smart Planner - Strategic category allocation\n")
                self.personality_text.insert(tk.END, "* Flexible Spender - Balanced with occasional splurges\n")
                self.personality_text.insert(tk.END, "* Careful Saver - Minimalist approach\n")
                self.personality_text.insert(tk.END, "* Adventurous - Willing to explore and try new things\n")
            else:
                if self.personality_analyzer:
                    personality = self.personality_analyzer.analyze_personality()
                    
                    self.personality_text.insert(tk.END, 
                        f"{personality['icon']} {personality['personality']}\n"
                        f"Confidence: {personality['confidence']:.0f}%\n\n"
                        f"{personality['description']}\n\n"
                    )
                    
                    if personality['traits']:
                        self.personality_text.insert(tk.END, "Your Traits:\n")
                        for trait in personality['traits']:
                            self.personality_text.insert(tk.END, f"  * {trait}\n")
                        self.personality_text.insert(tk.END, "\n")
                    
                    suggestions = self.personality_analyzer.get_improvement_suggestions(personality['personality'])
                    self.personality_text.insert(tk.END, "Suggestions for you:\n")
                    for i, suggestion in enumerate(suggestions, 1):
                        self.personality_text.insert(tk.END, f"{i}. {suggestion}\n")
                else:
                    self.personality_text.insert(tk.END, "Personality analysis not available\n")
            
            # Update simulator
            self.simulator_text.delete(1.0, tk.END)
            if is_empty:
                self.simulator_text.insert(tk.END, "What-If Simulator\n\n")
                self.simulator_text.insert(tk.END, "Try adjusting your spending in different categories to see:\n\n")
                self.simulator_text.insert(tk.END, "* How much you could save\n")
                self.simulator_text.insert(tk.END, "* New budget allocation\n")
                self.simulator_text.insert(tk.END, "* Overall financial impact\n\n")
                self.simulator_text.insert(tk.END, "Add expenses first, then use the controls above to simulate!")
            else:
                self.simulator_text.insert(tk.END, "Select a category and percentage, then click 'Simulate'")
            
            print("[OK] Dashboard refresh complete!")
            
        except Exception as e:
            print(f"[ERROR] Dashboard refresh failed: {e}")
            import traceback
            traceback.print_exc()
    
    def run_simulation(self):
        """Run what-if simulation"""
        try:
            category = self.sim_category_var.get()
            reduction_str = self.sim_percent_var.get()
            
            # Validate input
            if not reduction_str:
                messagebox.showerror("Error", "Please enter a reduction percentage")
                return
            
            reduction = float(reduction_str)
            if reduction < 0 or reduction > 100:
                messagebox.showerror("Error", "Reduction must be between 0 and 100%")
                return
            
            # Run simulation
            result = self.simulation_engine.simulate_category_reduction(category, reduction)
            summary = self.simulation_engine.get_simulation_summary(result)
            
            # Display results
            self.simulator_text.delete(1.0, tk.END)
            self.simulator_text.insert(tk.END, summary)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")


class AddExpenseFrame(ttk.Frame):
    """Add expense view with form"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        
        # Import voice recognition
        self.voice_recognizer = None
        self.voice_parser = None
        try:
            from utils.voice_command import VoiceRecognizer, VoiceCommandParser
            self.voice_recognizer = VoiceRecognizer()
            self.voice_parser = VoiceCommandParser()
            if not self.voice_recognizer.is_available():
                print(f"Warning: Voice not available - {self.voice_recognizer.get_error_message()}")
        except Exception as e:
            print(f"Warning: Could not initialize voice - {str(e)}")
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create form widgets"""
        # Title
        title_label = ttk.Label(self, text="Add Expense", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = ttk.Frame(self, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Amount
        ttk.Label(form_frame, text="Amount ($):", style='Normal.TLabel').grid(row=0, column=0, sticky=tk.W, pady=10)
        self.amount_entry = ttk.Entry(form_frame, width=30, font=(config.FONT_FAMILY, 11))
        self.amount_entry.grid(row=0, column=1, sticky=tk.EW, pady=10, padx=10)
        
        # Category
        ttk.Label(form_frame, text="Category:", style='Normal.TLabel').grid(row=1, column=0, sticky=tk.W, pady=10)
        self.category_var = tk.StringVar(value=config.EXPENSE_CATEGORIES[0])
        category_combo = ttk.Combobox(
            form_frame, textvariable=self.category_var, values=config.EXPENSE_CATEGORIES,
            state='readonly', width=27, font=(config.FONT_FAMILY, 11)
        )
        category_combo.grid(row=1, column=1, sticky=tk.EW, pady=10, padx=10)
        
        # Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):", style='Normal.TLabel').grid(row=2, column=0, sticky=tk.W, pady=10)
        self.date_entry = ttk.Entry(form_frame, width=30, font=(config.FONT_FAMILY, 11))
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, sticky=tk.EW, pady=10, padx=10)
        
        # Description
        ttk.Label(form_frame, text="Description:", style='Normal.TLabel').grid(row=3, column=0, sticky=tk.NW, pady=10)
        self.desc_text = tk.Text(
            form_frame, height=5, width=33, font=(config.FONT_FAMILY, 10),
            bg=self.controller.current_theme['entry_bg'],
            fg=self.controller.current_theme['text_primary']
        )
        self.desc_text.grid(row=3, column=1, sticky=tk.EW, pady=10, padx=10)
        
        form_frame.columnconfigure(1, weight=1)
        
        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Save Expense", command=self.save_expense).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Voice button (always show, but might be disabled)
        self.voice_button = ttk.Button(button_frame, text="🎤 Add by Voice", command=self.add_by_voice)
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Check if voice is available
        if not self.voice_recognizer:
            self.voice_button.configure(state='disabled')
    
    def add_by_voice(self):
        """Add expense using voice command"""
        if not self.voice_recognizer or not self.voice_recognizer.is_available():
            error_msg = "Voice recognition is not available"
            if self.voice_recognizer:
                error_msg += f"\n\n{self.voice_recognizer.get_error_message()}"
                error_msg += "\n\nTo enable voice features, please install PyAudio:\npip install PyAudio"
            messagebox.showerror("Voice Not Available", error_msg)
            return
        
        # Show listening message
        status_window = tk.Toplevel(self.controller)
        status_window.title("Voice Input")
        status_window.geometry("300x100")
        status_window.resizable(False, False)
        
        status_label = ttk.Label(status_window, text="Listening...", style='Heading.TLabel')
        status_label.pack(pady=20)
        
        instructions = ttk.Label(status_window, text='Say: "Add 500 food expense"', style='Normal.TLabel')
        instructions.pack(pady=10)
        
        status_window.update()
        
        try:
            # Listen for voice input
            success, text, error = self.voice_recognizer.listen()
            
            if not success:
                status_window.destroy()
                messagebox.showerror("Error", f"Voice input failed: {error}")
                return
            
            # Parse the command
            parsed = self.voice_parser.parse_command(text)
            status_window.destroy()
            
            if not parsed['success']:
                messagebox.showerror("Error", f"Could not parse command: {parsed['message']}")
                return
            
            # Fill form with parsed data
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, str(parsed['amount']))
            
            if parsed['category']:
                self.category_var.set(parsed['category'])
            
            if parsed['description']:
                self.desc_text.insert(tk.END, parsed['description'])
            
            messagebox.showinfo("Voice Command", f"Parsed: {parsed['message']}\nPlease review and save.")
            
        except Exception as e:
            status_window.destroy()
            messagebox.showerror("Error", f"Voice command failed: {str(e)}")
    
    def save_expense(self):
        """Save expense to database"""
        try:
            amount = self.amount_entry.get()
            category = self.category_var.get()
            date = self.date_entry.get()
            description = self.desc_text.get(1.0, tk.END).strip()
            
            # Validate inputs
            valid, msg = validate_all_expense_fields(amount, category, date, config.EXPENSE_CATEGORIES)
            if not valid:
                messagebox.showerror("Invalid Input", msg)
                return
            
            # Save to database with user_id
            if self.db.add_expense(self.controller.current_user_id, float(amount), category, date, description):
                messagebox.showinfo("Success", "Expense added successfully!")
                self.clear_form()
                self.controller.check_budget_alert()
                self.controller.frames[DashboardFrame].refresh()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saving expense: {str(e)}")
    
    def clear_form(self):
        """Clear form fields"""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set(config.EXPENSE_CATEGORIES[0])
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.desc_text.delete(1.0, tk.END)
    
    def refresh(self):
        """Refresh on view change"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))


class ReportsFrame(ttk.Frame):
    """Reports view with charts and analytics"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create report widgets"""
        # Title
        title_label = ttk.Label(self, text="Reports", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Month/Year selector
        selector_frame = ttk.Frame(self)
        selector_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(selector_frame, text="Month:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.month_var = tk.IntVar(value=datetime.now().month)
        month_combo = ttk.Combobox(
            selector_frame, textvariable=self.month_var,
            values=list(range(1, 13)), state='readonly', width=5
        )
        month_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(selector_frame, text="Year:", style='Normal.TLabel').pack(side=tk.LEFT, padx=5)
        self.year_var = tk.IntVar(value=datetime.now().year)
        year_entry = ttk.Entry(selector_frame, textvariable=self.year_var, width=5)
        year_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(selector_frame, text="Generate Reports", command=self.generate_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="Export to PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=5)
        
        # Canvas frame for charts
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def generate_reports(self):
        """Generate charts"""
        # Clear previous charts
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        year = self.year_var.get()
        month = self.month_var.get()
        
        # Get data
        categories = self.db.get_category_summary(self.controller.current_user_id, year, month)
        
        if not categories:
            ttk.Label(
                self.canvas_frame, text="No data available for selected month",
                style='Normal.TLabel'
            ).pack(pady=20)
            return
        
        # Generate chart
        monthly_totals = self.db.get_monthly_totals(self.controller.current_user_id, year)
        fig = ChartGenerator.create_report_figure(categories, monthly_totals, self.controller.current_theme, year)
        
        # Display in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def export_pdf(self):
        """Export report to PDF"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            year = self.year_var.get()
            month = self.month_var.get()
            
            # Get data
            categories = self.db.get_category_summary(self.controller.current_user_id, year, month)
            total = sum([c[1] for c in categories])
            
            # Export
            export_report_to_pdf(file_path, categories, year, month, total)
            messagebox.showinfo("Success", f"PDF exported to {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def refresh(self):
        """Refresh reports"""
        self.generate_reports()


class SettingsFrame(ttk.Frame):
    """Settings view for app configuration"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Title
        title_label = ttk.Label(self, text="Settings", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Settings frame
        settings_frame = ttk.Frame(self, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Monthly Budget
        ttk.Label(settings_frame, text="Monthly Budget ($):", style='Normal.TLabel').grid(row=0, column=0, sticky=tk.W, pady=15)
        self.budget_entry = ttk.Entry(settings_frame, width=30, font=(config.FONT_FAMILY, 11))
        self.budget_entry.grid(row=0, column=1, sticky=tk.EW, pady=15, padx=10)
        
        # Currency
        ttk.Label(settings_frame, text="Currency:", style='Normal.TLabel').grid(row=1, column=0, sticky=tk.W, pady=15)
        self.currency_var = tk.StringVar()
        currency_combo = ttk.Combobox(
            settings_frame, textvariable=self.currency_var,
            values=config.CURRENCIES, state='readonly', width=27, font=(config.FONT_FAMILY, 11)
        )
        currency_combo.grid(row=1, column=1, sticky=tk.EW, pady=15, padx=10)
        
        settings_frame.columnconfigure(1, weight=1)
        
        # Data management
        ttk.Separator(settings_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky='ew', pady=20)
        
        ttk.Label(settings_frame, text="Data Management", style='Heading.TLabel').grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        ttk.Button(button_frame, text="Export to Excel", command=self.export_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        
        # Load current settings
        self.load_settings()
    
    def load_settings(self):
        """Load current settings"""
        settings = self.db.get_settings(self.controller.current_user_id)
        self.budget_entry.insert(0, str(settings[0]))
        self.currency_var.set(settings[2])
    
    def save_settings(self):
        """Save settings"""
        try:
            budget = self.budget_entry.get()
            currency = self.currency_var.get()
            
            # Validate
            valid, msg = validate_budget(budget)
            if not valid:
                messagebox.showerror("Invalid Input", msg)
                return
            
            # Pass user_id to update_settings
            self.db.update_settings(
                user_id=self.controller.current_user_id,
                budget=float(budget),
                currency=currency
            )
            messagebox.showinfo("Success", "Settings saved successfully!")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
    
    def export_excel(self):
        """Export to Excel"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.db.export_to_excel(file_path)
            messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def refresh(self):
        """Refresh on view change"""
        self.budget_entry.delete(0, tk.END)
        self.load_settings()


class SpendingHeatmapFrame(ttk.Frame):
    """Spending heatmap with calendar view"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.db = controller.db
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.create_widgets()
    
    def create_widgets(self):
        """Create heatmap widgets"""
        # Title
        title_label = ttk.Label(self, text="Spending Heatmap 🔥", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(controls_frame, text="◀ Prev", command=self.prev_month).pack(side=tk.LEFT, padx=5)
        self.month_label = ttk.Label(controls_frame, text=self._get_month_name(), style='Heading.TLabel')
        self.month_label.pack(side=tk.LEFT, padx=20)
        ttk.Button(controls_frame, text="Next ▶", command=self.next_month).pack(side=tk.LEFT, padx=5)
        
        # Calendar frame
        calendar_frame = ttk.Frame(self)
        calendar_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.calendar_canvas = tk.Canvas(
            calendar_frame,
            bg=self.controller.current_theme['entry_bg'],
            highlightthickness=0,
            height=500
        )
        self.calendar_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw calendar
        self.draw_calendar()
    
    def _get_month_name(self):
        """Get month name for display"""
        from datetime import datetime
        return datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
    
    def prev_month(self):
        """Go to previous month"""
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.month_label.configure(text=self._get_month_name())
        self.draw_calendar()
    
    def next_month(self):
        """Go to next month"""
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.month_label.configure(text=self._get_month_name())
        self.draw_calendar()
    
    def draw_calendar(self):
        """Draw the calendar heatmap"""
        self.calendar_canvas.delete("all")
        
        # Get daily spending data
        daily_spending = self.db.get_month_daily_spending(self.controller.current_user_id, self.current_year, self.current_month)
        spending_dict = {date: amount for date, amount in daily_spending}
        
        # Get budget for color intensity reference
        settings = self.db.get_settings(self.controller.current_user_id)
        budget = settings[0]
        daily_budget = budget / 30  # Approximate daily budget
        
        # Get calendar for the month
        import calendar as cal
        month_calendar = cal.monthcalendar(self.current_year, self.current_month)
        
        # Canvas setup
        cell_size = 60
        cell_margin = 5
        start_x = 20
        start_y = 30
        
        # Draw day names
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day_name in enumerate(day_names):
            x = start_x + i * (cell_size + cell_margin)
            self.calendar_canvas.create_text(
                x + cell_size // 2, start_y - 15,
                text=day_name,
                font=(config.FONT_FAMILY, config.FONT_SIZES['small'], 'bold'),
                fill=self.controller.current_theme['text_primary']
            )
        
        # Draw calendar grid
        current_y = start_y
        for week_num, week in enumerate(month_calendar):
            current_x = start_x
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    current_x += cell_size + cell_margin
                    continue
                
                # Get spending for this day
                date_str = f"{self.current_year}-{self.current_month:02d}-{day:02d}"
                amount = spending_dict.get(date_str, 0)
                
                # Calculate color intensity (0-9 scale)
                if amount == 0:
                    intensity = 0
                elif amount < daily_budget * 0.5:
                    intensity = 1
                elif amount < daily_budget:
                    intensity = 3
                elif amount < daily_budget * 1.5:
                    intensity = 5
                elif amount < daily_budget * 2:
                    intensity = 7
                else:
                    intensity = 9
                
                # Get color based on intensity
                color = self._get_intensity_color(intensity)
                
                # Draw cell
                self.calendar_canvas.create_rectangle(
                    current_x, current_y,
                    current_x + cell_size, current_y + cell_size,
                    fill=color, outline=self.controller.current_theme['text_secondary']
                )
                
                # Draw day number
                self.calendar_canvas.create_text(
                    current_x + 10, current_y + 10,
                    text=str(day),
                    font=(config.FONT_FAMILY, config.FONT_SIZES['normal'], 'bold'),
                    fill='white' if intensity > 5 else self.controller.current_theme['text_primary'],
                    anchor='nw'
                )
                
                # Draw amount
                if amount > 0:
                    self.calendar_canvas.create_text(
                        current_x + cell_size // 2, current_y + cell_size - 10,
                        text=f"${amount:.0f}",
                        font=(config.FONT_FAMILY, config.FONT_SIZES['small']),
                        fill='white' if intensity > 5 else self.controller.current_theme['text_primary']
                    )
                
                current_x += cell_size + cell_margin
            
            current_y += cell_size + cell_margin * 2
        
        # Draw legend
        legend_y = current_y + 20
        legend_labels = ['None', 'Low', 'Medium', 'High', 'Very High']
        legend_colors = [
            self._get_intensity_color(0),
            self._get_intensity_color(1),
            self._get_intensity_color(4),
            self._get_intensity_color(7),
            self._get_intensity_color(9)
        ]
        
        for i, (label, color) in enumerate(zip(legend_labels, legend_colors)):
            x = start_x + i * 150
            self.calendar_canvas.create_rectangle(
                x, legend_y, x + 20, legend_y + 20,
                fill=color, outline=self.controller.current_theme['text_secondary']
            )
            self.calendar_canvas.create_text(
                x + 30, legend_y + 10,
                text=label,
                font=(config.FONT_FAMILY, config.FONT_SIZES['small']),
                fill=self.controller.current_theme['text_primary'],
                anchor='w'
            )
        
        # Update canvas scroll region
        self.calendar_canvas.configure(scrollregion=self.calendar_canvas.bbox("all"))
    
    def _get_intensity_color(self, intensity):
        """Get color based on intensity (0-9)"""
        # Green (low) to Red (high) gradient
        if intensity == 0:
            return "#E8F5E9"  # Lightest green
        elif intensity == 1:
            return "#C8E6C9"  # Light green
        elif intensity == 2:
            return "#A5D6A7"  # Medium light green
        elif intensity == 3:
            return "#81C784"  # Medium green
        elif intensity == 4:
            return "#66BB6A"  # Green
        elif intensity == 5:
            return "#FFE082"  # Light yellow
        elif intensity == 6:
            return "#FFD54F"  # Yellow
        elif intensity == 7:
            return "#FFA726"  # Orange
        elif intensity == 8:
            return "#EF5350"  # Light red
        else:
            return "#C62828"  # Dark red
    
    def refresh(self):
        """Refresh calendar when tab is selected"""
        self.draw_calendar()
