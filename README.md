# Smart Expense Analyzer

A modern, professional-looking desktop expense tracking application built with Python and Tkinter.

## Features

✨ **Modern UI Design**

- Dark/Light mode toggle with seamless theme switching
- Professional sidebar navigation
- Dashboard layout inspired by fintech apps
- Smooth transitions between views
- Responsive design

💰 **Expense Management**

- Add expenses with amount, category, date, and description
- 7 predefined categories (Food, Travel, Shopping, Bills, Entertainment, Health, Others)
- SQLite database for persistent storage
- Input validation
- Recent transactions display

📊 **Dashboard**

- Real-time summary of monthly expenses
- Budget tracking and remaining balance
- Category-wise spending breakdown
- Recent transactions list

📈 **Reports & Analytics**

- Interactive pie chart showing category distribution
- Bar chart showing monthly spending trends
- Month and year selectors for custom date ranges
- Data visualization using Matplotlib

💾 **Data Export**

- Export all expenses to Excel (.xlsx)
- Generate PDF reports with summary statistics
- Exportable monthly reports

⚙️ **Settings**

- Customize monthly budget
- Select preferred currency
- Dark/Light mode toggle
- Budget alerts when spending exceeds limit

## Requirements

```
Python 3.7 or higher
tkinter (usually bundled with Python)
matplotlib
pandas
reportlab
sqlite3 (built-in)
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install matplotlib pandas reportlab
```

### 2. Run the Application

```bash
python smart_expense_analyzer.py
```

The application will automatically:

- Create a SQLite database (`expenses.db`)
- Initialize tables for expenses and settings
- Create default settings with $5000 monthly budget

## Project Structure (Single File)

```
smart_expense_analyzer.py
├── DatabaseManager (database operations)
├── ThemeManager (UI theming)
├── SmartExpenseAnalyzer (main app)
├── DashboardFrame (dashboard view)
├── AddExpenseFrame (expense form)
├── ReportsFrame (charts & analytics)
└── SettingsFrame (app settings)
```

## How to Use

### Adding an Expense

1. Click **➕ Add Expense** in the sidebar
2. Enter amount, select category, set date
3. Optionally add description
4. Click **Save Expense**

### Viewing Dashboard

1. Click **📊 Dashboard** to see overview
2. View this month's total spending
3. See category breakdown
4. Check recent transactions

### Generating Reports

1. Click **📈 Reports**
2. Select month and year
3. Click **Generate Reports** to see charts
4. Click **Export to PDF** to save report

### Exporting Data

1. Click **⚙️ Settings**
2. Click **Export to Excel** to save all data
3. Choose location and filename

### Toggling Dark Mode

- Use the **🌙 Dark Mode** toggle in the bottom-left of sidebar
- Settings persist automatically

## Database Schema

### expenses table

```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### settings table

```sql
CREATE TABLE settings (
    id INTEGER PRIMARY KEY,
    monthly_budget REAL DEFAULT 5000,
    dark_mode INTEGER DEFAULT 1,
    currency TEXT DEFAULT 'USD'
)
```

## Modularizing the Code

For a larger project, you can split `smart_expense_analyzer.py` into:

```
project/
├── main.py                 # Application entry point
├── database/
│   └── db_manager.py      # DatabaseManager class
├── ui/
│   ├── __init__.py
│   ├── app.py             # SmartExpenseAnalyzer class
│   ├── themes.py          # ThemeManager class
│   ├── frames.py          # All frame classes
│   └── widgets.py         # Custom widgets (if needed)
├── utils/
│   ├── __init__.py
│   └── validators.py      # Input validation functions
├── reports/
│   └── chart_generator.py # Chart generation
├── config.py              # Configuration constants
└── expenses.db            # SQLite database (auto-created)
```

## Tips & Tricks

1. **Date Format**: Use YYYY-MM-DD format (e.g., 2024-01-15)
2. **Budget Alerts**: You'll see a popup if spending exceeds budget
3. **Dark Mode**: Automatically saves your preference
4. **Charts**: Dynamically update based on selected month
5. **PDF Export**: Includes summary statistics and category breakdown
6. **Excel Export**: All data with timestamps for external analysis

## Troubleshooting

### ModuleNotFoundError for matplotlib, pandas, or reportlab

```bash
pip install matplotlib pandas reportlab
```

### Database locked error

- Close the application properly and try again

### Charts not displaying

- Ensure matplotlib is installed and compatible with your Python version

### PDF export fails

- Check write permissions in the chosen directory

## Future Enhancement Ideas

1. **Budget Categories**: Set different budgets per category
2. **Recurring Expenses**: Add recurring expense templates
3. **Import CSV**: Import expenses from CSV files
4. **Multi-currency**: Automatic conversion rates
5. **Goals Tracking**: Set and track savings goals
6. **Backup/Restore**: Auto-backup to cloud
7. **Mobile App**: Sync with mobile application
8. **Notifications**: Desktop notifications for budget alerts

## License

This project is open source and available for personal and educational use.

## Contact & Support

For issues or suggestions, ensure:

- Python and all dependencies are properly installed
- Database permissions are correct
- Date formats follow YYYY-MM-DD standard

---

**Version**: 1.0  
**Last Updated**: 2024  
**Built with**: Python, Tkinter, SQLite, Matplotlib, Pandas, ReportLab
