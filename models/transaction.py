"""
Transaction model for Finance Tracker
"""

from datetime import datetime
from typing import Dict, Any


class Transaction:
    """Represents a financial transaction"""
    
    def __init__(self, description: str, category: str, amount: float, transaction_type: str):
        self.description = description
        self.category = category
        self.amount = amount
        self.transaction_type = transaction_type.capitalize()
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.balance = 0.0  # Will be set when calculating balance
    
    def to_row(self) -> list:
        """Convert transaction to spreadsheet row format"""
        return [
            self.date,
            self.description,
            self.category,
            self.amount,
            self.transaction_type,
            self.balance
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary"""
        return {
            'date': self.date,
            'description': self.description,
            'category': self.category,
            'amount': self.amount,
            'type': self.transaction_type,
            'balance': self.balance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary"""
        transaction = cls(
            description=data['description'],
            category=data['category'],
            amount=float(data['amount']),
            transaction_type=data['type']
        )
        transaction.date = data['date']
        transaction.balance = float(data['balance'])
        return transaction
    
    def is_expense(self) -> bool:
        """Check if transaction is an expense"""
        return self.amount < 0
    
    def is_income(self) -> bool:
        """Check if transaction is income"""
        return self.amount > 0
    
    def get_absolute_amount(self) -> float:
        """Get absolute value of amount"""
        return abs(self.amount)
    
    def __str__(self) -> str:
        """String representation of transaction"""
        amount_str = f"${self.get_absolute_amount():.2f}"
        return f"{self.date}: {self.description} ({self.category}) - {amount_str} [{self.transaction_type}]"
    
    def __repr__(self) -> str:
        """Debug representation of transaction"""
        return f"Transaction(description='{self.description}', amount={self.amount}, type='{self.transaction_type}')" 