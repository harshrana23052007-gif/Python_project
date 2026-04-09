"""
Theme management for Smart Expense Analyzer
Handles light and dark mode theming with CustomTkinter
"""

class ThemeManager:
    """Manages light and colorful themes for CustomTkinter"""
    
    # Light theme with enhanced modern colors
    LIGHT_THEME = {
        'bg': '#f5f7fa',
        'fg': '#1a202c',
        'sidebar_bg': '#e6f2ff',
        'button_bg': '#2563eb',
        'button_fg': '#ffffff',
        'button_hover': '#1d4ed8',
        'frame_bg': '#ffffff',
        'entry_bg': '#f0f4f8',
        'entry_fg': '#1a202c',
        'entry_border': '#cbd5e1',
        'accent': '#2563eb',
        'accent_light': '#dbeafe',
        'text_primary': '#1a202c',
        'text_secondary': '#64748b',
        'border': '#e2e8f0',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#0ea5e9',
        # Card colors for visual variety
        'card_bg': '#ffffff',
        'card_border': '#e2e8f0',
        # Sidebar button colors
        'sidebar_button_hover': '#dbeafe',
        'sidebar_text': '#1a202c'
    }
    
    # Modern dark theme (alternative)
    DARK_THEME = {
        'bg': '#0f172a',
        'fg': '#f1f5f9',
        'sidebar_bg': '#1e293b',
        'button_bg': '#3b82f6',
        'button_fg': '#ffffff',
        'button_hover': '#2563eb',
        'frame_bg': '#1e293b',
        'entry_bg': '#334155',
        'entry_fg': '#f1f5f9',
        'entry_border': '#475569',
        'accent': '#3b82f6',
        'accent_light': '#1e3a8a',
        'text_primary': '#f1f5f9',
        'text_secondary': '#cbd5e1',
        'border': '#334155',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#f87171',
        'info': '#0ea5e9',
        'card_bg': '#1e293b',
        'card_border': '#334155',
        'sidebar_button_hover': '#1e3a8a',
        'sidebar_text': '#f1f5f9'
    }
    
    @staticmethod
    def get_theme(dark_mode=True):
        """Get current theme"""
        return ThemeManager.DARK_THEME if dark_mode else ThemeManager.LIGHT_THEME
