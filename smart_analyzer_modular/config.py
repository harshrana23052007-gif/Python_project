"""
Configuration constants for Smart Expense Analyzer
"""

# Database
DATABASE_NAME = "expenses.db"
DEFAULT_BUDGET = 5000
DEFAULT_CURRENCY = "INR"

# UI Constants
DEFAULT_THEME = "dark"  # "dark" or "light"

# Window
WINDOW_TITLE = "Smart Expense Analyzer"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
MIN_WIDTH = 1000
MIN_HEIGHT = 600

# Font
FONT_FAMILY = "Segoe UI"
FONT_SIZES = {
    "title": 24,
    "heading": 14,
    "normal": 10,
    "small": 9,
}

# Categories
EXPENSE_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Others"
]

# Currency options
CURRENCIES = ["USD", "EUR", "GBP", "INR", "AUD"]

# Recent transactions limit
RECENT_LIMIT = 5

# Chart settings
CHART_DPI = 100
CHART_SIZE = (12, 5)
