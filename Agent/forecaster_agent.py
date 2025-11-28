'''Forecaster Agent
Wraps the Forecaster functionality to run all 3 forecasting models
and output results to the centralized media folder.
'''

import sys
import os

# Ensure project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Forecaster.modals.lightgbm_forecast import run_lightgbm_forecast
from Forecaster.modals.xgboost_forecast import run_xgboost_forecast
from Forecaster.modals.random_forest_forecast import run_random_forest_forecast


class ForecasterAgent:
    """Agent responsible for running forecasting models.

    Data is read from ``../media/hospital_data_csv`` and all output
    (CSV files and visualisations) is stored under ``../media/forecast``.
    """

    def __init__(self, data_dir='media/hospital_data_csv', output_dir='media/forecast'):
        self.data_dir = data_dir
        self.output_dir = output_dir
        # Sub‑folders for organised output
        self.csv_dir = os.path.join(self.output_dir, 'csv')
        self.viz_dir = os.path.join(self.output_dir, 'visualizations')
        self.status = "initialized"
        self.results = {}

    def run_forecasts(self, target_column='total_patients', horizon_days=7):
        """Run all three forecasting models.

        Parameters
        ----------
        target_column: str
            Column to forecast.
        horizon_days: int
            Forecast horizon in days.
        """
        print("=" * 80)
        print(" " * 28 + "FORECASTER AGENT")
        print(" " * 20 + "Multi-Model Demand Forecasting")
        print("=" * 80)
        try:
            # Ensure output directories exist
            os.makedirs(self.csv_dir, exist_ok=True)
            os.makedirs(self.viz_dir, exist_ok=True)

            print(f"\nTarget: {target_column}")
            print(f"Horizon: {horizon_days} days")
            print(f"Data source: {self.data_dir}")
            print(f"Output: {self.output_dir}")

            # LightGBM ---------------------------------------------------
            print("\n" + "#" * 80)
            print("# MODEL 1: LightGBM")
            print("#" * 80)
            try:
                lgb_forecaster, lgb_forecast = run_lightgbm_forecast(
                    target_column=target_column,
                    horizon_days=horizon_days,
                    data_dir=self.data_dir,
                    output_dir=self.output_dir,
                )
                self.results['lightgbm'] = {'status': 'success', 'forecaster': lgb_forecaster}
                self._organize_output_files('lightgbm', horizon_days)
            except Exception as e:
                print(f"[x] LightGBM failed: {e}")
                self.results['lightgbm'] = {'status': 'failed', 'error': str(e)}

            # XGBoost ---------------------------------------------------
            print("\n" + "#" * 80)
            print("# MODEL 2: XGBoost")
            print("#" * 80)
            try:
                xgb_forecaster, xgb_forecast = run_xgboost_forecast(
                    target_column=target_column,
                    horizon_days=horizon_days,
                    data_dir=self.data_dir,
                    output_dir=self.output_dir,
                )
                self.results['xgboost'] = {'status': 'success', 'forecaster': xgb_forecaster}
                self._organize_output_files('xgboost', horizon_days)
            except Exception as e:
                print(f"[x] XGBoost failed: {e}")
                self.results['xgboost'] = {'status': 'failed', 'error': str(e)}

            # Random Forest --------------------------------------------
            print("\n" + "#" * 80)
            print("# MODEL 3: Random Forest")
            print("#" * 80)
            try:
                rf_forecaster, rf_forecast = run_random_forest_forecast(
                    target_column=target_column,
                    horizon_days=horizon_days,
                    data_dir=self.data_dir,
                    output_dir=self.output_dir,
                )
                self.results['random_forest'] = {'status': 'success', 'forecaster': rf_forecaster}
                self._organize_output_files('random_forest', horizon_days)
            except Exception as e:
                print(f"[x] Random Forest failed: {e}")
                self.results['random_forest'] = {'status': 'failed', 'error': str(e)}

            self.status = "completed"
            successful_models = sum(1 for r in self.results.values() if r['status'] == 'success')
            result = {
                "status": "success" if successful_models > 0 else "failed",
                "models_run": len(self.results),
                "models_successful": successful_models,
                "output_dir": self.output_dir,
                "target_column": target_column,
                "horizon_days": horizon_days,
                "message": f"{successful_models}/{len(self.results)} models completed successfully",
            }
            print("\n" + "=" * 80)
            print("[OK] FORECASTING COMPLETED!")
            print("=" * 80)
            print(f"  Models successful: {successful_models}/{len(self.results)}")
            print(f"  Output directory: {self.output_dir}")
            return result
        except Exception as e:
            self.status = "failed"
            print(f"\n[x] Error during forecasting: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "failed", "error": str(e), "message": "Forecasting failed"}

    def _organize_output_files(self, model_name, horizon_days):
        """Move generated CSV and PNG files into organised sub‑folders."""
        import shutil
        # CSV ----------------------------------------------------------
        csv_file = f"{model_name}_forecast_{horizon_days}day.csv"
        src_csv = os.path.join(self.output_dir, csv_file)
        dst_csv = os.path.join(self.csv_dir, csv_file)
        if os.path.exists(src_csv):
            shutil.move(src_csv, dst_csv)
        # PNG ----------------------------------------------------------
        for suffix in ['forecast', 'actual_vs_predicted', 'feature_importance', 'residuals']:
            png_file = f"{model_name}_{suffix}_{horizon_days}day.png" if suffix == 'forecast' else f"{model_name}_{suffix}.png"
            src_png = os.path.join(self.output_dir, png_file)
            dst_png = os.path.join(self.viz_dir, png_file)
            if os.path.exists(src_png):
                shutil.move(src_png, dst_png)

    def get_status(self):
        """Return a concise status dictionary for the agent."""
        return {
            "agent": "ForecasterAgent",
            "status": self.status,
            "output_dir": self.output_dir,
            "results": {k: v['status'] for k, v in self.results.items()},
        }


def run_forecaster_agent():
    """Standalone runner for the Forecaster Agent."""
    agent = ForecasterAgent()
    result = agent.run_forecasts()
    return agent, result

if __name__ == "__main__":
    agent, result = run_forecaster_agent()
    print(f"\nAgent Status: {agent.get_status()}")
