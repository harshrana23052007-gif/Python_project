"""
Voice Command Module - Speech recognition for expense entry
"""

import re
from datetime import datetime


class VoiceCommandParser:
    """Parses voice commands for expense entry"""
    
    def __init__(self):
        self.currency_symbol = "₹"
        self.category_keywords = {
            'food': ['food', 'eat', 'lunch', 'dinner', 'breakfast', 'restaurant', 'coffee', 'pizza', 'burger'],
            'travel': ['travel', 'uber', 'taxi', 'bus', 'train', 'flight', 'gas', 'parking'],
            'shopping': ['shopping', 'buy', 'purchase', 'shop', 'clothes', 'dress', 'shoes', 'mall'],
            'bills': ['bill', 'electric', 'water', 'internet', 'phone', 'rent', 'mortgage'],
            'entertainment': ['movie', 'cinema', 'game', 'entertainment', 'sport', 'concert', 'theater'],
            'health': ['health', 'doctor', 'medicine', 'pharmacy', 'hospital', 'gym', 'fitness'],
            'others': ['other', 'misc', 'miscellaneous']
        }
    
    def parse_command(self, text):
        """
        Parse voice command text into expense details
        Expected formats:
        - "Add 500 food expense"
        - "500 for lunch"
        - "Spent 25 on coffee"
        - "Add expense 100 shopping"
        """
        text = text.lower().strip()
        
        result = {
            'amount': None,
            'category': None,
            'description': None,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'success': False,
            'message': ''
        }
        
        # Extract amount
        amount_match = re.search(r'(\d+(?:\.\d{1,2})?)', text)
        if amount_match:
            try:
                result['amount'] = float(amount_match.group(1))
            except ValueError:
                result['message'] = 'Could not parse amount'
                return result
        else:
            result['message'] = 'No amount found in command'
            return result
        
        # Extract category
        category = self._extract_category(text)
        if category:
            result['category'] = category
        
        # Extract description from remaining text
        description = self._extract_description(text, amount_match)
        if description:
            result['description'] = description
        
        result['success'] = True
        result['message'] = f"Parsed: ₹{result['amount']:.2f} for {result['category']}"
        
        return result
    
    def _extract_category(self, text):
        """Extract category from text"""
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return category.capitalize()
        return None
    
    def _extract_description(self, text, amount_match):
        """Extract description from text"""
        # Remove amount and common words
        cleaned = text.replace(str(amount_match.group(1)), '')
        cleaned = re.sub(r'\b(add|expense|for|to|at|on|of|a|the)\b', '', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned if cleaned else None
    
    def is_valid_command(self, text):
        """Check if text contains valid expense command"""
        # Must have an amount
        if not re.search(r'\d+(?:\.\d{1,2})?', text):
            return False
        
        # Should have some expense-related keywords
        expense_keywords = ['expense', 'cost', 'spent', 'pay', 'bought', 'add']
        text_lower = text.lower()
        
        # Check if amount is mentioned
        if re.search(r'\d+(?:\.\d{1,2})?', text_lower):
            return True
        
        return False


class VoiceRecognizer:
    """Handles speech recognition"""
    
    def __init__(self):
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            try:
                self.microphone = sr.Microphone()
                self.available = True
            except Exception as mic_error:
                self.available = False
                self.error_message = f"Microphone not available: {str(mic_error)}"
        except ImportError:
            self.available = False
            self.error_message = "speech_recognition library not installed"
    
    def is_available(self):
        """Check if voice recognition is available"""
        return self.available
    
    def get_error_message(self):
        """Get error message if not available"""
        return getattr(self, 'error_message', 'Unknown error')
    
    def listen(self, timeout=10):
        """
        Listen for voice input
        Returns: (success: bool, text: str, error: str)
        """
        if not self.available:
            return False, "", "Voice recognition not available"
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio)
                return True, text, ""
            except self.sr.UnknownValueError:
                return False, "", "Could not understand audio"
            except self.sr.RequestError as e:
                return False, "", f"API error: {str(e)}"
        
        except self.sr.UnknownValueError:
            return False, "", "Could not understand audio"
        except Exception as e:
            return False, "", str(e)
