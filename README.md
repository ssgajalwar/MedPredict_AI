# MedPredict AI - Hospital Patient Volume Forecasting System

## Overview
MedPredict AI is a comprehensive hospital management and forecasting system that uses machine learning to predict patient volumes, optimize resource allocation, and provide actionable insights for healthcare facilities.

## Project Structure

```
MedPredict_AI/
├── backend/                          # Backend API System
│   ├── api/
│   │   ├── unified_api.py           # Main FastAPI application
│   │   └── routers/                 # API endpoint routers
│   │       ├── dashboard.py         # Dashboard endpoints
│   │       ├── analytics.py         # Analytics endpoints
│   │       ├── forecast.py          # Forecasting endpoints
│   │       └── departments.py       # Department endpoints
│   ├── services/                    # Service layers for ML models
│   │   ├── model1_service.py        # Patient Volume Forecasting
│   │   ├── model2_service.py        # Department Distribution
│   │   ├── model3_service.py        # Severity Classification
│   │   ├── model4_service.py        # Anomaly Detection
│   │   └── dashboard_service.py     # Dashboard Aggregator
│   ├── models/                      # Trained ML models (.pkl files)
│   │   ├── patient_volume_forecaster.pkl
│   │   ├── department_distribution_predictor.pkl
│   │   ├── severity_classifier.pkl
│   │   ├── severity_label_encoder.pkl
│   │   └── anomaly_detector.pkl
│   └── data/                        # Training and reference data
│       ├── patient_volume_training_data.csv
│       ├── department_training_data.csv
│       ├── severity_training_data.csv
│       └── events.csv
│
├── frontend/                        # React Frontend Application
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── api/                    # API client
│   │   └── assets/                 # Static assets
│   └── package.json
│
├── Data_Generator/                  # Data Generation Scripts
│   ├── hospital_data_generator.py  # Main data generator
│   ├── prepare_training_data.py    # Model 1 data preparation
│   ├── prepare_department_data.py  # Model 2 data preparation
│   └── prepare_severity_data.py    # Model 3 data preparation
│
├── Forecaster/                      # Model Training Scripts
│   ├── train_patient_volume_model.py
│   ├── train_department_model.py
│   ├── train_severity_model.py
│   └── train_anomaly_model.py
│
├── media/                           # Generated Data Storage
│   ├── hospital_data_csv/          # Raw generated data
│   └── modal_train_data/           # Prepared training data
│
├── docs/                            # Documentation
│   ├── Forecaster_README.md
│   ├── Agent_README.md
│   └── Resource_Allocator_README.md
│
├── test_unified_api.py             # API test script
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## Machine Learning Models

### Model 1: Patient Volume Forecasting
- **File**: `backend/models/patient_volume_forecaster.pkl`
- **Purpose**: Predicts daily total patient volume
- **Algorithm**: XGBoost Regressor
- **Performance**: MAE: 16.61, R²: 0.65

### Model 2: Department-wise Distribution
- **File**: `backend/models/department_distribution_predictor.pkl`
- **Purpose**: Predicts patient volume for each of 13 departments
- **Algorithm**: MultiOutput RandomForest Regressor
- **Departments**: Emergency, Cardiology, Orthopedics, Pediatrics, OB/GYN, ICU, Surgery, Internal Medicine, Respiratory, Neurology, ENT, Radiology, Lab

### Model 3: Severity Classification
- **Files**: 
  - `backend/models/severity_classifier.pkl`
  - `backend/models/severity_label_encoder.pkl`
- **Purpose**: Classifies daily alert levels (Normal/Alert/Critical)
- **Algorithm**: RandomForest Classifier
- **Performance**: Accuracy: 0.97

### Model 4: Anomaly Detection
- **File**: `backend/models/anomaly_detector.pkl`
- **Purpose**: Detects unusual spikes or patterns in hospital data
- **Algorithm**: Isolation Forest
- **Contamination**: 5%

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Virtual environment (recommended)

### Backend Setup

1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start API Server**:
   ```bash
   python -m uvicorn backend.api.unified_api:app --host 0.0.0.0 --port 8000
   ```

4. **Access API Documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to Frontend**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

4. **Access Frontend**:
   - URL: http://localhost:5173

## API Endpoints

### Dashboard
- `GET /api/v1/dashboard/overview` - Complete dashboard with all metrics

### Analytics
- `GET /api/v1/analytics/surge-patterns` - Festival and epidemic surge analysis
- `GET /api/v1/analytics/department-trends` - Department utilization trends
- `GET /api/v1/analytics/admission-predictions` - 7-day admission forecast
- `GET /api/v1/analytics/environmental-impact` - AQI, weather, health advisory

### Forecast (Model 1)
- `GET /api/v1/forecast/predict` - Custom date range predictions
- `GET /api/v1/forecast/quick?days=N` - Quick N-day forecast

### Departments (Model 2)
- `GET /api/v1/departments/utilization` - Current department utilization

## Data Generation

### Generate Hospital Data
```bash
python Data_Generator/hospital_data_generator.py
```

### Prepare Training Data
```bash
# Model 1 - Patient Volume
python Data_Generator/prepare_training_data.py

# Model 2 - Departments
python Data_Generator/prepare_department_data.py

# Model 3 - Severity
python Data_Generator/prepare_severity_data.py
```

## Model Training

```bash
# Train Model 1 - Patient Volume
python Forecaster/train_patient_volume_model.py

# Train Model 2 - Departments
python Forecaster/train_department_model.py

# Train Model 3 - Severity
python Forecaster/train_severity_model.py

# Train Model 4 - Anomaly Detection
python Forecaster/train_anomaly_model.py
```

## Testing

### Test API Endpoints
```bash
python test_unified_api.py
```

This will test all 10+ API endpoints and provide a comprehensive report.

## Features

### Backend
- ✅ 4 ML models integrated
- ✅ RESTful API with FastAPI
- ✅ Automatic API documentation
- ✅ CORS enabled for frontend
- ✅ Modular service architecture
- ✅ Comprehensive error handling

### Frontend
- ✅ React with Vite
- ✅ TailwindCSS styling
- ✅ Interactive charts (Recharts)
- ✅ Real-time data visualization
- ✅ Responsive design
- ✅ Dashboard, Analytics, Reports

### Data & Models
- ✅ Synthetic data generation
- ✅ Feature engineering
- ✅ Model training scripts
- ✅ Model persistence (.pkl)
- ✅ Historical data management

## Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
```

### CORS Settings
Update `backend/api/unified_api.py` to add allowed origins:
```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

## Documentation

- **API Documentation**: http://localhost:8000/docs
- **Forecaster Guide**: `docs/Forecaster_README.md`
- **Agent Guide**: `docs/Agent_README.md`
- **Resource Allocator**: `docs/Resource_Allocator_README.md`

## Development

### Project Workflow
1. Generate synthetic data
2. Prepare training data
3. Train models
4. Start backend API
5. Start frontend
6. Test integration

### Adding New Models
1. Create service in `backend/services/`
2. Create router in `backend/api/routers/`
3. Register router in `unified_api.py`
4. Update frontend API client

## Troubleshooting

### Backend Issues
- **Models not found**: Ensure PKL files are in `backend/models/`
- **Data not found**: Ensure CSV files are in `backend/data/`
- **Import errors**: Check Python path and virtual environment

### Frontend Issues
- **API connection failed**: Verify backend is running on port 8000
- **CORS errors**: Check CORS settings in `unified_api.py`
- **Build errors**: Delete `node_modules` and run `npm install`

## Technology Stack

### Backend
- Python 3.8+
- FastAPI
- scikit-learn
- XGBoost
- pandas, numpy
- uvicorn

### Frontend
- React 18
- Vite
- TailwindCSS
- Recharts
- Axios

## License
MIT License

## Contributors
- MedPredict AI Team

## Support
For issues and questions, please check the documentation in the `docs/` folder.
