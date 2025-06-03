"""
Settings Service for Finance Tracker
Handles user preferences and configuration persistence
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

from config.settings import DEFAULT_CURRENCY, SUPPORTED_CURRENCIES
from services.currency_service import Currency, get_currency_service


class SettingsService:
    """Service for managing user settings and preferences"""
    
    def __init__(self, settings_file: str = 'user_settings.json'):
        self.settings_file = Path(settings_file)
        self.settings: Dict[str, Any] = {}
        self.load_settings()
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                # Initialize with default settings
                self.settings = self._get_default_settings()
                self.save_settings()
            
            # Apply settings to services
            self._apply_settings()
            
        except Exception as e:
            print(f"Warning: Could not load settings file: {e}")
            self.settings = self._get_default_settings()
            self._apply_settings()
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default settings"""
        return {
            'currency': DEFAULT_CURRENCY,
            'decimal_places': 2,
            'show_currency_symbol': True,
            'date_format': '%Y-%m-%d %H:%M:%S',
            'max_recent_transactions': 10,
            'auto_update_charts': True,
            'color_coding': True,
            'first_run': True
        }
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save settings: {e}")
    
    def _apply_settings(self):
        """Apply current settings to services"""
        # Set currency in currency service
        currency_code = self.settings.get('currency', DEFAULT_CURRENCY)
        try:
            currency_service = get_currency_service()
            currency_service.set_currency(currency_code)
        except ValueError:
            print(f"Warning: Invalid currency '{currency_code}', using default")
            self.settings['currency'] = DEFAULT_CURRENCY
            currency_service.set_currency(DEFAULT_CURRENCY)
    
    def get_currency(self) -> str:
        """Get current currency code"""
        return self.settings.get('currency', DEFAULT_CURRENCY)
    
    def set_currency(self, currency_code: str):
        """Set currency preference"""
        if currency_code.upper() not in SUPPORTED_CURRENCIES:
            raise ValueError(f"Unsupported currency: {currency_code}")
        
        self.settings['currency'] = currency_code.upper()
        self.save_settings()
        
        # Apply to currency service
        currency_service = get_currency_service()
        currency_service.set_currency(currency_code)
    
    def get_decimal_places(self) -> int:
        """Get number of decimal places for currency display"""
        return self.settings.get('decimal_places', 2)
    
    def set_decimal_places(self, decimal_places: int):
        """Set number of decimal places"""
        if not 0 <= decimal_places <= 4:
            raise ValueError("Decimal places must be between 0 and 4")
        
        self.settings['decimal_places'] = decimal_places
        self.save_settings()
    
    def get_show_currency_symbol(self) -> bool:
        """Get whether to show currency symbol"""
        return self.settings.get('show_currency_symbol', True)
    
    def set_show_currency_symbol(self, show_symbol: bool):
        """Set whether to show currency symbol"""
        self.settings['show_currency_symbol'] = show_symbol
        self.save_settings()
    
    def get_max_recent_transactions(self) -> int:
        """Get maximum number of recent transactions to display"""
        return self.settings.get('max_recent_transactions', 10)
    
    def set_max_recent_transactions(self, max_transactions: int):
        """Set maximum number of recent transactions"""
        if max_transactions < 1:
            raise ValueError("Max transactions must be at least 1")
        
        self.settings['max_recent_transactions'] = max_transactions
        self.save_settings()
    
    def get_auto_update_charts(self) -> bool:
        """Get whether to auto-update charts"""
        return self.settings.get('auto_update_charts', True)
    
    def set_auto_update_charts(self, auto_update: bool):
        """Set auto-update charts preference"""
        self.settings['auto_update_charts'] = auto_update
        self.save_settings()
    
    def is_first_run(self) -> bool:
        """Check if this is the first time running the app"""
        return self.settings.get('first_run', True)
    
    def set_first_run_complete(self):
        """Mark first run as complete"""
        self.settings['first_run'] = False
        self.save_settings()
    
    def get_available_currencies(self) -> Dict[str, Dict[str, str]]:
        """Get available currencies"""
        return SUPPORTED_CURRENCIES.copy()
    
    def get_current_currency_info(self) -> Dict[str, str]:
        """Get current currency information"""
        currency_code = self.get_currency()
        return SUPPORTED_CURRENCIES.get(currency_code, SUPPORTED_CURRENCIES[DEFAULT_CURRENCY])
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update multiple settings at once"""
        for key, value in new_settings.items():
            if key in self.settings:
                self.settings[key] = value
        
        self.save_settings()
        self._apply_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self._get_default_settings()
        self.save_settings()
        self._apply_settings()
    
    def export_settings(self, file_path: str):
        """Export settings to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, file_path: str) -> bool:
        """Import settings from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # Validate imported settings
            valid_settings = {}
            for key, value in imported_settings.items():
                if key in self._get_default_settings():
                    valid_settings[key] = value
            
            if valid_settings:
                self.settings.update(valid_settings)
                self.save_settings()
                self._apply_settings()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False


# Global settings service instance
_settings_service: Optional[SettingsService] = None


def get_settings_service() -> SettingsService:
    """Get the global settings service instance"""
    global _settings_service
    if _settings_service is None:
        _settings_service = SettingsService()
    return _settings_service


def initialize_settings():
    """Initialize the settings service"""
    return get_settings_service() 