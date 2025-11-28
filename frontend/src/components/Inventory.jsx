import React, { useEffect, useState } from 'react';
import { fetchInventoryStatus, fetchInventoryForecast } from '../api/client';
import { Package, AlertOctagon, TrendingDown, CheckCircle, Search, Filter } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const Inventory = () => {
    const [statusData, setStatusData] = useState(null);
    const [forecastData, setForecastData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState('All');

    useEffect(() => {
        const loadData = async () => {
            try {
                const [status, forecast] = await Promise.all([
                    fetchInventoryStatus(),
                    fetchInventoryForecast()
                ]);
                setStatusData(status);
                setForecastData(forecast);
            } catch (error) {
                console.error("Failed to load inventory data", error);
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, []);

    if (loading) return (
        <div className="flex items-center justify-center h-96">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );

    const categories = ['All', ...Object.keys(statusData?.categories || {})];

    const getFilteredItems = () => {
        if (activeCategory === 'All') return statusData?.all_items || [];
        return statusData?.categories[activeCategory] || [];
    };

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Inventory Management</h2>
                    <p className="text-slate-500">Real-time stock tracking and predictive replenishment</p>
                </div>
                <div className="flex space-x-3">
                    <button className="px-4 py-2 bg-white border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 font-medium text-sm flex items-center">
                        <Filter className="w-4 h-4 mr-2" /> Filter
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm flex items-center shadow-sm shadow-blue-200">
                        <Package className="w-4 h-4 mr-2" /> Add Item
                    </button>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-500">Total Items</p>
                        <h3 className="text-3xl font-bold text-slate-900 mt-1">{statusData?.summary?.total_items}</h3>
                    </div>
                    <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                        <Package className="w-6 h-6 text-blue-500" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-500">Critical Low Stock</p>
                        <h3 className="text-3xl font-bold text-red-600 mt-1">{statusData?.summary?.critical_items}</h3>
                    </div>
                    <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center">
                        <AlertOctagon className="w-6 h-6 text-red-500" />
                    </div>
                </div>

                <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex items-center justify-between">
                    <div>
                        <p className="text-sm font-medium text-slate-500">Restock Recommended</p>
                        <h3 className="text-3xl font-bold text-orange-500 mt-1">{forecastData?.recommended_orders?.length || 0}</h3>
                    </div>
                    <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center">
                        <TrendingDown className="w-6 h-6 text-orange-500" />
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Inventory List */}
                <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                    <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        <h3 className="font-bold text-slate-800">Stock Levels</h3>

                        {/* Category Tabs */}
                        <div className="flex space-x-1 bg-slate-100 p-1 rounded-lg overflow-x-auto">
                            {categories.map(cat => (
                                <button
                                    key={cat}
                                    onClick={() => setActiveCategory(cat)}
                                    className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all whitespace-nowrap ${activeCategory === cat
                                            ? 'bg-white text-slate-900 shadow-sm'
                                            : 'text-slate-500 hover:text-slate-700'
                                        }`}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-100">
                                <tr>
                                    <th className="px-6 py-4">Item Name</th>
                                    <th className="px-6 py-4">Category</th>
                                    <th className="px-6 py-4">Stock</th>
                                    <th className="px-6 py-4">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100">
                                {getFilteredItems().slice(0, 8).map((item, idx) => (
                                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4 font-medium text-slate-900">{item.name}</td>
                                        <td className="px-6 py-4 text-slate-500">{item.category || 'General'}</td>
                                        <td className="px-6 py-4 font-mono text-slate-600">{item.quantity}</td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${item.quantity < 20
                                                    ? 'bg-red-100 text-red-800'
                                                    : item.quantity < 50
                                                        ? 'bg-yellow-100 text-yellow-800'
                                                        : 'bg-green-100 text-green-800'
                                                }`}>
                                                {item.quantity < 20 ? 'Critical' : item.quantity < 50 ? 'Low' : 'Good'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Forecast & Recommendations */}
                <div className="space-y-6">
                    {/* Forecast Chart */}
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <h3 className="font-bold text-slate-800 mb-4">Depletion Forecast</h3>
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={forecastData?.predicted_shortages} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="item" type="category" width={100} tick={{ fontSize: 11 }} />
                                    <Tooltip />
                                    <Bar dataKey="days_left" name="Days Left" fill="#f59e0b" radius={[0, 4, 4, 0]} barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Recommended Orders */}
                    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                        <h3 className="font-bold text-slate-800 mb-4">Smart Reorder</h3>
                        <div className="space-y-3">
                            {forecastData?.recommended_orders?.map((order, idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl border border-slate-100">
                                    <div>
                                        <p className="text-sm font-semibold text-slate-900">{order.item}</p>
                                        <p className="text-xs text-slate-500">Qty: {order.quantity}</p>
                                    </div>
                                    <button className="px-3 py-1.5 bg-white border border-slate-200 text-blue-600 text-xs font-bold rounded-lg hover:bg-blue-50 transition-colors">
                                        Order
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Inventory;
