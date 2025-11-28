import React, { useEffect, useState } from 'react';
import { fetchReportsList, generateDailyReport } from '../api/client';
import { FileText, Download, RefreshCw, Calendar, CheckCircle, Clock, AlertOctagon } from 'lucide-react';

const Reports = () => {
    const [reports, setReports] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    const loadReports = async () => {
        try {
            const data = await fetchReportsList();
            setReports(data);
        } catch (error) {
            console.error("Failed to load reports", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadReports();
    }, []);

    const handleGenerateReport = async () => {
        setGenerating(true);
        try {
            await generateDailyReport();
            // In a real app, we would add the new report to the list
            // For now, just simulate a refresh
            setTimeout(() => {
                loadReports();
                setGenerating(false);
            }, 1500);
        } catch (error) {
            console.error("Failed to generate report", error);
            setGenerating(false);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center h-96">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h2 className="text-2xl font-bold text-slate-900">Reports & Insights</h2>
                    <p className="text-slate-500">Automated daily summaries and performance analysis</p>
                </div>
                <button
                    onClick={handleGenerateReport}
                    disabled={generating}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 font-semibold shadow-lg shadow-blue-200 flex items-center transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                >
                    {generating ? (
                        <>
                            <RefreshCw className="w-5 h-5 mr-2 animate-spin" /> Generating...
                        </>
                    ) : (
                        <>
                            <FileText className="w-5 h-5 mr-2" /> Generate Daily Report
                        </>
                    )}
                </button>
            </div>

            {/* Recent Reports Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Daily Reports List */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h3 className="font-bold text-slate-800 flex items-center">
                                <Clock className="w-5 h-5 mr-2 text-blue-500" /> Recent Daily Summaries
                            </h3>
                        </div>
                        <div className="divide-y divide-slate-100">
                            {reports?.daily_reports?.map((report) => (
                                <div key={report.id} className="p-5 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-10 h-10 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 group-hover:bg-blue-100 transition-colors">
                                            <FileText className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-slate-900">{report.title}</h4>
                                            <p className="text-sm text-slate-500">{report.date} • {report.status}</p>
                                        </div>
                                    </div>
                                    <button className="p-2 text-slate-400 hover:text-blue-600 transition-colors">
                                        <Download className="w-5 h-5" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h3 className="font-bold text-slate-800 flex items-center">
                                <Calendar className="w-5 h-5 mr-2 text-purple-500" /> Monthly Performance
                            </h3>
                        </div>
                        <div className="divide-y divide-slate-100">
                            {reports?.monthly_reports?.map((report) => (
                                <div key={report.id} className="p-5 hover:bg-slate-50 transition-colors flex items-center justify-between group">
                                    <div className="flex items-center space-x-4">
                                        <div className="w-10 h-10 rounded-full bg-purple-50 flex items-center justify-center text-purple-600 group-hover:bg-purple-100 transition-colors">
                                            <Calendar className="w-5 h-5" />
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-slate-900">{report.title}</h4>
                                            <p className="text-sm text-slate-500">{report.date} • {report.status}</p>
                                        </div>
                                    </div>
                                    <button className="p-2 text-slate-400 hover:text-purple-600 transition-colors">
                                        <Download className="w-5 h-5" />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Incident Reports & Stats */}
                <div className="space-y-6">
                    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                        <h3 className="font-bold text-slate-800 mb-4">Report Statistics</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                                <span className="text-slate-600 font-medium">Total Generated</span>
                                <span className="text-xl font-bold text-slate-900">124</span>
                            </div>
                            <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                                <span className="text-slate-600 font-medium">Pending Review</span>
                                <span className="text-xl font-bold text-orange-500">3</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100 bg-red-50">
                            <h3 className="font-bold text-red-800 flex items-center">
                                <AlertOctagon className="w-5 h-5 mr-2" /> Critical Incidents
                            </h3>
                        </div>
                        <div className="divide-y divide-slate-100">
                            {reports?.incident_reports?.map((report) => (
                                <div key={report.id} className="p-5 hover:bg-slate-50 transition-colors">
                                    <h4 className="font-semibold text-slate-900 mb-1">{report.title}</h4>
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs font-medium px-2 py-1 bg-red-100 text-red-700 rounded-full">
                                            {report.severity} Severity
                                        </span>
                                        <span className="text-xs text-slate-400">{report.date}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Reports;
