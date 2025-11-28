import React from 'react';
import { Search, Bell, User } from 'lucide-react';

const Layout = ({ children }) => {
    return (
        <div className="flex-1 flex flex-col ml-64 bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 min-h-screen">
            {/* Top Header Bar */}
            <header className="bg-white border-b border-slate-200 px-8 py-4 sticky top-0 z-40 shadow-sm">
                <div className="flex items-center justify-between">
                    {/* Page Title */}
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
                    </div>

                    {/* Search and Actions */}
                    <div className="flex items-center space-x-6">
                        {/* Search Bar */}
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                            <input
                                type="text"
                                placeholder="Search here..."
                                className="pl-10 pr-4 py-2 w-80 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>

                        {/* Language Selector */}
                        <button className="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors">
                            <span className="text-2xl">🇺🇸</span>
                            <span className="text-sm font-medium text-slate-600">Eng (US)</span>
                        </button>

                        {/* Notifications */}
                        <button className="relative p-2 hover:bg-slate-50 rounded-lg transition-colors">
                            <Bell className="w-5 h-5 text-slate-600" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-orange-500 rounded-full"></span>
                        </button>

                        {/* User Profile */}
                        <div className="flex items-center space-x-3 pl-4 border-l border-slate-200">
                            <div className="text-right">
                                <p className="text-sm font-semibold text-slate-900">Admin</p>
                                <p className="text-xs text-slate-500">Hospital Admin</p>
                            </div>
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                                <User className="w-5 h-5 text-white" />
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content Area */}
            <main className="flex-1 p-8">
                {children}
            </main>
        </div>
    );
};

export default Layout;
