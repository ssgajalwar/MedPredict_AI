"""
Resource Mapping Knowledge Base for Agent C: The Logistics Commander

This module defines the comprehensive mapping of medical conditions to required resources,
including staffing requirements and inventory needs.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum


class ConditionType(Enum):
    """Types of medical conditions/surges"""
    RESPIRATORY_SURGE = "respiratory_surge"
    BURN_TRAUMA = "burn_trauma"
    DENGUE_OUTBREAK = "dengue_outbreak"
    CARDIAC_EMERGENCY = "cardiac_emergency"
    TRAUMA_SURGE = "trauma_surge"
    INFECTIOUS_DISEASE = "infectious_disease"
    GENERAL_SURGE = "general_surge"


class StaffRole(Enum):
    """Medical staff roles"""
    PULMONOLOGIST = "pulmonologist"
    RESPIRATORY_THERAPIST = "respiratory_therapist"
    PLASTIC_SURGEON = "plastic_surgeon"
    TRIAGE_NURSE = "triage_nurse"
    PHLEBOTOMIST = "phlebotomist"
    GENERAL_PHYSICIAN = "general_physician"
    CARDIOLOGIST = "cardiologist"
    EMERGENCY_PHYSICIAN = "emergency_physician"
    ICU_NURSE = "icu_nurse"
    GENERAL_NURSE = "general_nurse"
    ANESTHETIST = "anesthetist"


@dataclass
class StaffingRequirement:
    """Staffing requirement for a condition"""
    role: StaffRole
    ratio: float  # Staff per N patients
    patients_per_staff: int  # N patients per 1 staff
    priority: str  # "critical", "high", "medium", "low"
    on_call_acceptable: bool = False


@dataclass
class InventoryRequirement:
    """Inventory requirement for a condition"""
    item_name: str
    sku: str
    units_per_patient: float  # Average consumption per patient
    unit_type: str  # "units", "kg", "liters", etc.
    priority: str  # "critical", "high", "medium", "low"
    lead_time_days: int  # Typical delivery time
    vendor_id: str


@dataclass
class ConditionMapping:
    """Complete resource mapping for a medical condition"""
    condition_type: ConditionType
    condition_name: str
    description: str
    staffing_requirements: List[StaffingRequirement]
    inventory_requirements: List[InventoryRequirement]
    typical_patient_volume_multiplier: float = 1.0


class ResourceMappingKB:
    """
    Knowledge Base for Resource Mapping
    
    This class maintains the comprehensive mapping of medical conditions
    to their required resources (staffing and inventory).
    """
    
    def __init__(self):
        self.mappings: Dict[ConditionType, ConditionMapping] = {}
        self._initialize_mappings()
    
    def _initialize_mappings(self):
        """Initialize all condition-to-resource mappings"""
        
        # 1. RESPIRATORY SURGE (Smog/Air Quality Related)
        self.mappings[ConditionType.RESPIRATORY_SURGE] = ConditionMapping(
            condition_type=ConditionType.RESPIRATORY_SURGE,
            condition_name="Respiratory Surge",
            description="Surge in respiratory conditions due to air pollution/smog",
            staffing_requirements=[
                StaffingRequirement(
                    role=StaffRole.PULMONOLOGIST,
                    ratio=0.05,  # 1 per 20 patients
                    patients_per_staff=20,
                    priority="high",
                    on_call_acceptable=True
                ),
                StaffingRequirement(
                    role=StaffRole.RESPIRATORY_THERAPIST,
                    ratio=0.1,  # 1 per 10 patients
                    patients_per_staff=10,
                    priority="critical",
                    on_call_acceptable=False
                ),
                StaffingRequirement(
                    role=StaffRole.GENERAL_NURSE,
                    ratio=0.25,  # 1 per 4 patients
                    patients_per_staff=4,
                    priority="critical",
                    on_call_acceptable=False
                )
            ],
            inventory_requirements=[
                InventoryRequirement(
                    item_name="Nebulizer Masks",
                    sku="MED-NEB-001",
                    units_per_patient=2.0,
                    unit_type="units",
                    priority="critical",
                    lead_time_days=1,
                    vendor_id="MEDEQUIP_A"
                ),
                InventoryRequirement(
                    item_name="Albuterol Sulfate Inhalation Solution",
                    sku="MED-ALB-500",
                    units_per_patient=3.0,
                    unit_type="vials",
                    priority="critical",
                    lead_time_days=2,
                    vendor_id="PHARMA_CORP_A"
                ),
                InventoryRequirement(
                    item_name="Oxygen Cylinders (Type D)",
                    sku="MED-OXY-D",
                    units_per_patient=0.5,
                    unit_type="cylinders",
                    priority="critical",
                    lead_time_days=2,
                    vendor_id="MEDGAS_SUPPLY"
                ),
                InventoryRequirement(
                    item_name="N95 Respirator Masks",
                    sku="PPE-N95-001",
                    units_per_patient=5.0,
                    unit_type="masks",
                    priority="high",
                    lead_time_days=1,
                    vendor_id="PPE_DIRECT"
                ),
                InventoryRequirement(
                    item_name="Pulse Oximeters",
                    sku="MED-PULOX-01",
                    units_per_patient=0.1,
                    unit_type="units",
                    priority="medium",
                    lead_time_days=3,
                    vendor_id="MEDEQUIP_A"
                )
            ],
            typical_patient_volume_multiplier=1.3
        )
        
        # 2. BURN TRAUMA (Festival/Diwali Related)
        self.mappings[ConditionType.BURN_TRAUMA] = ConditionMapping(
            condition_type=ConditionType.BURN_TRAUMA,
            condition_name="Burn Trauma Surge",
            description="Surge in burn injuries during festivals (Diwali)",
            staffing_requirements=[
                StaffingRequirement(
                    role=StaffRole.PLASTIC_SURGEON,
                    ratio=0.1,  # 1 per 10 critical cases
                    patients_per_staff=10,
                    priority="critical",
                    on_call_acceptable=True
                ),
                StaffingRequirement(
                    role=StaffRole.TRIAGE_NURSE,
                    ratio=0.4,  # 2 per 5 critical cases
                    patients_per_staff=5,
                    priority="critical",
                    on_call_acceptable=False
                ),
                StaffingRequirement(
                    role=StaffRole.ANESTHETIST,
                    ratio=0.05,
                    patients_per_staff=20,
                    priority="high",
                    on_call_acceptable=True
                )
            ],
            inventory_requirements=[
                InventoryRequirement(
                    item_name="Silver Sulfadiazine Cream 500g",
                    sku="MED-SSD-500",
                    units_per_patient=1.5,
                    unit_type="tubes",
                    priority="critical",
                    lead_time_days=2,
                    vendor_id="PHARMA_CORP_A"
                ),
                InventoryRequirement(
                    item_name="Sterile Gauze Pads (4x4)",
                    sku="MED-GAU-44",
                    units_per_patient=20.0,
                    unit_type="pads",
                    priority="critical",
                    lead_time_days=1,
                    vendor_id="SURGICAL_SUPPLY"
                ),
                InventoryRequirement(
                    item_name="IV Fluids - Lactated Ringer's 1L",
                    sku="MED-LR-1000",
                    units_per_patient=3.0,
                    unit_type="bags",
                    priority="critical",
                    lead_time_days=1,
                    vendor_id="PHARMA_CORP_B"
                ),
                InventoryRequirement(
                    item_name="Burn Dressing Kits",
                    sku="MED-BURN-KIT",
                    units_per_patient=2.0,
                    unit_type="kits",
                    priority="high",
                    lead_time_days=2,
                    vendor_id="SURGICAL_SUPPLY"
                ),
                InventoryRequirement(
                    item_name="Morphine Sulfate 10mg/ml",
                    sku="MED-MOR-10",
                    units_per_patient=2.0,
                    unit_type="vials",
                    priority="high",
                    lead_time_days=3,
                    vendor_id="PHARMA_CORP_A"
                )
            ],
            typical_patient_volume_multiplier=1.5
        )
        
        # 3. DENGUE OUTBREAK
        self.mappings[ConditionType.DENGUE_OUTBREAK] = ConditionMapping(
            condition_type=ConditionType.DENGUE_OUTBREAK,
            condition_name="Dengue Outbreak",
            description="Dengue fever outbreak during monsoon season",
            staffing_requirements=[
                StaffingRequirement(
                    role=StaffRole.PHLEBOTOMIST,
                    ratio=0.1,  # 1 per 10 patients (for blood collection)
                    patients_per_staff=10,
                    priority="high",
                    on_call_acceptable=False
                ),
                StaffingRequirement(
                    role=StaffRole.GENERAL_PHYSICIAN,
                    ratio=0.05,  # 1 per 20 patients
                    patients_per_staff=20,
                    priority="high",
                    on_call_acceptable=True
                ),
                StaffingRequirement(
                    role=StaffRole.GENERAL_NURSE,
                    ratio=0.2,  # 1 per 5 patients
                    patients_per_staff=5,
                    priority="high",
                    on_call_acceptable=False
                )
            ],
            inventory_requirements=[
                InventoryRequirement(
                    item_name="Platelet Concentrate Kits",
                    sku="MED-PLT-KIT",
                    units_per_patient=0.3,  # Not all patients need
                    unit_type="units",
                    priority="critical",
                    lead_time_days=1,
                    vendor_id="BLOOD_BANK"
                ),
                InventoryRequirement(
                    item_name="IV Paracetamol 1g/100ml",
                    sku="MED-PARA-IV",
                    units_per_patient=4.0,
                    unit_type="vials",
                    priority="high",
                    lead_time_days=2,
                    vendor_id="PHARMA_CORP_B"
                ),
                InventoryRequirement(
                    item_name="NS1 Dengue Antigen Test Kits",
                    sku="LAB-DEN-NS1",
                    units_per_patient=1.0,
                    unit_type="kits",
                    priority="high",
                    lead_time_days=2,
                    vendor_id="LAB_DIAGNOSTICS"
                ),
                InventoryRequirement(
                    item_name="Mosquito Nets (Hospital Grade)",
                    sku="PPE-MOSQ-NET",
                    units_per_patient=0.5,
                    unit_type="nets",
                    priority="medium",
                    lead_time_days=3,
                    vendor_id="PPE_DIRECT"
                ),
                InventoryRequirement(
                    item_name="IV Saline 0.9% 1L",
                    sku="MED-SAL-1000",
                    units_per_patient=5.0,
                    unit_type="bags",
                    priority="high",
                    lead_time_days=1,
                    vendor_id="PHARMA_CORP_B"
                )
            ],
            typical_patient_volume_multiplier=1.4
        )
        
        # 4. GENERAL SURGE (Default/Fallback)
        self.mappings[ConditionType.GENERAL_SURGE] = ConditionMapping(
            condition_type=ConditionType.GENERAL_SURGE,
            condition_name="General Patient Surge",
            description="General increase in patient volume",
            staffing_requirements=[
                StaffingRequirement(
                    role=StaffRole.GENERAL_PHYSICIAN,
                    ratio=0.05,
                    patients_per_staff=20,
                    priority="high",
                    on_call_acceptable=True
                ),
                StaffingRequirement(
                    role=StaffRole.GENERAL_NURSE,
                    ratio=0.25,
                    patients_per_staff=4,
                    priority="high",
                    on_call_acceptable=False
                )
            ],
            inventory_requirements=[
                InventoryRequirement(
                    item_name="Disposable Syringes 5ml",
                    sku="MED-SYR-5",
                    units_per_patient=3.0,
                    unit_type="syringes",
                    priority="medium",
                    lead_time_days=1,
                    vendor_id="SURGICAL_SUPPLY"
                ),
                InventoryRequirement(
                    item_name="Surgical Gloves (Latex)",
                    sku="PPE-GLV-LAT",
                    units_per_patient=10.0,
                    unit_type="pairs",
                    priority="medium",
                    lead_time_days=1,
                    vendor_id="PPE_DIRECT"
                ),
                InventoryRequirement(
                    item_name="IV Cannula 20G",
                    sku="MED-CAN-20",
                    units_per_patient=1.0,
                    unit_type="units",
                    priority="medium",
                    lead_time_days=2,
                    vendor_id="SURGICAL_SUPPLY"
                )
            ],
            typical_patient_volume_multiplier=1.0
        )
    
    def get_mapping(self, condition_type: ConditionType) -> ConditionMapping:
        """Get resource mapping for a specific condition"""
        return self.mappings.get(condition_type, self.mappings[ConditionType.GENERAL_SURGE])
    
    def get_all_mappings(self) -> Dict[ConditionType, ConditionMapping]:
        """Get all resource mappings"""
        return self.mappings
    
    def detect_condition_from_context(self, context: Dict) -> ConditionType:
        """
        Detect the most likely condition type from contextual data
        
        Parameters:
        - context: Dict with keys like 'aqi', 'event_type', 'season', 'epidemic_alert'
        
        Returns:
        - ConditionType enum value
        """
        # Check for respiratory surge (high AQI)
        if context.get('aqi', 0) > 150:
            return ConditionType.RESPIRATORY_SURGE
        
        # Check for burn trauma (festival events)
        if context.get('event_type') in ['festival', 'diwali', 'holi']:
            return ConditionType.BURN_TRAUMA
        
        # Check for dengue (monsoon + epidemic alert)
        if context.get('season') == 'monsoon' and context.get('epidemic_alert', 0) > 0:
            if context.get('disease_name', '').lower() in ['dengue', 'dengue fever']:
                return ConditionType.DENGUE_OUTBREAK
        
        # Default to general surge
        return ConditionType.GENERAL_SURGE
    
    def calculate_total_requirements(self, condition_type: ConditionType, 
                                     predicted_patients: int) -> Tuple[Dict, Dict]:
        """
        Calculate total staffing and inventory requirements
        
        Parameters:
        - condition_type: Type of medical condition
        - predicted_patients: Number of patients predicted
        
        Returns:
        - Tuple of (staffing_dict, inventory_dict)
        """
        mapping = self.get_mapping(condition_type)
        
        # Calculate staffing requirements
        staffing_requirements = {}
        for staff_req in mapping.staffing_requirements:
            required_count = int(predicted_patients * staff_req.ratio) + 1  # Round up
            staffing_requirements[staff_req.role.value] = {
                'required_count': required_count,
                'ratio': staff_req.ratio,
                'patients_per_staff': staff_req.patients_per_staff,
                'priority': staff_req.priority,
                'on_call_acceptable': staff_req.on_call_acceptable
            }
        
        # Calculate inventory requirements
        inventory_requirements = {}
        for inv_req in mapping.inventory_requirements:
            required_units = int(predicted_patients * inv_req.units_per_patient) + 1
            inventory_requirements[inv_req.sku] = {
                'item_name': inv_req.item_name,
                'required_units': required_units,
                'units_per_patient': inv_req.units_per_patient,
                'unit_type': inv_req.unit_type,
                'priority': inv_req.priority,
                'lead_time_days': inv_req.lead_time_days,
                'vendor_id': inv_req.vendor_id
            }
        
        return staffing_requirements, inventory_requirements


# Global instance
resource_kb = ResourceMappingKB()


if __name__ == "__main__":
    # Test the knowledge base
    print("=" * 60)
    print("RESOURCE MAPPING KNOWLEDGE BASE TEST")
    print("=" * 60)
    
    kb = ResourceMappingKB()
    
    # Test scenario: 100 respiratory patients
    print("\nScenario: 100 Respiratory Surge Patients")
    print("-" * 60)
    staffing, inventory = kb.calculate_total_requirements(
        ConditionType.RESPIRATORY_SURGE, 100
    )
    
    print("\nStaffing Requirements:")
    for role, req in staffing.items():
        print(f"  {role}: {req['required_count']} staff (1 per {req['patients_per_staff']} patients)")
    
    print("\nInventory Requirements:")
    for sku, req in inventory.items():
        print(f"  {req['item_name']}: {req['required_units']} {req['unit_type']}")
    
    # Test condition detection
    print("\n" + "=" * 60)
    print("CONDITION DETECTION TEST")
    print("=" * 60)
    
    context1 = {'aqi': 200, 'season': 'winter'}
    detected1 = kb.detect_condition_from_context(context1)
    print(f"\nContext: {context1}")
    print(f"Detected: {detected1.value}")
    
    context2 = {'event_type': 'diwali', 'aqi': 100}
    detected2 = kb.detect_condition_from_context(context2)
    print(f"\nContext: {context2}")
    print(f"Detected: {detected2.value}")
    
    print("\n✓ Knowledge Base test completed!")
