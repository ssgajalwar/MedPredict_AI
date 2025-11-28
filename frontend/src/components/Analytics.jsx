import React, { useEffect, useState } from 'react';
import { fetchSurgePatterns, fetchDepartmentTrends, fetchAdmissionPredictions, fetchEnvironmentalImpact } from '../api/client';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, AreaChart, Area } from 'recharts';
import { Activity, AlertTriangle, CloudRain, Thermometer, Calendar, TrendingUp } from 'lucide-react';

const Analytics = () => {
    const [surgeData, setSurgeData] = useState(null);
    const [deptData, setDeptData] = useState(null);
    const [predictionData, setPredictionData] = useState(null);
    const [envData, setEnvData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadAllData = async () => {
            try {
                const [surge, dept, pred, env] = await Promise.all([
                    fetchSurgePatterns(),
                    fetchDepartmentTrends(),
                    fetchAdmissionPredictions(),
                    fetchEnvironmentalImpact()
                ]);
                setSurgeData(surge);
                setDeptData(dept);
                setPredictionData(pred);
                setEnvData(env);
            } catch (error) {
                console.error("Failed to load analytics data", error);
            } finally {
                setLoading(false);
            }
        };
        loadAllData();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center h-96">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header */}
            <div>
                <h2 className="text-2xl font-bold text-slate-900">Predictive Analytics</h2>
                <p className="text-slate-500">AI-driven insights for patient surges and resource planning</p>
            </div>

            {/* Environmental & Surge Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Pollution Impact */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-slate-700">Environmental Impact</h3>
                        <CloudRain className="w-5 h-5 text-blue-500" />
                    </div>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-500">Air Quality (AQI)</span>
                            <span className={`text-lg font-bold ${envData?.air_quality?.aqi_level > 200 ? 'text-red-500' : 'text-green-500'}`}>
                                {envData?.air_quality?.aqi_level || 'N/A'}
                            </span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-2">
                            <div
                                className={`h-2 rounded-full ${envData?.air_quality?.aqi_level > 200 ? 'bg-red-500' : 'bg-green-500'}`}
                                style={{ width: `${Math.min(100, (envData?.air_quality?.aqi_level / 500) * 100)}%` }}
                            ></div>
                        </div>
                        <p className="text-xs text-slate-400">
                            {envData?.health_advisory}
                        </p>
                    </div>
                </div>

                {/* Festival Impact */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-slate-700">Upcoming Events</h3>
                        <Calendar className="w-5 h-5 text-purple-500" />
                    </div>
                    <div className="space-y-3">
                        {surgeData?.surge_causes?.festivals?.slice(0, 3).map((event, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 bg-purple-50 rounded-lg">
                                <span className="text-sm font-medium text-purple-900">{event.name}</span>
                                <span className="text-xs bg-white px-2 py-1 rounded text-purple-600 font-bold">
                                    +{Math.round((event.expected_surge - 1) * 100)}% Surge
                                </span>
                            </div>
                        ))}
                        {(!surgeData?.surge_causes?.festivals || surgeData.surge_causes.festivals.length === 0) && (
                            <p className="text-sm text-slate-400">No major events detected nearby.</p>
                        )}
                    </div>
                </div>

                {/* Epidemic Watch */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-slate-700">Epidemic Watch</h3>
                        <AlertTriangle className="w-5 h-5 text-orange-500" />
                    </div>
                    <div className="space-y-3">
                        {surgeData?.surge_causes?.epidemics?.length > 0 ? (
                            surgeData.surge_causes.epidemics.slice(0, 3).map((epi, idx) => (
                                <div key={idx} className="flex items-center space-x-3">
                                    <div className="w-2 h-2 rounded-full bg-orange-500"></div>
                                    <div>
                                        <p className="text-sm font-medium text-slate-700 capitalize">{epi.type}</p>
                                        <p className="text-xs text-slate-400">Source: {epi.source}</p>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="flex flex-col items-center justify-center h-24 text-slate-400">
                                <Activity className="w-8 h-8 mb-2 opacity-20" />
                                <span className="text-sm">No active alerts</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Admission Predictions */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <h3 className="font-bold text-slate-800 mb-6">7-Day Admission Forecast</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={predictionData?.predictions}>
                                <defs>
                                    <linearGradient id="colorAdmissions" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="predicted_admissions"
                                    stroke="#3b82f6"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorAdmissions)"
                                    name="Predicted Admissions"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Department Trends */}
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <h3 className="font-bold text-slate-800 mb-6">Department Utilization</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={deptData?.departments} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
                                <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} />
                                <YAxis dataKey="name" type="category" width={100} stroke="#64748b" fontSize={12} tickLine={false} />
                                <Tooltip
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Bar dataKey="utilization" name="Utilization %" fill="#8b5cf6" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Analytics;
