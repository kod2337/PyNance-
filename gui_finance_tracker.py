#!/usr/bin/env python3
"""
Modern GUI Finance Tracker
Clean, minimal design with full functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import threading
from typing import Optional

from finance_tracker_modular import FinanceTracker


class FinanceTrackerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_services()
        self.create_widgets()
        self.current_balance = 0.0
        self.refresh_data()
    
    def setup_window(self):
        """Configure main window"""
        self.root.title("💰 Finance Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Center window
        self.root.eval('tk::PlaceWindow . center')
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Action.TButton', font=('Arial', 10, 'bold'))
    
    def setup_services(self):
        """Initialize services"""
        try:
            self.tracker = FinanceTracker()
            
            # Check connection
            if not self.tracker.is_connected():
                raise Exception("Failed to connect to Google Sheets")
                
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to initialize services: {str(e)}")
            self.root.destroy()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="💰 Personal Finance Tracker", style='Title.TLabel')
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
        ttk.Label(controls_frame, text="Amount:", style='Header.TLabel').grid(row=0, column=0, sticky="w", pady=5)
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
    
    def add_transaction(self, is_income: bool):
        """Add a transaction"""
        try:
            amount_str = self.amount_var.get().strip()
            category = self.category_var.get().strip()
            description = self.description_var.get().strip()
            
            if not amount_str or not category:
                messagebox.showwarning("Input Error", "Amount and Category are required!")
                return
            
            amount = float(amount_str)
            transaction_type = "income" if is_income else "expense"
            description = description or "No description"
            
            self.status_var.set("Adding transaction...")
            self.root.update()
            
            # Add transaction using the main tracker
            threading.Thread(target=self._add_transaction_background, 
                           args=(description, category, amount, transaction_type), daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid amount!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
    
    def _add_transaction_background(self, description: str, category: str, amount: float, transaction_type: str):
        """Add transaction in background thread"""
        try:
            success = self.tracker.add_transaction(description, category, amount, transaction_type)
            if success:
                self.root.after(0, lambda: [
                    self.clear_inputs(),
                    self.refresh_data(),
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
    
    def clear_inputs(self):
        """Clear input fields"""
        self.amount_var.set("")
        self.category_var.set("")
        self.description_var.set("")
    
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
            records = self.tracker.sheets_service.get_all_transactions()
            self.root.after(0, lambda: self._update_display(records))
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to refresh data: {str(e)}"),
                self.status_var.set("Error refreshing data")
            ])
    
    def _update_display(self, records):
        """Update display with new data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update balance
        self.current_balance = float(records[-1]['Balance']) if records else 0.0
        balance_color = 'green' if self.current_balance >= 0 else 'red'
        self.balance_label.configure(text=f"${self.current_balance:,.2f}", foreground=balance_color)
        
        # Add recent transactions (last 20)
        for record in records[-20:]:
            amount = float(record['Amount'])
            amount_str = f"${amount:,.2f}" if amount >= 0 else f"-${abs(amount):,.2f}"
            
            self.tree.insert('', 0, values=(
                record['Date'][:10],
                amount_str,
                record['Category'],
                record['Description'][:30] + "..." if len(record['Description']) > 30 else record['Description']
            ))
        
        self.status_var.set(f"Data refreshed - {len(records)} total transactions")
    
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