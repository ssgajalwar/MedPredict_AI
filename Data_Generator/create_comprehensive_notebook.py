import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
data_dir = os.path.join(project_root, 'media', 'hospital_data_csv')

# Create comprehensive notebook with all correlation analyses
cells = []

# Title
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["# Comprehensive Hospital Data Analysis\n## Patient Correlations with All Data Sources"]
})

# Imports
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "import os\n",
        "import warnings\n",
        "warnings.filterwarnings('ignore')\n",
        "\n",
        "plt.style.use('seaborn-v0_8-whitegrid')\n",
        "sns.set_palette('husl')\n",
        "plt.rcParams['figure.figsize'] = (14, 6)\n",
        "print('Libraries loaded')"
    ]
})

# Load data
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## Load All Data"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        f"DATA_DIR = r'{data_dir}'\n",
        "print(f'Data Directory: {DATA_DIR}')\n",
        "\n",
        "locations = pd.read_csv(os.path.join(DATA_DIR, 'locations.csv'))\n",
        "hospitals = pd.read_csv(os.path.join(DATA_DIR, 'hospitals.csv'))\n",
        "departments = pd.read_csv(os.path.join(DATA_DIR, 'departments.csv'))\n",
        "staff = pd.read_csv(os.path.join(DATA_DIR, 'staff.csv'))\n",
        "weather = pd.read_csv(os.path.join(DATA_DIR, 'weather_data.csv'), parse_dates=['record_date'])\n",
        "aqi = pd.read_csv(os.path.join(DATA_DIR, 'air_quality_data.csv'), parse_dates=['record_date'])\n",
        "events = pd.read_csv(os.path.join(DATA_DIR, 'events.csv'), parse_dates=['start_date', 'end_date'])\n",
        "epidemic = pd.read_csv(os.path.join(DATA_DIR, 'epidemic_surveillance.csv'), parse_dates=['date'])\n",
        "visits = pd.read_csv(os.path.join(DATA_DIR, 'patient_visits.csv'), parse_dates=['visit_date'])\n",
        "diagnoses = pd.read_csv(os.path.join(DATA_DIR, 'diagnoses.csv'))\n",
        "staff_avail = pd.read_csv(os.path.join(DATA_DIR, 'staff_availability.csv'), parse_dates=['snapshot_date'])\n",
        "inventory = pd.read_csv(os.path.join(DATA_DIR, 'supply_inventory.csv'), parse_dates=['snapshot_date'])\n",
        "\n",
        "print(f'Loaded {len(visits):,} patient visits')\n",
        "print('All data loaded successfully!')"
    ]
})

# 1. Air Quality vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 1. Air Quality vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "daily_visits = visits.groupby('visit_date').size().reset_index(name='visit_count')\n",
        "daily_aqi = aqi.groupby('record_date')['aqi_level'].mean().reset_index()\n",
        "daily_aqi.columns = ['visit_date', 'aqi_level']\n",
        "aqi_patients = daily_visits.merge(daily_aqi, on='visit_date')\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "axes[0].scatter(aqi_patients['aqi_level'], aqi_patients['visit_count'], alpha=0.5, c='red')\n",
        "axes[0].set_title('Patient Visits vs AQI Level', fontsize=14, fontweight='bold')\n",
        "axes[0].set_xlabel('AQI Level')\n",
        "axes[0].set_ylabel('Daily Patient Visits')\n",
        "axes[0].grid(True, alpha=0.3)\n",
        "\n",
        "aqi_patients['month'] = pd.to_datetime(aqi_patients['visit_date']).dt.month\n",
        "monthly_data = aqi_patients.groupby('month').agg({'visit_count':'sum', 'aqi_level':'mean'})\n",
        "ax2 = axes[1]\n",
        "ax2.plot(monthly_data.index, monthly_data['visit_count'], 'b-o', label='Patients', linewidth=2)\n",
        "ax2.set_ylabel('Patient Visits', color='b')\n",
        "ax2.tick_params(axis='y', labelcolor='b')\n",
        "ax3 = ax2.twinx()\n",
        "ax3.plot(monthly_data.index, monthly_data['aqi_level'], 'r-s', label='AQI', linewidth=2)\n",
        "ax3.set_ylabel('AQI Level', color='r')\n",
        "ax3.tick_params(axis='y', labelcolor='r')\n",
        "ax2.set_title('Monthly Patients vs AQI', fontsize=14, fontweight='bold')\n",
        "ax2.set_xlabel('Month')\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "corr = aqi_patients[['visit_count', 'aqi_level']].corr().iloc[0,1]\n",
        "print(f'Correlation: {corr:.3f}')"
    ]
})

# 2. Department wise patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 2. Department-wise Patient Admissions"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "visits_dept = visits.merge(departments, on='department_id')\n",
        "dept_stats = visits_dept.groupby('department_name').agg({\n",
        "    'visit_id': 'count',\n",
        "    'admission_flag': 'sum'\n",
        "}).rename(columns={'visit_id': 'total_visits', 'admission_flag': 'admissions'})\n",
        "dept_stats['admission_rate'] = (dept_stats['admissions'] / dept_stats['total_visits'] * 100)\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "dept_stats.sort_values('total_visits', ascending=True).plot(kind='barh', y='total_visits', ax=axes[0], color='skyblue', legend=False)\n",
        "axes[0].set_title('Total Visits by Department', fontsize=14, fontweight='bold')\n",
        "axes[0].set_xlabel('Number of Visits')\n",
        "\n",
        "dept_stats.sort_values('admission_rate', ascending=True).plot(kind='barh', y='admission_rate', ax=axes[1], color='coral', legend=False)\n",
        "axes[1].set_title('Admission Rate by Department', fontsize=14, fontweight='bold')\n",
        "axes[1].set_xlabel('Admission Rate (%)')\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print(dept_stats.sort_values('total_visits', ascending=False))"
    ]
})

# 3. Disease wise patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 3. Disease-wise Patient Distribution"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "disease_counts = diagnoses['disease_name'].value_counts().head(15)\n",
        "visits_with_diag = visits.merge(diagnoses[diagnoses['is_primary']==True], on='visit_id')\n",
        "disease_severity = visits_with_diag.groupby('disease_name')['severity_level'].mean().sort_values(ascending=False).head(15)\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "disease_counts.plot(kind='barh', ax=axes[0], color='green', alpha=0.7)\n",
        "axes[0].set_title('Top 15 Diseases by Patient Count', fontsize=14, fontweight='bold')\n",
        "axes[0].set_xlabel('Number of Patients')\n",
        "\n",
        "disease_severity.plot(kind='barh', ax=axes[1], color='red', alpha=0.7)\n",
        "axes[1].set_title('Average Severity by Disease', fontsize=14, fontweight='bold')\n",
        "axes[1].set_xlabel('Average Severity Level')\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 4. Epidemic vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 4. Epidemic Surveillance vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "epidemic['month'] = epidemic['date'].dt.month\n",
        "visits['month'] = visits['visit_date'].dt.month\n",
        "monthly_epidemic = epidemic.groupby('month')['confirmed_cases'].sum()\n",
        "monthly_visits = visits.groupby('month').size()\n",
        "\n",
        "fig, ax1 = plt.subplots(figsize=(14, 6))\n",
        "ax1.bar(monthly_epidemic.index, monthly_visits, alpha=0.6, color='blue', label='Patient Visits')\n",
        "ax1.set_xlabel('Month')\n",
        "ax1.set_ylabel('Patient Visits', color='blue')\n",
        "ax1.tick_params(axis='y', labelcolor='blue')\n",
        "\n",
        "ax2 = ax1.twinx()\n",
        "ax2.plot(monthly_epidemic.index, monthly_epidemic.values, 'r-o', linewidth=2, markersize=8, label='Epidemic Cases')\n",
        "ax2.set_ylabel('Confirmed Epidemic Cases', color='red')\n",
        "ax2.tick_params(axis='y', labelcolor='red')\n",
        "plt.title('Patient Visits vs Epidemic Cases by Month', fontsize=14, fontweight='bold')\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 5. Events vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 5. Events vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "event_impact = []\n",
        "for _, event in events.iterrows():\n",
        "    event_visits = visits[(visits['visit_date'] >= event['start_date']) & (visits['visit_date'] <= event['end_date'])]\n",
        "    event_impact.append({'event_name': event['event_name'], 'event_type': event['event_type'], 'visits': len(event_visits), 'impact_multiplier': event['impact_multiplier']})\n",
        "\n",
        "event_df = pd.DataFrame(event_impact)\n",
        "event_summary = event_df.groupby('event_type').agg({'visits': 'sum', 'impact_multiplier': 'mean'}).sort_values('visits', ascending=False)\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "event_summary['visits'].plot(kind='bar', ax=axes[0], color='gold', alpha=0.7)\n",
        "axes[0].set_title('Patient Visits During Events by Type', fontsize=14, fontweight='bold')\n",
        "axes[0].set_ylabel('Total Visits')\n",
        "axes[0].set_xlabel('Event Type')\n",
        "axes[0].tick_params(axis='x', rotation=45)\n",
        "\n",
        "event_summary['impact_multiplier'].plot(kind='bar', ax=axes[1], color='crimson', alpha=0.7)\n",
        "axes[1].set_title('Average Impact Multiplier by Event Type', fontsize=14, fontweight='bold')\n",
        "axes[1].set_ylabel('Impact Multiplier')\n",
        "axes[1].set_xlabel('Event Type')\n",
        "axes[1].tick_params(axis='x', rotation=45)\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 6. Staff availability vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 6. Available Staff vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "daily_staff = staff_avail.groupby('snapshot_date').agg({'doctors_available': 'sum', 'nurses_available': 'sum'})\n",
        "daily_staff.columns = ['doctors', 'nurses']\n",
        "daily_staff = daily_staff.reset_index()\n",
        "daily_staff.columns = ['visit_date', 'doctors', 'nurses']\n",
        "staff_patients = daily_visits.merge(daily_staff, on='visit_date')\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "axes[0].scatter(staff_patients['doctors'], staff_patients['visit_count'], alpha=0.5, c='blue')\n",
        "axes[0].set_title('Patient Visits vs Available Doctors', fontsize=14, fontweight='bold')\n",
        "axes[0].set_xlabel('Available Doctors')\n",
        "axes[0].set_ylabel('Daily Patient Visits')\n",
        "axes[0].grid(True, alpha=0.3)\n",
        "\n",
        "axes[1].scatter(staff_patients['nurses'], staff_patients['visit_count'], alpha=0.5, c='green')\n",
        "axes[1].set_title('Patient Visits vs Available Nurses', fontsize=14, fontweight='bold')\n",
        "axes[1].set_xlabel('Available Nurses')\n",
        "axes[1].set_ylabel('Daily Patient Visits')\n",
        "axes[1].grid(True, alpha=0.3)\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 7. Required staff calculation
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 7. Available vs Required Staff"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "staff_patients['required_doctors'] = (staff_patients['visit_count'] / 50).apply(np.ceil)\n",
        "staff_patients['required_nurses'] = (staff_patients['visit_count'] / 20).apply(np.ceil)\n",
        "staff_patients['doctor_shortage'] = staff_patients['required_doctors'] - staff_patients['doctors']\n",
        "staff_patients['nurse_shortage'] = staff_patients['required_nurses'] - staff_patients['nurses']\n",
        "\n",
        "fig, axes = plt.subplots(2, 2, figsize=(16, 10))\n",
        "axes[0,0].plot(staff_patients['visit_date'], staff_patients['doctors'], label='Available', linewidth=2)\n",
        "axes[0,0].plot(staff_patients['visit_date'], staff_patients['required_doctors'], label='Required', linewidth=2, linestyle='--')\n",
        "axes[0,0].set_title('Doctors: Available vs Required', fontsize=14, fontweight='bold')\n",
        "axes[0,0].set_ylabel('Number of Doctors')\n",
        "axes[0,0].legend()\n",
        "axes[0,0].grid(True, alpha=0.3)\n",
        "\n",
        "axes[0,1].plot(staff_patients['visit_date'], staff_patients['nurses'], label='Available', linewidth=2)\n",
        "axes[0,1].plot(staff_patients['visit_date'], staff_patients['required_nurses'], label='Required', linewidth=2, linestyle='--')\n",
        "axes[0,1].set_title('Nurses: Available vs Required', fontsize=14, fontweight='bold')\n",
        "axes[0,1].set_ylabel('Number of Nurses')\n",
        "axes[0,1].legend()\n",
        "axes[0,1].grid(True, alpha=0.3)\n",
        "\n",
        "axes[1,0].hist(staff_patients['doctor_shortage'], bins=30, color='red', alpha=0.7, edgecolor='black')\n",
        "axes[1,0].set_title('Doctor Shortage Distribution', fontsize=14, fontweight='bold')\n",
        "axes[1,0].set_xlabel('Shortage (negative = surplus)')\n",
        "axes[1,0].axvline(0, color='black', linestyle='--', linewidth=2)\n",
        "\n",
        "axes[1,1].hist(staff_patients['nurse_shortage'], bins=30, color='orange', alpha=0.7, edgecolor='black')\n",
        "axes[1,1].set_title('Nurse Shortage Distribution', fontsize=14, fontweight='bold')\n",
        "axes[1,1].set_xlabel('Shortage (negative = surplus)')\n",
        "axes[1,1].axvline(0, color='black', linestyle='--', linewidth=2)\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print(f'Average doctor shortage: {staff_patients[\"doctor_shortage\"].mean():.1f}')\n",
        "print(f'Average nurse shortage: {staff_patients[\"nurse_shortage\"].mean():.1f}')"
    ]
})

# 8. Inventory vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 8. Supply Inventory vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "daily_inventory = inventory.groupby('snapshot_date')['qty_on_hand'].sum().reset_index()\n",
        "daily_inventory.columns = ['visit_date', 'total_inventory']\n",
        "inv_patients = daily_visits.merge(daily_inventory, on='visit_date')\n",
        "\n",
        "fig, ax1 = plt.subplots(figsize=(14, 6))\n",
        "ax1.plot(inv_patients['visit_date'], inv_patients['visit_count'], 'b-', linewidth=2, label='Patient Visits')\n",
        "ax1.set_xlabel('Date')\n",
        "ax1.set_ylabel('Patient Visits', color='b')\n",
        "ax1.tick_params(axis='y', labelcolor='b')\n",
        "\n",
        "ax2 = ax1.twinx()\n",
        "ax2.plot(inv_patients['visit_date'], inv_patients['total_inventory'], 'g-', linewidth=2, label='Total Inventory')\n",
        "ax2.set_ylabel('Total Inventory', color='g')\n",
        "ax2.tick_params(axis='y', labelcolor='g')\n",
        "plt.title('Patient Visits vs Total Inventory Over Time', fontsize=14, fontweight='bold')\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 9. Weather vs Patients
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 9. Weather Data vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "daily_weather = weather.groupby('record_date').agg({'temperature_avg': 'mean', 'rainfall_mm': 'mean', 'humidity_percent': 'mean'})\n",
        "daily_weather = daily_weather.reset_index()\n",
        "daily_weather.columns = ['visit_date', 'temperature', 'rainfall', 'humidity']\n",
        "weather_patients = daily_visits.merge(daily_weather, on='visit_date')\n",
        "\n",
        "fig, axes = plt.subplots(2, 2, figsize=(16, 10))\n",
        "axes[0,0].scatter(weather_patients['temperature'], weather_patients['visit_count'], alpha=0.5, c='orange')\n",
        "axes[0,0].set_title('Patients vs Temperature', fontsize=14, fontweight='bold')\n",
        "axes[0,0].set_xlabel('Temperature (°C)')\n",
        "axes[0,0].set_ylabel('Daily Visits')\n",
        "axes[0,0].grid(True, alpha=0.3)\n",
        "\n",
        "axes[0,1].scatter(weather_patients['rainfall'], weather_patients['visit_count'], alpha=0.5, c='blue')\n",
        "axes[0,1].set_title('Patients vs Rainfall', fontsize=14, fontweight='bold')\n",
        "axes[0,1].set_xlabel('Rainfall (mm)')\n",
        "axes[0,1].set_ylabel('Daily Visits')\n",
        "axes[0,1].grid(True, alpha=0.3)\n",
        "\n",
        "axes[1,0].scatter(weather_patients['humidity'], weather_patients['visit_count'], alpha=0.5, c='green')\n",
        "axes[1,0].set_title('Patients vs Humidity', fontsize=14, fontweight='bold')\n",
        "axes[1,0].set_xlabel('Humidity (%)')\n",
        "axes[1,0].set_ylabel('Daily Visits')\n",
        "axes[1,0].grid(True, alpha=0.3)\n",
        "\n",
        "corr_matrix = weather_patients[['visit_count', 'temperature', 'rainfall', 'humidity']].corr()\n",
        "sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=axes[1,1], fmt='.2f')\n",
        "axes[1,1].set_title('Correlation Matrix', fontsize=14, fontweight='bold')\n",
        "plt.tight_layout()\n",
        "plt.show()"
    ]
})

# 10. Required inventory
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 10. Available vs Required Inventory"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "inv_patients['required_inventory'] = inv_patients['visit_count'] * 5\n",
        "inv_patients['inventory_shortage'] = inv_patients['required_inventory'] - inv_patients['total_inventory']\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
        "axes[0].plot(inv_patients['visit_date'], inv_patients['total_inventory'], label='Available', linewidth=2)\n",
        "axes[0].plot(inv_patients['visit_date'], inv_patients['required_inventory'], label='Required', linewidth=2, linestyle='--')\n",
        "axes[0].set_title('Inventory: Available vs Required', fontsize=14, fontweight='bold')\n",
        "axes[0].set_ylabel('Total Inventory Units')\n",
        "axes[0].legend()\n",
        "axes[0].grid(True, alpha=0.3)\n",
        "\n",
        "axes[1].hist(inv_patients['inventory_shortage'], bins=30, color='purple', alpha=0.7, edgecolor='black')\n",
        "axes[1].set_title('Inventory Shortage Distribution', fontsize=14, fontweight='bold')\n",
        "axes[1].set_xlabel('Shortage (negative = surplus)')\n",
        "axes[1].axvline(0, color='black', linestyle='--', linewidth=2)\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "print(f'Average inventory shortage: {inv_patients[\"inventory_shortage\"].mean():.1f}')"
    ]
})

# 11. Combined dashboard
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": ["## 11. Combined Dashboard - All Factors vs Patient Visits"]
})

cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "combined = daily_visits.merge(daily_aqi, on='visit_date', how='left')\n",
        "combined = combined.merge(daily_weather, on='visit_date', how='left')\n",
        "combined = combined.merge(daily_staff, on='visit_date', how='left')\n",
        "combined = combined.merge(daily_inventory, on='visit_date', how='left')\n",
        "combined['month'] = pd.to_datetime(combined['visit_date']).dt.month\n",
        "\n",
        "monthly_combined = combined.groupby('month').agg({\n",
        "    'visit_count': 'sum',\n",
        "    'aqi_level': 'mean',\n",
        "    'temperature': 'mean',\n",
        "    'rainfall': 'sum',\n",
        "    'doctors': 'mean',\n",
        "    'nurses': 'mean',\n",
        "    'total_inventory': 'mean'\n",
        "})\n",
        "\n",
        "fig = plt.figure(figsize=(20, 12))\n",
        "gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)\n",
        "\n",
        "ax1 = fig.add_subplot(gs[0, :])\n",
        "ax1.plot(monthly_combined.index, monthly_combined['visit_count'], 'b-o', linewidth=3, markersize=10, label='Patient Visits')\n",
        "ax1.set_title('Monthly Patient Visits Trend', fontsize=16, fontweight='bold')\n",
        "ax1.set_ylabel('Total Visits', fontsize=12)\n",
        "ax1.grid(True, alpha=0.3)\n",
        "ax1.legend(fontsize=12)\n",
        "\n",
        "ax2 = fig.add_subplot(gs[1, 0])\n",
        "ax2.bar(monthly_combined.index, monthly_combined['aqi_level'], color='red', alpha=0.7)\n",
        "ax2.set_title('Average AQI', fontsize=14, fontweight='bold')\n",
        "ax2.set_ylabel('AQI Level')\n",
        "\n",
        "ax3 = fig.add_subplot(gs[1, 1])\n",
        "ax3.bar(monthly_combined.index, monthly_combined['temperature'], color='orange', alpha=0.7)\n",
        "ax3.set_title('Average Temperature', fontsize=14, fontweight='bold')\n",
        "ax3.set_ylabel('Temperature (°C)')\n",
        "\n",
        "ax4 = fig.add_subplot(gs[1, 2])\n",
        "ax4.bar(monthly_combined.index, monthly_combined['rainfall'], color='blue', alpha=0.7)\n",
        "ax4.set_title('Total Rainfall', fontsize=14, fontweight='bold')\n",
        "ax4.set_ylabel('Rainfall (mm)')\n",
        "\n",
        "ax5 = fig.add_subplot(gs[2, 0])\n",
        "ax5.plot(monthly_combined.index, monthly_combined['doctors'], 'g-o', linewidth=2, label='Doctors')\n",
        "ax5.plot(monthly_combined.index, monthly_combined['nurses'], 'b-s', linewidth=2, label='Nurses')\n",
        "ax5.set_title('Average Staff Availability', fontsize=14, fontweight='bold')\n",
        "ax5.set_ylabel('Staff Count')\n",
        "ax5.legend()\n",
        "\n",
        "ax6 = fig.add_subplot(gs[2, 1])\n",
        "ax6.bar(monthly_combined.index, monthly_combined['total_inventory'], color='purple', alpha=0.7)\n",
        "ax6.set_title('Average Inventory', fontsize=14, fontweight='bold')\n",
        "ax6.set_ylabel('Total Units')\n",
        "\n",
        "ax7 = fig.add_subplot(gs[2, 2])\n",
        "corr_data = combined[['visit_count', 'aqi_level', 'temperature', 'rainfall', 'doctors', 'nurses', 'total_inventory']].corr()\n",
        "sns.heatmap(corr_data, annot=True, cmap='coolwarm', center=0, ax=ax7, fmt='.2f', cbar_kws={'shrink': 0.8})\n",
        "ax7.set_title('Correlation Heatmap', fontsize=14, fontweight='bold')\n",
        "\n",
        "plt.suptitle('Comprehensive Hospital Analytics Dashboard', fontsize=18, fontweight='bold', y=0.995)\n",
        "plt.show()\n",
        "\n",
        "print('\\nKey Correlations with Patient Visits:')\n",
        "for col in ['aqi_level', 'temperature', 'rainfall', 'doctors', 'nurses', 'total_inventory']:\n",
        "    corr = combined[['visit_count', col]].corr().iloc[0,1]\n",
        "    print(f'{col}: {corr:.3f}')"
    ]
})

notebook_content = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.8.0"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

output_path = 'hospital_data_analysis.ipynb'
with open(output_path, 'w') as f:
    json.dump(notebook_content, f, indent=1)

print(f"Successfully created: {output_path}")
print(f"Data directory: {data_dir}")
print("\nNotebook includes:")
print("1. Air Quality vs Patients")
print("2. Department-wise Admissions")
print("3. Disease-wise Patients")
print("4. Epidemic vs Patients")
print("5. Events vs Patients")
print("6. Available Staff vs Patients")
print("7. Required vs Available Staff")
print("8. Inventory vs Patients")
print("9. Weather vs Patients")
print("10. Required vs Available Inventory")
print("11. Combined Dashboard with All Factors")
