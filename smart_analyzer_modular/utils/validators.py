"""
Input validators for Smart Expense Analyzer
Validates user input in forms
"""

def validate_amount(amount_str):
    """Validate expense amount"""
    try:
        amount = float(amount_str)
        return amount > 0, "Amount must be greater than 0"
    except ValueError:
        return False, "Please enter a valid amount"


def validate_date(date_str):
    """Validate date format (YYYY-MM-DD)"""
    if not date_str or len(date_str) != 10:
        return False, "Please enter date in YYYY-MM-DD format"
    
    parts = date_str.split('-')
    if len(parts) != 3:
        return False, "Invalid date format"
    
    try:
        year = int(parts[0])
        month = int(parts[1])
        day = int(parts[2])
        
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return False, "Invalid month or day"
        
        return True, "Valid date"
    except ValueError:
        return False, "Invalid date format"


def validate_budget(budget_str):
    """Validate budget amount"""
    try:
        budget = float(budget_str)
        return budget > 0, "Budget must be greater than 0"
    except ValueError:
        return False, "Please enter a valid budget amount"


def validate_all_expense_fields(amount, category, date, categories_list):
    """Validate all expense form fields"""
    # Validate amount
    valid, msg = validate_amount(amount)
    if not valid:
        return False, msg
    
    # Validate category
    if category not in categories_list:
        return False, "Please select a valid category"
    
    # Validate date
    valid, msg = validate_date(date)
    if not valid:
        return False, msg
    
    return True, "All fields valid"
