"""
Financial Advisor System - Analyzes spending patterns and provides insights
"""

from datetime import datetime, timedelta
from collections import defaultdict


class FinancialAdvisor:
    """Provides smart financial advice based on spending patterns"""
    
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
    
    def analyze_spending_patterns(self, year=None, month=None):
        """Analyze spending patterns and return insights"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get expenses for the month
        expenses = self.db.get_expenses_by_month(self.user_id, year, month)
        
        if not expenses:
            return {
                'overspending_categories': [],
                'most_expensive_day': None,
                'saving_tips': ['Start tracking your expenses to get personalized advice!'],
                'total_spent': 0,
                'budget_status': 'No expenses yet'
            }
        
        # Get budget
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        total_spent = self.db.get_current_month_total(self.user_id)
        
        # Analyze by category
        category_analysis = self._analyze_by_category(expenses, budget, total_spent)
        
        # Find most expensive day
        most_expensive_day = self._find_most_expensive_day(expenses)
        
        # Generate tips
        tips = self._generate_tips(category_analysis, total_spent, budget, expenses)
        
        # Budget status
        if total_spent > budget:
            budget_status = f"Over budget by ${total_spent - budget:.2f}"
        elif total_spent > budget * 0.9:
            budget_status = f"Approaching budget limit (90% spent)"
        else:
            remaining = budget - total_spent
            budget_status = f"On track! ${remaining:.2f} remaining"
        
        return {
            'overspending_categories': category_analysis['alerts'],
            'most_expensive_day': most_expensive_day,
            'saving_tips': tips,
            'total_spent': total_spent,
            'budget': budget,
            'budget_status': budget_status,
            'category_breakdown': category_analysis['breakdown']
        }
    
    def _analyze_by_category(self, expenses, budget, total_spent):
        """Analyze spending by category"""
        category_totals = defaultdict(float)
        
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            category_totals[category] += amount
        
        # Determine which categories are overspending
        alerts = []
        breakdown = []
        
        avg_per_category = total_spent / len(category_totals) if category_totals else 0
        
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spent * 100) if total_spent > 0 else 0
            breakdown.append({
                'category': category,
                'amount': amount,
                'percentage': percentage
            })
            
            # Alert if category exceeds average significantly
            if amount > avg_per_category * 1.5:
                savings_potential = amount * 0.1  # 10% reduction potential
                alerts.append({
                    'category': category,
                    'amount': amount,
                    'savings_potential': savings_potential,
                    'percentage': percentage
                })
        
        return {
            'alerts': alerts,
            'breakdown': breakdown
        }
    
    def _find_most_expensive_day(self, expenses):
        """Find the day with highest spending"""
        daily_totals = defaultdict(float)
        
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            daily_totals[date] += amount
        
        if not daily_totals:
            return None
        
        most_expensive = max(daily_totals.items(), key=lambda x: x[1])
        day_name = datetime.strptime(most_expensive[0], "%Y-%m-%d").strftime("%A")
        
        return {
            'date': most_expensive[0],
            'day_name': day_name,
            'amount': most_expensive[1]
        }
    
    def _get_day_frequency(self, expenses):
        """Get spending frequency by day of week"""
        day_spending = defaultdict(lambda: {'total': 0, 'count': 0})
        
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            day_of_week = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
            day_spending[day_of_week]['total'] += amount
            day_spending[day_of_week]['count'] += 1
        
        return day_spending
    
    def _generate_tips(self, category_analysis, total_spent, budget, expenses):
        """Generate personalized saving tips"""
        tips = []
        
        # Tip 1: Category alerts
        if category_analysis['alerts']:
            top_alert = category_analysis['alerts'][0]
            savings = top_alert['savings_potential']
            tips.append(
                f"💡 Reduce {top_alert['category']} spending by just 10% "
                f"to save ${savings:.2f} this month!"
            )
        
        # Tip 2: Day of week analysis
        day_spending = self._get_day_frequency(expenses)
        if day_spending:
            avg_day = total_spent / 30  # Approximate
            expensive_days = [d for d, s in day_spending.items() if s['total'] > avg_day * 1.5]
            if expensive_days:
                tips.append(
                    f"📅 You spend more on {expensive_days[0]}s. "
                    f"Plan ahead to reduce weekend spending!"
                )
        
        # Tip 3: Budget status
        if total_spent > budget:
            overage = total_spent - budget
            tips.append(
                f"⚠️ Your current spending exceeds budget by ${overage:.2f}. "
                f"Focus on reducing luxury categories this month."
            )
        elif total_spent > budget * 0.8:
            tips.append(
                f"📊 You've used {(total_spent/budget*100):.0f}% of your budget. "
                f"Monitor spending closely in the remaining days."
            )
        else:
            remaining_days = 30 - datetime.now().day
            remaining_budget = budget - total_spent
            daily_allowance = remaining_budget / remaining_days if remaining_days > 0 else 0
            tips.append(
                f"✅ Excellent! You have ${remaining_budget:.2f} left. "
                f"Daily allowance: ${daily_allowance:.2f}"
            )
        
        # Tip 4: Consistency
        if len(expenses) > 0:
            tips.append(
                f"📈 You made {len(expenses)} transactions this month. "
                f"Keep tracking to build better spending habits!"
            )
        
        return tips[:4]  # Return top 4 tips
    
    def get_category_insights(self):
        """Get insights about each spending category"""
        now = datetime.now()
        expenses = self.db.get_expenses_by_month(self.user_id, now.year, now.month)
        
        category_stats = defaultdict(lambda: {'count': 0, 'total': 0, 'avg': 0})
        
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            category_stats[category]['count'] += 1
            category_stats[category]['total'] += amount
        
        for category in category_stats:
            if category_stats[category]['count'] > 0:
                category_stats[category]['avg'] = (
                    category_stats[category]['total'] / category_stats[category]['count']
                )
        
        return dict(category_stats)
