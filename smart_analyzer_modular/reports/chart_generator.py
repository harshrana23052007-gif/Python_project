"""
Chart generation for Reports
Handles Matplotlib chart creation
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import calendar
import config


class ChartGenerator:
    """Generates charts and reports"""
    
    @staticmethod
    def create_report_figure(categories_data, monthly_totals, theme, year):
        """Create figure with pie and bar charts"""
        fig = Figure(figsize=config.CHART_SIZE, dpi=config.CHART_DPI, 
                    facecolor=theme['frame_bg'])
        
        # Pie chart
        ax1 = fig.add_subplot(121)
        categories_list = [c[0] for c in categories_data]
        amounts = [c[1] for c in categories_data]
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
        ax1.pie(amounts, labels=categories_list, autopct='%1.1f%%', colors=colors)
        ax1.set_title('Spending by Category', fontsize=12, fontweight='bold', 
                     color=theme['text_primary'])
        ax1.set_facecolor(theme['frame_bg'])
        
        # Bar chart for monthly trend
        ax2 = fig.add_subplot(122)
        months = [calendar.month_abbr[i] for i in range(1, 13)]
        
        bars = ax2.bar(months, monthly_totals, color=theme['accent'])
        ax2.set_title('Monthly Spending Trend', fontsize=12, fontweight='bold', 
                     color=theme['text_primary'])
        ax2.set_ylabel('Amount ($)', color=theme['text_primary'])
        ax2.tick_params(colors=theme['text_primary'])
        ax2.set_facecolor(theme['frame_bg'])
        ax2.grid(axis='y', alpha=0.3)
        
        # Set spine colors
        for ax in [ax1, ax2]:
            for spine in ax.spines.values():
                spine.set_color(theme['border'])
        
        fig.tight_layout()
        return fig
