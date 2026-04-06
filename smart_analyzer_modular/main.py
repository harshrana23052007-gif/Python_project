"""
Smart Expense Analyzer - Main Entry Point
Run this file to start the application
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ui.app import SmartExpenseAnalyzer


if __name__ == "__main__":
    app = SmartExpenseAnalyzer()
    app.mainloop()
