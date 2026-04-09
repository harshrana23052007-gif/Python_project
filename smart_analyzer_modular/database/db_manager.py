"""
Database management for Smart Expense Analyzer
Handles all SQLite operations
"""

import sqlite3
from tkinter import messagebox
import pandas as pd
import config
from utils.auth_utils import hash_password, verify_password


class DatabaseManager:
    """Manages all database operations for expenses"""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_NAME
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create expenses table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create settings table with user_id
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                monthly_budget REAL DEFAULT {config.DEFAULT_BUDGET},
                dark_mode INTEGER DEFAULT 1,
                currency TEXT DEFAULT '{config.DEFAULT_CURRENCY}',
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create streak tracking table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                current_streak INTEGER DEFAULT 0,
                longest_streak INTEGER DEFAULT 0,
                last_tracked_date TEXT,
                last_under_budget_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create achievements table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                badge_name TEXT NOT NULL,
                earned_date TEXT,
                description TEXT,
                UNIQUE (user_id, badge_name),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        # Create daily spending table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_spending (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                total_amount REAL DEFAULT 0,
                expense_count INTEGER DEFAULT 0,
                UNIQUE (user_id, date),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ==================== USER AUTHENTICATION ====================
    
    def register_user(self, username, password):
        """
        Register a new user
        Returns: (success: bool, message: str, user_id: int or None)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            if cursor.fetchone():
                conn.close()
                return False, "Username already exists", None
            
            # Hash password and insert user
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (username, password_hash))
            
            user_id = cursor.lastrowid
            
            # Create user settings and streak records
            cursor.execute('''
                INSERT INTO settings (user_id, monthly_budget, dark_mode)
                VALUES (?, ?, 1)
            ''', (user_id, config.DEFAULT_BUDGET))
            
            cursor.execute('''
                INSERT INTO streaks (user_id, current_streak, longest_streak)
                VALUES (?, 0, 0)
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            
            return True, "User registered successfully", user_id
        except Exception as e:
            return False, f"Registration error: {str(e)}", None
    
    def login_user(self, username, password):
        """
        Login a user
        Returns: (success: bool, message: str, user_id: int or None)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user record
            cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False, "Username not found", None
            
            user_id, password_hash = result
            
            # Verify password
            if verify_password(password, password_hash):
                conn.close()
                return True, "Login successful", user_id
            else:
                conn.close()
                return False, "Password incorrect", None
        except Exception as e:
            return False, f"Login error: {str(e)}", None
    
    def get_username(self, user_id):
        """Get username for a user_id"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except:
            return None
    
    def add_expense(self, user_id, amount, category, date, description):
        """Add a new expense for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, amount, category, date, description))
            conn.commit()
            conn.close()
            
            # Track daily spending
            self.update_daily_spending(user_id, date, amount)
            
            return True
        except Exception as e:
            messagebox.showerror("Database Error", f"Error adding expense: {str(e)}")
            return False
    
    def get_all_expenses(self, user_id):
        """Get all expenses for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC', (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_expenses_by_month(self, user_id, year, month):
        """Get expenses for a specific month for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        date_pattern = f"{year}-{month:02d}%"
        cursor.execute('''
            SELECT * FROM expenses WHERE user_id = ? AND date LIKE ? ORDER BY date DESC
        ''', (user_id, date_pattern))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_current_month_total(self, user_id):
        """Get total expenses for current month for a user"""
        from datetime import datetime
        now = datetime.now()
        date_pattern = f"{now.year}-{now.month:02d}%"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date LIKE ?
        ''', (user_id, date_pattern))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0
    
    def get_category_summary(self, user_id, year, month):
        """Get spending summary by category for a user for a specific month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        date_pattern = f"{year}-{month:02d}%"
        cursor.execute('''
            SELECT category, SUM(amount) FROM expenses 
            WHERE user_id = ? AND date LIKE ? 
            GROUP BY category
        ''', (user_id, date_pattern))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_recent_expenses(self, user_id, limit=None):
        """Get recent expenses for a user"""
        if limit is None:
            limit = config.RECENT_LIMIT
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?
        ''', (user_id, limit))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_settings(self, user_id):
        """Get application settings for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT monthly_budget, dark_mode, currency FROM settings WHERE user_id = ?
        ''', (user_id,))
        data = cursor.fetchone()
        conn.close()
        return data if data else (config.DEFAULT_BUDGET, 1, config.DEFAULT_CURRENCY)
    
    def update_settings(self, user_id, budget=None, dark_mode=None, currency=None):
        """Update application settings for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if budget is not None:
            cursor.execute('UPDATE settings SET monthly_budget = ? WHERE user_id = ?', 
                         (budget, user_id))
        if dark_mode is not None:
            cursor.execute('UPDATE settings SET dark_mode = ? WHERE user_id = ?', 
                         (dark_mode, user_id))
        if currency is not None:
            cursor.execute('UPDATE settings SET currency = ? WHERE user_id = ?', 
                         (currency, user_id))
        
        conn.commit()
        conn.close()
    
    def delete_expense(self, user_id, expense_id):
        """Delete an expense for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ? AND user_id = ?', (expense_id, user_id))
        conn.commit()
        conn.close()
    
    def export_to_excel(self, user_id, file_path):
        """Export expenses to Excel for a user"""
        try:
            expenses = self.get_all_expenses(user_id)
            if not expenses:
                raise ValueError("No expenses to export")
            
            df = pd.DataFrame(expenses, columns=['ID', 'User ID', 'Amount', 'Category', 'Date', 'Description', 'Created At'])
            
            # Create Excel writer with formatting
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Expenses', index=False)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Expenses']
                
                # Auto-adjust column widths
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(
                        df[col].astype(str).map(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(64 + idx)].width = max_length + 2
            
            return True
        except ImportError:
            raise Exception("openpyxl library not installed. Please install it: pip install openpyxl")
        except Exception as e:
            raise Exception(f"Excel export error: {str(e)}")
    
    def get_monthly_totals(self, user_id, year):
        """Get monthly totals for a user for a specific year"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        monthly_totals = []
        
        for month in range(1, 13):
            date_pattern = f"{year}-{month:02d}%"
            cursor.execute('''
                SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date LIKE ?
            ''', (user_id, date_pattern))
            total = cursor.fetchone()[0] or 0
            monthly_totals.append(total)
        
        conn.close()
        return monthly_totals
    
    # ==================== STREAK & ACHIEVEMENT METHODS ====================
    
    def get_streak_info(self, user_id):
        """Get current streak information for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT current_streak, longest_streak, last_under_budget_date FROM streaks 
            WHERE user_id = ?
        ''', (user_id,))
        data = cursor.fetchone()
        conn.close()
        return data if data else (0, 0, None)
    
    def update_streak(self, user_id, current_streak, longest_streak, last_under_budget_date):
        """Update streak information for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE streaks 
            SET current_streak = ?, longest_streak = ?, last_under_budget_date = ?
            WHERE user_id = ?
        ''', (current_streak, longest_streak, last_under_budget_date, user_id))
        conn.commit()
        conn.close()
    
    def add_achievement(self, user_id, badge_name, description):
        """Add an achievement badge for a user"""
        try:
            from datetime import datetime
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR IGNORE INTO achievements (user_id, badge_name, earned_date, description)
                VALUES (?, ?, ?, ?)
            ''', (user_id, badge_name, datetime.now().strftime("%Y-%m-%d"), description))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding achievement: {str(e)}")
            return False
    
    def get_achievements(self, user_id):
        """Get all earned achievements for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT badge_name, earned_date, description FROM achievements 
            WHERE user_id = ? ORDER BY earned_date DESC
        ''', (user_id,))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def has_achievement(self, user_id, badge_name):
        """Check if user has earned a specific achievement"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM achievements WHERE user_id = ? AND badge_name = ?
        ''', (user_id, badge_name))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    
    def update_daily_spending(self, user_id, date, amount):
        """Update daily spending total for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if date already exists for this user
        cursor.execute('''
            SELECT total_amount, expense_count FROM daily_spending 
            WHERE user_id = ? AND date = ?
        ''', (user_id, date))
        result = cursor.fetchone()
        
        if result:
            new_amount = result[0] + amount
            new_count = result[1] + 1
            cursor.execute('''
                UPDATE daily_spending SET total_amount = ?, expense_count = ? 
                WHERE user_id = ? AND date = ?
            ''', (new_amount, new_count, user_id, date))
        else:
            cursor.execute('''
                INSERT INTO daily_spending (user_id, date, total_amount, expense_count)
                VALUES (?, ?, ?, 1)
            ''', (user_id, date, amount))
        
        conn.commit()
        conn.close()
    
    def get_daily_spending(self, user_id, start_date, end_date):
        """Get daily spending for a user for a date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, total_amount FROM daily_spending 
            WHERE user_id = ? AND date BETWEEN ? AND ? 
            ORDER BY date
        ''', (user_id, start_date, end_date))
        data = cursor.fetchall()
        conn.close()
        return data
    
    def get_month_daily_spending(self, user_id, year, month):
        """Get daily spending for a user for a specific month"""
        from datetime import date, timedelta
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_daily_spending(user_id, str(first_day), str(last_day))
