"""
Model Training Agent
Trains all 4 ML models and saves them as .pkl files.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class ModelTrainingAgent:
    """Agent responsible for training all ML models"""
    
    def __init__(self):
        self.status = "initialized"
        self.models_trained = []
        
    def train_all_models(self):
        """Train all 4 models and save to backend/models/"""
        print("\n[Model Training Agent] Starting model training pipeline...")
        
        start_time = datetime.now()
        results = {
            'status': 'in_progress',
            'models': {},
            'start_time': start_time.isoformat()
        }
        
        try:
            # Ensure output directories exist
            os.makedirs('backend/models', exist_ok=True)
            os.makedirs('media/data', exist_ok=True)
            os.makedirs('media/modal_train_data', exist_ok=True)
            
            # Step 1: Prepare training data
            print("\n[Step 1/5] Preparing training data...")
            prep_result = self._prepare_training_data()
            results['data_preparation'] = prep_result
            
            if prep_result['status'] != 'success':
                raise Exception("Data preparation failed")
            
            # Step 2: Train Model 1 - Patient Volume
            print("\n[Step 2/5] Training Patient Volume Forecaster...")
            model1_result = self._train_model1()
            results['models']['patient_volume'] = model1_result
            
            # Step 3: Train Model 2 - Department Distribution
            print("\n[Step 3/5] Training Department Distribution Predictor...")
            model2_result = self._train_model2()
            results['models']['department_distribution'] = model2_result
            
            # Step 4: Train Model 3 - Severity Classification
            print("\n[Step 4/5] Training Severity Classifier...")
            model3_result = self._train_model3()
            results['models']['severity_classification'] = model3_result
            
            # Step 5: Train Model 4 - Anomaly Detection
            print("\n[Step 5/5] Training Anomaly Detector...")
            model4_result = self._train_model4()
            results['models']['anomaly_detection'] = model4_result
            
            # Update status
            results['status'] = 'success'
            results['end_time'] = datetime.now().isoformat()
            results['duration_seconds'] = (datetime.now() - start_time).total_seconds()
            results['models_trained'] = len([m for m in results['models'].values() if m['status'] == 'success'])
            
            print(f"\n✓ Model training completed: {results['models_trained']}/4 models trained successfully")
            
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = str(e)
            print(f"\n✗ Model training failed: {str(e)}")
            
        return results
        
    def _prepare_training_data(self):
        """Prepare all training data"""
        try:
            from Data_Generator.prepare_training_data import prepare_training_data
            from Data_Generator.prepare_department_data import prepare_department_data
            from Data_Generator.prepare_severity_data import prepare_severity_data
            
            # Prepare Model 1 data
            print("  → Preparing patient volume data...")
            prepare_training_data()
            
            # Prepare Model 2 data
            print("  → Preparing department data...")
            prepare_department_data()
            
            # Prepare Model 3 data
            print("  → Preparing severity data...")
            prepare_severity_data()
            
            return {
                'status': 'success',
                'message': 'All training data prepared successfully'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
        
    def _train_model1(self):
        """Train Patient Volume Forecaster"""
        try:
            from Forecaster.train_patient_volume_model import PatientVolumeModelTrainer
            
            trainer = PatientVolumeModelTrainer(
                data_dir='media/modal_train_data',
                output_dir='backend'
            )
            trainer.train()
            
            return {
                'status': 'success',
                'model_file': 'backend/models/patient_volume_forecaster.pkl',
                'data_file': 'media/data/patient_volume_training_data.csv'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
            
    def _train_model2(self):
        """Train Department Distribution Predictor"""
        try:
            from Forecaster.train_department_model import DepartmentVolumeForecaster
            
            forecaster = DepartmentVolumeForecaster(
                data_path='media/modal_train_data/department_training_data.csv',
                output_dir='backend/models'
            )
            forecaster.train()
            
            return {
                'status': 'success',
                'model_file': 'backend/models/department_distribution_predictor.pkl'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
            
    def _train_model3(self):
        """Train Severity Classifier"""
        try:
            from Forecaster.train_severity_model import SeverityClassifier
            
            classifier = SeverityClassifier(
                data_path='media/modal_train_data/severity_training_data.csv',
                output_dir='backend/models'
            )
            classifier.train()
            
            return {
                'status': 'success',
                'model_file': 'backend/models/severity_classifier.pkl',
                'encoder_file': 'backend/models/severity_label_encoder.pkl'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
            
    def _train_model4(self):
        """Train Anomaly Detector"""
        try:
            from Forecaster.train_anomaly_model import AnomalyDetector
            
            detector = AnomalyDetector(
                data_path='media/modal_train_data/severity_training_data.csv',
                output_dir='backend/models'
            )
            detector.train()
            
            return {
                'status': 'success',
                'model_file': 'backend/models/anomaly_detector.pkl'
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
