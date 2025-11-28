"""
Test data service directly
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.data_service import data_service
from app.services.allocation_service import allocation_service
from app.services.forecast_service import forecast_service

print("="*80)
print("TESTING DATA SERVICE")
print("="*80)

print(f"\nBase path: {data_service.base_path}")
print(f"Base path exists: {data_service.base_path.exists()}")
print(f"Data path: {data_service.data_path}")
print(f"Data path exists: {data_service.data_path.exists()}")

print("\n" + "="*80)
print("TESTING get_latest_patient_data()")
print("="*80)
patient_data = data_service.get_latest_patient_data()
print(f"Result: {patient_data}")

print("\n" + "="*80)
print("TESTING get_staff_data()")
print("="*80)
staff_data = data_service.get_staff_data()
print(f"Result: {staff_data}")

print("\n" + "="*80)
print("TESTING get_inventory_data()")
print("="*80)
inventory_data = data_service.get_inventory_data()
print(f"Result: {inventory_data}")

print("\n" + "="*80)
print("TESTING get_events_data()")
print("="*80)
events_data = data_service.get_events_data()
print(f"Result: {events_data[:2] if events_data else 'No events'}")

print("\n" + "="*80)
print("TESTING allocation_service.get_latest_allocation()")
print("="*80)
allocation_data = allocation_service.get_latest_allocation()
print(f"Result: {allocation_data}")

print("\n" + "="*80)
print("TESTING forecast_service.get_latest_forecast()")
print("="*80)
forecast_data = forecast_service.get_latest_forecast()
print(f"Result: {forecast_data}")
