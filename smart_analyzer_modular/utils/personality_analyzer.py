"""
Financial Personality Analyzer - Classifies user spending behavior
"""

from datetime import datetime, timedelta
from collections import defaultdict


class PersonalityAnalyzer:
    """Analyzes spending habits to classify user personality type"""
    
    # Personality types with descriptions
    PERSONALITIES = {
        'Saver': {
            'icon': '🏦',
            'color': '#4CAF50',
            'description': 'You are a careful spender who keeps expenses well under budget',
            'traits': [
                'Maintains low monthly spending',
                'Consistently under budget',
                'Builds savings',
                'Makes thoughtful purchases'
            ]
        },
        'Impulse Spender': {
            'icon': '⚡',
            'color': '#FF6F00',
            'description': 'You tend to make spontaneous purchases and may overspend',
            'traits': [
                'Frequent small transactions',
                'Often exceeds budget',
                'Varied spending patterns',
                'Needs to plan better'
            ]
        },
        'Category-Focused': {
            'icon': '🎯',
            'color': '#2196F3',
            'description': 'You prioritize spending in specific categories',
            'traits': [
                'High concentration in 1-2 categories',
                'Dedicated budget allocation',
                'Clear spending priorities',
                'Specialized lifestyle'
            ]
        },
        'Weekend Spender': {
            'icon': '🎉',
            'color': '#9C27B0',
            'description': 'You spend significantly more on weekends',
            'traits': [
                'Weekend spending spikes',
                'Weekday restraint',
                'Social spending pattern',
                'Higher entertainment costs'
            ]
        },
        'Consistent Budgeter': {
            'icon': '📊',
            'color': '#00BCD4',
            'description': 'Your spending is steady and predictable each month',
            'traits': [
                'Stable monthly spending',
                'Predictable patterns',
                'Well balanced budget',
                'Disciplined spender'
            ]
        }
    }
    
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
    
    def analyze_personality(self, year=None, month=None):
        """Analyze user spending personality"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get all data for analysis
        expenses = self.db.get_expenses_by_month(self.user_id, year, month)
        
        if not expenses:
            return {
                'personality': 'New Saver',
                'icon': '🌱',
                'confidence': 0,
                'description': 'Start tracking expenses to discover your spending personality!',
                'traits': []
            }
        
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        total_spent = self.db.get_current_month_total(self.user_id)
        
        # Collect analysis data
        analysis_data = {
            'total_spent': total_spent,
            'budget': budget,
            'transaction_count': len(expenses),
            'category_breakdown': self._get_category_breakdown(expenses),
            'daily_patterns': self._analyze_daily_patterns(expenses),
            'day_of_week_spending': self._get_day_of_week_spending(expenses)
        }
        
        # Determine personality
        personality = self._classify_personality(analysis_data, total_spent, budget)
        
        return personality
    
    def _get_category_breakdown(self, expenses):
        """Get spending by category"""
        breakdown = defaultdict(float)
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            breakdown[category] += amount
        return dict(breakdown)
    
    def _analyze_daily_patterns(self, expenses):
        """Analyze daily spending patterns"""
        daily = defaultdict(float)
        for expense in expenses:
            id, user_id, amount, category, date, description, created_at = expense
            daily[date] += amount
        return daily
    
    def _get_day_of_week_spending(self, expenses):
        """Get spending by day of week"""
        day_spending = defaultdict(lambda: {'total': 0, 'count': 0})
        for expense in expenses:
            id, user_id, amount, category, date_str, description, created_at = expense
            day_of_week = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
            day_spending[day_of_week]['total'] += amount
            day_spending[day_of_week]['count'] += 1
        return dict(day_spending)
    
    def _classify_personality(self, data, total_spent, budget):
        """Classify user into personality type"""
        scores = {
            'Saver': 0,
            'Impulse Spender': 0,
            'Category-Focused': 0,
            'Weekend Spender': 0,
            'Consistent Budgeter': 0
        }
        
        # Score 1: Budget adherence
        budget_ratio = total_spent / budget if budget > 0 else 0
        if budget_ratio <= 0.5:
            scores['Saver'] += 30
        elif budget_ratio >= 1.2:
            scores['Impulse Spender'] += 25
        else:
            scores['Consistent Budgeter'] += 15
        
        # Score 2: Transaction frequency
        if data['transaction_count'] > 25:
            scores['Impulse Spender'] += 20
        elif data['transaction_count'] < 10:
            scores['Saver'] += 15
        else:
            scores['Consistent Budgeter'] += 10
        
        # Score 3: Category concentration
        categories = data['category_breakdown']
        if categories:
            total = sum(categories.values())
            top_category_pct = max(categories.values()) / total if total > 0 else 0
            
            if top_category_pct > 0.45:
                scores['Category-Focused'] += 35
            else:
                scores['Consistent Budgeter'] += 10
        
        # Score 4: Weekend spending pattern
        day_of_week = data['day_of_week_spending']
        if day_of_week:
            weekday_avg = sum(
                day['total'] for day in day_of_week.values()
                if any(wd in str(day) for wd in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
            ) / 5 if len(day_of_week) >= 5 else 0
            
            weekend_avg = sum(
                day['total'] for day in day_of_week.values()
                if any(wd in str(day) for wd in ['Saturday', 'Sunday'])
            ) / 2 if any(wd in str(day) for wd in ['Saturday', 'Sunday'] for day in day_of_week.values()) else 0
            
            if weekend_avg > weekday_avg * 1.5:
                scores['Weekend Spender'] += 30
        
        # Score 5: Consistency
        daily_values = list(data['daily_patterns'].values())
        if daily_values:
            avg_daily = sum(daily_values) / len(daily_values)
            variance = sum((x - avg_daily) ** 2 for x in daily_values) / len(daily_values)
            std_dev = variance ** 0.5
            
            coefficient_of_variation = std_dev / avg_daily if avg_daily > 0 else 0
            
            if coefficient_of_variation < 0.5:
                scores['Consistent Budgeter'] += 25
            elif coefficient_of_variation > 1.0:
                scores['Impulse Spender'] += 20
        
        # Determine winner
        best_personality = max(scores, key=scores.get)
        confidence = scores[best_personality]
        
        personality_info = self.PERSONALITIES.get(best_personality, {})
        
        return {
            'personality': best_personality,
            'icon': personality_info.get('icon', '💰'),
            'color': personality_info.get('color', '#2196F3'),
            'confidence': min(confidence, 100),
            'description': personality_info.get('description', ''),
            'traits': personality_info.get('traits', []),
            'scores': scores
        }
    
    def get_improvement_suggestions(self, personality_type):
        """Get personalized suggestions based on personality"""
        suggestions = {
            'Saver': [
                '🎉 Great job! Consider treating yourself occasionally!',
                '📈 You could allocate more budget for entertainment',
                '💝 Consider gift-giving or charitable donations',
                '🎓 Invest in self-improvement courses'
            ],
            'Impulse Spender': [
                '⏸️ Wait 24 hours before making non-essential purchases',
                '📋 Create a shopping list and stick to it',
                '💳 Consider using cash for discretionary spending',
                '📊 Set daily spending limits for categories'
            ],
            'Category-Focused': [
                '🔄 Diversify your spending to enjoy more variety',
                '📚 Explore other categories to round out lifestyle',
                f'🎯 You excel in your focus area - maintain the passion!',
                '⚖️ Balance your specialty with other important areas'
            ],
            'Weekend Spender': [
                '🏃 Plan weekday activities to reduce weekend spending',
                '🎬 Look for free or low-cost weekend activities',
                '🍽️ Set weekend budget limits in advance',
                '👥 Suggest budget-friendly group activities'
            ],
            'Consistent Budgeter': [
                '⭐ Perfect consistency! You have great control!',
                '🎯 Your predictability makes budgeting easy',
                '💎 Consider increasing savings goals',
                '🌟 You are a role model for financial discipline!'
            ]
        }
        
        return suggestions.get(personality_type, [])
