"""
Staffing Optimization Module for Agent C: The Logistics Commander

This module implements dynamic roster allocation, on-call activation,
and elective procedure rescheduling logic.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from resource_mapping import resource_kb, ConditionType, StaffRole


class StaffingAction(Enum):
    """Types of staffing actions"""
    NO_ACTION = "NO_ACTION"
    REALLOCATE = "REALLOCATE"
    ACTIVATE_ON_CALL = "ACTIVATE_ON_CALL"
    REQUEST_AGENCY = "REQUEST_AGENCY"
    CRITICAL_SHORTAGE = "CRITICAL_SHORTAGE"


@dataclass
class StaffingActionResult:
    """Result of staffing analysis"""
    role: str
    current_roster_count: int
    required_count: int
    deficit: int
    action: StaffingAction
    priority: str
    source_dept: Optional[str]
    target_dept: str
    count: int
    target_personnel_ids: List[str]
    notes: str
    urgency_score: float


@dataclass
class ElectiveRecommendation:
    """Recommendation for elective procedure rescheduling"""
    procedure_type: str
    scheduled_date: datetime
    department: str
    beds_freed: int
    staff_freed: int
    recommendation: str


class StaffingOptimizer:
    """
    Dynamic Staffing Optimization System
    
    Implements intelligent staff allocation using:
    1. Internal reallocation (move from low to high priority)
    2. On-call activation
    3. Agency staffing requests
    """
    
    def __init__(self):
        self.current_roster: Dict[str, Dict] = {}
        self.department_priorities: Dict[str, int] = {}
        self.on_call_staff: Dict[str, List[str]] = {}
    
    def load_current_roster(self, staff_data: pd.DataFrame):
        """
        Load current staff roster from database/CSV
        
        Parameters:
        - staff_data: DataFrame with columns [role, department, count, on_call_ids]
        """
        for _, row in staff_data.iterrows():
            role = row.get('role', 'unknown')
            dept = row.get('department_id', 'general')
            
            key = f"{role}_{dept}"
            self.current_roster[key] = {
                'role': role,
                'department': dept,
                'count': row.get('available_count', 0),
                'on_call_ids': row.get('on_call_ids', [])
            }
    
    def set_department_priorities(self, priorities: Dict[str, int]):
        """
        Set department priority levels
        
        Parameters:
        - priorities: Dict mapping department to priority (1=highest, 5=lowest)
        """
        self.department_priorities = priorities
    
    def calculate_staffing_gap(self, role: str, department: str, required_count: int) -> int:
        """
        Calculate staffing gap for a specific role in a department
        
        Parameters:
        - role: Staff role
        - department: Department name
        - required_count: Required number of staff
        
        Returns:
        - Deficit (negative if shortage, positive if surplus)
        """
        key = f"{role}_{department}"
        current_count = self.current_roster.get(key, {}).get('count', 0)
        return current_count - required_count
    
    def find_reallocation_sources(self, role: str, target_dept: str, needed_count: int) -> List[Tuple[str, int]]:
        """
        Find departments that can provide staff for reallocation
        
        Strategy: Move from lower priority departments to higher priority
        
        Parameters:
        - role: Staff role needed
        - target_dept: Target department
        - needed_count: Number of staff needed
        
        Returns:
        - List of (source_dept, count) tuples
        """
        target_priority = self.department_priorities.get(target_dept, 3)
        sources = []
        remaining_need = needed_count
        
        # Find departments with same role and lower priority (higher number)
        for key, roster_info in self.current_roster.items():
            if roster_info['role'] != role:
                continue
            
            source_dept = roster_info['department']
            if source_dept == target_dept:
                continue
            
            source_priority = self.department_priorities.get(source_dept, 3)
            
            # Only reallocate from lower priority departments
            if source_priority > target_priority:
                available = roster_info['count']
                # Don't completely empty a department
                can_move = max(0, available - 1)
                
                if can_move > 0:
                    move_count = min(can_move, remaining_need)
                    sources.append((source_dept, move_count))
                    remaining_need -= move_count
                    
                    if remaining_need <= 0:
                        break
        
        return sources
    
    def get_on_call_staff(self, role: str, needed_count: int) -> List[str]:
        """
        Get on-call staff IDs for a specific role
        
        Parameters:
        - role: Staff role
        - needed_count: Number of staff needed
        
        Returns:
        - List of staff IDs
        """
        # Collect on-call staff for this role across all departments
        on_call_ids = []
        for key, roster_info in self.current_roster.items():
            if roster_info['role'] == role:
                on_call_ids.extend(roster_info.get('on_call_ids', []))
        
        # Return up to needed_count
        return on_call_ids[:needed_count]
    
    def generate_staffing_actions(self,
                                  condition_type: ConditionType,
                                  predicted_patients: int,
                                  target_department: str = "Emergency") -> List[StaffingActionResult]:
        """
        Generate staffing actions based on predicted demand
        
        Parameters:
        - condition_type: Type of medical condition
        - predicted_patients: Number of patients predicted
        - target_department: Department where surge is expected
        
        Returns:
        - List of StaffingActionResult objects
        """
        # Get staffing requirements from knowledge base
        staffing_requirements, _ = resource_kb.calculate_total_requirements(
            condition_type, predicted_patients
        )
        
        actions = []
        
        for role, req in staffing_requirements.items():
            required_count = req['required_count']
            
            # Calculate gap
            deficit = -self.calculate_staffing_gap(role, target_department, required_count)
            
            if deficit <= 0:
                # No shortage
                actions.append(StaffingActionResult(
                    role=role,
                    current_roster_count=required_count - deficit,
                    required_count=required_count,
                    deficit=0,
                    action=StaffingAction.NO_ACTION,
                    priority=req['priority'],
                    source_dept=None,
                    target_dept=target_department,
                    count=0,
                    target_personnel_ids=[],
                    notes="Adequate staffing available.",
                    urgency_score=0.0
                ))
                continue
            
            # There's a shortage - determine mitigation strategy
            current_count = required_count - deficit
            
            # Level 1: Try internal reallocation
            reallocation_sources = self.find_reallocation_sources(role, target_department, deficit)
            
            if reallocation_sources and sum(count for _, count in reallocation_sources) >= deficit:
                # Can fully cover with reallocation
                for source_dept, count in reallocation_sources:
                    actions.append(StaffingActionResult(
                        role=role,
                        current_roster_count=current_count,
                        required_count=required_count,
                        deficit=deficit,
                        action=StaffingAction.REALLOCATE,
                        priority=req['priority'],
                        source_dept=source_dept,
                        target_dept=target_department,
                        count=count,
                        target_personnel_ids=[],
                        notes=f"Reallocate {count} {role}(s) from {source_dept} to {target_department}.",
                        urgency_score=self._calculate_urgency_score(deficit, required_count, req['priority'])
                    ))
                continue
            
            # Level 2: Try on-call activation
            if req.get('on_call_acceptable', False):
                on_call_ids = self.get_on_call_staff(role, deficit)
                
                if len(on_call_ids) >= deficit:
                    # Can cover with on-call
                    actions.append(StaffingActionResult(
                        role=role,
                        current_roster_count=current_count,
                        required_count=required_count,
                        deficit=deficit,
                        action=StaffingAction.ACTIVATE_ON_CALL,
                        priority=req['priority'],
                        source_dept=None,
                        target_dept=target_department,
                        count=deficit,
                        target_personnel_ids=on_call_ids[:deficit],
                        notes=f"Activate {deficit} on-call {role}(s). Send automated notifications.",
                        urgency_score=self._calculate_urgency_score(deficit, required_count, req['priority'])
                    ))
                    continue
            
            # Level 3: Request agency staff
            if req['priority'] in ['critical', 'high']:
                actions.append(StaffingActionResult(
                    role=role,
                    current_roster_count=current_count,
                    required_count=required_count,
                    deficit=deficit,
                    action=StaffingAction.REQUEST_AGENCY,
                    priority=req['priority'],
                    source_dept=None,
                    target_dept=target_department,
                    count=deficit,
                    target_personnel_ids=[],
                    notes=f"Request {deficit} temporary agency {role}(s). High cost option.",
                    urgency_score=self._calculate_urgency_score(deficit, required_count, req['priority'])
                ))
            else:
                # Critical shortage - cannot be resolved
                actions.append(StaffingActionResult(
                    role=role,
                    current_roster_count=current_count,
                    required_count=required_count,
                    deficit=deficit,
                    action=StaffingAction.CRITICAL_SHORTAGE,
                    priority=req['priority'],
                    source_dept=None,
                    target_dept=target_department,
                    count=deficit,
                    target_personnel_ids=[],
                    notes=f"CRITICAL: Cannot fulfill {role} requirement. Shortage of {deficit} staff.",
                    urgency_score=1.0
                ))
        
        # Sort by urgency
        actions.sort(key=lambda x: x.urgency_score, reverse=True)
        
        return actions
    
    def _calculate_urgency_score(self, deficit: int, required: int, priority: str) -> float:
        """Calculate urgency score (0-1)"""
        # Deficit severity (0-0.5)
        deficit_severity = min(0.5, deficit / required * 0.5)
        
        # Priority weight (0-0.5)
        priority_weights = {
            'critical': 0.5,
            'high': 0.35,
            'medium': 0.2,
            'low': 0.1
        }
        priority_weight = priority_weights.get(priority, 0.2)
        
        return deficit_severity + priority_weight
    
    def recommend_elective_reductions(self, 
                                      surge_date: datetime,
                                      surge_severity: float) -> List[ElectiveRecommendation]:
        """
        Recommend elective procedure rescheduling during surge
        
        Parameters:
        - surge_date: Date of predicted surge
        - surge_severity: Severity score (0-1)
        
        Returns:
        - List of ElectiveRecommendation objects
        """
        recommendations = []
        
        # Only recommend if surge is severe (>0.7)
        if surge_severity < 0.7:
            return recommendations
        
        # Common elective procedures
        elective_procedures = [
            {'type': 'Cosmetic Surgery', 'dept': 'Plastic Surgery', 'beds': 2, 'staff': 3},
            {'type': 'Knee Replacement', 'dept': 'Orthopedics', 'beds': 1, 'staff': 2},
            {'type': 'Cataract Surgery', 'dept': 'Ophthalmology', 'beds': 1, 'staff': 2},
            {'type': 'Hernia Repair', 'dept': 'General Surgery', 'beds': 1, 'staff': 2},
        ]
        
        for procedure in elective_procedures:
            recommendations.append(ElectiveRecommendation(
                procedure_type=procedure['type'],
                scheduled_date=surge_date,
                department=procedure['dept'],
                beds_freed=procedure['beds'],
                staff_freed=procedure['staff'],
                recommendation=f"Recommend rescheduling {procedure['type']} to free {procedure['beds']} bed(s) and {procedure['staff']} staff."
            ))
        
        return recommendations
    
    def generate_staffing_json(self, actions: List[StaffingActionResult]) -> List[Dict]:
        """Generate structured staffing action data"""
        staffing_actions = []
        
        for action_result in actions:
            if action_result.action == StaffingAction.NO_ACTION:
                continue
            
            staff_action = {
                "role": action_result.role,
                "current_roster_count": action_result.current_roster_count,
                "required_count": action_result.required_count,
                "deficit": action_result.deficit,
                "action": action_result.action.value,
                "priority": action_result.priority.upper(),
                "target_dept": action_result.target_dept,
                "count": action_result.count,
                "urgency_score": round(action_result.urgency_score, 3),
                "notes": action_result.notes
            }
            
            if action_result.source_dept:
                staff_action["source_dept"] = action_result.source_dept
            
            if action_result.target_personnel_ids:
                staff_action["target_personnel_ids"] = action_result.target_personnel_ids
            
            staffing_actions.append(staff_action)
        
        return staffing_actions
    
    def get_summary_statistics(self, actions: List[StaffingActionResult]) -> Dict:
        """Get summary statistics of staffing actions"""
        total_roles = len(actions)
        roles_needing_action = sum(1 for a in actions if a.action != StaffingAction.NO_ACTION)
        reallocations = sum(1 for a in actions if a.action == StaffingAction.REALLOCATE)
        on_call_activations = sum(1 for a in actions if a.action == StaffingAction.ACTIVATE_ON_CALL)
        agency_requests = sum(1 for a in actions if a.action == StaffingAction.REQUEST_AGENCY)
        critical_shortages = sum(1 for a in actions if a.action == StaffingAction.CRITICAL_SHORTAGE)
        
        return {
            "total_roles_analyzed": total_roles,
            "roles_needing_action": roles_needing_action,
            "internal_reallocations": reallocations,
            "on_call_activations": on_call_activations,
            "agency_requests": agency_requests,
            "critical_shortages": critical_shortages
        }


if __name__ == "__main__":
    # Test the staffing optimizer
    print("=" * 60)
    print("STAFFING OPTIMIZER TEST")
    print("=" * 60)
    
    # Create sample roster data
    sample_roster = pd.DataFrame([
        {'role': 'pulmonologist', 'department_id': 'Emergency', 'available_count': 2, 'on_call_ids': ['DR_SHARMA_01', 'DR_GUPTA_02']},
        {'role': 'respiratory_therapist', 'department_id': 'Emergency', 'available_count': 5, 'on_call_ids': []},
        {'role': 'general_nurse', 'department_id': 'Emergency', 'available_count': 15, 'on_call_ids': []},
        {'role': 'general_nurse', 'department_id': 'Dermatology', 'available_count': 8, 'on_call_ids': []},
        {'role': 'general_physician', 'department_id': 'OPD', 'available_count': 10, 'on_call_ids': ['DR_PATEL_05']},
    ])
    
    # Initialize optimizer
    optimizer = StaffingOptimizer()
    optimizer.load_current_roster(sample_roster)
    
    # Set department priorities (1=highest, 5=lowest)
    optimizer.set_department_priorities({
        'Emergency': 1,
        'ICU': 1,
        'Surgery': 2,
        'OPD': 4,
        'Dermatology': 5
    })
    
    print("\nCurrent Roster:")
    for key, roster in optimizer.current_roster.items():
        print(f"  {roster['role']} in {roster['department']}: {roster['count']} staff")
    
    # Test scenario: 150 respiratory patients
    print("\n" + "=" * 60)
    print("SCENARIO: 150 Respiratory Patients")
    print("=" * 60)
    
    actions = optimizer.generate_staffing_actions(
        condition_type=ConditionType.RESPIRATORY_SURGE,
        predicted_patients=150,
        target_department="Emergency"
    )
    
    print("\nStaffing Actions:")
    for action in actions:
        print(f"\n{action.role}:")
        print(f"  Current: {action.current_roster_count}, Required: {action.required_count}, Deficit: {action.deficit}")
        print(f"  Action: {action.action.value}")
        print(f"  Priority: {action.priority}")
        print(f"  Urgency Score: {action.urgency_score:.3f}")
        print(f"  Notes: {action.notes}")
        if action.source_dept:
            print(f"  Source Dept: {action.source_dept}")
        if action.target_personnel_ids:
            print(f"  Personnel IDs: {action.target_personnel_ids}")
    
    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    summary = optimizer.get_summary_statistics(actions)
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n✓ Staffing Optimizer test completed!")
