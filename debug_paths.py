"""
Debug script to check if paths are correct
"""
from pathlib import Path

# Simulate the path resolution from data_service.py
script_path = Path(__file__)
print(f"Script path: {script_path}")

# This is what data_service.py does
base_path = Path(__file__).parent / "media"
print(f"Base path (from script): {base_path}")
print(f"Base path exists: {base_path.exists()}")

# What it should be (from backend/app/services/)
backend_service_simulation = Path(__file__).parent / "backend" / "app" / "services" / "data_service.py"
print(f"\nSimulating from: {backend_service_simulation}")

# From backend/app/services/data_service.py, going up 4 levels
correct_base = Path(__file__).parent.parent.parent.parent.parent / "backend" / "app" / "services"
media_from_service = correct_base.parent.parent.parent / "media"
print(f"Media path from service: {media_from_service}")
print(f"Media exists: {media_from_service.exists()}")

# Check actual media folder
actual_media = Path(__file__).parent / "media"
print(f"\nActual media folder: {actual_media}")
print(f"Exists: {actual_media.exists()}")

if actual_media.exists():
    print(f"\nContents of media folder:")
    for item in actual_media.iterdir():
        print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
    
    data_path = actual_media / "data" / "hospital_data"
    print(f"\nData path: {data_path}")
    print(f"Data path exists: {data_path.exists()}")
    
    if data_path.exists():
        print(f"\nCSV files in hospital_data:")
        for csv_file in data_path.glob("*.csv"):
            print(f"  - {csv_file.name}")
