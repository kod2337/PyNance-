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
from pathlib import Path

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
        # Use the correct path for settings file
        self.settings_service = get_settings_service()
        self.settings_service.settings_file = Path('config/user_settings.json')
        self.settings_service.load_settings()  # Reload with correct path
        
        self.current_balance = 0.0
        
        # Cache for reducing API calls
        self.cached_records = []
        self.cache_timestamp = 0
        self.cache_duration = 30  # Cache for 30 seconds
        
        # Load saved currency setting
        try:
            saved_currency = self.settings_service.get_currency()
            self.currency_service.set_currency(saved_currency)
        except Exception as e:
            print(f"Warning: Could not load saved currency: {e}")
        
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
        self.title_label = ttk.Label(main_frame, text=title_text, style='Title.TLabel')
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Balance display
        self.balance_frame = ttk.LabelFrame(main_frame, text="Current Balance", padding="10")
        self.balance_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        # Use dynamic currency formatting instead of hardcoded "$0.00"
        initial_balance = self.currency_service.format_balance(0.0)
        self.balance_label = ttk.Label(self.balance_frame, text=initial_balance, 
                                      font=('Arial', 24, 'bold'), foreground='green')
        self.balance_label.pack()
        
        # Left panel - Controls
        controls_frame = ttk.LabelFrame(main_frame, text="Actions", padding="10")
        controls_frame.grid(row=2, column=0, sticky="new", padx=(0, 10))
        
        # Transaction input
        symbol = self.currency_service.get_currency_symbol()
        self.amount_label = ttk.Label(controls_frame, text=f"Amount ({symbol}):", style='Header.TLabel')
        self.amount_label.grid(row=0, column=0, sticky="w", pady=5)
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
        ttk.Button(button_frame, text="💱 Currency Settings", command=self.open_currency_settings, 
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
    
    def open_currency_settings(self):
        """Open currency settings dialog with validation"""
        try:
            # Get current currency info
            current_info = self.currency_service.get_currency_info()
            available_currencies = self.currency_service.get_available_currencies()
            
            # Create list of currency options
            currency_options = []
            current_index = 0
            for i, (code, info) in enumerate(available_currencies.items()):
                currency_text = f"{info['name']} ({info['symbol']})"
                currency_options.append(currency_text)
                if code == current_info['code']:
                    current_index = i
            
            # Show selection dialog
            from tkinter import simpledialog
            
            title = "💱 Currency Settings"
            prompt = f"Current Currency: {current_info['name']} ({current_info['symbol']})\n\nSelect new currency:"
            
            # Create custom dialog for currency selection
            selection_window = tk.Toplevel(self.root)
            selection_window.title(title)
            selection_window.geometry("350x400")
            selection_window.transient(self.root)
            selection_window.grab_set()
            
            # Center the window
            selection_window.update_idletasks()
            x = (selection_window.winfo_screenwidth() // 2) - (350 // 2)
            y = (selection_window.winfo_screenheight() // 2) - (400 // 2)
            selection_window.geometry(f"350x400+{x}+{y}")
            
            # Main frame
            main_frame = ttk.Frame(selection_window, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="💱 Currency Settings", 
                                   font=('Arial', 14, 'bold'))
            title_label.pack(pady=(0, 15))
            
            # Current currency display
            current_text = f"Current: {current_info['name']} ({current_info['symbol']})"
            current_label = ttk.Label(main_frame, text=current_text, font=('Arial', 10))
            current_label.pack(pady=(0, 20))
            
            # Currency selection
            selection_frame = ttk.LabelFrame(main_frame, text="Select New Currency", padding="10")
            selection_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Selection variable
            selected_currency = tk.StringVar()
            
            # Create radio buttons
            for code, info in available_currencies.items():
                currency_text = f"{info['name']} ({info['symbol']})"
                radio = ttk.Radiobutton(selection_frame, text=currency_text, 
                                       variable=selected_currency, value=code)
                radio.pack(anchor="w", pady=5)
                
                # Set current currency as selected
                if code == current_info['code']:
                    selected_currency.set(code)
            
            # Preview section
            preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
            preview_frame.pack(fill="x", pady=(0, 20))
            
            preview_text = tk.Text(preview_frame, height=3, width=30, wrap=tk.WORD)
            preview_text.pack()
            
            def update_preview():
                """Update preview when selection changes"""
                try:
                    selected = selected_currency.get()
                    if selected:
                        # Create temporary currency service for preview
                        from services.currency_service import CurrencyService
                        temp_service = CurrencyService()
                        temp_service.set_currency(selected)
                        
                        # Generate preview
                        balance = temp_service.format_balance(1234.56)
                        income = temp_service.format_transaction_amount(500.00)
                        expense = temp_service.format_transaction_amount(-75.25)
                        
                        preview_content = f"Balance: {balance}\nIncome: {income}\nExpense: {expense}"
                        
                        preview_text.delete(1.0, tk.END)
                        preview_text.insert(1.0, preview_content)
                except Exception as e:
                    preview_text.delete(1.0, tk.END)
                    preview_text.insert(1.0, f"Preview error: {str(e)}")
            
            # Bind preview update
            selected_currency.trace("w", lambda *args: update_preview())
            update_preview()  # Initial preview
            
            # Result variable
            result = {"changed": False, "new_currency": None}
            
            def apply_changes():
                """Apply currency changes with validation"""
                try:
                    new_currency = selected_currency.get()
                    
                    if not new_currency:
                        messagebox.showwarning("Selection Required", "Please select a currency.")
                        return
                    
                    if new_currency == current_info['code']:
                        messagebox.showinfo("No Change", "Currency is already set to this value.")
                        selection_window.destroy()
                        return
                    
                    # Get new currency info for confirmation
                    new_info = available_currencies[new_currency]
                    
                    # Confirmation dialog
                    confirm_msg = (f"Change currency from {current_info['name']} ({current_info['symbol']}) "
                                  f"to {new_info['name']} ({new_info['symbol']})?\n\n"
                                  f"This will update all displays and save the preference.")
                    
                    if messagebox.askyesno("Confirm Currency Change", confirm_msg):
                        # Apply the change
                        self.currency_service.set_currency(new_currency)
                        self.settings_service.set_currency(new_currency)
                        
                        # Update all GUI displays
                        self._update_currency_displays()
                        
                        # Refresh data to show in new currency
                        self.refresh_data()
                        
                        # Success message
                        success_msg = f"Currency changed to {new_info['name']} ({new_info['symbol']})"
                        self.status_var.set(success_msg)
                        messagebox.showinfo("Success", success_msg)
                        
                        result["changed"] = True
                        result["new_currency"] = new_currency
                        
                        selection_window.destroy()
                    
                except Exception as e:
                    error_msg = f"Failed to change currency: {str(e)}"
                    self.status_var.set(error_msg)
                    messagebox.showerror("Error", error_msg)
            
            def cancel_changes():
                """Cancel without changes"""
                selection_window.destroy()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x")
            
            ttk.Button(button_frame, text="Apply", command=apply_changes).pack(side="right", padx=(5, 0))
            ttk.Button(button_frame, text="Cancel", command=cancel_changes).pack(side="right")
            
        except Exception as e:
            error_msg = f"Failed to open currency settings: {str(e)}"
            self.status_var.set(error_msg)
            messagebox.showerror("Error", error_msg)
    
    def _update_currency_displays(self):
        """Update all currency-related displays in the GUI"""
        try:
            # Update title with new currency info
            currency_info = self.currency_service.get_currency_info()
            title_text = f"💰 Personal Finance Tracker ({currency_info['name']})"
            self.title_label.config(text=title_text)
            
            # Update amount entry label
            symbol = self.currency_service.get_currency_symbol()
            self.amount_label.config(text=f"Amount ({symbol}):")
            
            # Update balance display
            self._update_balance_display()
            
            # Note: Transaction list will be updated when refresh_data is called
            
        except Exception as e:
            print(f"Error updating currency displays: {str(e)}")
            self.status_var.set(f"Error updating displays: {str(e)}")
    
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