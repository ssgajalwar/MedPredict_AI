'''Data Generator Agent
Wraps the Data_Generator functionality to generate synthetic hospital data
and output to the centralized media folder.
'''

import sys
import os
from datetime import datetime

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Data_Generator.hospital_data_generator import ComprehensiveHospitalDataGenerator


class DataGeneratorAgent:
    """Agent responsible for generating synthetic hospital data.

    The generated CSV files are stored under ``../media/hospital_data_csv``
    which is the central location used by all downstream agents.
    """

    def __init__(self, output_dir='media/hospital_data_csv'):
        self.output_dir = output_dir
        self.generator = None
        self.status = "initialized"

    def generate_data(self, start_date="2022-01-01", end_date="2024-11-22"):
        """Generate synthetic hospital data.

        Parameters
        ----------
        start_date: str
            Start date for data generation.
        end_date: str
            End date for data generation.
        """
        print("=" * 80)
        print(" " * 25 + "DATA GENERATOR AGENT")
        print(" " * 20 + "Synthetic Hospital Data Generation")
        print("=" * 80)
        try:
            print(f"\n[1/3] Initializing data generator...")
            print(f"  Date range: {start_date} to {end_date}")
            self.generator = ComprehensiveHospitalDataGenerator(start_date=start_date, end_date=end_date)

            print(f"\n[2/3] Generating hospital data...")
            self.generator.run_complete_generation()

            print(f"\n[3/3] Exporting data to media folder...")
            self.generator.export_data(output_dir=self.output_dir)

            self.status = "completed"
            result = {
                "status": "success",
                "output_dir": self.output_dir,
                "tables_generated": len(self.generator.data),
                "date_range": f"{start_date} to {end_date}",
                "message": "Hospital data generated successfully",
            }
            print("\n" + "=" * 80)
            print("[OK] DATA GENERATION COMPLETED SUCCESSFULLY!")
            print("=" * 80)
            print(f"  Output directory: {self.output_dir}")
            print(f"  Tables generated: {result['tables_generated']}")
            return result
        except Exception as e:
            self.status = "failed"
            print(f"\n[x] Error during data generation: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "error": str(e), "message": "Data generation failed"}

    def get_status(self):
        """Get current agent status."""
        return {"agent": "DataGeneratorAgent", "status": self.status, "output_dir": self.output_dir}


def run_data_generator_agent():
    """Standalone runner for Data Generator Agent."""
    agent = DataGeneratorAgent()
    result = agent.generate_data()
    return agent, result

if __name__ == "__main__":
    agent, result = run_data_generator_agent()
    print(f"\nAgent Status: {agent.get_status()}")
