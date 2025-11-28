"""
Inventory Management Module for Agent C: The Logistics Commander

This module implements the Gap Analysis Algorithm and intelligent inventory management
including purchase order generation and lead time awareness.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from resource_mapping import resource_kb, ConditionType


class InventoryAction(Enum):
    """Types of inventory actions"""
    GENERATE_PO = "GENERATE_PO"
    NO_ACTION = "NO_ACTION"
    EMERGENCY_LOAN = "EMERGENCY_LOAN"
    CRITICAL_ALERT = "CRITICAL_ALERT"


@dataclass
class InventoryStatus:
    """Current inventory status for an item"""
    sku: str
    item_name: str
    current_stock: int
    reorder_level: int
    safety_buffer: int
    lead_time_days: int
    vendor_id: str


@dataclass
class InventoryActionResult:
    """Result of inventory analysis"""
    sku: str
    item_name: str
    current_stock: int
    predicted_demand: int
    gap: int
    action: InventoryAction
    quantity: int
    priority: str
    vendor_id: str
    notes: str
    urgency_score: float


class InventoryManager:
    """
    Intelligent Inventory Management System
    
    Implements gap analysis algorithm and generates purchase orders
    based on predicted demand and current stock levels.
    """
    
    def __init__(self, safety_buffer_multiplier: float = 1.2):
        """
        Initialize Inventory Manager
        
        Parameters:
        - safety_buffer_multiplier: Multiplier for safety buffer (default 1.2 = 20% buffer)
        """
        self.safety_buffer_multiplier = safety_buffer_multiplier
        self.current_inventory: Dict[str, InventoryStatus] = {}
    
    def load_current_inventory(self, inventory_data: pd.DataFrame):
        """
        Load current inventory levels from database/CSV
        
        Parameters:
        - inventory_data: DataFrame with columns [sku, item_name, current_stock, reorder_level, lead_time_days, vendor_id]
        """
        for _, row in inventory_data.iterrows():
            sku = row['item_code'] if 'item_code' in row else row.get('sku', 'UNKNOWN')
            
            # Calculate safety buffer
            reorder_level = row.get('reorder_level', 100)
            safety_buffer = int(reorder_level * (self.safety_buffer_multiplier - 1.0))
            
            self.current_inventory[sku] = InventoryStatus(
                sku=sku,
                item_name=row.get('item_name', 'Unknown Item'),
                current_stock=row.get('qty_on_hand', 0),
                reorder_level=reorder_level,
                safety_buffer=safety_buffer,
                lead_time_days=row.get('estimated_lead_days', 3),
                vendor_id=row.get('vendor_id', 'DEFAULT_VENDOR')
            )
    
    def calculate_inventory_gap(self, sku: str, predicted_demand: int) -> Tuple[int, InventoryAction]:
        """
        Calculate inventory gap using Gap Analysis Algorithm
        
        Formula:
        Required_Units = Predicted_Demand
        Stock_Gap = Current_Stock - Required_Units
        If Stock_Gap < Safety_Buffer: TRIGGER_ORDER
        
        Parameters:
        - sku: Stock Keeping Unit identifier
        - predicted_demand: Predicted consumption units
        
        Returns:
        - Tuple of (gap, action)
        """
        if sku not in self.current_inventory:
            # Unknown SKU - create default entry
            return -predicted_demand, InventoryAction.CRITICAL_ALERT
        
        inv_status = self.current_inventory[sku]
        
        # Calculate gap
        stock_gap = inv_status.current_stock - predicted_demand
        
        # Determine action
        if stock_gap < -inv_status.safety_buffer:
            # Critical shortage
            action = InventoryAction.CRITICAL_ALERT
        elif stock_gap < inv_status.safety_buffer:
            # Below safety buffer - trigger order
            action = InventoryAction.GENERATE_PO
        else:
            # Adequate stock
            action = InventoryAction.NO_ACTION
        
        return stock_gap, action
    
    def check_lead_time_feasibility(self, sku: str, days_until_surge: int) -> bool:
        """
        Check if lead time allows for normal delivery
        
        Parameters:
        - sku: Stock Keeping Unit
        - days_until_surge: Days until predicted surge
        
        Returns:
        - True if normal delivery is feasible, False if emergency action needed
        """
        if sku not in self.current_inventory:
            return False
        
        inv_status = self.current_inventory[sku]
        return inv_status.lead_time_days <= days_until_surge
    
    def generate_inventory_actions(self, 
                                   condition_type: ConditionType,
                                   predicted_patients: int,
                                   days_until_surge: int = 7) -> List[InventoryActionResult]:
        """
        Generate inventory actions based on predicted demand
        
        Parameters:
        - condition_type: Type of medical condition
        - predicted_patients: Number of patients predicted
        - days_until_surge: Days until the surge is expected
        
        Returns:
        - List of InventoryActionResult objects
        """
        # Get resource requirements from knowledge base
        _, inventory_requirements = resource_kb.calculate_total_requirements(
            condition_type, predicted_patients
        )
        
        actions = []
        
        for sku, req in inventory_requirements.items():
            predicted_demand = req['required_units']
            
            # Calculate gap
            stock_gap, action = self.calculate_inventory_gap(sku, predicted_demand)
            
            # Check lead time feasibility
            lead_time_ok = self.check_lead_time_feasibility(sku, days_until_surge)
            
            # Adjust action based on lead time
            if action == InventoryAction.GENERATE_PO and not lead_time_ok:
                action = InventoryAction.EMERGENCY_LOAN
            
            # Calculate order quantity
            if action in [InventoryAction.GENERATE_PO, InventoryAction.EMERGENCY_LOAN]:
                # Order enough to cover demand + safety buffer
                inv_status = self.current_inventory.get(sku)
                if inv_status:
                    order_qty = predicted_demand + inv_status.safety_buffer - inv_status.current_stock
                    order_qty = max(order_qty, inv_status.reorder_level)
                else:
                    order_qty = predicted_demand * 2  # Default: 2x demand
            else:
                order_qty = 0
            
            # Calculate urgency score (0-1, higher = more urgent)
            urgency_score = self._calculate_urgency_score(
                stock_gap, predicted_demand, days_until_surge, req['priority']
            )
            
            # Generate notes
            notes = self._generate_notes(action, stock_gap, lead_time_ok, days_until_surge)
            
            # Get current stock
            current_stock = self.current_inventory.get(sku).current_stock if sku in self.current_inventory else 0
            vendor_id = self.current_inventory.get(sku).vendor_id if sku in self.current_inventory else req['vendor_id']
            
            actions.append(InventoryActionResult(
                sku=sku,
                item_name=req['item_name'],
                current_stock=current_stock,
                predicted_demand=predicted_demand,
                gap=stock_gap,
                action=action,
                quantity=order_qty,
                priority=req['priority'],
                vendor_id=vendor_id,
                notes=notes,
                urgency_score=urgency_score
            ))
        
        # Sort by urgency score (descending)
        actions.sort(key=lambda x: x.urgency_score, reverse=True)
        
        return actions
    
    def _calculate_urgency_score(self, stock_gap: int, predicted_demand: int, 
                                 days_until_surge: int, priority: str) -> float:
        """
        Calculate urgency score (0-1)
        
        Factors:
        - Stock gap severity
        - Time until surge
        - Priority level
        """
        # Gap severity (0-0.4)
        if predicted_demand > 0:
            gap_severity = min(0.4, max(0, -stock_gap / predicted_demand * 0.4))
        else:
            gap_severity = 0
        
        # Time urgency (0-0.3)
        time_urgency = min(0.3, max(0, (7 - days_until_surge) / 7 * 0.3))
        
        # Priority weight (0-0.3)
        priority_weights = {
            'critical': 0.3,
            'high': 0.2,
            'medium': 0.1,
            'low': 0.05
        }
        priority_weight = priority_weights.get(priority, 0.1)
        
        return gap_severity + time_urgency + priority_weight
    
    def _generate_notes(self, action: InventoryAction, stock_gap: int, 
                       lead_time_ok: bool, days_until_surge: int) -> str:
        """Generate human-readable notes for the action"""
        if action == InventoryAction.NO_ACTION:
            return f"Stock adequate. Current surplus: {stock_gap} units."
        elif action == InventoryAction.GENERATE_PO:
            return f"Generate purchase order. Stock deficit: {-stock_gap} units. Normal delivery timeline."
        elif action == InventoryAction.EMERGENCY_LOAN:
            return f"URGENT: Lead time exceeds surge timeline ({days_until_surge} days). Request inter-hospital loan or emergency vendor delivery."
        elif action == InventoryAction.CRITICAL_ALERT:
            return f"CRITICAL: Severe shortage detected. Stock deficit: {-stock_gap} units. Immediate action required."
        else:
            return "Action required."
    
    def generate_purchase_orders_json(self, actions: List[InventoryActionResult]) -> List[Dict]:
        """
        Generate structured purchase order data
        
        Parameters:
        - actions: List of InventoryActionResult
        
        Returns:
        - List of purchase order dictionaries
        """
        purchase_orders = []
        
        for action_result in actions:
            if action_result.action in [InventoryAction.GENERATE_PO, InventoryAction.EMERGENCY_LOAN]:
                po = {
                    "item_name": action_result.item_name,
                    "sku": action_result.sku,
                    "current_stock": action_result.current_stock,
                    "predicted_demand": action_result.predicted_demand,
                    "action": action_result.action.value,
                    "quantity": action_result.quantity,
                    "priority": action_result.priority.upper(),
                    "vendor_id": action_result.vendor_id,
                    "urgency_score": round(action_result.urgency_score, 3),
                    "notes": action_result.notes
                }
                purchase_orders.append(po)
        
        return purchase_orders
    
    def get_summary_statistics(self, actions: List[InventoryActionResult]) -> Dict:
        """Get summary statistics of inventory actions"""
        total_items = len(actions)
        items_needing_action = sum(1 for a in actions if a.action != InventoryAction.NO_ACTION)
        critical_items = sum(1 for a in actions if a.action == InventoryAction.CRITICAL_ALERT)
        emergency_loans = sum(1 for a in actions if a.action == InventoryAction.EMERGENCY_LOAN)
        total_po_value = sum(a.quantity for a in actions if a.action == InventoryAction.GENERATE_PO)
        
        return {
            "total_items_analyzed": total_items,
            "items_needing_action": items_needing_action,
            "critical_alerts": critical_items,
            "emergency_loans_required": emergency_loans,
            "purchase_orders_generated": items_needing_action - critical_items - emergency_loans,
            "total_units_to_order": total_po_value
        }


if __name__ == "__main__":
    # Test the inventory manager
    print("=" * 60)
    print("INVENTORY MANAGER TEST")
    print("=" * 60)
    
    # Create sample inventory data
    sample_inventory = pd.DataFrame([
        {'item_code': 'MED-NEB-001', 'item_name': 'Nebulizer Masks', 'qty_on_hand': 50, 'reorder_level': 100, 'estimated_lead_days': 1, 'vendor_id': 'MEDEQUIP_A'},
        {'item_code': 'MED-ALB-500', 'item_name': 'Albuterol Solution', 'qty_on_hand': 80, 'reorder_level': 150, 'estimated_lead_days': 2, 'vendor_id': 'PHARMA_CORP_A'},
        {'item_code': 'MED-OXY-D', 'item_name': 'Oxygen Cylinders', 'qty_on_hand': 30, 'reorder_level': 50, 'estimated_lead_days': 2, 'vendor_id': 'MEDGAS_SUPPLY'},
        {'item_code': 'PPE-N95-001', 'item_name': 'N95 Masks', 'qty_on_hand': 200, 'reorder_level': 500, 'estimated_lead_days': 1, 'vendor_id': 'PPE_DIRECT'},
    ])
    
    # Initialize manager
    manager = InventoryManager(safety_buffer_multiplier=1.2)
    manager.load_current_inventory(sample_inventory)
    
    print("\nLoaded inventory:")
    for sku, status in manager.current_inventory.items():
        print(f"  {status.item_name}: {status.current_stock} units (reorder: {status.reorder_level})")
    
    # Test scenario: 150 respiratory patients in 3 days
    print("\n" + "=" * 60)
    print("SCENARIO: 150 Respiratory Patients in 3 Days")
    print("=" * 60)
    
    actions = manager.generate_inventory_actions(
        condition_type=ConditionType.RESPIRATORY_SURGE,
        predicted_patients=150,
        days_until_surge=3
    )
    
    print("\nInventory Actions:")
    for action in actions:
        print(f"\n{action.item_name} ({action.sku}):")
        print(f"  Current Stock: {action.current_stock}")
        print(f"  Predicted Demand: {action.predicted_demand}")
        print(f"  Gap: {action.gap}")
        print(f"  Action: {action.action.value}")
        print(f"  Order Quantity: {action.quantity}")
        print(f"  Priority: {action.priority}")
        print(f"  Urgency Score: {action.urgency_score:.3f}")
        print(f"  Notes: {action.notes}")
    
    # Generate purchase orders
    print("\n" + "=" * 60)
    print("PURCHASE ORDERS")
    print("=" * 60)
    
    pos = manager.generate_purchase_orders_json(actions)
    for po in pos:
        print(f"\nPO for {po['item_name']}:")
        print(f"  Quantity: {po['quantity']} units")
        print(f"  Vendor: {po['vendor_id']}")
        print(f"  Priority: {po['priority']}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    summary = manager.get_summary_statistics(actions)
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n✓ Inventory Manager test completed!")
