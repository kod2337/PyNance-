#!/usr/bin/env python3
"""
Modern GUI Finance Tracker
Clean, minimal design with full functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import threading
import time
from typing import Optional, Dict, Any
from colorama import Fore

from core.finance_tracker_modular import FinanceTracker
from services.currency_service import get_currency_service
from services.settings_service import get_settings_service
from config.settings import (
    MAX_TRANSACTION_AMOUNT, 
    MAX_DESCRIPTION_LENGTH, 
    MAX_CATEGORY_LENGTH,
    validate_credentials
)


class FinanceTrackerGUI:
    def __init__(self):
        self.tracker = FinanceTracker()
        self.currency_service = get_currency_service()
        self.settings_service = get_settings_service()
        self.current_balance = 0.0
        
        # Cache for reducing API calls
        self.cached_records = []
        self.cache_timestamp = 0
        self.cache_duration = 30  # Cache for 30 seconds
        
        # Validate credentials and show warnings
        credential_warnings = validate_credentials()
        if credential_warnings:
            for warning in credential_warnings:
                print(f"⚠️  Security Warning: {warning}")
        
        self.setup_window()
        self.setup_services()
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
    
    def setup_window(self):
        """Setup main window"""
        self.root = tk.Tk()
        self.root.title("💰 Finance Tracker")
        self.root.geometry("1000x700")
        
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        style.configure('Action.TButton', padding=10)
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
    
    def setup_services(self):
        """Setup and initialize services"""
        try:
            if not self.tracker.is_connected():
                messagebox.showerror("Connection Error", 
                                   "Could not connect to Google Sheets. Please check your setup.")
                self.root.destroy()
                return
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to initialize: {str(e)}")
            self.root.destroy()
            return
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title with currency info
        currency_info = self.currency_service.get_currency_info()
        title_text = f"💰 Personal Finance Tracker ({currency_info['name']})"
        title_label = ttk.Label(main_frame, text=title_text, style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Balance display
        self.balance_frame = ttk.LabelFrame(main_frame, text="Current Balance", padding="10")
        self.balance_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        self.balance_label = ttk.Label(self.balance_frame, text="$0.00", 
                                      font=('Arial', 24, 'bold'), foreground='green')
        self.balance_label.pack()
        
        # Left panel - Controls
        controls_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        controls_frame.grid(row=2, column=0, sticky="new", padx=(0, 10))
        
        # Transaction input
        symbol = self.currency_service.get_currency_symbol()
        ttk.Label(controls_frame, text=f"Amount ({symbol}):", style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=5)
        self.amount_var = tk.StringVar()
        amount_entry = ttk.Entry(controls_frame, textvariable=self.amount_var, width=15)
        amount_entry.grid(row=0, column=1, sticky="w", pady=5)
        
        ttk.Label(controls_frame, text="Category:", style='Header.TLabel').grid(row=1, column=0, sticky="w", pady=5)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(controls_frame, textvariable=self.category_var, width=12,
                                    values=['Food', 'Transportation', 'Entertainment', 'Bills', 
                                           'Shopping', 'Healthcare', 'Income', 'Investment', 'Other'])
        category_combo.grid(row=1, column=1, sticky="w", pady=5)
        
        ttk.Label(controls_frame, text="Description:", style='Header.TLabel').grid(row=2, column=0, sticky="w", pady=5)
        self.description_var = tk.StringVar()
        description_entry = ttk.Entry(controls_frame, textvariable=self.description_var, width=15)
        description_entry.grid(row=2, column=1, sticky="w", pady=5)
        
        # Buttons
        button_frame = ttk.Frame(controls_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="💸 Add Expense", command=self.add_expense, 
                  style='Action.TButton').pack(pady=5, fill='x')
        ttk.Button(button_frame, text="💰 Add Income", command=self.add_income, 
                  style='Action.TButton').pack(pady=5, fill='x')
        ttk.Button(button_frame, text="💳 Refresh Balance", command=self.refresh_balance, 
                  style='Action.TButton').pack(pady=5, fill='x')
        ttk.Button(button_frame, text="📊 Update Charts", command=self.update_charts, 
                  style='Action.TButton').pack(pady=5, fill='x')
        ttk.Button(button_frame, text="🔄 Refresh Data", command=self.refresh_data, 
                  style='Action.TButton').pack(pady=5, fill='x')
        
        # Right panel - Recent Transactions
        self.transactions_frame = ttk.LabelFrame(main_frame, text="Recent Transactions", padding="10")
        self.transactions_frame.grid(row=2, column=1, sticky="nsew")
        main_frame.rowconfigure(2, weight=1)
        
        # Treeview for transactions
        columns = ('Date', 'Amount', 'Category', 'Description')
        self.tree = ttk.Treeview(self.transactions_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.transactions_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.transactions_frame.columnconfigure(0, weight=1)
        self.transactions_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
    
    def add_expense(self):
        """Add expense transaction"""
        self.add_transaction(is_income=False)
    
    def add_income(self):
        """Add income transaction"""
        self.add_transaction(is_income=True)
    
    def _validate_and_sanitize_inputs(self, amount_str: str, category: str, description: str) -> tuple:
        """Validate and sanitize user inputs"""
        errors = []
        
        # Validate and sanitize amount
        if not amount_str or not amount_str.strip():
            errors.append("Amount is required")
        else:
            try:
                amount = self.currency_service.parse_amount(amount_str.strip())
                if amount <= 0:
                    errors.append("Amount must be positive")
                elif amount > MAX_TRANSACTION_AMOUNT:
                    errors.append(f"Amount is too large (max: {MAX_TRANSACTION_AMOUNT:,.0f})")
            except ValueError:
                errors.append("Invalid amount format")
        
        # Validate and sanitize category
        if not category or not category.strip():
            errors.append("Category is required")
        else:
            category = category.strip()[:MAX_CATEGORY_LENGTH]  # Limit length
            # Remove potentially harmful characters
            category = ''.join(c for c in category if c.isalnum() or c in ' -_')
            if not category:
                errors.append("Category contains invalid characters")
        
        # Validate and sanitize description
        description = description.strip()[:MAX_DESCRIPTION_LENGTH] if description else "No description"  # Limit length
        # Remove potentially harmful characters but allow more variety
        description = ''.join(c for c in description if c.isprintable() and c not in '<>&"\'')
        if not description:
            description = "No description"
        
        return errors, amount_str.strip() if not errors else None, category, description

    def add_transaction(self, is_income: bool):
        """Add a transaction"""
        try:
            amount_str = self.amount_var.get()
            category = self.category_var.get()
            description = self.description_var.get()
            
            # Validate and sanitize inputs
            errors, sanitized_amount_str, sanitized_category, sanitized_description = \
                self._validate_and_sanitize_inputs(amount_str, category, description)
            
            if errors:
                messagebox.showwarning("Input Error", "\n".join(errors))
                return
            
            # Use currency service to parse amount
            amount = self.currency_service.parse_amount(sanitized_amount_str)
                
            transaction_type = "Income" if is_income else "Expense"
            
            self.status_var.set("Adding transaction...")
            self.root.update()
            
            # Add transaction using the main tracker
            threading.Thread(target=self._add_transaction_background, 
                           args=(sanitized_description, sanitized_category, amount, transaction_type), daemon=True).start()
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid amount format: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
    
    def _add_transaction_background(self, description: str, category: str, amount: float, transaction_type: str):
        """Add transaction in background thread"""
        try:
            success = self.tracker.add_transaction(description, category, amount, transaction_type)
            if success:
                # Invalidate cache since we added new data
                self._invalidate_cache()
                
                # Small delay to ensure Google Sheets has updated
                time.sleep(0.5)
                
                self.root.after(0, lambda: [
                    self.clear_inputs(),
                    self._update_balance_display(),  # Update balance immediately
                    self._refresh_data_sync(),  # Refresh data synchronously
                    self.status_var.set("Transaction added successfully!")
                ])
            else:
                self.root.after(0, lambda: [
                    messagebox.showerror("Error", "Failed to add transaction"),
                    self.status_var.set("Error adding transaction")
                ])
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to add transaction: {str(e)}"),
                self.status_var.set("Error adding transaction")
            ])
    
    def _refresh_data_sync(self):
        """Refresh data synchronously (for use after adding transactions)"""
        try:
            # Force refresh by invalidating cache
            self._invalidate_cache()
            records = self._get_records_with_cache()
            self._update_display(records)
        except Exception as e:
            self.status_var.set(f"Error refreshing data: {str(e)}")
    
    def _update_balance_display(self):
        """Update just the balance display"""
        try:
            # Get current balance from tracker
            self.current_balance = self.tracker.get_current_balance()
            
            # Determine color based on balance
            balance_color = 'green' if self.current_balance >= 0 else 'red'
            
            # Format balance using currency service
            formatted_balance = self.currency_service.format_balance(self.current_balance)
            
            # Update the label
            self.balance_label.configure(text=formatted_balance, foreground=balance_color)
            
        except Exception as e:
            error_msg = f"Error updating balance display: {str(e)}"
            
            # Show error in the balance display
            self.balance_label.configure(text="Error loading balance", foreground='red')
            
            # Also update status
            self.status_var.set("Error: Could not load balance")
    
    def clear_inputs(self):
        """Clear input fields"""
        self.amount_var.set("")
        self.category_var.set("")
        self.description_var.set("")
    
    def refresh_balance(self):
        """Manually refresh the balance display"""
        self.status_var.set("Refreshing balance...")
        try:
            # Force refresh balance display
            self._update_balance_display()
            self.status_var.set("Balance refreshed successfully!")
        except Exception as e:
            self.status_var.set(f"Error refreshing balance: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh balance: {str(e)}")
    
    def update_charts(self):
        """Update charts in background"""
        self.status_var.set("Updating charts...")
        threading.Thread(target=self._update_charts_background, daemon=True).start()
    
    def _update_charts_background(self):
        """Update charts in background thread"""
        try:
            success = self.tracker.create_charts()
            if success:
                self.root.after(0, lambda: self.status_var.set("Charts updated successfully!"))
            else:
                self.root.after(0, lambda: self.status_var.set("Error updating charts"))
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to update charts: {str(e)}"),
                self.status_var.set("Error updating charts")
            ])
    
    def refresh_data(self):
        """Refresh transaction data"""
        self.status_var.set("Refreshing data...")
        threading.Thread(target=self._refresh_data_background, daemon=True).start()
    
    def _refresh_data_background(self):
        """Refresh data in background thread"""
        try:
            # Force refresh by invalidating cache
            self._invalidate_cache()
            records = self._get_records_with_cache()
            self.root.after(0, lambda: self._update_display(records))
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to refresh data: {str(e)}"),
                self.status_var.set("Error refreshing data")
            ])
    
    def _update_display(self, records):
        """Update display with new data"""
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Update balance - use the tracker's method instead of parsing records directly
            self._update_balance_display()  # Use the dedicated method
            
            # Add recent transactions (last 20)
            recent_records = records[-20:] if len(records) > 20 else records
            recent_records.reverse()  # Show most recent first
            
            for record in recent_records:
                try:
                    # Safely parse amount
                    amount = float(record.get('Amount', 0))
                    amount_str = self.currency_service.format_transaction_amount(amount)
                    
                    # Get other fields safely
                    date_str = str(record.get('Date', ''))[:10]
                    category = str(record.get('Category', 'Unknown'))
                    description = str(record.get('Description', 'No description'))
                    
                    # Truncate long descriptions
                    if len(description) > 30:
                        description = description[:30] + "..."
                    
                    self.tree.insert('', 0, values=(
                        date_str,
                        amount_str,
                        category,
                        description
                    ))
                except (ValueError, KeyError) as e:
                    # Skip invalid records
                    continue
            
            self.status_var.set(f"Data refreshed - {len(records)} total transactions")
            
        except Exception as e:
            self.status_var.set(f"Error updating display: {str(e)}")
            messagebox.showerror("Display Error", f"Failed to update display: {str(e)}")
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        return (time.time() - self.cache_timestamp) < self.cache_duration
    
    def _get_records_with_cache(self) -> list:
        """Get records with caching to reduce API calls"""
        if self._is_cache_valid() and self.cached_records:
            return self.cached_records
        
        # Cache is expired or empty, fetch new data
        try:
            self.cached_records = self.tracker.sheets_service.get_all_records()
            self.cache_timestamp = time.time()
            return self.cached_records
        except Exception as e:
            # If fetch fails, return cached data if available
            if self.cached_records:
                print(f"{Fore.YELLOW}⚠️  Using cached data due to fetch error: {str(e)}")
                return self.cached_records
            raise e
    
    def _invalidate_cache(self):
        """Invalidate the cache to force refresh on next access"""
        self.cache_timestamp = 0
    
    def run(self):
        """Start the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = FinanceTrackerGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Finance Tracker closed.")
    except Exception as e:
        print(f"❌ Error starting application: {str(e)}") 