import React, { useEffect, useState } from 'react';
import { DollarSign, ShoppingCart, Package, Users, FileText, TrendingUp, MapPin, Activity } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import ColorfulMetricCard from './ColorfulMetricCard';
import { fetchDashboardOverview } from '../api/client';

const Dashboard = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadData = async () => {
            try {
                const result = await fetchDashboardOverview();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center h-96">
            <div className="text-center">
                <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-slate-600 font-medium">Loading Dashboard...</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-6 text-center">
            <p className="text-red-600 font-semibold">Error loading dashboard: {error}</p>
        </div>
    );

    const { sensory_data, analysis, forecast, real_data } = data;
    const { prediction, resources } = analysis;

    // Transform data for charts
    const forecastData = forecast?.forecasts?.map((f, i) => ({
        day: f.date || `Day ${i + 1}`,
        patients: f.predicted_patients,
        lowerBound: f.lower_bound,
        upperBound: f.upper_bound
    })) || [];

    // Revenue data (mock - replace with real data)
    const revenueData = [
        { month: 'Mon', online: 8000, offline: 6000 },
        { month: 'Tue', online: 9500, offline: 8500 },
        { month: 'Wed', online: 11000, offline: 7000 },
        { month: 'Thu', online: 10000, offline: 9000 },
        { month: 'Fri', online: 12000, offline: 10500 },
        { month: 'Sat', online: 13500, offline: 9500 },
        { month: 'Sun', online: 14000, offline: 11000 },
    ];

    // Customer satisfaction data
    const satisfactionData = [
        { month: 'Jan', lastMonth: 3000, thisMonth: 2500 },
        { month: 'Feb', lastMonth: 3200, thisMonth: 3000 },
        { month: 'Mar', lastMonth: 2800, thisMonth: 3800 },
        { month: 'Apr', lastMonth: 3500, thisMonth: 3200 },
        { month: 'May', lastMonth: 3300, thisMonth: 4000 },
        { month: 'Jun', lastMonth: 3800, thisMonth: 3600 },
    ];

    // Target vs Reality
    const targetData = [
        { name: 'Week 1', reality: 8500, target: 9500 },
        { name: 'Week 2', reality: 9200, target: 9800 },
        { name: 'Week 3', reality: 10500, target: 10200 },
        { name: 'Week 4', reality: 9800, target: 10500 },
        { name: 'Week 5', reality: 11200, target: 11000 },
        { name: 'Week 6', reality: 10800, target: 11500 },
    ];

    // Volume vs Service Level
    const volumeData = [
        { day: 'Mon', volume: 1200, service: 850 },
        { day: 'Tue', volume: 1350, service: 920 },
        { day: 'Wed', volume: 980, service: 680 },
        { day: 'Thu', volume: 1180, service: 800 },
        { day: 'Fri', volume: 1420, service: 950 },
        { day: 'Sat', volume: 1150, service: 780 },
        { day: 'Sun', volume: 890, service: 620 },
    ];

    // Top departments (using real data if available)
    const topDepartments = real_data?.patients?.by_department ?
        Object.entries(real_data.patients.by_department)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 4)
            .map(([dept, count], index) => ({
                rank: index + 1,
                name: `Department ${dept}`,
                popularity: count,
                percentage: Math.min(100, (count / 50) * 100)
            })) :
        [
            { rank: 1, name: 'Emergency', popularity: 850, percentage: 85 },
            { rank: 2, name: 'Cardiology', popularity: 720, percentage: 72 },
            { rank: 3, name: 'Pediatrics', popularity: 580, percentage: 58 },
            { rank: 4, name: 'Orthopedics', popularity: 450, percentage: 45 },
        ];

    const barColors = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B'];

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-sm font-semibold text-slate-600 mb-1">Today's Overview</h2>
                    <p className="text-xs text-slate-400">Hospital Summary</p>
                </div>
                <button className="px-4 py-2 bg-white border-2 border-blue-500 text-blue-600 rounded-lg text-sm font-semibold hover:bg-blue-50 transition-colors">
                    Export Report
                </button>
            </div>

            {/* Colorful Metrics Row */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
                <ColorfulMetricCard
                    title="Total Patients"
                    value={real_data?.patients?.total_patients || prediction.total_patients}
                    change={prediction.surge_percentage}
                    changeLabel="from yesterday"
                    icon={Users}
                    color="pink"
                />
                <ColorfulMetricCard
                    title="Staff on Duty"
                    value={real_data?.staff?.available_staff || resources.current_staff}
                    change={-5}
                    changeLabel="from yesterday"
                    icon={Users}
                    color="orange"
                />
                <ColorfulMetricCard
                    title="Bed Occupancy"
                    value={`${resources.bed_occupancy_predicted}%`}
                    change={12}
                    changeLabel="from yesterday"
                    icon={Activity}
                    color="green"
                />
                <ColorfulMetricCard
                    title="Critical Cases"
                    value={real_data?.patients?.admissions || 264}
                    change={8}
                    changeLabel="from yesterday"
                    icon={TrendingUp}
                    color="purple"
                />
            </div>

            {/* Charts Grid - Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Patient Forecast */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-5">
                        <h3 className="text-base font-bold text-slate-900">Patient Forecast</h3>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={forecastData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <Tooltip
                                    contentStyle={{
                                        borderRadius: '12px',
                                        border: 'none',
                                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                                        fontSize: '12px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="patients"
                                    stroke="#8b5cf6"
                                    strokeWidth={3}
                                    dot={{ fill: '#8b5cf6', r: 4 }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Visitor Insights (Area Chart) */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-5">
                        <h3 className="text-base font-bold text-slate-900">Visitor Insights</h3>
                    </div>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={satisfactionData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} />
                                <Legend wrapperStyle={{ fontSize: '12px' }} />
                                <Line type="monotone" dataKey="lastMonth" stroke="#8b5cf6" strokeWidth={2.5} name="Last Month" />
                                <Line type="monotone" dataKey="thisMonth" stroke="#3b82f6" strokeWidth={2.5} name="This Month" />
                                <Line type="monotone" dataKey="thisMonth" stroke="#10b981" strokeWidth={2.5} name="Forecast" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Charts Grid - Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Total Revenue */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Daily Patient Flow</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={revenueData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} />
                                <Legend wrapperStyle={{ fontSize: '11px' }} />
                                <Bar dataKey="online" fill="#3b82f6" radius={[6, 6, 0, 0]} name="Walk-in" />
                                <Bar dataKey="offline" fill="#10b981" radius={[6, 6, 0, 0]} name="Appointment" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Customer Satisfaction */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Patient Satisfaction</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={satisfactionData}>
                                <defs>
                                    <linearGradient id="colorLast" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorThis" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} />
                                <Legend wrapperStyle={{ fontSize: '11px' }} />
                                <Area type="monotone" dataKey="lastMonth" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorLast)" name="Last Month" />
                                <Area type="monotone" dataKey="thisMonth" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorThis)" name="This Month" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex items-center justify-around mt-4 pt-4 border-t border-slate-100">
                        <div className="text-center">
                            <p className="text-xs text-slate-500 mb-1">Last Month</p>
                            <p className="text-sm font-bold text-slate-900">$3,054</p>
                        </div>
                        <div className="text-center">
                            <p className="text-xs text-slate-500 mb-1">This Month</p>
                            <p className="text-sm font-bold text-slate-900">$4,504</p>
                        </div>
                    </div>
                </div>

                {/* Target vs Reality */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Target vs Reality</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={targetData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} />
                                <Bar dataKey="reality" fill="#10b981" radius={[6, 6, 0, 0]} />
                                <Bar dataKey="target" fill="#fbbf24" radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex items-center justify-around mt-4 pt-4 border-t border-slate-100">
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 rounded-full bg-green-500"></div>
                            <div>
                                <p className="text-xs text-slate-500">Reality Sales</p>
                                <p className="text-sm font-bold text-slate-900">8,823</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                            <div>
                                <p className="text-xs text-slate-500">Target Sales</p>
                                <p className="text-sm font-bold text-slate-900">12,122</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Top Departments */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Top Departments</h3>
                    <div className="space-y-4">
                        {topDepartments.map((dept, index) => (
                            <div key={dept.rank}>
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center space-x-3">
                                        <span className="text-xs font-semibold text-slate-400 w-6">{String(dept.rank).padStart(2, '0')}</span>
                                        <span className="text-sm font-medium text-slate-700">{dept.name}</span>
                                    </div>
                                    <span className="px-2.5 py-1 bg-slate-50 text-slate-700 text-xs font-semibold rounded-full">{dept.percentage}%</span>
                                </div>
                                <div className="relative w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                                    <div
                                        className="absolute left-0 top-0 h-full rounded-full transition-all duration-500"
                                        style={{
                                            width: `${dept.percentage}%`,
                                            background: barColors[index % barColors.length]
                                        }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Regional Distribution Map */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Patient Distribution</h3>
                    <div className="flex items-center justify-center h-48">
                        <div className="text-center">
                            <MapPin className="w-16 h-16 text-blue-500 mx-auto mb-3" />
                            <p className="text-sm font-medium text-slate-600">Mumbai Region</p>
                            <p className="text-xs text-slate-400 mt-1">Interactive map coming soon</p>
                        </div>
                    </div>
                </div>

                {/* Volume vs Service Level */}
                <div className="bg-white rounded-2xl p-6 border-2 border-slate-100 shadow-sm hover:shadow-md transition-shadow">
                    <h3 className="text-base font-bold text-slate-900 mb-5">Volume vs Service Level</h3>
                    <div className="h-48">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={volumeData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} tickLine={false} axisLine={false} />
                                <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: '12px' }} />
                                <Bar dataKey="volume" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                                <Bar dataKey="service" fill="#10b981" radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex items-center justify-around mt-4 pt-4 border-t border-slate-100">
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                            <div>
                                <p className="text-xs text-slate-500">Volume</p>
                                <p className="text-sm font-bold text-slate-900">1,195</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 rounded-full bg-green-500"></div>
                            <div>
                                <p className="text-xs text-slate-500">Services</p>
                                <p className="text-sm font-bold text-slate-900">635</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
