"""
Currency Service for Finance Tracker
Handles currency formatting, symbols, and localization
"""

from enum import Enum
from typing import Union, Dict, Any
from decimal import Decimal


class Currency(Enum):
    """Supported currencies"""
    USD = {"code": "USD", "symbol": "$", "name": "US Dollar", "position": "prefix"}
    PHP = {"code": "PHP", "symbol": "₱", "name": "Philippine Peso", "position": "prefix"}
    
    @property
    def code(self) -> str:
        return self.value["code"]
    
    @property
    def symbol(self) -> str:
        return self.value["symbol"]
    
    @property
    def name(self) -> str:
        return self.value["name"]
    
    @property
    def position(self) -> str:
        return self.value["position"]


class CurrencyService:
    """Service for handling currency operations"""
    
    def __init__(self, default_currency: Currency = Currency.USD):
        self.current_currency = default_currency
        self._exchange_rates = self._get_base_exchange_rates()
    
    def _get_base_exchange_rates(self) -> Dict[str, float]:
        """Base exchange rates (USD as base)"""
        return {
            "USD": 1.0,
            "PHP": 56.0  # Approximate rate - in real app, you'd fetch from API
        }
    
    def set_currency(self, currency: Union[Currency, str]):
        """Set the current currency"""
        if isinstance(currency, str):
            try:
                currency = Currency[currency.upper()]
            except KeyError:
                raise ValueError(f"Unsupported currency: {currency}")
        
        self.current_currency = currency
    
    def get_currency_symbol(self) -> str:
        """Get the current currency symbol"""
        return self.current_currency.symbol
    
    def get_currency_code(self) -> str:
        """Get the current currency code"""
        return self.current_currency.code
    
    def get_currency_name(self) -> str:
        """Get the current currency name"""
        return self.current_currency.name
    
    def format_amount(self, amount: Union[float, Decimal, int], show_symbol: bool = True, 
                     show_sign: bool = False, decimal_places: int = 2) -> str:
        """
        Format amount with current currency
        
        Args:
            amount: The amount to format
            show_symbol: Whether to show currency symbol
            show_sign: Whether to show + for positive amounts
            decimal_places: Number of decimal places
        
        Returns:
            Formatted currency string
        """
        if amount is None:
            amount = 0
        
        # Convert to float for formatting
        amount_float = float(amount)
        
        # Format the number
        if decimal_places == 0:
            formatted_number = f"{abs(amount_float):,.0f}"
        else:
            formatted_number = f"{abs(amount_float):,.{decimal_places}f}"
        
        # Add sign
        if amount_float < 0:
            sign = "-"
        elif amount_float > 0 and show_sign:
            sign = "+"
        else:
            sign = ""
        
        # Add currency symbol
        if show_symbol:
            symbol = self.current_currency.symbol
            if self.current_currency.position == "prefix":
                return f"{sign}{symbol}{formatted_number}"
            else:
                return f"{sign}{formatted_number}{symbol}"
        else:
            return f"{sign}{formatted_number}"
    
    def format_balance(self, balance: Union[float, Decimal, int]) -> str:
        """Format balance with currency symbol"""
        return self.format_amount(balance, show_symbol=True, show_sign=False)
    
    def format_transaction_amount(self, amount: Union[float, Decimal, int]) -> str:
        """Format transaction amount with sign and symbol"""
        return self.format_amount(amount, show_symbol=True, show_sign=True)
    
    def parse_amount(self, amount_str: str) -> float:
        """
        Parse amount string to float, removing currency symbols
        
        Args:
            amount_str: String representation of amount
            
        Returns:
            Float value of the amount
        """
        if not amount_str:
            return 0.0
        
        # Remove currency symbols and common separators
        cleaned = amount_str.strip()
        for currency in Currency:
            cleaned = cleaned.replace(currency.symbol, "")
        
        # Remove common formatting
        cleaned = cleaned.replace(",", "").replace(" ", "").strip()
        
        # Handle negative amounts
        negative = cleaned.startswith("-") or cleaned.startswith("(")
        cleaned = cleaned.lstrip("-+(").rstrip(")")
        
        try:
            amount = float(cleaned)
            return -amount if negative else amount
        except ValueError:
            raise ValueError(f"Invalid amount format: {amount_str}")
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another
        Note: In a real application, you'd fetch live exchange rates
        """
        if from_currency == to_currency:
            return amount
        
        from_rate = self._exchange_rates.get(from_currency.upper(), 1.0)
        to_rate = self._exchange_rates.get(to_currency.upper(), 1.0)
        
        # Convert to USD first, then to target currency
        usd_amount = amount / from_rate
        return usd_amount * to_rate
    
    def get_available_currencies(self) -> Dict[str, Dict[str, str]]:
        """Get list of available currencies"""
        return {
            currency.code: {
                "code": currency.code,
                "symbol": currency.symbol,
                "name": currency.name
            }
            for currency in Currency
        }
    
    def get_currency_info(self) -> Dict[str, Any]:
        """Get current currency information"""
        return {
            "code": self.current_currency.code,
            "symbol": self.current_currency.symbol,
            "name": self.current_currency.name,
            "position": self.current_currency.position
        }
    
    def format_amount_with_color(self, amount: Union[float, Decimal, int], 
                                positive_color: str = "", negative_color: str = "", 
                                reset_color: str = "") -> str:
        """
        Format amount with color codes for terminal display
        
        Args:
            amount: The amount to format
            positive_color: ANSI color code for positive amounts
            negative_color: ANSI color code for negative amounts  
            reset_color: ANSI reset color code
        
        Returns:
            Formatted amount with color codes
        """
        formatted = self.format_transaction_amount(amount)
        
        if float(amount) < 0 and negative_color:
            return f"{negative_color}{formatted}{reset_color}"
        elif float(amount) > 0 and positive_color:
            return f"{positive_color}{formatted}{reset_color}"
        else:
            return formatted


# Global currency service instance
currency_service = CurrencyService()


def get_currency_service() -> CurrencyService:
    """Get the global currency service instance"""
    return currency_service


def format_currency(amount: Union[float, Decimal, int], **kwargs) -> str:
    """Convenience function to format currency using global service"""
    return currency_service.format_amount(amount, **kwargs)


def set_default_currency(currency: Union[Currency, str]):
    """Set the default currency for the application"""
    currency_service.set_currency(currency) 