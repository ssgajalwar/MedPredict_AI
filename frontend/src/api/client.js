const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const fetchDashboardOverview = async () => {
    const response = await fetch(`${API_BASE_URL}/dashboard/overview`);
    if (!response.ok) throw new Error('Failed to fetch dashboard data');
    return response.json();
};

export const fetchPatientHistory = async (days = 30) => {
    const response = await fetch(`${API_BASE_URL}/dashboard/history?days=${days}`);
    if (!response.ok) throw new Error('Failed to fetch patient history');
    return response.json();
};

export const fetchResourceStatus = async () => {
    const response = await fetch(`${API_BASE_URL}/resources/status`);
    if (!response.ok) throw new Error('Failed to fetch resource status');
    return response.json();
};

export const beautifyBroadcast = async (draftText) => {
    const response = await fetch(`${API_BASE_URL}/broadcast/beautify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft_text: draftText }),
    });
    if (!response.ok) throw new Error('Failed to beautify text');
    return response.json();
};

export const sendBroadcast = async (draftText) => {
    const response = await fetch(`${API_BASE_URL}/broadcast/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft_text: draftText }),
    });
    if (!response.ok) throw new Error('Failed to send broadcast');
    return response.json();
};

// Analytics API
export const fetchSurgePatterns = async () => {
    const response = await fetch(`${API_BASE_URL}/analytics/surge-patterns`);
    if (!response.ok) throw new Error('Failed to fetch surge patterns');
    return response.json();
};

export const fetchDepartmentTrends = async () => {
    const response = await fetch(`${API_BASE_URL}/analytics/department-trends`);
    if (!response.ok) throw new Error('Failed to fetch department trends');
    return response.json();
};

export const fetchAdmissionPredictions = async () => {
    const response = await fetch(`${API_BASE_URL}/analytics/admission-predictions`);
    if (!response.ok) throw new Error('Failed to fetch admission predictions');
    return response.json();
};

export const fetchEnvironmentalImpact = async () => {
    const response = await fetch(`${API_BASE_URL}/analytics/environmental-impact`);
    if (!response.ok) throw new Error('Failed to fetch environmental impact');
    return response.json();
};

// Inventory API
export const fetchInventoryStatus = async () => {
    const response = await fetch(`${API_BASE_URL}/inventory/status`);
    if (!response.ok) throw new Error('Failed to fetch inventory status');
    return response.json();
};

export const fetchInventoryForecast = async () => {
    const response = await fetch(`${API_BASE_URL}/inventory/forecast`);
    if (!response.ok) throw new Error('Failed to fetch inventory forecast');
    return response.json();
};

// Reports API
export const fetchReportsList = async () => {
    const response = await fetch(`${API_BASE_URL}/reports/list`);
    if (!response.ok) throw new Error('Failed to fetch reports list');
    return response.json();
};

export const generateDailyReport = async () => {
    const response = await fetch(`${API_BASE_URL}/reports/generate/daily`);
    if (!response.ok) throw new Error('Failed to generate daily report');
    return response.json();
};
