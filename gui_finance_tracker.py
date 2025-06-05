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
        
        # Basic Transaction Buttons
        basic_frame = ttk.LabelFrame(button_frame, text="💰 Basic Transactions", padding="5")
        basic_frame.pack(fill='x', pady=5)
        
        ttk.Button(basic_frame, text="💸 Add Expense", command=self.add_expense, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(basic_frame, text="💰 Add Income", command=self.add_income, 
                  style='Action.TButton').pack(pady=2, fill='x')
        
        # AI-Powered Transaction Buttons
        ai_frame = ttk.LabelFrame(button_frame, text="🤖 AI-Powered Features", padding="5")
        ai_frame.pack(fill='x', pady=5)
        
        ttk.Button(ai_frame, text="🤖 Smart Add (AI Categories)", command=self.add_ai_transaction, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(ai_frame, text="💬 Natural Language Entry", command=self.add_natural_language, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(ai_frame, text="🧠 Generate AI Insights", command=self.show_ai_insights, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(ai_frame, text="📊 AI Financial Report", command=self.generate_ai_report, 
                  style='Action.TButton').pack(pady=2, fill='x')
        
        # Utility Buttons
        utility_frame = ttk.LabelFrame(button_frame, text="⚙️ Utilities", padding="5")
        utility_frame.pack(fill='x', pady=5)
        
        ttk.Button(utility_frame, text="💳 Refresh Balance", command=self.refresh_balance, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(utility_frame, text="📊 Update Charts", command=self.update_charts, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(utility_frame, text="💱 Currency Settings", command=self.open_currency_settings, 
                  style='Action.TButton').pack(pady=2, fill='x')
        ttk.Button(utility_frame, text="🔄 Refresh Data", command=self.refresh_data, 
                  style='Action.TButton').pack(pady=2, fill='x')
        
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
    
    def add_ai_transaction(self):
        """Add transaction with AI-powered smart categorization"""
        try:
            if not self.tracker.is_ai_available():
                messagebox.showwarning("AI Not Available", 
                                     "AI features are not available. Please check your GEMINI_API_KEY.")
                return
            
            amount_str = self.amount_var.get()
            description = self.description_var.get()
            
            if not amount_str or not description:
                messagebox.showwarning("Input Required", "Please enter both amount and description for AI categorization.")
                return
            
            # Validate amount
            try:
                amount = self.currency_service.parse_amount(amount_str.strip())
                if amount <= 0:
                    messagebox.showerror("Invalid Amount", "Amount must be positive.")
                    return
            except ValueError:
                messagebox.showerror("Invalid Amount", "Invalid amount format.")
                return
            
            # Ask for transaction type
            transaction_type = self._ask_transaction_type()
            if not transaction_type:
                return
            
            self.status_var.set("🤖 AI is analyzing transaction...")
            self.root.update()
            
            # Run AI categorization in background
            threading.Thread(target=self._add_ai_transaction_background, 
                           args=(description.strip(), amount, transaction_type), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process AI transaction: {str(e)}")
    
    def _ask_transaction_type(self):
        """Ask user to choose between Income or Expense"""
        choice_window = tk.Toplevel(self.root)
        choice_window.title("Transaction Type")
        choice_window.geometry("300x150")
        choice_window.transient(self.root)
        choice_window.grab_set()
        
        # Center the window
        choice_window.update_idletasks()
        x = (choice_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (choice_window.winfo_screenheight() // 2) - (150 // 2)
        choice_window.geometry(f"300x150+{x}+{y}")
        
        result = {"type": None}
        
        # Main frame
        main_frame = ttk.Frame(choice_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Is this transaction an:", font=('Arial', 12)).pack(pady=10)
        
        def set_expense():
            result["type"] = "Expense"
            choice_window.destroy()
        
        def set_income():
            result["type"] = "Income"
            choice_window.destroy()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="💸 Expense", command=set_expense).pack(side="left", padx=5)
        ttk.Button(button_frame, text="💰 Income", command=set_income).pack(side="left", padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=choice_window.destroy).pack(side="left", padx=5)
        
        choice_window.wait_window()
        return result["type"]
    
    def _add_ai_transaction_background(self, description: str, amount: float, transaction_type: str):
        """Add AI transaction in background"""
        try:
            success = self.tracker.add_transaction_with_ai_category(description, amount, transaction_type)
            if success:
                self._invalidate_cache()
                time.sleep(0.5)
                
                self.root.after(0, lambda: [
                    self.clear_inputs(),
                    self._update_balance_display(),
                    self._refresh_data_sync(),
                    self.status_var.set("🤖 AI transaction added successfully!")
                ])
            else:
                self.root.after(0, lambda: [
                    messagebox.showerror("Error", "Failed to add AI transaction"),
                    self.status_var.set("❌ Error adding AI transaction")
                ])
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"AI transaction failed: {str(e)}"),
                self.status_var.set("❌ AI transaction error")
            ])
    
    def add_natural_language(self):
        """Add transaction using natural language processing"""
        try:
            if not self.tracker.is_ai_available():
                messagebox.showwarning("AI Not Available", 
                                     "AI features are not available. Please check your GEMINI_API_KEY.")
                return
            
            # Create natural language input dialog
            nl_window = tk.Toplevel(self.root)
            nl_window.title("💬 Natural Language Transaction")
            nl_window.geometry("500x300")
            nl_window.transient(self.root)
            nl_window.grab_set()
            
            # Center the window
            nl_window.update_idletasks()
            x = (nl_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (nl_window.winfo_screenheight() // 2) - (300 // 2)
            nl_window.geometry(f"500x300+{x}+{y}")
            
            main_frame = ttk.Frame(nl_window, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(main_frame, text="💬 Natural Language Transaction Entry", 
                     font=('Arial', 14, 'bold')).pack(pady=(0, 15))
            
            # Instructions
            instructions = (
                "Describe your transaction in plain English:\n\n"
                "Examples:\n"
                "• 'I spent $25 on groceries at Walmart yesterday'\n"
                "• 'Got paid $500 for freelance work today'\n"
                "• 'Bought coffee for $4.50 this morning'\n"
                "• 'Received $100 cash gift from mom'"
            )
            ttk.Label(main_frame, text=instructions, font=('Arial', 9)).pack(pady=(0, 15))
            
            # Text input
            ttk.Label(main_frame, text="Enter your transaction:", font=('Arial', 10, 'bold')).pack(anchor="w")
            text_entry = tk.Text(main_frame, height=3, width=50, wrap=tk.WORD)
            text_entry.pack(fill="x", pady=5)
            
            # Result preview
            preview_frame = ttk.LabelFrame(main_frame, text="AI Preview", padding="10")
            preview_frame.pack(fill="both", expand=True, pady=(10, 0))
            
            preview_text = tk.Text(preview_frame, height=4, width=50, wrap=tk.WORD, state=tk.DISABLED)
            preview_text.pack(fill="both", expand=True)
            
            def process_natural_language():
                """Process the natural language input"""
                try:
                    input_text = text_entry.get("1.0", tk.END).strip()
                    if not input_text:
                        messagebox.showwarning("Input Required", "Please enter a transaction description.")
                        return
                    
                    # Show processing status
                    preview_text.config(state=tk.NORMAL)
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert("1.0", "🤖 AI is processing your transaction...")
                    preview_text.config(state=tk.DISABLED)
                    nl_window.update()
                    
                    # Process in background
                    threading.Thread(target=self._process_nl_background, 
                                   args=(input_text, preview_text, nl_window), daemon=True).start()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to process: {str(e)}")
            
            def cancel():
                nl_window.destroy()
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(button_frame, text="🤖 Process with AI", command=process_natural_language).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="❌ Cancel", command=cancel).pack(side="left")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open natural language dialog: {str(e)}")
    
    def _process_nl_background(self, input_text: str, preview_text: tk.Text, parent_window: tk.Toplevel):
        """Process natural language input in background"""
        try:
            success = self.tracker.add_transaction_natural_language(input_text)
            
            if success:
                self._invalidate_cache()
                time.sleep(0.5)
                
                self.root.after(0, lambda: [
                    self._update_balance_display(),
                    self._refresh_data_sync(),
                    self.status_var.set("💬 Natural language transaction added!"),
                    parent_window.destroy(),
                    messagebox.showinfo("Success", "Transaction processed and added successfully!")
                ])
            else:
                self.root.after(0, lambda: [
                    preview_text.config(state=tk.NORMAL),
                    preview_text.delete("1.0", tk.END),
                    preview_text.insert("1.0", "❌ Failed to process transaction"),
                    preview_text.config(state=tk.DISABLED),
                    self.status_var.set("❌ Natural language processing failed")
                ])
                
        except Exception as e:
            self.root.after(0, lambda: [
                preview_text.config(state=tk.NORMAL),
                preview_text.delete("1.0", tk.END),
                preview_text.insert("1.0", f"❌ Error: {str(e)}"),
                preview_text.config(state=tk.DISABLED),
                messagebox.showerror("Error", f"Processing failed: {str(e)}")
            ])
    
    def show_ai_insights(self):
        """Display AI-generated financial insights"""
        try:
            if not self.tracker.is_ai_available():
                messagebox.showwarning("AI Not Available", 
                                     "AI features are not available. Please check your GEMINI_API_KEY.")
                return
            
            self.status_var.set("🧠 Generating AI insights...")
            self.root.update()
            
            # Generate insights in background
            threading.Thread(target=self._generate_insights_background, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate insights: {str(e)}")
    
    def _generate_insights_background(self):
        """Generate AI insights in background"""
        try:
            # Get data
            transactions = self.tracker.sheets_service.get_all_records()
            current_balance = self.tracker.get_current_balance()
            
            if not transactions:
                self.root.after(0, lambda: [
                    messagebox.showinfo("No Data", "No transactions found. Add some transactions first."),
                    self.status_var.set("Ready")
                ])
                return
            
            insights = self.tracker.ai_service.generate_financial_insights(transactions, current_balance)
            
            self.root.after(0, lambda: self._display_insights_window(insights))
            
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to generate insights: {str(e)}"),
                self.status_var.set("❌ Insights generation failed")
            ])
    
    def _display_insights_window(self, insights: dict):
        """Display insights in a new window"""
        try:
            # Create insights window
            insights_window = tk.Toplevel(self.root)
            insights_window.title("🧠 AI Financial Insights")
            insights_window.geometry("700x600")
            insights_window.transient(self.root)
            
            # Center the window
            insights_window.update_idletasks()
            x = (insights_window.winfo_screenwidth() // 2) - (700 // 2)
            y = (insights_window.winfo_screenheight() // 2) - (600 // 2)
            insights_window.geometry(f"700x600+{x}+{y}")
            
            main_frame = ttk.Frame(insights_window, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(main_frame, text="🧠 AI Financial Insights", 
                     font=('Arial', 16, 'bold')).pack(pady=(0, 15))
            
            # Create scrollable text area
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill="both", expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 10))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Format and display insights
            insights_text = self._format_insights_display(insights)
            text_widget.insert("1.0", insights_text)
            text_widget.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=insights_window.destroy).pack(pady=(15, 0))
            
            self.status_var.set("🧠 AI insights generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display insights: {str(e)}")
    
    def _format_insights_display(self, insights: dict) -> str:
        """Format insights for display"""
        formatted = "🤖 AI FINANCIAL INSIGHTS\n"
        formatted += "=" * 50 + "\n\n"
        
        sections = [
            ("📊 SPENDING PATTERNS", "spending_patterns"),
            ("💡 BUDGET RECOMMENDATIONS", "budget_recommendations"),
            ("💰 SAVINGS TIPS", "savings_tips"),
            ("🚨 ANOMALIES DETECTED", "anomalies"),
            ("📈 MONTHLY TREND", "monthly_trend"),
            ("🏆 TOP CATEGORIES", "top_categories")
        ]
        
        for title, key in sections:
            formatted += f"{title}:\n"
            insight = insights.get(key, f"No {key.replace('_', ' ')} available")
            
            if isinstance(insight, list):
                for item in insight:
                    formatted += f"• {item}\n"
            else:
                formatted += f"{insight}\n"
            formatted += "\n"
        
        return formatted
    
    def generate_ai_report(self):
        """Generate AI financial report"""
        try:
            if not self.tracker.is_ai_available():
                messagebox.showwarning("AI Not Available", 
                                     "AI features are not available. Please check your GEMINI_API_KEY.")
                return
            
            # Ask for report period
            period = self._ask_report_period()
            if not period:
                return
            
            self.status_var.set(f"📊 Generating {period} AI report...")
            self.root.update()
            
            # Generate report in background
            threading.Thread(target=self._generate_report_background, args=(period,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def _ask_report_period(self):
        """Ask user to choose report period"""
        period_window = tk.Toplevel(self.root)
        period_window.title("📊 Report Period")
        period_window.geometry("300x200")
        period_window.transient(self.root)
        period_window.grab_set()
        
        # Center the window
        period_window.update_idletasks()
        x = (period_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (period_window.winfo_screenheight() // 2) - (200 // 2)
        period_window.geometry(f"300x200+{x}+{y}")
        
        result = {"period": None}
        
        main_frame = ttk.Frame(period_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="📊 Select Report Period:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        def set_weekly():
            result["period"] = "weekly"
            period_window.destroy()
        
        def set_monthly():
            result["period"] = "monthly"
            period_window.destroy()
        
        def set_yearly():
            result["period"] = "yearly"
            period_window.destroy()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="📅 Weekly", command=set_weekly).pack(pady=2, fill='x')
        ttk.Button(button_frame, text="📆 Monthly", command=set_monthly).pack(pady=2, fill='x')
        ttk.Button(button_frame, text="📋 Yearly", command=set_yearly).pack(pady=2, fill='x')
        ttk.Button(button_frame, text="❌ Cancel", command=period_window.destroy).pack(pady=2, fill='x')
        
        period_window.wait_window()
        return result["period"]
    
    def _generate_report_background(self, period: str):
        """Generate AI report in background"""
        try:
            transactions = self.tracker.sheets_service.get_all_records()
            
            if not transactions:
                self.root.after(0, lambda: [
                    messagebox.showinfo("No Data", "No transactions found. Add some transactions first."),
                    self.status_var.set("Ready")
                ])
                return
            
            report = self.tracker.ai_service.generate_expense_report(transactions, period)
            
            self.root.after(0, lambda: self._display_report_window(report, period))
            
        except Exception as e:
            self.root.after(0, lambda: [
                messagebox.showerror("Error", f"Failed to generate report: {str(e)}"),
                self.status_var.set("❌ Report generation failed")
            ])
    
    def _display_report_window(self, report: str, period: str):
        """Display report in a new window"""
        try:
            # Create report window
            report_window = tk.Toplevel(self.root)
            report_window.title(f"📊 {period.title()} AI Financial Report")
            report_window.geometry("800x700")
            report_window.transient(self.root)
            
            # Center the window
            report_window.update_idletasks()
            x = (report_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (report_window.winfo_screenheight() // 2) - (700 // 2)
            report_window.geometry(f"800x700+{x}+{y}")
            
            main_frame = ttk.Frame(report_window, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(main_frame, text=f"📊 {period.title()} Financial Report", 
                     font=('Arial', 16, 'bold')).pack(pady=(0, 15))
            
            # Create scrollable text area
            text_frame = ttk.Frame(main_frame)
            text_frame.pack(fill="both", expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Courier', 9))
            scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Display report
            text_widget.insert("1.0", report)
            text_widget.config(state=tk.DISABLED)
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill="x", pady=(15, 0))
            
            def save_report():
                """Save report to file"""
                try:
                    from tkinter import filedialog
                    filename = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                        title="Save Financial Report"
                    )
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(report)
                        messagebox.showinfo("Success", f"Report saved to {filename}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save report: {str(e)}")
            
            ttk.Button(button_frame, text="💾 Save Report", command=save_report).pack(side="left", padx=(0, 5))
            ttk.Button(button_frame, text="Close", command=report_window.destroy).pack(side="left")
            
            self.status_var.set(f"📊 {period.title()} AI report generated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display report: {str(e)}")
    
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