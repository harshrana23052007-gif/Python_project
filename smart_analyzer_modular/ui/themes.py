"""
Theme management for Smart Expense Analyzer
Handles light and dark mode theming with CustomTkinter
"""

class ThemeManager:
    """Manages light and colorful themes for CustomTkinter"""
    
    # Light theme with pastel colors
    LIGHT_THEME = {
        'bg': '#f8f9fa',
        'fg': '#2c3e50',
        'sidebar_bg': '#e8f4f8',
        'button_bg': '#3498db',
        'button_fg': '#ffffff',
        'button_hover': '#2980b9',
        'frame_bg': '#ffffff',
        'entry_bg': '#ecf0f1',
        'entry_fg': '#2c3e50',
        'entry_border': '#bdc3c7',
        'accent': '#3498db',
        'accent_light': '#d6eaf8',
        'text_primary': '#2c3e50',
        'text_secondary': '#7f8c8d',
        'border': '#d0d0d0',
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#2980b9',
        # Card colors for visual variety
        'card_bg': '#ffffff',
        'card_border': '#bdc3c7',
        # Sidebar button colors
        'sidebar_button_hover': '#d6eaf8',
        'sidebar_text': '#2c3e50'
    }
    
    # Modern dark theme (alternative)
    DARK_THEME = {
        'bg': '#1a1a2e',
        'fg': '#eaeaea',
        'sidebar_bg': '#16213e',
        'button_bg': '#0f3460',
        'button_fg': '#ffffff',
        'button_hover': '#1a5f7a',
        'frame_bg': '#0f3460',
        'entry_bg': '#2d3561',
        'entry_fg': '#eaeaea',
        'entry_border': '#3d4563',
        'accent': '#00d4ff',
        'accent_light': '#1a5f7a',
        'text_primary': '#eaeaea',
        'text_secondary': '#a0a0a0',
        'border': '#3d3d3d',
        'success': '#4ec9b0',
        'warning': '#ce9178',
        'danger': '#f48771',
        'info': '#00d4ff',
        'card_bg': '#16213e',
        'card_border': '#3d4563',
        'sidebar_button_hover': '#1a5f7a',
        'sidebar_text': '#eaeaea'
    }
    
    @staticmethod
    def get_theme(dark_mode=True):
        """Get current theme"""
        return ThemeManager.DARK_THEME if dark_mode else ThemeManager.LIGHT_THEME
