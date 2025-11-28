"""
Data Connector for Agent C

Connects to hospital data sources (CSV files) to load current inventory and staffing data.
"""

import pandas as pd
import os
from typing import Tuple


class DataConnector:
    """Connect to hospital data sources"""
    
    def __init__(self, data_dir='../media/hospital_data_csv'):
        self.data_dir = data_dir
    
    def load_inventory_data(self) -> pd.DataFrame:
        """Load current inventory levels"""
        inv_path = os.path.join(self.data_dir, 'supply_inventory.csv')
        
        if not os.path.exists(inv_path):
            raise FileNotFoundError(f"Inventory data not found: {inv_path}")
        
        df = pd.read_csv(inv_path, parse_dates=['snapshot_date'])
        
        # Get most recent snapshot
        latest_date = df['snapshot_date'].max()
        latest_inv = df[df['snapshot_date'] == latest_date]
        
        return latest_inv
    
    def load_staffing_data(self) -> pd.DataFrame:
        """Load current staff availability"""
        staff_path = os.path.join(self.data_dir, 'staff_availability.csv')
        
        if not os.path.exists(staff_path):
            raise FileNotFoundError(f"Staffing data not found: {staff_path}")
        
        df = pd.read_csv(staff_path, parse_dates=['snapshot_date'])
        
        # Get most recent snapshot
        latest_date = df['snapshot_date'].max()
        latest_staff = df[df['snapshot_date'] == latest_date]
        
        # Aggregate by department
        agg_staff = latest_staff.groupby(['department_id']).agg({
            'doctors_available': 'sum',
            'nurses_available': 'sum',
            'technicians_available': 'sum'
        }).reset_index()
        
        return agg_staff
    
    def load_historical_consumption(self, days=30) -> pd.DataFrame:
        """Load historical consumption patterns"""
        inv_path = os.path.join(self.data_dir, 'supply_inventory.csv')
        
        if not os.path.exists(inv_path):
            return pd.DataFrame()
        
        df = pd.read_csv(inv_path, parse_dates=['snapshot_date'])
        
        # Get last N days
        latest_date = df['snapshot_date'].max()
        cutoff_date = latest_date - pd.Timedelta(days=days)
        recent = df[df['snapshot_date'] >= cutoff_date]
        
        # Calculate daily consumption (stock decrease)
        consumption = recent.groupby(['item_code', 'snapshot_date'])['qty_on_hand'].first().diff()
        
        return consumption


if __name__ == "__main__":
    connector = DataConnector()
    try:
        inv = connector.load_inventory_data()
        print(f"Loaded inventory: {len(inv)} items")
        print(inv.head())
        
        staff = connector.load_staffing_data()
        print(f"\nLoaded staffing: {len(staff)} departments")
        print(staff.head())
    except Exception as e:
        print(f"Error: {e}")
