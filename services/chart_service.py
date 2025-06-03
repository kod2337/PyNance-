"""
Chart service for Finance Tracker
"""

from typing import List, Dict, Any
from colorama import Fore

from config.settings import MAX_BALANCE_TREND_ENTRIES


class ChartService:
    """Handles chart creation in Google Sheets"""
    
    def __init__(self, sheets_service):
        self.sheets_service = sheets_service
    
    def create_all_charts(self, records: List[Dict[str, Any]]) -> bool:
        """Create all charts for the given transaction records"""
        try:
            if not records:
                print(f"{Fore.YELLOW}📝 No data available for charts")
                return False
            
            print(f"{Fore.CYAN}📊 Creating charts...")
            
            # Get or create charts worksheet
            charts_worksheet = self.sheets_service.get_or_create_charts_worksheet()
            
            # Clear existing charts first
            self._clear_existing_charts(charts_worksheet)
            
            # Create different types of charts
            self._create_category_pie_chart(charts_worksheet, records)
            self._create_balance_trend_chart(charts_worksheet, records)
            self._create_monthly_summary_chart(charts_worksheet, records)
            
            print(f"{Fore.GREEN}✅ Charts created successfully!")
            print(f"{Fore.CYAN}📈 Check the 'Charts & Analysis' tab in your spreadsheet")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error creating charts: {str(e)}")
            return False
    
    def _create_category_pie_chart(self, worksheet, records: List[Dict[str, Any]]):
        """Create pie chart for expense categories"""
        try:
            # Calculate category expenses
            category_expenses = self._calculate_category_expenses(records)
            
            if not category_expenses:
                return
            
            # Clear and setup data
            worksheet.clear()
            worksheet.update('A1', 'Category Expense Analysis')
            worksheet.update('A3', 'Category')
            worksheet.update('B3', 'Amount')
            
            # Add data
            row = 4
            for category, amount in category_expenses.items():
                worksheet.update(f'A{row}', category)
                worksheet.update(f'B{row}', amount)
                row += 1
            
            # Create chart
            chart_request = self._build_pie_chart_request(worksheet.id, row)
            self.sheets_service.batch_update([chart_request])
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create category chart: {str(e)}")
    
    def _clear_existing_charts(self, worksheet):
        """Clear all existing charts from the worksheet"""
        try:
            # Get all charts in the spreadsheet
            spreadsheet_metadata = self.sheets_service.spreadsheet.fetch_sheet_metadata()
            
            delete_requests = []
            
            # Find charts in our worksheet and prepare delete requests
            for sheet in spreadsheet_metadata['sheets']:
                if sheet['properties']['sheetId'] == worksheet.id:
                    if 'charts' in sheet:
                        for chart in sheet['charts']:
                            delete_requests.append({
                                'deleteEmbeddedObject': {
                                    'objectId': chart['chartId']
                                }
                            })
            
            # Execute delete requests if any charts exist
            if delete_requests:
                self.sheets_service.batch_update(delete_requests)
                
        except Exception as e:
            # If we can't delete existing charts, just continue
            # This might happen if no charts exist yet
            pass
    
    def _create_balance_trend_chart(self, worksheet, records: List[Dict[str, Any]]):
        """Create line chart for balance over time"""
        try:
            # Prepare balance data
            balance_data = self._prepare_balance_data(records)
            
            if len(balance_data) < 2:
                return
            
            # Add data starting from row 15
            start_row = 15
            worksheet.update(f'A{start_row}', 'Balance Trend Analysis')
            worksheet.update(f'A{start_row + 2}', 'Date')
            worksheet.update(f'B{start_row + 2}', 'Balance')
            
            for i, (date_str, balance) in enumerate(balance_data):
                row = start_row + 3 + i
                worksheet.update(f'A{row}', date_str)
                worksheet.update(f'B{row}', balance)
            
            end_row = start_row + 3 + len(balance_data)
            
            # Create chart
            chart_request = self._build_line_chart_request(worksheet.id, start_row, end_row)
            self.sheets_service.batch_update([chart_request])
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create balance trend chart: {str(e)}")
    
    def _create_monthly_summary_chart(self, worksheet, records: List[Dict[str, Any]]):
        """Create bar chart for monthly income vs expenses"""
        try:
            # Calculate monthly data
            monthly_data = self._calculate_monthly_data(records)
            
            if not monthly_data:
                return
            
            # Add data starting from row 30
            start_row = 30
            worksheet.update(f'A{start_row}', 'Monthly Income vs Expenses')
            worksheet.update(f'A{start_row + 2}', 'Month')
            worksheet.update(f'B{start_row + 2}', 'Income')
            worksheet.update(f'C{start_row + 2}', 'Expenses')
            
            row = start_row + 3
            for month, data in sorted(monthly_data.items()):
                worksheet.update(f'A{row}', month)
                worksheet.update(f'B{row}', data['income'])
                worksheet.update(f'C{row}', data['expenses'])
                row += 1
            
            # Create chart
            chart_request = self._build_column_chart_request(worksheet.id, start_row, row)
            self.sheets_service.batch_update([chart_request])
            
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Could not create monthly summary chart: {str(e)}")
    
    def _calculate_category_expenses(self, records: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total expenses by category"""
        category_expenses = {}
        for record in records:
            if float(record['Amount']) < 0:  # Only expenses
                category = record['Category']
                amount = abs(float(record['Amount']))
                category_expenses[category] = category_expenses.get(category, 0) + amount
        return category_expenses
    
    def _prepare_balance_data(self, records: List[Dict[str, Any]]) -> List[tuple]:
        """Prepare balance trend data for charting"""
        balance_data = []
        for record in records[-MAX_BALANCE_TREND_ENTRIES:]:
            date_str = record['Date'][:10]  # Just the date part
            balance = float(record['Balance'])
            balance_data.append((date_str, balance))
        return balance_data
    
    def _calculate_monthly_data(self, records: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate monthly income and expenses"""
        monthly_data = {}
        for record in records:
            date_str = record['Date'][:7]  # YYYY-MM format
            amount = float(record['Amount'])
            
            if date_str not in monthly_data:
                monthly_data[date_str] = {'income': 0, 'expenses': 0}
            
            if amount < 0:
                monthly_data[date_str]['expenses'] += abs(amount)
            else:
                monthly_data[date_str]['income'] += amount
        
        return monthly_data
    
    def _build_pie_chart_request(self, sheet_id: int, end_row: int) -> Dict[str, Any]:
        """Build pie chart request for Google Sheets API"""
        return {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': 'Expenses by Category',
                        'pieChart': {
                            'legendPosition': 'RIGHT_LEGEND',
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 3,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': 0,
                                        'endColumnIndex': 1
                                    }]
                                }
                            },
                            'series': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': 3,
                                        'endRowIndex': end_row,
                                        'startColumnIndex': 1,
                                        'endColumnIndex': 2
                                    }]
                                }
                            }
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {
                                'sheetId': sheet_id,
                                'rowIndex': 2,
                                'columnIndex': 4
                            },
                            'offsetXPixels': 0,
                            'offsetYPixels': 0,
                            'widthPixels': 500,
                            'heightPixels': 300
                        }
                    }
                }
            }
        }
    
    def _build_line_chart_request(self, sheet_id: int, start_row: int, end_row: int) -> Dict[str, Any]:
        """Build line chart request for Google Sheets API"""
        return {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': 'Balance Over Time',
                        'basicChart': {
                            'chartType': 'LINE',
                            'legendPosition': 'RIGHT_LEGEND',
                            'axis': [
                                {'position': 'BOTTOM_AXIS', 'title': 'Date'},
                                {'position': 'LEFT_AXIS', 'title': 'Balance ($)'}
                            ],
                            'domains': [{
                                'domain': {
                                    'sourceRange': {
                                        'sources': [{
                                            'sheetId': sheet_id,
                                            'startRowIndex': start_row + 2,
                                            'endRowIndex': end_row,
                                            'startColumnIndex': 0,
                                            'endColumnIndex': 1
                                        }]
                                    }
                                }
                            }],
                            'series': [{
                                'series': {
                                    'sourceRange': {
                                        'sources': [{
                                            'sheetId': sheet_id,
                                            'startRowIndex': start_row + 2,
                                            'endRowIndex': end_row,
                                            'startColumnIndex': 1,
                                            'endColumnIndex': 2
                                        }]
                                    }
                                },
                                'targetAxis': 'LEFT_AXIS'
                            }]
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {
                                'sheetId': sheet_id,
                                'rowIndex': 22,
                                'columnIndex': 4
                            },
                            'offsetXPixels': 0,
                            'offsetYPixels': 0,
                            'widthPixels': 500,
                            'heightPixels': 300
                        }
                    }
                }
            }
        }
    
    def _build_column_chart_request(self, sheet_id: int, start_row: int, end_row: int) -> Dict[str, Any]:
        """Build column chart request for Google Sheets API"""
        return {
            'addChart': {
                'chart': {
                    'spec': {
                        'title': 'Monthly Income vs Expenses',
                        'basicChart': {
                            'chartType': 'COLUMN',
                            'legendPosition': 'RIGHT_LEGEND',
                            'axis': [
                                {'position': 'BOTTOM_AXIS', 'title': 'Month'},
                                {'position': 'LEFT_AXIS', 'title': 'Amount ($)'}
                            ],
                            'domains': [{
                                'domain': {
                                    'sourceRange': {
                                        'sources': [{
                                            'sheetId': sheet_id,
                                            'startRowIndex': start_row + 2,
                                            'endRowIndex': end_row,
                                            'startColumnIndex': 0,
                                            'endColumnIndex': 1
                                        }]
                                    }
                                }
                            }],
                            'series': [
                                {
                                    'series': {
                                        'sourceRange': {
                                            'sources': [{
                                                'sheetId': sheet_id,
                                                'startRowIndex': start_row + 2,
                                                'endRowIndex': end_row,
                                                'startColumnIndex': 1,
                                                'endColumnIndex': 2
                                            }]
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                },
                                {
                                    'series': {
                                        'sourceRange': {
                                            'sources': [{
                                                'sheetId': sheet_id,
                                                'startRowIndex': start_row + 2,
                                                'endRowIndex': end_row,
                                                'startColumnIndex': 2,
                                                'endColumnIndex': 3
                                            }]
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                }
                            ]
                        }
                    },
                    'position': {
                        'overlayPosition': {
                            'anchorCell': {
                                'sheetId': sheet_id,
                                'rowIndex': 42,
                                'columnIndex': 4
                            },
                            'offsetXPixels': 0,
                            'offsetYPixels': 0,
                            'widthPixels': 500,
                            'heightPixels': 300
                        }
                    }
                }
            }
        } 