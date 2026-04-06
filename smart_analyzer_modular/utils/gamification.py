"""
Gamification Module - Tracking streaks and awarding badges
"""

from datetime import datetime, timedelta


class GamificationManager:
    """Manages user achievements and streaks"""
    
    # Badge definitions
    BADGES = {
        'Budget Master': {
            'icon': '👑',
            'description': 'Stay under budget for 7 consecutive days',
            'requirement': 'streak_7'
        },
        'Smart Saver': {
            'icon': '💎',
            'description': 'Spend 30% less than budget in a month',
            'requirement': 'budget_30_percent'
        },
        'Consistent Tracker': {
            'icon': '📊',
            'description': 'Track expenses for 20 consecutive days',
            'requirement': 'tracked_20_days'
        },
        'Weekend Warrior': {
            'icon': '⚡',
            'description': 'Complete a weekend without overspending',
            'requirement': 'weekend_safe'
        },
        'Financial Champion': {
            'icon': '🏆',
            'description': 'Earn 3 different badges',
            'requirement': 'three_badges'
        }
    }
    
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
    
    def update_daily_streak(self):
        """Update the daily saving streak"""
        current_total = self.db.get_current_month_total(self.user_id)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        today = datetime.now().strftime("%Y-%m-%d")
        
        current_streak, longest_streak, last_date = self.db.get_streak_info(self.user_id)
        
        # Check if today is under budget
        is_under_budget = current_total <= budget
        
        if is_under_budget:
            # Update last_under_budget_date
            self.db.update_streak(
                self.user_id,
                current_streak + 1,
                max(longest_streak, current_streak + 1),
                today
            )
            current_streak += 1
        else:
            # Reset streak if over budget
            if longest_streak < current_streak:
                longest_streak = current_streak
            self.db.update_streak(self.user_id, 0, longest_streak, today)
            current_streak = 0
        
        # Check for badge eligibility
        self._check_streak_badges(current_streak)
        self._check_monthly_badges()
        
        return current_streak, longest_streak
    
    def _check_streak_badges(self, current_streak):
        """Check and award streak-based badges"""
        if current_streak == 7 and not self.db.has_achievement(self.user_id, 'Budget Master'):
            self.db.add_achievement(
                self.user_id,
                'Budget Master',
                'Stayed under budget for 7 consecutive days'
            )
        
        if current_streak == 14 and not self.db.has_achievement(self.user_id, 'Consistent Tracker'):
            self.db.add_achievement(
                self.user_id,
                'Consistent Tracker',
                'Tracked expenses for 14 consecutive days'
            )
    
    def _check_monthly_badges(self):
        """Check and award monthly-based badges"""
        now = datetime.now()
        current_total = self.db.get_current_month_total(self.user_id)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        
        # Smart Saver: Spend 30% less than budget
        if current_total <= budget * 0.7 and not self.db.has_achievement(self.user_id, 'Smart Saver'):
            self.db.add_achievement(self.user_id,
                'Smart Saver',
                f'Spent only ${current_total:.2f} of ${budget:.2f} budget'
            )
        
        # Weekend Warrior
        self._check_weekend_badge()
        
        # Financial Champion
        self._check_champion_badge()
    
    def _check_weekend_badge(self):
        """Check if user qualifies for weekend warrior badge"""
        if self.db.has_achievement(self.user_id, 'Weekend Warrior'):
            return
        
        # Get weekend expenses for current month
        from datetime import date
        now = datetime.now()
        
        # Find the last complete weekend
        today = now.date()
        last_sunday = today - timedelta(days=(today.weekday() + 1) % 7 or 7)
        saturday = last_sunday - timedelta(days=1)
        
        expenses = self.db.get_expenses_by_month(self.user_id, now.year, now.month)
        
        weekend_expenses = []
        for expense in expenses:
            id, user_id, amount, category, date_str, description, created_at = expense
            exp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if exp_date in [saturday, last_sunday]:
                weekend_expenses.append(amount)
        
        # Simple check: no weekend expenses or minimal spending
        if not weekend_expenses or sum(weekend_expenses) < 50:
            self.db.add_achievement(
                self.user_id,
                'Weekend Warrior',
                'Completed a weekend without overspending'
            )
    
    def _check_champion_badge(self):
        """Check if user qualifies for financial champion badge"""
        if self.db.has_achievement(self.user_id, 'Financial Champion'):
            return
        
        achievements = self.db.get_achievements(self.user_id)
        # Exclude the "Financial Champion" badge itself from count
        achievement_count = len([a for a in achievements if a[0] != 'Financial Champion'])
        
        if achievement_count >= 3:
            self.db.add_achievement(
                self.user_id,
                'Financial Champion',
                'Earned 3 or more achievement badges'
            )
    
    def get_all_badges(self):
        """Get all available badges with their status"""
        earned_achievements = self.db.get_achievements(self.user_id)
        earned_badge_names = {a[0] for a in earned_achievements}
        
        badges_list = []
        for badge_name, badge_info in self.BADGES.items():
            badges_list.append({
                'name': badge_name,
                'icon': badge_info['icon'],
                'description': badge_info['description'],
                'earned': badge_name in earned_badge_names
            })
        
        return badges_list
    
    def get_earned_badges(self):
        """Get only earned badges"""
        achievements = self.db.get_achievements(self.user_id)
        badges = []
        
        for name, earned_date, description in achievements:
            if name in self.BADGES:
                badges.append({
                    'name': name,
                    'icon': self.BADGES[name]['icon'],
                    'description': description,
                    'earned_date': earned_date
                })
        
        return badges
    
    def get_progress_stats(self):
        """Get progress towards next badge"""
        current_streak, longest_streak, _ = self.db.get_streak_info(self.user_id)
        now = datetime.now()
        current_total = self.db.get_current_month_total(self.user_id)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        
        stats = {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'budget_master_progress': f"{current_streak}/7 days",
            'smart_saver_progress': f"{(current_total/budget*100):.0f}% of budget spent",
            'consistent_tracker_progress': f"{current_streak}/20 days"
        }
        
        return stats
