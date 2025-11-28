import React from 'react';
import { LayoutDashboard, TrendingUp, Users, Package, BarChart3, MessageSquare, Settings, LogOut, Activity, Sparkles } from 'lucide-react';
import { cn } from '../lib/utils';

const Sidebar = ({ activeTab, setActiveTab }) => {
    const menuItems = [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { id: 'analytics', label: 'Analytics', icon: TrendingUp },
        { id: 'resources', label: 'Resources', icon: Users },
        { id: 'inventory', label: 'Inventory', icon: Package },
        { id: 'reports', label: 'Reports', icon: BarChart3 },
        { id: 'broadcast', label: 'Broadcast', icon: MessageSquare },
    ];

    const bottomItems = [
        { id: 'settings', label: 'Settings', icon: Settings },
        { id: 'signout', label: 'Sign Out', icon: LogOut },
    ];

    return (
        <div className="w-64 bg-white border-r border-slate-200 h-screen fixed left-0 top-0 flex flex-col shadow-lg z-50">
            {/* Logo and Branding */}
            <div className="p-6 border-b border-slate-200">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-teal-500 flex items-center justify-center shadow-lg">
                        <Activity className="w-6 h-6 text-white" strokeWidth={2.5} />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-teal-600 bg-clip-text text-transparent">
                            MedPredict AI
                        </h1>
                        <p className="text-xs text-slate-400">Intelligence Platform</p>
                    </div>
                </div>
            </div>

            {/* Main Navigation */}
            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    return (
                        <button
                            key={item.id}
                            onClick={() => setActiveTab(item.id)}
                            className={cn(
                                "w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group",
                                isActive
                                    ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/30"
                                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                            )}
                        >
                            <Icon className={cn("w-5 h-5", isActive ? "text-white" : "text-slate-400 group-hover:text-slate-600")} />
                            <span className="font-medium text-sm">{item.label}</span>
                        </button>
                    );
                })}
            </nav>

            {/* Bottom Section */}
            <div className="p-4 border-t border-slate-200 space-y-1">
                {bottomItems.map((item) => {
                    const Icon = item.icon;
                    return (
                        <button
                            key={item.id}
                            onClick={() => item.id === 'signout' ? console.log('Sign out') : setActiveTab(item.id)}
                            className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-all duration-200 group"
                        >
                            <Icon className="w-5 h-5 text-slate-400 group-hover:text-slate-600" />
                            <span className="font-medium text-sm">{item.label}</span>
                        </button>
                    );
                })}
            </div>

            {/* Upgrade Card */}
            <div className="m-4 p-5 rounded-2xl bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 text-white shadow-xl">
                <div className="flex justify-center mb-3">
                    <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                        <Sparkles className="w-6 h-6 text-white" />
                    </div>
                </div>
                <h3 className="text-center font-bold text-base mb-1">MedPredict Pro</h3>
                <p className="text-center text-xs text-white/80 mb-4">
                    Get access to all premium features today!
                </p>
                <button className="w-full py-2.5 bg-white text-blue-600 rounded-lg font-semibold text-sm hover:bg-white/90 transition-colors shadow-lg">
                    Upgrade Now
                </button>
            </div>
        </div>
    );
};

export default Sidebar;
