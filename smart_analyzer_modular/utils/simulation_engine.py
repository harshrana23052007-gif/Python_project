"""
What-If Simulation - Simulate budget changes and savings
"""

from datetime import datetime


class SimulationEngine:
    """Simulates spending changes and shows savings potential"""
    
    def __init__(self, db_manager, user_id):
        self.db = db_manager
        self.user_id = user_id
    
    def simulate_category_reduction(self, category_name, reduction_percentage, year=None, month=None):
        """
        Simulate reducing spending in a category
        
        Args:
            category_name: Category to reduce (e.g., 'Food', 'Shopping')
            reduction_percentage: Percentage to reduce (0-100)
            year: Analysis year
            month: Analysis month
        
        Returns:
            Dictionary with simulation results
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        # Get actual data
        expenses = self.db.get_expenses_by_month(self.user_id, year, month)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        
        # Calculate current totals
        total_spent = sum(exp[2] for exp in expenses)  # exp[2] is amount
        category_spent = sum(exp[2] for exp in expenses if exp[3] == category_name)  # exp[3] is category
        
        # Calculate simulation
        reduction_amount = category_spent * (reduction_percentage / 100)
        new_category_total = category_spent - reduction_amount
        new_total_spent = total_spent - reduction_amount
        new_remaining = budget - new_total_spent
        old_remaining = budget - total_spent
        
        savings = new_total_spent - total_spent  # Negative = savings
        
        # Calculate impact
        budget_ratio_before = total_spent / budget if budget > 0 else 0
        budget_ratio_after = new_total_spent / budget if budget > 0 else 0
        
        return {
            'category': category_name,
            'reduction_percentage': reduction_percentage,
            'simulation': {
                'reduced_category_amount': new_category_total,
                'category_reduction_amount': reduction_amount,
                'total_spent_before': total_spent,
                'total_spent_after': new_total_spent,
                'total_savings': reduction_amount,
                'budget_before': budget,
                'budget_after': budget,  # Budget doesn't change
                'remaining_before': old_remaining,
                'remaining_after': new_remaining,
                'budget_ratio_before': budget_ratio_before,
                'budget_ratio_after': budget_ratio_after,
                'within_budget_before': total_spent <= budget,
                'within_budget_after': new_total_spent <= budget,
                'improvement': new_remaining - old_remaining
            }
        }
    
    def simulate_multiple_categories(self, reductions, year=None, month=None):
        """
        Simulate reducing multiple categories at once
        
        Args:
            reductions: Dict of {category: reduction_percentage}
            year: Analysis year
            month: Analysis month
        
        Returns:
            Combined simulation results
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        expenses = self.db.get_expenses_by_month(self.user_id, year, month)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        
        # Calculate totals
        total_spent = sum(exp[2] for exp in expenses)  # exp[2] is amount
        old_remaining = budget - total_spent
        
        # Apply all reductions
        total_reduction = 0
        category_changes = {}
        
        for category, reduction_pct in reductions.items():
            category_amount = sum(exp[1] for exp in expenses if exp[2] == category)
            reduction_amount = category_amount * (reduction_pct / 100)
            total_reduction += reduction_amount
            category_changes[category] = {
                'before': category_amount,
                'after': category_amount - reduction_amount,
                'reduction': reduction_amount,
                'reduction_percentage': reduction_pct
            }
        
        new_total = total_spent - total_reduction
        new_remaining = budget - new_total
        
        return {
            'reductions': reductions,
            'simulation': {
                'total_spent_before': total_spent,
                'total_spent_after': new_total,
                'total_savings': total_reduction,
                'remaining_before': old_remaining,
                'remaining_after': new_remaining,
                'improvement': new_remaining - old_remaining,
                'budget': budget,
                'within_budget_before': total_spent <= budget,
                'within_budget_after': new_total <= budget,
                'category_changes': category_changes
            }
        }
    
    def suggest_reductions(self, target_amount=None, year=None, month=None):
        """
        Suggest category reductions to reach a target savings
        
        Args:
            target_amount: Target savings amount (if None, uses 10% of budget)
            year: Analysis year
            month: Analysis month
        
        Returns:
            Suggested reductions to achieve target
        """
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month
        
        expenses = self.db.get_expenses_by_month(self.user_id, year, month)
        settings = self.db.get_settings(self.user_id)
        budget = settings[0]
        
        total_spent = sum(exp[1] for exp in expenses)
        
        if target_amount is None:
            target_amount = budget * 0.1  # 10% of budget
        
        # Get category totals
        category_totals = {}
        for expense in expenses:
            category = expense[2]
            amount = expense[1]
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += amount
        
        # Sort categories by spending (highest first)
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate reductions needed
        remaining_target = target_amount
        suggested_reductions = {}
        
        for category, amount in sorted_categories:
            if remaining_target <= 0:
                break
            
            # Suggest reducing this category by minimum of:
            # 1. What's needed to meet target
            # 2. 25% of current category spending
            max_reduction = amount * 0.25  # Don't reduce by more than 25%
            reduction_needed = min(remaining_target, max_reduction)
            reduction_pct = (reduction_needed / amount * 100) if amount > 0 else 0
            
            if reduction_pct > 0:
                suggested_reductions[category] = reduction_pct
                remaining_target -= reduction_needed
        
        return {
            'target_savings': target_amount,
            'suggested_reductions': suggested_reductions,
            'total_achievable_savings': target_amount - remaining_target,
            'categories': category_totals
        }
    
    def get_simulation_summary(self, simulation_result):
        """Get a text summary of simulation"""
        sim = simulation_result['simulation']
        
        summary = f"""
📊 WHAT-IF SIMULATION RESULTS

Current State:
  💰 Total Spending: ₹{sim['total_spent_before']:.2f}
  📋 Remaining Budget: ₹{sim['remaining_before']:.2f}
  Status: {'✅ Under budget' if sim['within_budget_before'] else '⚠️ Over budget'}

After Reduction:
  💰 New Total Spending: ₹{sim['total_spent_after']:.2f}
  📋 New Remaining Budget: ₹{sim['remaining_after']:.2f}
  Status: {'✅ Under budget' if sim['within_budget_after'] else '⚠️ Over budget'}

Impact:
  💡 Potential Savings: ₹{sim['total_savings']:.2f}
  📈 Budget Improvement: ₹{sim['improvement']:.2f}
"""
        
        return summary.strip()
