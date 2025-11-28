# Predictive Hospital Management System (Dhanvantari-AI)

## 🏥 Agentic AI Challenge
**Predictive Hospital Management During Festivals, Pollution Spikes, and Epidemics in India**

Healthcare centers in India face unpredictable surges in patients during major festivals (such as Diwali, Holi, Ganesh Chaturthi), seasonal pollution spikes (winter smog, crop burning seasons), or epidemics. These surges strain staffing, medical supplies, and facilities, leading to overcrowding and longer wait times.

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the pipeline
python Agent/run_pipeline.py
```

## 🧠 Adaptive Learning (New!)
Dhanvantari-AI now features a **Self-Correcting Feedback Loop**:
1.  **Monitors Performance**: Tracks "Forecast vs. Actual" accuracy.
2.  **Adjusts Safety Buffers**:
    *   *Too many patients?* → Increases safety stock for next time.
    *   *Too much waste?* → Reduces buffer to save costs.
3.  **Persists Knowledge**: Learns over time using `agent_memory.json`.

## 📂 Output Structure
All generated files are organized in the `media/` directory:

```
media/
├── data/
│   └── hospital_data/          # Synthetic datasets (CSV)
├── forecasts/
│   ├── csv/                    # Forecast results
│   └── visualizations/         # Graphs & charts
├── allocations/                # Resource directives (JSON)
└── pipeline_report.json        # Execution summary
```
