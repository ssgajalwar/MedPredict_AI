
import React, { useEffect, useState } from 'react';
import { Users, Package, Bed, AlertOctagon } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import MetricCard from './MetricCard';
import { fetchResourceStatus } from '../api/client';

const Resources = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const result = await fetchResourceStatus();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) return <div className="p-8 text-center">Loading Resources...</div>;
    if (error) return <div className="p-8 text-center text-red-500">Error: {error}</div>;

    const { recommended_staff, current_staff, staff_shortage, bed_occupancy_predicted, inventory_alert } = data;

    // Mocking time-series data based on current snapshot
    const staffGapData = [
        { time: '08:00', current: current_staff - 5, recommended: recommended_staff - 5 },
        { time: '12:00', current: current_staff, recommended: recommended_staff },
        { time: '16:00', current: current_staff - 2, recommended: recommended_staff + 5 },
        { time: '20:00', current: current_staff - 8, recommended: recommended_staff },
        { time: '00:00', current: current_staff - 10, recommended: recommended_staff - 10 },
    ];

    const inventoryData = [
        { day: 'Mon', stock: 100, demand: 80 },
        { day: 'Tue', stock: 90, demand: 85 },
        { day: 'Wed', stock: 80, demand: 95 },
        { day: 'Thu', stock: 120, demand: 100 },
        { day: 'Fri', stock: 110, demand: 130 },
    ];

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-slate-900">Resource Planning</h2>
                    <p className="text-slate-500 mt-1">Capacity management and inventory forecasting</p>
                </div>
            </div>

            {/* Top Row: Resource KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Staffing Level"
                    value={staff_shortage > 0 ? "Understaffed" : "Optimal"}
                    subtext={`Gap: -${staff_shortage} Nurses`}
                    icon={Users}
                    status={staff_shortage > 0 ? "warning" : "success"}
                />
                <MetricCard
                    title="Inventory Health"
                    value={inventory_alert === "Normal" ? "Healthy" : "Critical"}
                    subtext={inventory_alert === "Normal" ? "Stock levels optimal" : `Low: ${inventory_alert} `}
                    icon={Package}
                    status={inventory_alert === "Normal" ? "success" : "critical"}
                />
                <MetricCard
                    title="Bed Occupancy"
                    value={`${bed_occupancy_predicted}% `}
                    subtext="Predicted Peak"
                    icon={Bed}
                    trend={bed_occupancy_predicted > 85 ? 5 : -2}
                    status={bed_occupancy_predicted > 90 ? "critical" : "neutral"}
                />
                <MetricCard
                    title="Critical Alerts"
                    value={inventory_alert === "Normal" ? "None" : "1 Active"}
                    subtext={inventory_alert === "Normal" ? "System stable" : "Restock needed"}
                    icon={AlertOctagon}
                    status={inventory_alert === "Normal" ? "neutral" : "critical"}
                />
            </div>

            {/* Main Content: Comparison Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Staffing Gap Analysis</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={staffGapData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                <XAxis dataKey="time" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="current" name="Current Staff" stroke="#fbbf24" strokeWidth={3} />
                                <Line type="monotone" dataKey="recommended" name="AI Recommended" stroke="#0f172a" strokeWidth={3} strokeDasharray="5 5" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                    <h3 className="text-lg font-bold text-slate-800 mb-4">Inventory Demand Forecast</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={inventoryData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                                <XAxis dataKey="day" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Line type="monotone" dataKey="stock" name="Available Stock" stroke="#10b981" strokeWidth={3} />
                                <Line type="monotone" dataKey="demand" name="Predicted Demand" stroke="#ef4444" strokeWidth={3} strokeDasharray="5 5" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};
export default Resources;
